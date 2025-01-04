class GuildRequest:
    def __init__(self, guild_id: int, user_id: int, role_id: int, request_id: int):
        self.guild_id = guild_id
        self.user_id = user_id
        self.role_id = role_id
        self.request_id = request_id