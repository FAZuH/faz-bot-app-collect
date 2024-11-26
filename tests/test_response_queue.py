import unittest
from unittest.mock import MagicMock

from faz.bot.app.collect.task.response_queue import ResponseQueue


class TestResponseList(unittest.TestCase):
    def setUp(self) -> None:
        self.response_list = ResponseQueue()

    def test_put_and_get(self) -> None:
        response1 = MagicMock()
        response2 = MagicMock()

        self.response_list.put([response1, response2])

        result = self.response_list.get()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], response1)
        self.assertEqual(result[1], response2)

    def test_get_with_empty_list(self) -> None:
        result = self.response_list.get()

        self.assertEqual(len(result), 0)

    def tearDown(self) -> None:
        pass
