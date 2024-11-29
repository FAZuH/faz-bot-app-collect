import os
from typing import Callable

from dotenv import load_dotenv

from faz.bot.app.collect import __version__


class Properties:
    # Application constants
    AUTHOR = "FAZuH"
    VERSION = __version__

    # .env
    ADMIN_DISCORD_ID: int

    FAZCOLLECT_DISCORD_LOG_WEBHOOK: str
    FAZCOLLECT_DISCORD_STATUS_WEBHOOK: str

    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_USER: str
    MYSQL_PASSWORD: str

    MYSQL_FAZWYNN_DATABASE: str
    FAZWYNN_MAX_RETRIES: int

    # # Additional application property classes
    # ASSET: Asset

    @classmethod
    def setup(cls) -> None:
        """Bootstraps application properties."""
        cls._read_env()
        # cls.ASSET = Asset(cls.ASSET_DIR)
        # cls.ASSET.read_all()

    @classmethod
    def _read_env(cls) -> None:
        load_dotenv()
        cls.ADMIN_DISCORD_ID = cls._must_get_env("ADMIN_DISCORD_ID", int)

        cls.FAZCOLLECT_DISCORD_LOG_WEBHOOK = cls._must_get_env("FAZCOLLECT_DISCORD_LOG_WEBHOOK")
        cls.FAZCOLLECT_DISCORD_STATUS_WEBHOOK = cls._must_get_env(
            "FAZCOLLECT_DISCORD_STATUS_WEBHOOK"
        )
        cls.FAZWYNN_MAX_RETRIES = cls._must_get_env("FAZWYNN_MAX_RETRIES", int)

        cls.MYSQL_HOST = cls._must_get_env("MYSQL_HOST")
        cls.MYSQL_PORT = cls._must_get_env("MYSQL_PORT", int)
        cls.MYSQL_USER = cls._must_get_env("MYSQL_USER")
        cls.MYSQL_PASSWORD = cls._must_get_env("MYSQL_PASSWORD")

        cls.MYSQL_FAZWYNN_DATABASE = cls._must_get_env("MYSQL_FAZWYNN_DATABASE")

    @staticmethod
    def _must_get_env[T](key: str, type_strategy: Callable[[str], T] = str) -> T:
        try:
            env = os.getenv(key)
            return type_strategy(env)  # type: ignore
        except ValueError as exc:
            raise ValueError(
                f"Failed parsing environment variable {key} into type {type_strategy}"
            ) from exc
