from __future__ import annotations

from datetime import datetime
from threading import Lock
from typing import Any, Coroutine, TYPE_CHECKING

if TYPE_CHECKING:
    from faz.bot.wynn.api.base_response import BaseResponse

    type Resp = BaseResponse[Any, Any]
    type RespCoro = Coroutine[Resp, Any, Any]


class RequestQueue:
    def __init__(self) -> None:
        self._list: list[RequestQueue.RequestItem] = []
        self._lock: Lock = Lock()

    def dequeue(self, amount: int) -> list[RespCoro]:
        now = datetime.now().timestamp()
        ret: list[RespCoro] = []
        with self._lock:
            for _ in range(amount):
                try:
                    item = min(self._list)
                except ValueError:
                    break
                if item.is_eligible(now):
                    self._list.remove(item)
                    ret.append(item.coro)
        return ret

    def enqueue(self, request_ts: float, coro: RespCoro, priority: int = 100) -> None:
        with self._lock:
            item = self.RequestItem(coro, priority, request_ts)
            if item not in self._list:
                self._list.append(item)

    class RequestItem:
        def __init__(
            self,
            coro: RespCoro,
            priority: int,
            req_ts: float,
        ) -> None:
            self._req_ts = req_ts
            self._coro = coro
            self._priority = priority

        def is_eligible(self, timestamp: None | float = None) -> bool:
            timestamp = timestamp or datetime.now().timestamp()
            return self.req_ts < timestamp

        def __eq__(self, other: object | RequestQueue.RequestItem) -> bool:
            if isinstance(other, RequestQueue.RequestItem):
                return (
                    # HACK
                    (self.coro.cr_frame.f_locals == other.coro.cr_frame.f_locals)  # type: ignore
                    and (self.coro.__class__ == other.coro.__class__)
                )
            return False

        def __lt__(self, other: RequestQueue.RequestItem) -> bool:
            """For min() function.
            Return true to get favored more in min() function."""
            if self.is_eligible() is False:
                # items not eligible obviously shouldn't be returned in min()
                return False

            if self.priority != other.priority:
                # Higher priority is favored
                return self.priority > other.priority

            # Favor requests that has expired longer
            return self.req_ts < other.req_ts

        @property
        def req_ts(self) -> float:
            """Timestamp for when the cache of the resource will expire."""
            return self._req_ts

        @property
        def coro(self) -> RespCoro:
            return self._coro

        @property
        def priority(self) -> int:
            return self._priority
