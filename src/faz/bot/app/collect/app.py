from __future__ import annotations

from typing import Any, Callable

from faz.bot.core.logger_setup import LoggerSetup
from faz.bot.database.fazwynn.fazwynn_database import FazwynnDatabase
from faz.bot.wynn.api.wynn_api import WynnApi
from faz.utils.retry_handler import RetryHandler
from loguru import logger

from faz.bot.app.collect.heartbeat import Heartbeat
from faz.bot.app.collect.properties import Properties


class App:
    def __init__(self) -> None:
        self._properties = Properties()
        p = self.properties
        p.setup()
        LoggerSetup.setup(
            "logs",
            p.FAZCOLLECT_DISCORD_LOG_WEBHOOK,
            p.ADMIN_DISCORD_ID,
        )

        self._api = WynnApi()
        self._db = FazwynnDatabase(
            p.MYSQL_USER,
            p.MYSQL_PASSWORD,
            p.MYSQL_HOST,
            p.MYSQL_PORT,
            p.MYSQL_FAZWYNN_DATABASE,
        )
        self._heartbeat = Heartbeat(self.api, self.db)

        self._register_retry_handler()

    def start(self) -> None:
        logger.info("Starting WynnDb Heartbeat...")
        self.heartbeat.start()

    def stop(self) -> None:
        logger.info("Stopping Heartbeat...")
        self.heartbeat.stop()

    @property
    def api(self) -> WynnApi:
        return self._api

    @property
    def properties(self) -> Properties:
        return self._properties

    @property
    def db(self) -> FazwynnDatabase:
        return self._db

    @property
    def heartbeat(self) -> Heartbeat:
        return self._heartbeat

    def _register_retry_handler(self) -> None:
        """Registers retry handler to this appp"""
        register_lambda: Callable[[Callable[..., Any]], None] = (
            lambda func: RetryHandler.register(
                func, self.properties.FAZWYNN_MAX_RETRIES, Exception
            )
        )

        # Register retry handler to database
        repositories = self.db.repositories
        for repo in repositories:
            register_lambda(repo.table_disk_usage)
            register_lambda(repo.create_table)
            register_lambda(repo.insert)
            register_lambda(repo.delete)
            register_lambda(repo.is_exists)
