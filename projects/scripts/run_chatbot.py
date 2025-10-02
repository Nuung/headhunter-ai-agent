"""Headhunter AI Chatbot Launcher"""

import subprocess
import sys
import os

# Fix Windows encoding issue
if sys.platform == 'win32':
    try:
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def main():
    """Launch chatbot app"""
    chatbot_path = os.path.join("src", "streamlit_app", "chatbot_app.py")

    print("=" * 60)
    print("Headhunter AI Chatbot Starting...")
    print("=" * 60)
    print()
    print("Browser will open automatically.")
    print("Press Ctrl+C to stop.")
    print()
    print("=" * 60)

    try:
        subprocess.run([
            sys.executable,
            "-m",
            "streamlit",
            "run",
            chatbot_path,
            "--server.headless=false"
        ])
    except KeyboardInterrupt:
        print("\n\nChatbot stopped. Goodbye!")

if __name__ == "__main__":
    main()
