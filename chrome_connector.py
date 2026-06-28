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
        Start Chrome with remote debugging enabled.

        Returns:
            True if started successfully
        """
        try:
            # Chrome/Chromium paths
            chrome_paths = [
                "google-chrome",  # Linux
                "google-chrome-stable",  # Linux
                "chromium",  # Linux
                "chromium-browser",  # Linux
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",  # Windows
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",  # Windows 32-bit
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # macOS
            ]

            for chrome_path in chrome_paths:
                try:
                    subprocess.Popen(
                        [
                            chrome_path,
                            f"--remote-debugging-port={self.debug_port}",
                            "--no-first-run",
                            "--no-default-browser-check",
                        ]
                    )
                    print(f"✓ Chrome started with remote debugging on port {self.debug_port}")
                    time.sleep(3)  # Wait for Chrome to start
                    return True
                except FileNotFoundError:
                    continue

            print("✗ Could not find Chrome installation")
            return False

        except Exception as e:
            print(f"✗ Error starting Chrome: {e}")
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

            if not ws_endpoint:
                print("✗ Could not find Chrome WebSocket endpoint")
                print("Make sure Chrome is running with: chrome --remote-debugging-port=9222")
                return None

            print(f"✓ Found Chrome at: {ws_endpoint}")

            # Connect via WebSocket
            playwright = sync_playwright().start()
            self.browser = playwright.chromium.connect(ws_endpoint)

            # Get or create page
            contexts = self.browser.contexts
            if contexts:
                # Use existing context
                context = contexts[0]
            else:
                # Create new context
                context = self.browser.new_context()

            pages = context.pages
            if pages:
                # Use existing page
                self.page = pages[0]
            else:
                # Create new page
                self.page = context.new_page()

            print(f"✓ Connected to Chrome browser")
            return self.page

        except Exception as e:
            print(f"✗ Error connecting to Chrome: {e}")
            return None

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
