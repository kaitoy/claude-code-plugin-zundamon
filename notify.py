#!/usr/bin/env python3
"""
Claude Code Notification Script
Displays sprite notifications using tkinter.
"""

import os
import sys
import json
import argparse
import random
import re
import select
import subprocess
import threading
import collections
from pathlib import Path
import tkinter as tk


def load_plugin_config():
    duration = int(os.environ.get('CLAUDE_PLUGIN_OPTION_NOTIFICATION_DURATION', 60))
    voice_raw = os.environ.get('CLAUDE_PLUGIN_OPTION_VOICE_ENABLED', 'true')
    voice_enabled = voice_raw.lower() not in ('false', '0', '')
    suppress_raw = os.environ.get('CLAUDE_PLUGIN_OPTION_SUPPRESS_STOP_WHILE_ASYNC_AGENTS', 'true')
    suppress_pending_async = suppress_raw.lower() not in ('false', '0', '')
    return {
        'notification_duration': duration,
        'voice_enabled': voice_enabled,
        'suppress_pending_async': suppress_pending_async,
    }


def play_sound(sound_path):
    if not sound_path or not Path(sound_path).exists():
        return

    def _play():
        try:
            if sys.platform == 'win32':
                import winsound
                winsound.PlaySound(str(sound_path), winsound.SND_FILENAME)
            elif sys.platform == 'darwin':
                subprocess.run(['afplay', str(sound_path)], check=False)
            else:
                subprocess.run(['aplay', str(sound_path)], check=False)
        except Exception as e:
            print(f"Warning: Could not play sound: {e}", file=sys.stderr)

    threading.Thread(target=_play, daemon=True).start()


def send_notification(title, message, timeout=60, icon_path=None, sound_path=None):
    """
    Display a sprite notification using tkinter.

    Args:
        title: Notification title
        message: Notification message
        timeout: Duration in seconds (default: 60)
        icon_path: Path to image file (optional)
    """
    play_sound(sound_path)

    try:
        # Create window
        window = tk.Tk()
        window.title(title)
        window.attributes('-topmost', True)
        window.attributes('-transparentcolor', '#2d2d2d')
        window.overrideredirect(True)
        window.configure(bg='#2d2d2d')

        # Load and display image
        if icon_path and Path(icon_path).exists():
            try:
                img = tk.PhotoImage(file=str(icon_path))
                img_width = img.width()
                img_height = img.height()

                canvas = tk.Canvas(window, bg='#2d2d2d', height=img_height, width=img_width)
                canvas.create_image(0, 0, image=img, anchor=tk.NW)
                canvas.place(x=-2, y=-2)

                # Bind left click to close window
                def close_window(event=None):
                    window.destroy()
                    window.quit()

                if message:
                    # Create text widget for message
                    text_widget = tk.Text(
                        canvas,
                        font=("Meiryo UI", 15),
                        spacing2=-2,
                        wrap='word',
                        bg="white",
                        fg="#333333",
                        width=17,
                        height=3,
                        borderwidth=2,
                        relief='solid',
                        highlightthickness=2,
                        highlightbackground="green",
                        highlightcolor='green',
                        padx=5,
                        pady=5
                    )
                    text_widget.tag_configure("center", justify='center')
                    text_widget.insert(1.0, message, 'center')
                    text_widget.config(state='disabled')
                    canvas.create_window(
                        img_width / 2,
                        img_height - 100,
                        window=text_widget,
                        anchor=tk.S,
                        width=img_width - 4,
                    )
                    text_widget.bind('<Button-1>', close_window)

                window.bind('<Button-1>', close_window)
                canvas.bind('<Button-1>', close_window)
                window.bind('<b>', close_window)

                # Position window at bottom-right of screen
                screen_width = window.winfo_screenwidth()
                screen_height = window.winfo_screenheight()
                x = screen_width - img_width - 50
                y = screen_height - img_height - 50
                window.geometry(f'{img_width}x{img_height}+{x}+{y}')

            except Exception as e:
                print(f"Error loading image: {e}", file=sys.stderr)
                return 1
        else:
            print(f"Error: Image not found: {icon_path}", file=sys.stderr)
            return 1

        # Auto-close after timeout
        timeout_ms = int(timeout * 1000)
        window.after(timeout_ms, lambda: (window.destroy(), window.quit()))

        # Start main loop
        window.mainloop()

        return 0
    except Exception as e:
        print(f"Error displaying notification: {e}", file=sys.stderr)
        return 1


