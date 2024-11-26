from __future__ import annotations

import asyncio
from time import sleep

from loguru import logger

from faz.bot.app.collect.app import App


def main() -> None:
    app = App()
    try:
        with logger.catch(level="CRITICAL", reraise=True):
            app.start()
            while True:  # keep-alive
                sleep(5)
    finally:
        app.stop()

        async def _cleanup_logger_queue():
            await logger.complete()

        asyncio.run(_cleanup_logger_queue())


if __name__ == "__main__":
    main()
