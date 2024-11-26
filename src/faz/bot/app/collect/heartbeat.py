from __future__ import annotations

from typing import TYPE_CHECKING

from faz.utils.heartbeat.base_heartbeat import BaseHeartbeat

from faz.bot.app.collect.task.request_queue import RequestQueue
from faz.bot.app.collect.task.response_queue import ResponseQueue
from faz.bot.app.collect.task.task_api_request import TaskApiRequest
from faz.bot.app.collect.task.task_db_insert import TaskDbInsert

if TYPE_CHECKING:
    from faz.bot.database.fazwynn.fazwynn_database import FazwynnDatabase
    from faz.bot.wynn.api.wynn_api import WynnApi


class Heartbeat(BaseHeartbeat):
    def __init__(self, api: WynnApi, db: FazwynnDatabase) -> None:
        super().__init__("heartbeat_faz.bot.app.collect")

        request_queue = RequestQueue()
        response_queue = ResponseQueue()
        api_request = TaskApiRequest(api, request_queue, response_queue)
        db_insert = TaskDbInsert(api, db, request_queue, response_queue)

        self._add_task(api_request)
        self._add_task(db_insert)