def read_hook_input():
    """
    Read hook input from stdin if available.

    Returns:
        dict: Parsed JSON from stdin, or empty dict if no input
    """
    try:
        # Check if stdin has data (non-blocking on Unix, always try on Windows)
        if sys.platform == 'win32':
            # On Windows, try to read stdin
            if not sys.stdin.isatty():
                stdin_data = sys.stdin.read()
                if stdin_data.strip():
                    return json.loads(stdin_data)
        else:
            # On Unix-like systems, use select
            if select.select([sys.stdin], [], [], 0.0)[0]:
                stdin_data = sys.stdin.read()
                if stdin_data.strip():
                    return json.loads(stdin_data)
    except (json.JSONDecodeError, Exception) as e:
        print(f"Warning: Could not parse stdin JSON: {e}", file=sys.stderr)

    return {}


_TASK_NOTIFICATION_RE = re.compile(
    r'<task-notification>.*?<task-id>\s*(.*?)\s*</task-id>',
    re.DOTALL,
)
# Cap how many transcript lines we scan: keeps per-turn overhead bounded on
# long sessions, and lets a stuck/crashed agent's launch record age out of
# the window instead of suppressing the stop notification forever.
_TRANSCRIPT_TAIL_LINES = 2000


def _extract_launched_agent_id(entry):
    """Return the agentId if this transcript line is an async subagent launch."""
    tool_use_result = entry.get('toolUseResult')
    if not isinstance(tool_use_result, dict):
        return None
    if tool_use_result.get('isAsync') is True and tool_use_result.get('status') == 'async_launched':
        agent_id = tool_use_result.get('agentId')
        if isinstance(agent_id, str) and agent_id:
            return agent_id
    return None


def _extract_completed_agent_ids(entry):
    """Return the set of task-ids reported as finished by <task-notification> messages."""
    if entry.get('type') != 'user':
        return set()
    message = entry.get('message')
    if not isinstance(message, dict):
        return set()

    content = message.get('content')
    texts = []
    if isinstance(content, str):
        texts.append(content)
    elif isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get('type') == 'text':
                text = block.get('text')
                if isinstance(text, str):
                    texts.append(text)

    found = set()
    for text in texts:
        if '<task-notification>' not in text:
            continue
        for match in _TASK_NOTIFICATION_RE.finditer(text):
            task_id = match.group(1)
            if task_id:
                found.add(task_id)
    return found


