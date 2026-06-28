"""
Chrome Connector - Connect to user's existing Chrome browser instance
Instead of launching a new browser, use the one already open with user's session.

Usage:
1. Start Chrome with remote debugging:
   chrome --remote-debugging-port=9222

2. Connect from skill:
   connector = ChromeConnector()
   page = connector.connect()
   # Now use page for automation
"""

import json
import subprocess
import time
from typing import Dict, Optional
from pathlib import Path


class ChromeConnector:
    """
    Connect to an existing Chrome browser instance.

    Instead of creating a new automated browser (which triggers bot detection),
    connect to the user's real Chrome browser with their session intact.

    Requirements:
    - Chrome/Chromium running with --remote-debugging-port=9222
    - Or auto-start Chrome with that flag
    """

    def __init__(self, debug_port: int = 9222, auto_start: bool = True):
        """
        Initialize Chrome connector.

        Args:
            debug_port: Chrome remote debugging port (default 9222)
            auto_start: Auto-start Chrome if not running (default True)
        """
        self.debug_port = debug_port
        self.auto_start = auto_start
        self.browser = None
        self.page = None
        self.ws_endpoint = None

    def start_chrome(self) -> bool:
        """
        Start Chrome with remote debugging enabled (automatically).
        Finds Chrome on system and launches it.

        Returns:
            True if started successfully
        """
        try:
            import shutil
            import os

            # Try to find Chrome executable
            chrome_path = None

            # Check common paths
            possible_paths = [
                "google-chrome",
                "google-chrome-stable",
                "chromium",
                "chromium-browser",
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                "/usr/bin/chromium",
                "/snap/bin/chromium",
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            ]

            # Try to find Chrome using which/where
            for cmd_name in ["google-chrome", "chromium", "google-chrome-stable"]:
                try:
                    result = subprocess.run(
                        ["which", cmd_name] if os.name != "nt" else ["where", cmd_name],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    if result.returncode == 0:
                        chrome_path = result.stdout.strip().split('\n')[0]
                        break
                except:
                    pass

            # Check direct paths if which/where didn't work
            if not chrome_path:
                for path in possible_paths:
                    try:
                        if os.path.exists(path):
                            chrome_path = path
                            break
                        # Try running it
                        result = subprocess.run(
                            [path, "--version"],
                            capture_output=True,
                            timeout=2
                        )
                        if result.returncode == 0:
                            chrome_path = path
                            break
                    except:
                        continue

            if not chrome_path:
                raise Exception(
                    "Chrome not found on system. "
                    "Please install Google Chrome or Chromium."
                )

            # Start Chrome with debugging
            args = [
                chrome_path,
                f"--remote-debugging-port={self.debug_port}",
                "--no-first-run",
                "--no-default-browser-check",
            ]

            # Add no-sandbox for Linux
            if os.name != "nt":
                args.append("--no-sandbox")

            # Launch Chrome
            process = subprocess.Popen(
                args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=None if os.name == "nt" else os.setsid
            )

            # Wait for Chrome to be ready
            for attempt in range(10):
                time.sleep(1)
                if self.check_chrome_running():
                    return True

            return False

        except Exception as e:
            return False

    def connect(self) -> Optional:
        """
        Connect to existing Chrome instance via remote debugging.

        Returns:
            Playwright page object if connected, None if failed
        """
        try:
            from playwright.sync_api import sync_playwright

            # Get WebSocket endpoint from Chrome
            ws_endpoint = self._get_ws_endpoint()

            if ws_endpoint:
                # Connect via WebSocket to YOUR existing Chrome
                playwright = sync_playwright().start()
                self.browser = playwright.chromium.connect(ws_endpoint)

                # Get or create page
                contexts = self.browser.contexts
                if contexts:
                    context = contexts[0]
                else:
                    context = self.browser.new_context()

                pages = context.pages
                if pages:
                    self.page = pages[0]
                else:
                    self.page = context.new_page()

                return self.page

            # Chrome not running - auto-launch it
            if self.start_chrome():
                # Try connecting again
                ws_endpoint = self._get_ws_endpoint()
                if ws_endpoint:
                    playwright = sync_playwright().start()
                    self.browser = playwright.chromium.connect(ws_endpoint)
                    context = self.browser.new_context()
                    self.page = context.new_page()
                    return self.page

            raise Exception("Could not connect to Chrome or launch new instance")

        except Exception as e:
            raise Exception(f"Chrome connection failed: {str(e)}")

    def _get_ws_endpoint(self) -> Optional[str]:
        """
        Get WebSocket endpoint from Chrome's debugging protocol.

        Returns:
            WebSocket endpoint URL or None
        """
        try:
            import requests

            response = requests.get(
                f"http://localhost:{self.debug_port}/json/version",
                timeout=2
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("webSocketDebuggerUrl")

        except Exception:
            pass

        return None

    def check_chrome_running(self) -> bool:
        """
        Check if Chrome is already running on debug port.

        Returns:
            True if Chrome is running and accessible
        """
        try:
            import requests

            response = requests.get(
                f"http://localhost:{self.debug_port}/json/version",
                timeout=2
            )

            return response.status_code == 200

        except Exception:
            return False

    def close(self):
        """Close Chrome connection."""
        try:
            if self.page:
                self.page.close()
            if self.browser:
                self.browser.close()
        except:
            pass


if __name__ == "__main__":
    # Demo
    print("🌐 CHROME CONNECTOR DEMO\n")

    connector = ChromeConnector()

    # Check if Chrome is running
    print("1. Checking if Chrome is running...")
    if connector.check_chrome_running():
        print("   ✓ Chrome is already running on port 9222")
    else:
        print("   ✗ Chrome not running, starting it...")
        if connector.start_chrome():
            print("   ✓ Chrome started")
        else:
            print("   ✗ Could not start Chrome")
            print("\n   Manual start:")
            print("   chrome --remote-debugging-port=9222")
            exit(1)

    # Connect to Chrome
    print("\n2. Connecting to Chrome...")
    page = connector.connect()

    if page:
        print("   ✓ Connected!")
        print(f"   Current URL: {page.url}")
        print("\n   ✓ Ready to use page for shopping automation")
        # Don't close - let user keep using Chrome
    else:
        print("   ✗ Connection failed")
