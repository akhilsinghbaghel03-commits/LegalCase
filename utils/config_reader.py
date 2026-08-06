"""
config_reader.py - Replaces Java ConfigReader utility.

Reads configuration values from config/config.ini using Python's
built-in configparser module.
"""

import configparser
import os


class ConfigReader:
    """Reads properties from config/config.ini."""

    _config = None

    @classmethod
    def _load(cls):
        """Lazily load and cache the config file."""
        if cls._config is None:
            cls._config = configparser.ConfigParser()
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "config",
                "config.ini"
            )
            if not os.path.exists(config_path):
                raise FileNotFoundError(
                    f"Config file not found at: {config_path}"
                )
            cls._config.read(config_path)
        return cls._config

    @classmethod
    def get_property(cls, key: str, section: str = None) -> str:
        """
        Retrieve a property value by key.

        Searches all sections if section is not provided.

        Args:
            key: The config key to look up.
            section: Optional section name (e.g., 'settings', 'app', 'timeouts').

        Returns:
            The string value for the key.

        Raises:
            KeyError: If the key is not found in any section.
        """
        config = cls._load()
        if section:
            return config.get(section, key)

        for sec in config.sections():
            if config.has_option(sec, key):
                return config.get(sec, key)

        raise KeyError(
            f"Property '{key}' not found in any section of config.ini"
        )

    @classmethod
    def get_browser(cls) -> str:
        return cls.get_property("browser", "settings")

    @classmethod
    def is_headless(cls) -> bool:
        return cls.get_property("headless", "settings").lower() == "true"

    @classmethod
    def get_page_load_timeout(cls) -> int:
        return int(cls.get_property("page_load_timeout", "settings"))

    @classmethod
    def get_app_url(cls) -> str:
        return cls.get_property("url", "app")

    @classmethod
    def get_email(cls) -> str:
        return cls.get_property("email", "app")

    @classmethod
    def get_password(cls) -> str:
        return cls.get_property("password", "app")

    @classmethod
    def get_explicit_wait(cls) -> int:
        return int(cls.get_property("explicit_wait", "timeouts"))

    @classmethod
    def get_otp_wait(cls) -> int:
        return int(cls.get_property("otp_wait", "timeouts"))

    @classmethod
    def get_dashboard_wait(cls) -> int:
        return int(cls.get_property("dashboard_wait", "timeouts"))
