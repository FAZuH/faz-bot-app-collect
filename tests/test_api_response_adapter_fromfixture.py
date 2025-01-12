# import unittest
# from decimal import Decimal
# from types import NoneType
#
# from faz.bot.database.fazwynn.model.character_history import CharacterHistory
#
# from faz.bot.app.collect.task.api_response_adapter import ResponseAdapter
#
# from fazdb.util import ResponseAdapter
# from fazutil.db.fazdb.model import CharacterHistory
# from fazutil.db.fazdb.model.column import DateColumn, GamemodeColumn, UuidColumn


# from tests.fixtures_api import FixturesApi


# class TestResponseAdapterFromfixture(unittest.IsolatedAsyncioTestCase):
#     """Tests if db.models is properly storing data."""
#
#     async def asyncSetUp(self) -> None:
#         self.adapter = ResponseAdapter()
#
#         self.fixtures = FixturesApi()
#         self.mock_guildstats = self.fixtures.get_guilds()
#         self.mock_onlineuuids = self.fixtures.get_online_uuids()
#         self.mock_playerstats = self.fixtures.get_players()
#
#     async def test_character_history(self) -> None:
#         for stat in self.mock_playerstats:
#             for datum in self.adapter.Player.to_character_history(stat):
#                 self.assertIsInstance(datum, CharacterHistory)
#                 self.assertIsInstance(datum.character_uuid, UuidColumn)
#                 self.assertIsInstance(datum.level, int)
#                 self.assertIsInstance(datum.xp, int)
#                 self.assertIsInstance(datum.wars, int)
#                 self.assertIsInstance(datum.playtime, Decimal)
#                 self.assertIsInstance(datum.mobs_killed, int)
#                 self.assertIsInstance(datum.chests_found, int)
#                 self.assertIsInstance(datum.logins, int)
#                 self.assertIsInstance(datum.deaths, int)
#                 self.assertIsInstance(datum.discoveries, int)
#                 self.assertIsInstance(datum.gamemode, GamemodeColumn)
#                 self.assertIsInstance(datum.alchemism, Decimal)
#                 self.assertIsInstance(datum.armouring, Decimal)
#                 self.assertIsInstance(datum.cooking, Decimal)
#                 self.assertIsInstance(datum.jeweling, Decimal)
#                 self.assertIsInstance(datum.scribing, Decimal)
#                 self.assertIsInstance(datum.tailoring, Decimal)
#                 self.assertIsInstance(datum.weaponsmithing, Decimal)
#                 self.assertIsInstance(datum.woodworking, Decimal)
#                 self.assertIsInstance(datum.mining, Decimal)
#                 self.assertIsInstance(datum.woodcutting, Decimal)
#                 self.assertIsInstance(datum.farming, Decimal)
#                 self.assertIsInstance(datum.fishing, Decimal)
#                 self.assertIsInstance(datum.dungeon_completions, int)
#                 self.assertIsInstance(datum.quest_completions, int)
#                 self.assertIsInstance(datum.raid_completions, int)
#                 self.assertIsInstance(datum.datetime, DateColumn)
#
#     async def test_character_info(self) -> None:
#         for stat in self.mock_playerstats:
#             for datum in self.adapter.Player.to_character_info(stat):
#                 self.assertIsInstance(datum.character_uuid, UuidColumn)
#                 self.assertIsInstance(datum.uuid, UuidColumn)
#                 self.assertIsInstance(datum.type, str)
#
#     async def test_guild_history(self) -> None:
#         for stat in self.mock_guildstats:
#             datum = self.adapter.Guild.to_guild_history(stat)
#             self.assertIsInstance(datum.name, str)
#             self.assertIsInstance(datum.level, Decimal)
#             self.assertIsInstance(datum.territories, int)
#             self.assertIsInstance(datum.wars, int)
#             self.assertIsInstance(datum.member_total, int)
#             self.assertIsInstance(datum.online_members, int)
#             self.assertIsInstance(datum.datetime, DateColumn)
#
#     async def test_guild_info(self) -> None:
#         for stat in self.mock_guildstats:
#             datum = self.adapter.Guild.to_guild_info(stat)
#             self.assertIsInstance(datum.name, str)
#             self.assertIsInstance(datum.prefix, str)
#             self.assertIsInstance(datum.created, DateColumn)
#
#     async def test_guild_member_history(self) -> None:
#         for stat in self.mock_guildstats:
#             for datum in self.adapter.Guild.to_guild_member_history(stat):
#                 self.assertIsInstance(datum.uuid, UuidColumn)
#                 self.assertIsInstance(datum.contributed, int)
#                 self.assertIsInstance(datum.joined, DateColumn)
#                 self.assertIsInstance(datum.datetime, DateColumn)
#
#     async def test_online_players(self) -> None:
#         for datum in self.adapter.OnlinePlayers.to_online_players(
#             self.mock_onlineuuids
#         ):
#             self.assertIsInstance(datum.uuid, UuidColumn)
#             self.assertIsInstance(datum.server, str)
#
#     @unittest.skip("Needs long and time-consuming process to test.")
#     async def test_player_activity_history(self) -> None:
#         # TODO: simulate process
#         pass
#
#     async def test_player_history(self) -> None:
#         for stat in self.mock_playerstats:
#             datum = self.adapter.Player.to_player_history(stat)
#             self.assertIsInstance(datum.uuid, UuidColumn)
#             self.assertIsInstance(datum.username, str)
#             self.assertIsInstance(datum.support_rank, (NoneType, str))
#             self.assertIsInstance(datum.playtime, Decimal)
#             self.assertIsInstance(datum.guild_name, (NoneType, str))
#             self.assertIsInstance(datum.guild_rank, (NoneType, str))
#             self.assertIsInstance(datum.rank, str)
#             self.assertIsInstance(datum.datetime, DateColumn)
#
#     async def test_player_info(self) -> None:
#         for stat in self.mock_playerstats:
#             datum = self.adapter.Player.to_player_info(stat)
#             self.assertIsInstance(datum.uuid, UuidColumn)
#             self.assertIsInstance(datum.latest_username, str)
#             self.assertIsInstance(datum.first_join, DateColumn)
#
#     async def asyncTearDown(self) -> None:
#         # await self.wynnapi.close()
#         return
