#!/usr/bin/env python3
"""
Claude Code Notification Script
Displays desktop notifications for Claude Code hooks using Plyer.
"""

import sys
import json
import argparse
import select
from pathlib import Path
from plyer import notification


def send_notification(title, message, timeout=5, icon_path=None):
    """
    Send a desktop notification.

    Args:
        title: Notification title
        message: Notification message
        timeout: Duration in seconds (default: 10)
        icon_path: Path to icon file (optional)
    """
    try:
        kwargs = {
            'title': title,
            'message': message,
            'app_name': 'Claude Code',
            'timeout': timeout
        }

        # Add icon if path is provided and file exists
        if icon_path and Path(icon_path).exists():
            kwargs['app_icon'] = str(Path(icon_path).resolve())

        notification.notify(**kwargs)

        return 0
    except Exception as e:
        print(f"Error sending notification: {e}", file=sys.stderr)
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
        choices=['permission_prompt', 'idle_prompt', 'stop'],
        help='Type of hook that triggered the notification'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=10,
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

    # Define default messages and icons for each hook type
    notifications_config = {
        'permission_prompt': {
            'title': 'Claude Code: Permission Required',
            'message': args.message or stdin_message or 'Claude is requesting permission to perform an action.',
            'icon': icon_dir / 'zunmon_3015.ico'
        },
        'idle_prompt': {
            'title': 'Claude Code: Waiting for Input',
            'message': args.message or stdin_message or 'Claude is idle and waiting for your response.',
            'icon': icon_dir / 'zunmon_3016.ico'
        },
        'stop': {
            'title': 'Claude Code: Stopped',
            'message': args.message or stdin_message or 'Claude has stopped execution.',
            'icon': icon_dir / 'zunmon_3001.ico'
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
