"""
Chrome Connector - Use your real Chrome browser with persistent profile.

Profile selection uses priority:
1. RAMI_LEVI_CHROME_PROFILE environment variable
2. ~/.rami-levi-config.json config file
3. Interactive selection (saves for reuse)
"""

import subprocess
import time
import os
from typing import Optional
from profile_manager import ProfileManager


class ChromeConnector:
    """
    Connect to user's real Chrome browser with persistent profile.

    Profile is selected via:
    - Environment variable: RAMI_LEVI_CHROME_PROFILE
    - Config file: ~/.rami-levi-config.json
    - Interactive selection (first run)
    """

    def __init__(self, debug_port: int = 9222, auto_start: bool = True):
        """
        Initialize Chrome connector with user's selected profile.

        Args:
            debug_port: Chrome remote debugging port (default 9222)
            auto_start: Auto-start Chrome if not running (default True)
        """
        self.debug_port = debug_port
        self.auto_start = auto_start
        self.browser = None
        self.page = None
        self.ws_endpoint = None
        self.profile_path = None

        # Get profile using priority: env var → config file → interactive
        try:
            self.profile_path = ProfileManager.get_active_profile()
        except ValueError as e:
            print(str(e))
            raise

    def get_profile_info(self) -> str:
        """Get info about Chrome profile being used."""
        if self.profile_path:
            return f"✅ Using Chrome profile: {self.profile_path}\n   Cart data will persist between sessions!"
        else:
            return "⚠️  Error: No valid Chrome profile selected"

    def start_chrome(self) -> bool:
        """
        Start Chrome with remote debugging and user profile.

        Uses your actual Chrome profile so cart data persists.
        """
        try:
            # Find Chrome executable
            chrome_path = None
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

            # Try which/where first
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

            # Check direct paths
            if not chrome_path:
                for path in possible_paths:
                    try:
                        if os.path.exists(path):
                            chrome_path = path
                            break
                        result = subprocess.run([path, "--version"], capture_output=True, timeout=2)
                        if result.returncode == 0:
                            chrome_path = path
                            break
                    except:
                        continue

            if not chrome_path:
                raise Exception("Chrome not found on system.")

            # Build launch arguments
            args = [
                chrome_path,
                f"--remote-debugging-port={self.debug_port}",
                "--no-first-run",
                "--no-default-browser-check",
            ]

            # Add user data directory if found (Chrome will create Default profile)
            if self.profile_path:
                args.append(f"--user-data-dir={self.profile_path}")

            # Linux-specific flags
            if os.name != "nt":
                args.append("--no-sandbox")

            # Launch Chrome (keep it running, don't wait for completion)
            process = subprocess.Popen(
                args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=None if os.name == "nt" else os.setsid
            )

            # Wait for Chrome to be ready
            for attempt in range(15):
                time.sleep(1)
                if self.check_chrome_running():
                    return True

            return False

        except Exception as e:
            return False

    def connect(self) -> Optional:
        """
        Connect to user's Chrome with persistent profile.

        Priority:
        1. Existing Chrome with debugging port (keep running)
        2. Auto-start Chrome with user's profile (cart data persists)
        3. Only fallback to bundled Chromium if NO profile found

        Returns:
            Playwright page object if connected, None if failed
        """
        try:
            from playwright.sync_api import sync_playwright

            # Try to connect to existing Chrome
            ws_endpoint = self._get_ws_endpoint()

            if ws_endpoint:
                # Connected to existing Chrome - use it
                playwright = sync_playwright().start()
                self.browser = playwright.chromium.connect(ws_endpoint)
                contexts = self.browser.contexts
                if contexts:
                    context = contexts[0]
                else:
                    context = self.browser.new_context()
                pages = context.pages
                self.page = pages[0] if pages else context.new_page()
                return self.page

            # Chrome not running - auto-start with user profile
            if self.auto_start:
                if self.start_chrome():
                    # Try connecting again
                    for attempt in range(10):
                        time.sleep(1)
                        ws_endpoint = self._get_ws_endpoint()
                        if ws_endpoint:
                            playwright = sync_playwright().start()
                            self.browser = playwright.chromium.connect(ws_endpoint)
                            context = self.browser.new_context()
                            self.page = context.new_page()
                            return self.page

            # Only fallback to bundled Chromium if NO user profile exists
            # (ephemeral, but better than nothing)
            if not self.profile_path:
                print("⚠️  Warning: Using ephemeral Chromium (no user profile found). Cart will be lost!")
                playwright = sync_playwright().start()
                self.browser = playwright.chromium.launch(
                    headless=False,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-first-run',
                        '--no-default-browser-check',
                    ]
                )
            context = self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            self.page = context.new_page()
            self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => false });
            """)
            return self.page

        except Exception as e:
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
