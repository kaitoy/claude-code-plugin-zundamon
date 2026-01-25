#!/usr/bin/env python3
"""
Test script for notify.py
Simulates Claude Code hook input by piping JSON to notify.py
"""

import subprocess
import json
import sys


def test_permission_prompt():
    """Test permission_prompt notification with JSON input"""
    print("Testing permission_prompt with JSON input...")

    hook_input = {
        "message": "Claude is requesting permission to run: git status",
        "type": "permission_prompt"
    }

    process = subprocess.Popen(
        [sys.executable, "notify.py", "permission_prompt"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    stdout, stderr = process.communicate(input=json.dumps(hook_input))

    print(f"STDOUT: {stdout}")
    if stderr:
        print(f"STDERR: {stderr}")
    print(f"Return code: {process.returncode}\n")


def test_idle_prompt():
    """Test idle_prompt notification with JSON input"""
    print("Testing idle_prompt with JSON input...")

    hook_input = {
        "message": "Claude has been idle for 30 seconds and is waiting for your response.",
        "type": "idle_prompt"
    }

    process = subprocess.Popen(
        [sys.executable, "notify.py", "idle_prompt"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    stdout, stderr = process.communicate(input=json.dumps(hook_input))

    print(f"STDOUT: {stdout}")
    if stderr:
        print(f"STDERR: {stderr}")
    print(f"Return code: {process.returncode}\n")


def test_stop():
    """Test stop notification with JSON input"""
    print("Testing stop with JSON input...")

    hook_input = {
        "message": "Claude execution has been stopped by the user.",
        "type": "stop"
    }

    process = subprocess.Popen(
        [sys.executable, "notify.py", "stop"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    stdout, stderr = process.communicate(input=json.dumps(hook_input))

    print(f"STDOUT: {stdout}")
    if stderr:
        print(f"STDERR: {stderr}")
    print(f"Return code: {process.returncode}\n")


def test_default_message():
    """Test notification with default message (no stdin)"""
    print("Testing with default message (no stdin input)...")

    process = subprocess.run(
        [sys.executable, "notify.py", "permission_prompt"],
        capture_output=True,
        text=True
    )

    print(f"STDOUT: {process.stdout}")
    if process.stderr:
        print(f"STDERR: {process.stderr}")
    print(f"Return code: {process.returncode}\n")


def test_custom_message():
    """Test notification with custom message argument"""
    print("Testing with --message argument...")

    process = subprocess.run(
        [sys.executable, "notify.py", "idle_prompt", "--message", "Custom test message"],
        capture_output=True,
        text=True
    )

    print(f"STDOUT: {process.stdout}")
    if process.stderr:
        print(f"STDERR: {process.stderr}")
    print(f"Return code: {process.returncode}\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Claude Code Notification Test Suite")
    print("=" * 60 + "\n")

    test_permission_prompt()
    test_idle_prompt()
    test_stop()
    test_default_message()
    test_custom_message()

    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)
