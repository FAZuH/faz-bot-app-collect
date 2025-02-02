import asyncio
from datetime import datetime
from typing import Any, Coroutine, TYPE_CHECKING

from faz.bot.app.collect.objects.request_type import RequestType

if TYPE_CHECKING:
    from datetime import datetime
    from faz.bot.wynn.api.base_response import BaseResponse

    type Response = BaseResponse[Any, Any]
    type RespCoro = Coroutine[Response, Any, Any]


class Request:
    def __init__(
        self, coro: RespCoro, priority: int, scheduled_time: datetime, type_: RequestType
    ) -> None:
        self._scheduled_time = scheduled_time
        self._coro = coro
        self._priority = priority
        self._type = type_

        self._task: asyncio.Task | None = None

    async def run(self) -> None:
        self._task = asyncio.create_task(self._coro)

    def is_eligible(self, time: datetime | None = None) -> bool:
        """Check if the request is eligible to be run.

        Parameters
        ----------
        time : datetime | None, optional
            _description_, by default None

        Returns
        -------
        bool
            _description_
        """
        time = time or datetime.now()
        return self.scheduled_time < time

    @property
    def priority(self) -> int:
        return self._priority

    @property
    def type(self) -> RequestType:
        return self._type

    @property
    def scheduled_time(self) -> datetime:
        """The time when the request is eligible to be run.

        This timestamp indicates when the cached resource will expire
        and the request should be processed.

        Returns
        -------
        datetime
            The scheduled execution time.
        """
        return self._scheduled_time

    def get_result(self) -> Response:
        if self._task is None:
            raise RuntimeError("Request has not been run yet.")
        return self._task.result()
