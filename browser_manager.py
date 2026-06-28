"""
Browser Manager - Session Management Module
Manages Playwright browser lifecycle and session persistence for Rami Levy automation.
Stores session config in ~/.rami-levi-session.json for persistence between sessions.
"""

import json
import os
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from playwright.sync_api import sync_playwright, Browser, BrowserContext


class BrowserManager:
    """
    Manages browser lifecycle and session persistence for Rami Levy automation.

    Key features:
    - Launch and maintain Chrome browser instance
    - Store session config in ~/.rami-levi-session.json
    - Track browser process ID and WebSocket endpoint
    - Check if existing session is still active
    - Navigate to Rami Levy cart page
    - Update session metadata (items_added, cart_total, timestamps)
    """

    def __init__(self):
        """Initialize BrowserManager with config path and defaults"""
        self.config_path = Path.home() / ".rami-levi-session.json"
        self.playwright_instance = None
        self.browser = None
        self.browser_context = None
        self.page = None

    def open_browser(self) -> Dict:
        """
        Launch Chrome browser and store session information.

        Returns:
            {
                'success': bool,
                'browser_pid': int or None,
                'ws_endpoint': str or None,
                'message': str
            }
        """
        try:
            # Initialize Playwright
            self.playwright_instance = sync_playwright().start()

            # Launch browser in non-headless mode (user can see window)
            self.browser = self.playwright_instance.chromium.launch(headless=False)

            # Create new context and page
            self.browser_context = self.browser.new_context()
            self.page = self.browser_context.new_page()

            # Get browser process info
            try:
                browser_pid = self.browser.process.pid if hasattr(self.browser, 'process') and self.browser.process else None
            except:
                browser_pid = None

            try:
                ws_endpoint = self.browser.websocket_endpoint if hasattr(self.browser, 'websocket_endpoint') else None
            except:
                ws_endpoint = None

            # Navigate to Rami Levy cart page
            self.page.goto("https://www.rami-levy.co.il/he", wait_until="domcontentloaded", timeout=15000)

            # Initialize session config
            session_config = {
                "active": True,
                "browser_pid": browser_pid,
                "ws_endpoint": ws_endpoint,
                "opened_at": datetime.now().isoformat() + "Z",
                "items_added": 0,
                "cart_total": 0.0,
                "last_updated": datetime.now().isoformat() + "Z"
            }

            # Save session config
            self._save_config(session_config)

            return {
                'success': True,
                'browser_pid': browser_pid,
                'ws_endpoint': ws_endpoint,
                'message': f'✅ Browser opened successfully (PID: {browser_pid})'
            }

        except Exception as e:
            return {
                'success': False,
                'browser_pid': None,
                'ws_endpoint': None,
                'message': f'❌ Failed to open browser: {str(e)}'
            }

    def get_browser(self) -> Optional[Browser]:
        """
        Retrieve existing browser instance or None if not active.

        Returns:
            Browser instance if active, None otherwise
        """
        if self.browser is not None:
            return self.browser

        # Check if session config exists and is valid
        config = self.get_session_config()
        if not config or not config.get('active'):
            return None

        # Check if process is still running
        if not self.is_browser_open():
            return None

        return self.browser

    def is_browser_open(self) -> bool:
        """
        Check if browser session exists and process is running.

        Returns:
            True if active session with running process exists, False otherwise
        """
        # If we have an active browser instance, it's open
        if self.browser is not None:
            try:
                # Verify process is still running
                if self.browser.process and self.browser.process.poll() is None:
                    return True
            except:
                pass

        # Check session config file
        config = self.get_session_config()
        if not config or not config.get('active'):
            return False

        # Check if the process from config is still running
        browser_pid = config.get('browser_pid')
        if browser_pid is None:
            return False

        try:
            # Check if process exists (Unix/Linux specific)
            os.kill(browser_pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False

    def close_browser(self) -> Dict:
        """
        Close browser and cleanup session config.

        Returns:
            {'success': bool, 'message': str}
        """
        try:
            # Close browser resources
            if self.page:
                self.page.close()

            if self.browser_context:
                self.browser_context.close()

            if self.browser:
                self.browser.close()

            if self.playwright_instance:
                self.playwright_instance.stop()

            # Reset instance variables
            self.page = None
            self.browser_context = None
            self.browser = None
            self.playwright_instance = None

            # Remove session config
            if self.config_path.exists():
                self.config_path.unlink()

            return {
                'success': True,
                'message': '✅ Browser closed successfully'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'❌ Error closing browser: {str(e)}'
            }

    def navigate_to_cart(self) -> bool:
        """
        Navigate to Rami Levy shopping cart page.

        Returns:
            True if navigation successful, False otherwise
        """
        try:
            if not self.page:
                return False

            self.page.goto("https://www.rami-levy.co.il/he", wait_until="domcontentloaded", timeout=15000)
            return True

        except Exception as e:
            print(f"Error navigating to cart: {e}")
            return False

    def get_session_config(self) -> Dict:
        """
        Read and return session config from disk.

        Returns:
            Config dictionary if file exists, empty dict otherwise
        """
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error reading session config: {e}")

        return {}

    def update_session_config(self, updates: Dict) -> bool:
        """
        Update session config with new fields.

        Args:
            updates: Dictionary of fields to update

        Returns:
            True if update successful, False otherwise
        """
        try:
            # Load current config
            config = self.get_session_config()

            # Update with new values
            config.update(updates)

            # Always update last_updated timestamp
            config['last_updated'] = datetime.now().isoformat() + "Z"

            # Save updated config
            self._save_config(config)

            return True

        except Exception as e:
            print(f"Error updating session config: {e}")
            return False

    def _save_config(self, config: Dict) -> bool:
        """
        Save config dictionary to disk.

        Args:
            config: Configuration dictionary to save

        Returns:
            True if save successful, False otherwise
        """
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving session config: {e}")
            return False


if __name__ == "__main__":
    # Demo usage
    print("🌐 Browser Manager Demo")
    print("-" * 50)

    manager = BrowserManager()

    # Check initial state
    print(f"Browser open? {manager.is_browser_open()}")
    print(f"Config path: {manager.config_path}")

    # Open browser
    print("\nOpening browser...")
    result = manager.open_browser()
    print(f"Result: {result}")

    # Check state
    print(f"Browser open? {manager.is_browser_open()}")
    config = manager.get_session_config()
    print(f"Active config: {config.get('active')}")

    # Update config
    print("\nUpdating session config...")
    manager.update_session_config({"items_added": 5, "cart_total": 125.50})
    config = manager.get_session_config()
    print(f"Updated config: items_added={config.get('items_added')}, cart_total={config.get('cart_total')}")

    # Close browser
    print("\nClosing browser...")
    result = manager.close_browser()
    print(f"Result: {result}")
    print(f"Browser open? {manager.is_browser_open()}")
