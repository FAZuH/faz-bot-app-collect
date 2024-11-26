from datetime import datetime
from typing import Iterable

from faz.bot.wynn.api.response.guild_response import GuildResponse
from faz.bot.wynn.api.response.online_players_response import OnlinePlayersResponse
from faz.bot.wynn.api.response.player_response import PlayerResponse
from faz.bot.wynn.api.wynn_api import WynnApi

from faz.bot.app.collect.task.request_queue import RequestQueue


class ResponseHandler:
    """Handles Wynncraft response processing, queueing, and requeuing."""

    def __init__(self, api: WynnApi, request_list: RequestQueue) -> None:
        self._api = api
        self._request_list = request_list

        self._online_guilds: dict[str, set[str]] = {}
        self._online_players: dict[str, datetime] = {}
        self._logged_on_guilds: set[str] = set()
        self._logged_on_players: set[str] = set()

    def handle_onlineplayers_response(self, resp: None | OnlinePlayersResponse) -> None:
        if not resp or not resp.body.raw:
            return
        self._process_onlineplayers_response(resp)
        self._requeue_onlineplayers(resp)
        self._enqueue_player()

    def handle_player_response(self, resps: Iterable[PlayerResponse]) -> None:
        if not resps:
            return
        self._process_player_response(resps)
        self._requeue_player(resps)
        self._enqueue_guild()

    def handle_guild_response(self, resps: Iterable[GuildResponse]) -> None:
        if not resps:
            return
        self._requeue_guild(resps)

    # OnlinePlayersResponse
    def _process_onlineplayers_response(self, resp: OnlinePlayersResponse) -> None:
        new_online_uuids: set[str] = {str(uuid) for uuid in resp.body.players}
        prev_online_uuids: set[str] = set(self.online_players)

        logged_off: set[str] = prev_online_uuids - new_online_uuids
        self._logged_on_players: set[str] = new_online_uuids - prev_online_uuids

        for uuid in logged_off:
            del self.online_players[uuid]

        for uuid in self.logged_on_players:
            self.online_players[uuid] = resp.headers.to_datetime()

    def _enqueue_player(self) -> None:
        for uuid in self.logged_on_players:
            self._request_list.enqueue(0, self._api.player.get_full_stats(uuid))

    def _requeue_onlineplayers(self, resp: OnlinePlayersResponse) -> None:
        self._request_list.enqueue(
            resp.headers.expires.to_datetime().timestamp(),
            self._api.player.get_online_uuids(),
            priority=999,
        )

    # PlayerResponse
    def _process_player_response(self, resps: Iterable[PlayerResponse]) -> None:
        logged_on_guilds: set[str] = set()
        for resp in resps:
            if resp.body.guild is None:
                continue

            guild_name = resp.body.guild.name
            is_online = resp.body.online
            uuid = resp.body.uuid.uuid

            # If an uuid is online, and not in dictionary, create a new guild entry with the uuid.
            # This also means that the guild is LOGGED ON
            if is_online is True:
                if guild_name not in self.online_guilds:
                    self.online_guilds[guild_name] = {
                        uuid,
                    }
                    logged_on_guilds.add(guild_name)
                else:
                    # If guild is not LOGGED ON, add the uuid to the online uuids of that guild
                    self.online_guilds[guild_name].add(uuid)

            # If an uuid is offline, and in dictionary, remove the uuid from the set of that guild
            else:
                guild = self.online_guilds.get(guild_name)
                if not guild or uuid not in guild:
                    continue

                guild.remove(uuid)

                # Check the guild dictionary, if the set is empty, remove the guild from the dictionary.
                # This also means that the guild is LOGGED OFF
                if len(guild) == 0:
                    self.online_guilds.pop(guild_name)

        self._logged_on_guilds = logged_on_guilds.copy()

    def _enqueue_guild(self) -> None:
        for guild_name in self._logged_on_guilds:
            self._request_list.enqueue(0, self._api.guild.get(guild_name))

    def _requeue_player(self, resps: Iterable[PlayerResponse]) -> None:
        for resp in resps:
            if resp.body.online is False:
                continue

            self._request_list.enqueue(
                resp.headers.expires.to_datetime().timestamp(),
                self._api.player.get_full_stats(resp.body.uuid.uuid),
            )

    # GuildResponse
    def _requeue_guild(self, resps: Iterable[GuildResponse]) -> None:
        for resp in resps:
            if resp.body.members.get_online_members() <= 0:
                continue

            self._request_list.enqueue(
                resp.headers.expires.to_datetime().timestamp(),
                self._api.guild.get(resp.body.name),
            )

    @property
    def logged_on_guilds(self) -> set[str]:
        """Set of latest logged on guilds' names."""
        return self._logged_on_guilds

    @property
    def logged_on_players(self) -> set[str]:
        """Set of latest logged on players' uuids. Needed by PlayerActivityHistory."""
        return self._logged_on_players

    @property
    def online_players(self) -> dict[str, datetime]:
        """Dict of online players' uuids, paired with their logged on timestamp."""
        return self._online_players

    @property
    def online_guilds(self) -> dict[str, set[str]]:
        """guild_name: set(online_uuids)"""
        return self._online_guilds
