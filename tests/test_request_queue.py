from datetime import datetime as dt
from unittest import TestCase
from unittest.mock import MagicMock

from faz.bot.app.collect.task.request_queue import RequestQueue


class TestRequestList(TestCase):
    def setUp(self) -> None:
        self.request_list = RequestQueue()

    def test_enqueue_and_dequeue(self) -> None:
        # Prepare
        mock_coro1 = self.__create_mock_coro("foo")
        test_req_ts1 = dt.now().timestamp() - 100

        # Act
        self.request_list.enqueue(test_req_ts1, mock_coro1)

        # Assert
        # NOTE: Assert that the request is enqueued properly
        self.assertEqual(len(self.request_list._list), 1)
        self.assertEqual(self.request_list._list[0].coro, mock_coro1)
        self.assertEqual(self.request_list._list[0]._req_ts, test_req_ts1)

        # Act
        result = self.request_list.dequeue(1)

        # Assert
        # NOTE: Assert that the correct request is dequeued
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], mock_coro1)

    def test_dequeue_with_request_ts(self) -> None:
        # Prepare
        mock_coro1 = self.__create_mock_coro("foo")
        mock_coro2 = self.__create_mock_coro("bar")
        test_req_ts1 = dt.now().timestamp() - 100
        test_req_ts2 = dt.now().timestamp() - 200  # earlier timestamp

        self.request_list.enqueue(test_req_ts1, mock_coro1)
        self.request_list.enqueue(test_req_ts2, mock_coro2)

        # Act
        result = self.request_list.dequeue(1)

        # Assert
        # NOTE: Assert that the request with the earliest timestamp is dequeued first
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], mock_coro2)
        remaining_item = self.request_list._list.pop()
        # NOTE: Assert that the remaining item is the one with the later timestamp
        self.assertEqual(remaining_item.coro, mock_coro1)
        self.assertEqual(remaining_item._req_ts, test_req_ts1)

    def test_dequeue_with_priority(self) -> None:
        # Prepare
        mock_coro1 = self.__create_mock_coro("foo")
        mock_coro2 = self.__create_mock_coro("bar")
        test_req_ts1 = dt.now().timestamp() - 100
        test_req_ts2 = dt.now().timestamp() - 50  # should still return higher priority
        self.request_list.enqueue(test_req_ts1, mock_coro1, priority=100)
        self.request_list.enqueue(
            test_req_ts2, mock_coro2, priority=200
        )  # higher priority

        # Act
        result = self.request_list.dequeue(1)

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result.pop(), mock_coro2)

    def test_dequeue_equal_all(self) -> None:
        # Prepare
        test_coros = [self.__create_mock_coro(str(i)) for i in range(100)]
        test_req_ts = 0
        for coro in test_coros:
            self.request_list.enqueue(test_req_ts, coro)

        # Act
        result = self.request_list.dequeue(15)

        # Assert
        self.assertEqual(len(result), 15)
        for coro in result:
            self.assertTrue(coro in test_coros)

    def test_request_item_is_eligible(self) -> None:
        # Prepare
        mock_coro1 = self.__create_mock_coro("foo")
        test_req_ts1 = dt.now().timestamp() - 1  # Past timestamp
        request_item = RequestQueue.RequestItem(mock_coro1, 100, test_req_ts1)

        # Assert
        self.assertTrue(request_item.is_eligible())

    def test_request_item_is_not_eligible(self) -> None:
        # Prepare
        mock_coro1 = self.__create_mock_coro("foo")
        test_req_ts1 = dt.now().timestamp() + 1000  # Future timestamp
        request_item = RequestQueue.RequestItem(mock_coro1, 100, test_req_ts1)

        # Assert
        self.assertFalse(request_item.is_eligible())

    def test_request_item_comparison(self) -> None:
        # Prepare
        mock_coro1 = self.__create_mock_coro("foo")
        mock_coro2 = self.__create_mock_coro("bar")
        item1 = RequestQueue.RequestItem(mock_coro1, 100, 0)
        item2 = RequestQueue.RequestItem(mock_coro2, 200, 0)

        # Assert
        self.assertLess(item2, item1)

    def test_request_item_equality(self) -> None:
        # Prepare
        mock_coro1 = self.__create_mock_coro("foo")
        mock_coro2 = self.__create_mock_coro("foo")
        item1 = RequestQueue.RequestItem(mock_coro1, 100, 100)
        item2 = RequestQueue.RequestItem(mock_coro2, 100, 100)

        # Assert
        self.assertEqual(item1, item2)

    @staticmethod
    def __create_mock_coro(ret: str) -> MagicMock:
        mock = MagicMock()
        mock.return_value = ret
        mock.cr_frame.f_locals = ret
        mock.__class__ = MagicMock
        return mock

    def tearDown(self) -> None:
        pass
