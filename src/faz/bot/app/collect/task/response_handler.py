import asyncio
from datetime import datetime
from typing import Any, Coroutine, TYPE_CHECKING

from faz.bot.wynn.api.response.guild_response import GuildResponse
from faz.bot.wynn.api.response.online_players_response import OnlinePlayersResponse
from faz.bot.wynn.api.response.player_response import PlayerResponse

from faz.bot.app.collect.objects.request import Request
from faz.bot.app.collect.objects.request_type import RequestType
from faz.bot.app.collect.task._request_queue_manager import RequestQueueManager
from faz.bot.app.collect.task.response_queue import ResponseQueue
from faz.bot.app.collect.task.task_api_request import TaskApiRequest


class ResponseHandler:
    def __init__(
        self,
        request_queue_manager: RequestQueueManager,
        response_queue: ResponseQueue,
        api_request_task: TaskApiRequest,
    ) -> None:
        self._request_queue_manager = request_queue_manager
        self._response_queue = response_queue
        self._api_request_task = api_request_task

    def handle_response(self, request: Request) -> None:
        response = request.get_result()

        self._request_queue_manager.on_request_complete(response)
        self._response_queue.put([response])
        self._api_request_task.run_request()
