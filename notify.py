#!/usr/bin/env python3
"""
Claude Code Notification Script
Displays sprite notifications using tkinter.
"""

import sys
import json
import argparse
import select
from pathlib import Path
import tkinter as tk


def send_notification(title, message, timeout=60, icon_path=None):
    """
    Display a sprite notification using tkinter.

    Args:
        title: Notification title
        message: Notification message
        timeout: Duration in seconds (default: 60)
        icon_path: Path to image file (optional)
    """
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

                # Bind left click to close window
                def close_window(event=None):
                    window.destroy()
                    window.quit()

                window.bind('<Button-1>', close_window)
                canvas.bind('<Button-1>', close_window)
                text_widget.bind('<Button-1>', close_window)

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


def main():
    parser = argparse.ArgumentParser(
        description='Send desktop notifications for Claude Code hooks'
    )
    parser.add_argument(
        'hook_type',
        choices=['permission_prompt', 'idle_prompt', 'stop', 'permission_request'],
        help='Type of hook that triggered the notification'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=60,
        help='Notification timeout in seconds (default: 10)'
    )
    parser.add_argument(
        '--message',
        type=str,
        help='Custom notification message (overrides stdin message)'
    )

    args = parser.parse_args()

    # Read hook input from stdin
    hook_input = read_hook_input()

    # Extract message from hook input if available
    stdin_message = hook_input.get('message', '')

    # Get the script directory and icon paths
    script_dir = Path(__file__).parent
    icon_dir = script_dir / 'images'

    # Define default messages and images for each hook type
    notifications_config = {
        'permission_prompt': {
            'title': 'Claude Code: Permission Required',
            'message': args.message or stdin_message or 'Claude is requesting permission to perform an action.',
            'icon': icon_dir / 'zunmon_3015_small.png'
        },
        'permission_request': {
            'title': 'Claude Code: Permission Requested',
            'message': args.message or stdin_message or 'Claude is requesting permission to use a tool.',
            'icon': icon_dir / 'zunmon_3015_small.png'
        },
        'idle_prompt': {
            'title': 'Claude Code: Waiting for Input',
            'message': args.message or stdin_message or 'Claude is idle and waiting for your response.',
            'icon': icon_dir / 'zunmon_3016_small.png'
        },
        'stop': {
            'title': 'Claude Code: Stopped',
            'message': args.message or stdin_message or 'Claude has stopped execution.',
            'icon': icon_dir / 'zunmon_3001_small.png'
        }
    }

    config = notifications_config.get(args.hook_type)
    if not config:
        print(f"Unknown hook type: {args.hook_type}", file=sys.stderr)
        return 1

    return send_notification(
        title=config['title'],
        message=config['message'],
        timeout=args.timeout,
        icon_path=config.get('icon')
    )


if __name__ == '__main__':
    sys.exit(main())
