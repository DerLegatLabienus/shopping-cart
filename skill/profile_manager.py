"""
Chrome Profile Manager - Detect, select, and persist user's Chrome profile.

Handles:
1. Detecting available Chrome profiles
2. Loading from env var (RAMI_LEVI_CHROME_PROFILE)
3. Loading from config (~/.rami-levi-config.json)
4. Interactive selection on first run
5. Persisting selection for reuse
"""

import json
import os
from pathlib import Path
from typing import List, Optional, Dict


class ProfileManager:
    """Manage Chrome profile selection and persistence."""

    CONFIG_FILE = os.path.expanduser("~/.rami-levi-config.json")
    ENV_VAR = "RAMI_LEVI_CHROME_PROFILE"

    @staticmethod
    def detect_available_profiles() -> List[Dict[str, str]]:
        """
        Detect all available Chrome profiles on the system.

        Returns:
            List of dicts: [{"path": "/path/to/profile", "name": "Default", "base": "/path/to/config"}]
        """
        profiles = []
        home = str(Path.home())

        # Platform-specific base directories
        base_dirs = []
        if os.name != "nt":  # Linux/macOS
            base_dirs.extend([
                os.path.join(home, ".config/google-chrome"),
                os.path.join(home, ".config/chromium"),
                os.path.join(home, "Library/Application Support/Google/Chrome"),
                os.path.join(home, "Library/Application Support/Chromium"),
            ])
        else:  # Windows
            base_dirs.extend([
                os.path.join(home, "AppData/Local/Google/Chrome/User Data"),
                os.path.join(home, "AppData/Local/Chromium/User Data"),
            ])

        # Find all profiles in each base directory
        for base_dir in base_dirs:
            if not os.path.exists(base_dir):
                continue

            # Check for Default profile
            default_profile = os.path.join(base_dir, "Default")
            if os.path.isdir(default_profile):
                profiles.append({
                    "path": default_profile,
                    "name": "Default",
                    "base": base_dir
                })

            # Check for numbered profiles (Profile 1, Profile 2, etc.)
            for item in os.listdir(base_dir):
                if item.startswith("Profile ") and item[8:].isdigit():
                    profile_path = os.path.join(base_dir, item)
                    if os.path.isdir(profile_path):
                        profiles.append({
                            "path": profile_path,
                            "name": item,
                            "base": base_dir
                        })

        # Remove duplicates (same path from different base dirs)
        seen = set()
        unique_profiles = []
        for p in profiles:
            if p["path"] not in seen:
                seen.add(p["path"])
                unique_profiles.append(p)

        return unique_profiles

    @staticmethod
    def load_from_env() -> Optional[str]:
        """Load profile from environment variable."""
        profile = os.getenv(ProfileManager.ENV_VAR)
        if profile:
            if os.path.exists(profile):
                return profile
            else:
                raise ValueError(
                    f"❌ FATAL: Chrome profile not found\n"
                    f"   Env var {ProfileManager.ENV_VAR}={profile}\n"
                    f"   Directory does not exist or is inaccessible"
                )
        return None

    @staticmethod
    def load_from_config() -> Optional[str]:
        """Load profile from config file."""
        if not os.path.exists(ProfileManager.CONFIG_FILE):
            return None

        try:
            with open(ProfileManager.CONFIG_FILE, 'r') as f:
                config = json.load(f)
                profile = config.get("chrome_profile")
                if profile:
                    if os.path.exists(profile):
                        return profile
                    else:
                        raise ValueError(
                            f"❌ FATAL: Chrome profile not found\n"
                            f"   Config file: {ProfileManager.CONFIG_FILE}\n"
                            f"   Profile: {profile}\n"
                            f"   Directory does not exist or is inaccessible"
                        )
        except json.JSONDecodeError:
            raise ValueError(
                f"❌ FATAL: Invalid JSON in {ProfileManager.CONFIG_FILE}"
            )

        return None

    @staticmethod
    def save_to_config(profile_path: str) -> None:
        """Save selected profile to config file."""
        config = {"chrome_profile": profile_path}
        with open(ProfileManager.CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)

    @staticmethod
    def prompt_user_for_profile(profiles: List[Dict[str, str]]) -> str:
        """
        Prompt user to select a profile from available options.

        Args:
            profiles: List of available profiles from detect_available_profiles()

        Returns:
            Selected profile path
        """
        if not profiles:
            raise ValueError(
                "❌ No Chrome profiles found on system.\n"
                "Please install Google Chrome or Chromium first."
            )

        print()
        print("=" * 80)
        print("🔍 NO SAVED CHROME PROFILE - SELECT ONE")
        print("=" * 80)
        print()
        print("Available Chrome profiles:")
        print()

        for i, profile in enumerate(profiles, 1):
            print(f"  {i}. {profile['path']}")
            print(f"     ({profile['name']})")

        print()

        while True:
            try:
                choice = input("Select profile (1-{}): ".format(len(profiles)))
                index = int(choice) - 1

                if 0 <= index < len(profiles):
                    selected = profiles[index]["path"]
                    print()
                    print(f"✅ Selected: {selected}")
                    return selected
                else:
                    print(f"❌ Invalid choice. Enter 1-{len(profiles)}")
            except ValueError:
                print(f"❌ Invalid input. Enter a number 1-{len(profiles)}")

    @staticmethod
    def get_active_profile() -> str:
        """
        Get the active Chrome profile using priority:
        1. Environment variable (RAMI_LEVI_CHROME_PROFILE)
        2. Config file (~/.rami-levi-config.json)
        3. Interactive selection + save to config

        Returns:
            Path to Chrome profile

        Raises:
            ValueError: If profile not found or invalid
        """
        # Priority 1: Environment variable
        try:
            env_profile = ProfileManager.load_from_env()
            if env_profile:
                return env_profile
        except ValueError as e:
            raise e

        # Priority 2: Config file
        try:
            config_profile = ProfileManager.load_from_config()
            if config_profile:
                return config_profile
        except ValueError as e:
            raise e

        # Priority 3: Interactive selection
        profiles = ProfileManager.detect_available_profiles()
        selected = ProfileManager.prompt_user_for_profile(profiles)
        ProfileManager.save_to_config(selected)

        print()
        print(f"✅ Profile saved to: {ProfileManager.CONFIG_FILE}")
        print()

        return selected
