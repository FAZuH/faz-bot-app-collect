from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, override, TYPE_CHECKING

from faz.utils.heartbeat.task.itask import ITask
from loguru import logger

if TYPE_CHECKING:
    from faz.bot.wynn.api.base_response import BaseResponse
    from faz.bot.wynn.api.wynn_api import WynnApi

    from faz.bot.app.collect.task.request_queue import RequestQueue
    from faz.bot.app.collect.task.response_queue import ResponseQueue

    type Resp = BaseResponse[Any, Any]


class TaskApiRequest(ITask):
    """implements `TaskBase`"""

    _CONCURRENT_REQUESTS = 15

    def __init__(
        self, api: WynnApi, request_queue: RequestQueue, response_queue: ResponseQueue
    ) -> None:
        self._api = api
        self._request_list = request_queue
        self._response_list = response_queue

        self._event_loop = asyncio.new_event_loop()
        self._latest_run = datetime.now()
        self._running_requests: list[asyncio.Task[Resp]] = []

    @override
    def setup(self) -> None:
        logger.debug(f"Setting up {self.name}")
        self._event_loop.run_until_complete(self._api.start())
        # NOTE: Initial request. Results in a chain reaction of requests.
        self._request_list.enqueue(0, self._api.player.get_online_uuids(), priority=999)

    @override
    def teardown(self) -> None:
        logger.debug(f"Tearing down {self.name}")
        self._event_loop.run_until_complete(self._api.close())
        for req in self._running_requests:
            req.cancel()

    @override
    def run(self) -> None:
        with logger.catch(level="ERROR"):
            self._event_loop.run_until_complete(self._check_api_session())
            self._start_requests()
            self._check_responses()
        self._latest_run = datetime.now()

    async def _check_api_session(self) -> None:
        if not self._api.request.is_open():
            logger.warning("HTTP session is closed. Reopening...")
            await self._api.start()

    def _start_requests(self) -> None:
        running_request_count = len(self._running_requests)
        if running_request_count < self._CONCURRENT_REQUESTS:
            complement = self._CONCURRENT_REQUESTS - running_request_count
            new_requests = (
                self._event_loop.create_task(req) for req in self._request_list.dequeue(complement)
            )
            self._running_requests.extend(new_requests)

    def _check_responses(self) -> None:
        ok_results: list[Resp] = []
        tasks_to_remove = []
        for task in self._running_requests:
            if not task.done():
                continue

            tasks_to_remove.append(task)
            exc = task.exception()

            if exc is None:
                ok_results.append(task.result())
                continue

            if task.get_coro().__qualname__ == self._api.player.get_online_uuids.__qualname__:
                self._request_list.enqueue(0, self._api.player.get_online_uuids(), priority=999)

            with logger.catch(level="ERROR"):
                raise exc

        for task in tasks_to_remove:
            self._running_requests.remove(task)

        ok_result_count = len(ok_results)
        if ok_result_count > 0:
            logger.debug(f"{ok_result_count} responses from API")
            self._response_list.put(ok_results)

    @property
    def first_delay(self) -> float:
        return 2.0

    @property
    def interval(self) -> float:
        return 1.0

    @property
    def latest_run(self) -> datetime:
        return self._latest_run

    @property
    def name(self) -> str:
        return self.__class__.__name__