def has_pending_async_subagents(hook_input, tail_lines=_TRANSCRIPT_TAIL_LINES):
    """
    Best-effort check for async subagents (e.g. Agent tool forks) launched in
    this transcript that have not yet reported completion via a
    <task-notification> message. Relies on undocumented Claude Code internals,
    so any failure to read/parse the transcript falls back to False (i.e. show
    the notification as before) rather than suppressing it incorrectly.
    """
    transcript_path = hook_input.get('transcript_path')
    if not transcript_path:
        return False

    try:
        path = Path(transcript_path).expanduser()
        with path.open('r', encoding='utf-8', errors='replace') as f:
            lines = collections.deque(f, maxlen=tail_lines) if tail_lines else f

            launched = set()
            completed = set()
            for raw_line in lines:
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(entry, dict):
                    continue

                agent_id = _extract_launched_agent_id(entry)
                if agent_id:
                    launched.add(agent_id)

                completed |= _extract_completed_agent_ids(entry)

        return bool(launched - completed)
    except Exception as e:
        print(f"Warning: Could not evaluate transcript for pending async agents: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Send desktop notifications for Claude Code hooks'
    )
    parser.add_argument(
        'hook_type',
        choices=['permission_prompt', 'idle_prompt', 'stop', 'permission_request'],
        help='Type of hook that triggered the notification'
    )
    plugin_config = load_plugin_config()

    parser.add_argument(
        '--timeout',
        type=int,
        default=plugin_config['notification_duration'],
        help=f"Notification timeout in seconds (default: {plugin_config['notification_duration']})"
    )
    parser.add_argument(
        '--message',
        type=str,
        help='Custom notification message (overrides stdin message)'
    )
    parser.add_argument(
        '--background',
        action='store_true',
        help=argparse.SUPPRESS
    )

    args = parser.parse_args()

    script_dir = Path(__file__).parent
    icon_dir = script_dir / 'images'
    sound_dir = script_dir / 'sounds'

    # Define default messages, images, and sounds for each hook type
    notifications_config = {
        'permission_prompt': {
            'title': 'Claude Code: Permission Required',
            'default_message': 'Claude is requesting permission to perform an action.',
            'icon': icon_dir / 'zunmon_3015_small.png',
            'sound': random.choice([sound_dir / 'ask.wav', sound_dir / 'oi.wav', sound_dir / 'decision.wav', sound_dir / 'ask2.wav', sound_dir / 'ask3.wav'])
        },
        'permission_request': {
            'title': 'Claude Code: Permission Requested',
            'default_message': 'Claude is requesting permission to use a tool.',
            'icon': icon_dir / 'zunmon_3015_small.png',
            'sound': sound_dir / 'ask.wav'
        },
        'idle_prompt': {
            'title': 'Claude Code: Waiting for Input',
            'default_message': 'Claude is idle and waiting for your response.',
            'show_message': False,
            'icon': icon_dir / 'zunmon_3016_small.png',
            'sound': sound_dir / 'waiting.wav'
        },
        'stop': {
            'title': 'Claude Code: Stopped',
            'default_message': 'Claude has stopped execution.',
            'show_message': False,
            'icon': icon_dir / 'zunmon_3001_small.png',
            'sound': random.choice([sound_dir / 'done.wav', sound_dir / 'perfect.wav'])
        }
    }

    notif_config = notifications_config.get(args.hook_type)
    if not notif_config:
        print(f"Unknown hook type: {args.hook_type}", file=sys.stderr)
        return 1

    if not args.background:
        # Launcher mode: read stdin, resolve message, spawn detached worker
        hook_input = read_hook_input()

        if (args.hook_type == 'stop'
                and plugin_config['suppress_pending_async']
                and has_pending_async_subagents(hook_input)):
            print("Info: Skipping stop notification; async subagent(s) are still pending.", file=sys.stderr)
            return 0

        message = args.message or hook_input.get('message', '') or notif_config['default_message']

        cmd = [
            sys.executable,
            str(Path(__file__).resolve()),
            args.hook_type,
            '--message', message,
            '--timeout', str(args.timeout),
            '--background',
        ]
        kwargs = {
            'stdin': subprocess.DEVNULL,
            'stdout': subprocess.DEVNULL,
            'stderr': subprocess.DEVNULL,
        }
        if sys.platform == 'win32':
            kwargs['creationflags'] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            kwargs['start_new_session'] = True

        subprocess.Popen(cmd, **kwargs)
        return 0

    # Worker mode: display notification
    sound_path = notif_config.get('sound') if plugin_config['voice_enabled'] else None
    show_message = notif_config.get('show_message', True)
    message = (args.message or notif_config['default_message']) if show_message else None
    return send_notification(
        title=notif_config['title'],
        message=message,
        timeout=args.timeout,
        icon_path=notif_config.get('icon'),
        sound_path=sound_path
    )


if __name__ == '__main__':
    sys.exit(main())
