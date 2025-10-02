"""Headhunter AI Chatbot - Main Entry Point"""

import subprocess
import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    try:
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def main():
    """Launch chatbot application"""
    chatbot_path = os.path.join("src", "streamlit_app", "chatbot_app.py")

    print("=" * 60)
    print("🤖 Headhunter AI Chatbot")
    print("=" * 60)
    print()
    print("Starting chatbot...")
    print("Browser will open automatically at http://localhost:8501")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    print()

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
    except Exception as e:
        print(f"\n\nError: {e}")
        print("\nMake sure all dependencies are installed:")
        print("  python -m pip install -r requirements.txt")

if __name__ == "__main__":
    main()
