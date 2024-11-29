from datetime import datetime
from unittest import TestCase
from unittest.mock import MagicMock

from faz.bot.wynn.api.wynn_api import WynnApi

from faz.bot.app.collect.task._response_handler import ResponseHandler
from faz.bot.app.collect.task.request_queue import RequestQueue


class TestResponseHandler(TestCase):
    def setUp(self) -> None:
        self._api = MagicMock(spec_set=WynnApi)
        self.__request_list = MagicMock(spec_set=RequestQueue)
        self._manager = ResponseHandler(self._api, self.__request_list)

    # OnlinePlayerResponse
    def test_process_new_response(self) -> None:
        # Prepare
        uuid0 = "0"
        uuid1 = "1"
        uuid2 = "2"
        datetime0 = MagicMock(spec_set=datetime)
        datetime1 = MagicMock(spec_set=datetime)
        resp0 = MagicMock()
        resp1 = MagicMock()
        resp0.body.players = {uuid0, uuid1}
        resp0.headers.to_datetime.return_value = datetime0
        resp1.body.players = {uuid1, uuid2}
        resp1.headers.to_datetime.return_value = datetime1

        # Act
        self._manager._process_onlineplayers_response(resp0)

        # Assert
        # NOTE: Assert that player 1 and 2 has logged on.
        self.assertSetEqual(self._manager.logged_on_players, {uuid0, uuid1})
        # NOTE: Assert that player 1 and 2 is online, with the correct logged on datetime.
        self.assertDictEqual(self._manager.online_players, {uuid0: datetime0, uuid1: datetime0})

        # Act
        self._manager._process_onlineplayers_response(resp1)

        # Assert
        # NOTE: Assert that only player 2 has logged on because player 1 is already logged on.
        self.assertSetEqual(self._manager._logged_on_players, {uuid2})
        # NOTE: Assert that player 0 is no longer online, while player 1 and player 2 has the correct logged on datetime.
        self.assertDictEqual(self._manager.online_players, {uuid1: datetime0, uuid2: datetime1})

    def test_enqueue_player_stats(self) -> None:
        # Prepare
        uuid0 = "player0"
        self._manager._logged_on_players = {uuid0}

        # Act
        self._manager._enqueue_player()

        # Assert
        # NOTE: Assert that the correct player is being queued.
        self._api.player.get_full_stats.assert_called_once_with(uuid0)
        # NOTE: Assert that enqueue is called with the correct arguments.
        self.__request_list.enqueue.assert_called_once_with(0, self._api.player.get_full_stats())

    def test_requeueonline_players(self) -> None:
        # Prepare
        resp = MagicMock()
        resp.headers.expires.to_datetime().timestamp.return_value = 69

        # Act
        self._manager._requeue_onlineplayers(resp)

        # Assert
        # NOTE: Assert that enqueue is called with the correct arguments.
        self.__request_list.enqueue.assert_called_once_with(
            69, self._api.player.get_online_uuids(), priority=999
        )

    # PlayerResponse
    def test_process_player_response(self) -> None:
        # Prepare
        guild0 = "guild0"
        guild1 = "guild1"
        uuid0 = "0"
        uuid1 = "1"
        uuid2 = "2"
        mock1 = MagicMock()
        mock2 = MagicMock()
        mock3 = MagicMock()
        mock1.body.guild.name = guild0
        mock1.body.uuid.uuid = uuid0
        mock1.body.online = True
        mock2.body.guild.name = guild0
        mock2.body.uuid.uuid = uuid1
        mock2.body.online = True
        mock3.body.guild.name = guild1
        mock3.body.uuid.uuid = uuid2
        mock3.body.online = True

        # Act
        self._manager._process_player_response([mock1])

        # Assert
        # NOTE: Assert that guild "test0" is logged on.
        self.assertSetEqual(self._manager._logged_on_guilds, {guild0})
        # NOTE: Assert that guild "test0" is online with correct players.
        self.assertDictEqual(self._manager.online_guilds, {guild0: {uuid0}})

        # Act
        self._manager._process_player_response([mock2, mock3])

        # Assert
        # NOTE: Assert that only guild test1 is logged on, because test0 is already logged on.
        self.assertSetEqual(self._manager._logged_on_guilds, {guild1})
        # NOTE: Assert that both guilds are online with correct players.
        self.assertDictEqual(self._manager.online_guilds, {guild0: {uuid0, uuid1}, guild1: {uuid2}})

        # Prepare
        mock3.body.online = False

        # Act
        self._manager._process_player_response([mock3])

        # Assert
        # NOTE: Assert that guild test1 is no longer online.
        self.assertDictEqual(self._manager.online_guilds, {guild0: {uuid0, uuid1}})

    def test_enqueue_guild(self) -> None:
        # Prepare
        guild0 = "guild0"
        self._manager._logged_on_guilds = {guild0}

        # Act
        self._manager._enqueue_guild()

        # Assert
        # NOTE: Assert that the correct guild is being queued.
        self._api.guild.get.assert_called_once_with(guild0)
        # NOTE: Assert that enqueue is called with the correct arguments.
        self.__request_list.enqueue.assert_called_once_with(0, self._api.guild.get())

    def test_requeue_player(self) -> None:
        # Prepare
        resp1 = MagicMock()
        resp2 = MagicMock()  # continued
        resp1.body.online = True
        resp1.headers.expires.to_datetime().timestamp.return_value = 69
        resp2.body.online = False

        # Act
        self._manager._requeue_player([resp2, resp1])

        # Assert
        # NOTE: Assert that self._api.player.get_online_uuids() is called with the correct arguments
        self._api.player.get_full_stats.assert_called_once()
        # NOTE: Assert that enqueue is called with the correct arguments.
        self.__request_list.enqueue.assert_called_once_with(69, self._api.player.get_full_stats())

    # GuildResponse
    def test_requeue_guild(self) -> None:
        # Prepare
        test_name1 = "guild0"
        test_resp1 = MagicMock()
        test_resp2 = MagicMock()  # continued
        test_resp1.body.name = test_name1
        test_resp1.body.members.get_online_members.return_value = 1
        test_resp1.headers.expires.to_datetime().timestamp.return_value = 69
        test_resp2.body.members.get_online_members.return_value = 0

        # Act
        self._manager._requeue_guild([test_resp1, test_resp2])

        # Assert
        # NOTE: Assert that self._api.guild.get() is called with the correct arguments
        self._api.guild.get.assert_called_once_with(test_name1)
        # NOTE: Assert that enqueue is called with the correct arguments.
        self.__request_list.enqueue.assert_called_once_with(69, self._api.guild.get())
