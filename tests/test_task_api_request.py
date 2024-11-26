import unittest
from typing import override
from unittest.mock import AsyncMock, MagicMock, patch

from faz.bot.app.collect.task.task_api_request import TaskApiRequest


class TestTaskApiRequest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self._event_loop_patcher = patch(
            "faz.bot.app.collect.task.task_api_request.asyncio"
        )
        self._mock_event_loop = self._event_loop_patcher.start()
        self._mock_api = MagicMock()
        self._mock_request_queue = MagicMock()
        self._mock_response_queue = MagicMock()
        self._task_api_request = TaskApiRequest(
            self._mock_api, self._mock_request_queue, self._mock_response_queue
        )

    async def test_setup(self):
        # Act
        self._task_api_request.setup()
        # Assert
        self._mock_api.start.assert_called_once()
        self._mock_request_queue.enqueue.assert_called_once_with(
            0, self._mock_api.player.get_online_uuids(), priority=999
        )

    def test_teardown(self):
        # Prepare
        self._mock_api.close = MagicMock()
        # Act
        self._task_api_request.teardown()
        # Assert
        self._mock_api.close.assert_called_once()

    def test_run(self):
        # Prepare
        self._task_api_request._run = AsyncMock()
        # Act
        self._task_api_request.run()
        # Assert
        self._task_api_request._run.assert_called_once()
        self.assertIsNotNone(self._task_api_request._latest_run)

    async def test_check_api_session(self):
        # Prepare
        self._mock_api.request.is_open.return_value = False
        self._task_api_request._api.start = AsyncMock()
        # Act
        await self._task_api_request._check_api_session()
        # Assert
        self._mock_api.start.assert_called_once()

    async def test_start_requests(self):
        # Prepare
        self._mock_request_queue.dequeue.return_value = [AsyncMock(), AsyncMock()]
        # Act
        self._task_api_request._start_requests()
        # Assert
        self.assertEqual(len(self._task_api_request._running_requests), 2)

    def test_check_responses_unfinished_requests(self) -> None:
        # Prepare
        mock_task = MagicMock()
        mock_task.done.return_value = False
        self._task_api_request._running_requests.append(mock_task)
        # Act
        self._task_api_request._check_responses()
        # Assert
        mock_task.exception.assert_not_called()

    def test_check_responses_removes_tasks_with_exception(self) -> None:
        # Prepare
        mock_coro = MagicMock()
        mock_coro.__qualname__ = "NotPlayer"
        self._mock_api.player.get_online_uuids.__qualname__ = (
            "PlayerEndpoint.get_online_uuids"
        )
        mock_task = MagicMock()
        mock_task.get_coro.return_value = mock_coro
        self._task_api_request._running_requests.append(mock_task)
        # Act, Assert
        self._task_api_request._check_responses()
        self._mock_request_queue.enqueue.assert_not_called()
        self.assertNotIn(mock_task, self._task_api_request._running_requests)

    def test_check_responses_with_exception(self) -> None:
        """Test if tasks with exceptions are raised properly on _check_responses.
        Note that this is separated from test_check_responses_removes_tasks_with_exception,
        because logger is patched, and the exception is not handled inside.
        """
        # Prepare
        mock_coro = MagicMock()
        mock_coro.__qualname__ = "NotPlayer"
        self._mock_api.player.get_online_uuids.__qualname__ = (
            "PlayerEndpoint.get_online_uuids"
        )
        mock_task = MagicMock()
        mock_task.get_coro.return_value = mock_coro
        mock_task.exception.return_value = self._MockException
        self._task_api_request._running_requests.append(mock_task)
        with patch("faz.bot.app.collect.task.task_api_request.logger") as _:
            # Act, Assert
            with self.assertRaises(self._MockException):
                self._task_api_request._check_responses()
            self._mock_request_queue.enqueue.assert_not_called()

    def test_check_responses_with_online_players_exception(self) -> None:
        # Prepare
        mock_coro = MagicMock()
        mock_coro.__qualname__ = "PlayerEndpoint.get_online_uuids"
        self._mock_api.player.get_online_uuids.__qualname__ = (
            "PlayerEndpoint.get_online_uuids"
        )
        mock_task = MagicMock()
        mock_task.get_coro.return_value = mock_coro
        mock_task.exception.return_value = self._MockException
        self._task_api_request._running_requests.append(mock_task)
        # Act, Assert
        self._task_api_request._check_responses()
        self._mock_request_queue.enqueue.assert_called_once_with(
            0, self._mock_api.player.get_online_uuids.return_value, priority=999
        )

    def test_check_responses_successful_requests(self) -> None:
        # Prepare
        mock_task = MagicMock()
        mock_task.done.return_value = True
        mock_task.exception.return_value = None
        self._task_api_request._running_requests.append(mock_task)
        # Act
        self._task_api_request._check_responses()
        # Assert
        self.assertNotIn(mock_task, self._task_api_request._running_requests)
        self._mock_response_queue.put.assert_called_once_with(
            [mock_task.result.return_value]
        )

    @override
    def tearDown(self) -> None:
        self._event_loop_patcher.stop()

    class _MockException(Exception): ...
