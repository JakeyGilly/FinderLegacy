import asyncio, datetime, discord, re, info
from dateutil.relativedelta import relativedelta
from discord.ext import commands, tasks
def parse_duration_string(duration: str) -> relativedelta:
    if not re.compile(r"((?P<years>\d+?) ?(years|year|Y|y) ?)?((?P<months>\d+?) ?(months|month|M) ?)?((?P<weeks>\d+?) ?(weeks|week|W|w) ?)?((?P<days>\d+?) ?(days|day|D|d) ?)?((?P<hours>\d+?) ?(hours|hour|H|h) ?)?((?P<minutes>\d+?) ?(minutes|minute|m|min|mins) ?)?((?P<seconds>\d+?) ?(seconds|second|S|s|sec|secs))?").fullmatch(duration):
        return None
    return relativedelta(**{unit: int(amount) for unit, amount in re.compile(r"((?P<years>\d+?) ?(years|year|Y|y) ?)?((?P<months>\d+?) ?(months|month|M) ?)?((?P<weeks>\d+?) ?(weeks|week|W|w) ?)?((?P<days>\d+?) ?(days|day|D|d) ?)?((?P<hours>\d+?) ?(hours|hour|H|h) ?)?((?P<minutes>\d+?) ?(minutes|minute|m|min|mins) ?)?((?P<seconds>\d+?) ?(seconds|second|S|s|sec|secs))?").fullmatch(duration).groupdict(default=0).items()})
class DurationDelta(commands.Converter):
    async def convert(self, duration: str) -> relativedelta:
        if not (delta := parse_duration_string(duration)):
            raise commands.BadArgument(f"`{duration}` is not a valid duration string.")
        return delta
def humanize_delta(delta: relativedelta) -> str:
    time_strings = []
    for unit, value in ((f"year{'s'[:delta.years^1]}", delta.years),(f"month{'s'[:delta.months^1]}", delta.months),(f"day{'s'[:delta.days^1]}", delta.days),(f"hour{'s'[:delta.hours^1]}", delta.hours),(f"minute{'s'[:delta.minutes^1]}", delta.minutes),(f"second{'s'[:delta.seconds^1]}", delta.seconds)):
        if value:
            time_strings.append(f"{value} {unit}")
    if len(time_strings) > 1:
        time_strings[-1] = f"{time_strings[-2]} and {time_strings[-1]}"
        del time_strings[-2]
    return ", ".join(time_strings)
class BannedUser(commands.Converter):
    async def convert(self, ctx, user_id):
        if user_id.isdigit():
            try:
                return(await ctx.guild.fetch_ban(discord.Object(id=int(user_id)))).user
            except discord.NotFound:
                raise commands.UserNotFound(user_id)
        if [e.user for e in await ctx.guild.bans()] is not []:
            if (user := discord.utils.find(lambda u: str(u) == user_id, [e.user for e in await ctx.guild.bans()])):
                return user
            else:
                raise commands.UserNotFound(user_id)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_unban.start()
        self.check_unmute.start()
        self.mute_perms.start()

#TODO: add infractions in messages
#TODO: detect kicks and bans and muted role adding without bot commands and add to db
#TODO: make a logs command

    # ===============================
    # ============= Ban =============
    # ===============================
    @commands.command(name="ban", aliases=["b"])
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: commands.MemberConverter, *, reason="No Reason Provided"):
        if not await self.bot.db.settings.find_one({"_id": ctx.guild.id}):
            await self.bot.db.settings.insert_one({"_id": ctx.guild.id})
        if not await self.bot.db.logs.find_one({"_id": ctx.guild.id}):
            await self.bot.db.logs.insert_one({"_id": ctx.guild.id})
        if (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("disabled_mod_modules") and "ban" in (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("disabled_mod_modules"):
            await ctx.send(embed=discord.Embed(title="Banning Disabled", colour=0x3DF270).add_field(name="You can ban the user manually or contact the server owner", value="You can enable the ban command by changing the settings", inline=False).set_footer(text=f"FinderBot Version {info.version}"))
            return
        confirm = await ctx.send(embed=discord.Embed(title="Are you sure you want to ban this user?", colour=0x3DF270).add_field(name="User", value=f"{user.mention} ({user})", inline=False).add_field(name="for reason", value=f"{reason}", inline=False).set_footer(text=f"FinderBot Version {info.version}"))
        await confirm.add_reaction("✅")
        def check(_reaction, _author):
            return _author == ctx.message.author and _reaction.emoji == '✅' and _reaction.message.id == confirm.id
        try:
            await ctx.bot.wait_for('reaction_add', timeout=10.0, check=check) 
        except asyncio.TimeoutError:
            await confirm.edit(embed=discord.Embed(title="Timed Out", color=0xFF0000).add_field(name=f"{ctx.author.name}, You took too long to respond!", value="Try running the command again").set_footer(text=f"FinderBot Version {info.version}"))
        else:
            await user.send(embed=discord.Embed(title=f"You have been banned", colour=0x3DF270).add_field(name="Server", value=f"{ctx.guild.name}", inline=False).add_field(name="Reason", value=f"{reason}", inline=False).set_footer(text=f"FinderBot Version {info.version}").set_thumbnail(url=ctx.guild.icon_url))
            await ctx.guild.ban(user, reason=reason)
            await confirm.edit(embed=discord.Embed(title="User Banned", colour=0x3DF270).add_field(name="User", value=f"{user.mention} ({user})", inline=False).add_field(name="for reason", value=f"{reason}", inline=False).set_footer(text=f"FinderBot Version {info.version}"))
            if not await self.bot.db.logs.find_one({"_id": ctx.guild.id}):
                await self.bot.db.logs.insert_one({"_id": ctx.guild.id})
            await self.bot.db.logs.update_one({"_id": ctx.guild.id}, {"$inc": {f"{user.id}.bans": 1}})  
    # ===============================



    # ====================================
    # ============= Temp Ban =============
    # ====================================
    @commands.command(name="tempban", aliases=["temporaryban", "tempb", "tb", "tban"])
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def tempban(self, ctx, user: commands.MemberConverter, time, *, reason="No Reason Provided"):
        if not await self.bot.db.settings.find_one({"_id": ctx.guild.id}):
            await self.bot.db.settings.insert_one({"_id": ctx.guild.id})
        if not await self.bot.db.logs.find_one({"_id": ctx.guild.id}):
            await self.bot.db.logs.insert_one({"_id": ctx.guild.id})
        if (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("disabled_mod_modules") and "ban" in (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("disabled_mod_modules"):
            await ctx.send(embed=discord.Embed(title="Banning Disabled", colour=0x3DF270).add_field(name="You can ban the user manually or contact the server owner", value="You can enable the ban command by changing the settings", inline=False).set_footer(text=f"FinderBot Version {info.version}"))
            return
        confirm = await ctx.send(embed=discord.Embed(title="Are you sure you want to tempban this user?", colour=0x3DF270).add_field(name="User", value=f"{user.mention} ({user})", inline=False).add_field(name="for time", value=f"{time}", inline=False).add_field(name="for reason", value=f"{reason}", inline=False).set_footer(text=f"FinderBot Version {info.version}"))
        await confirm.add_reaction("✅")
        def check(_reaction, _author):
            return _author == ctx.message.author and str(_reaction.emoji) == '✅' and _reaction.message.id == confirm.id
        try:
            await ctx.bot.wait_for('reaction_add', timeout=10.0, check=check)
        except asyncio.TimeoutError:
            await confirm.edit(embed=discord.Embed(title="Timed Out", color=0xFF0000).add_field(name=f"{ctx.author.name}, You took too long to respond!", value="Try running the command again").set_footer(text=f"FinderBot Version {info.version}"))
        else:
            await user.send(embed=discord.Embed(title=f"You have been temp banned", colour=0x3DF270).add_field(name="Server", value=f"{ctx.guild.name}", inline=False).add_field(name="Reason", value=f"{reason}", inline=False).add_field(name="Time", value=f"{humanize_delta(await DurationDelta.convert(self, time))}").set_footer(text=f"FinderBot Version {info.version}").set_thumbnail(url=ctx.guild.icon_url))
            await ctx.guild.ban(user, reason=reason)
            await confirm.edit(embed=discord.Embed(title="User Temp Banned", colour=0x3DF270).add_field(name="User", value=f"{user.mention} ({user})", inline=False).add_field(name="for time", value=f"{humanize_delta(await DurationDelta.convert(self, time))}", inline=False).add_field(name="for reason", value=f"{reason}", inline=False).set_footer(text=f"FinderBot Version {info.version}"))
            await self.bot.db.logs.update_one({"_id": ctx.guild.id}, {"$inc": {f"{user.id}.bans": 1}, "$set": {f"{user.id}.unbans.time": datetime.datetime.now() + await DurationDelta.convert(self, time)}}) 
    
    
    # =========================================
    # =============== Ban Check ===============
    # =========================================
    @tasks.loop(seconds=5.0)
    async def check_unban(self):
        for guild in self.bot.guilds:
            if not await self.bot.db.settings.find_one({"_id": guild.id}):
                await self.bot.db.settings.insert_one({"_id": guild.id})
            if (await self.bot.db.settings.find_one({"_id": guild.id})).get("disabled_mod_modules") and "ban" in (await self.bot.db.settings.find_one({"_id": guild.id})).get("disabled_mod_modules"):
                return
            if await self.bot.db.logs.find_one({"_id": guild.id}):
                for user in (await self.bot.db.logs.find_one({"_id": guild.id})):
                    if not user == "_id" and (await self.bot.db.logs.find_one({"_id": guild.id}))[user].get("unbans") and (await self.bot.db.logs.find_one({"_id": guild.id}))[user].get("unbans").get("time") and (await self.bot.db.logs.find_one({"_id": guild.id}))[user].get("unbans").get("time") < datetime.datetime.now():
                        await guild.unban(discord.Object(id=int(user)))
                        await self.bot.db.logs.update_one({"_id": guild.id}, {"$unset": {f"{user.id}.unbans.time": ""}, "$inc": {f"{user.id}.unbans.unbans": 1}})
    @check_unban.before_loop
    async def before_unban(self):
        await self.bot.wait_until_ready()
    # ====================================



    # =================================
    # ============= Unban =============
    # =================================
    @commands.command(name="unban", aliases=["unb", "ub"])
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: BannedUser):
        if not await self.bot.db.settings.find_one({"_id": ctx.guild.id}):
            await self.bot.db.settings.insert_one({"_id": ctx.guild.id})
        if not await self.bot.db.logs.find_one({"_id": ctx.guild.id}):
                await self.bot.db.logs.insert_one({"_id": ctx.guild.id, "users": []})
        if (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("disabled_mod_modules") and "ban" in (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("disabled_mod_modules"):
            await ctx.send(embed=discord.Embed(title="Banning Disabled", colour=0x3DF270).add_field(name="You can ban the user manually or contact the server owner", value="You can enable the ban command by changing the settings", inline=False).set_footer(text=f"FinderBot Version {info.version}"))
            return
        confirm = await ctx.send(embed=discord.Embed(title="Are you sure you want to unban this user?", colour=0x3DF270).add_field(name="User", value=user, inline=False).set_footer(text=f"FinderBot Version {info.version}"))
        await confirm.add_reaction("✅")
        def check(_reaction, _author):
            return _author == ctx.message.author and str(_reaction.emoji) == '✅' and _reaction.message.id == confirm.id
        try:
            await ctx.bot.wait_for('reaction_add', timeout=10.0, check=check)
        except asyncio.TimeoutError:
            await confirm.edit(embed=discord.Embed(title="Timed Out", color=0xFF0000).add_field(name=f"{ctx.author.name}, You took too long to respond!", value="Try running the command again").set_footer(text=f"FinderBot Version {info.version}"))
        else:
            await ctx.guild.unban(user)
            await confirm.edit(embed=discord.Embed(title="User Unbanned", colour=0x3DF270).add_field(name="User", value=user, inline=False).set_footer(text=f"FinderBot Version {info.version}"))
            await self.bot.db.logs.update_one({"_id": ctx.guild.id}, {"$unset": {f"{user.id}.unbans.time": ""}, "$inc": {f"{user.id}.unbans.unbans": 1}})
    # =================================



    # ================================
    # ============= Kick =============
    # ================================
    @commands.command(name="kick", aliases=["k", "boot"])
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: commands.MemberConverter, *, reason="No Reason Provided"):
        if not await self.bot.db.settings.find_one({"_id": ctx.guild.id}):
            await self.bot.db.settings.insert_one({"_id": ctx.guild.id})
        if not await self.bot.db.logs.find_one({"_id": ctx.guild.id}):
                await self.bot.db.logs.insert_one({"_id": ctx.guild.id})
        if (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("disabled_mod_modules") and "kick" in (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("disabled_mod_modules"):
            await ctx.send(embed=discord.Embed(title="Kicking Disabled", colour=0x3DF270).add_field(name="You can kick the user manually or contact the server owner", value="You can enable the kick command by changing the settings", inline=False).set_footer(text=f"FinderBot Version {info.version}"))
            return
        confirm = await ctx.send(embed=discord.Embed(title="Are you sure you want to kick this user?", colour=0x3DF270).add_field(name="User", value=f"{user.mention} ({user})", inline=False).add_field(name="for reason", value=f"{reason}", inline=False).set_footer(text=f"FinderBot Version {info.version}"))
        await confirm.add_reaction("✅")
        def check(_reaction, _author):
            return _author == ctx.message.author and str(_reaction.emoji) == '✅' and _reaction.message.id == confirm.id
        try:
            await ctx.bot.wait_for('reaction_add', timeout=10.0, check=check)
        except asyncio.TimeoutError:
            await confirm.edit(embed=discord.Embed(title="Timed Out", color=0xFF0000).add_field(name=f"{ctx.author.name}, You took too long to respond!", value="Try running the command again").set_footer(text=f"FinderBot Version {info.version}"))
        else:
            await user.send(embed=discord.Embed(title="You have been kicked", colour=0x3DF270).add_field(name="Server", value=f"{ctx.guild.name}", inline=False).add_field(name="Reason", value=f"{reason}", inline=False).set_footer(text=f"FinderBot Version {info.version}").set_thumbnail(url=ctx.guild.icon_url))
            await ctx.guild.kick(user, reason=reason)
            await confirm.edit(embed=discord.Embed(title="User Kicked", colour=0x3DF270).add_field(name="User", value=f"{user.mention} ({user})", inline=False).add_field(name="for reason", value=f"{reason}", inline=False).set_footer(text=f"FinderBot Version {info.version}"))
            await self.bot.db.logs.update_one({"_id": ctx.guild.id}, {"$inc": {f"{user.id}.kicks": 1}})
    # ================================



    # ================================
    # ============= Warn =============
    # ================================
    @commands.command(name="warn", aliases=["w", "warning"])
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, user: commands.MemberConverter, *, reason="No Reason Provided"):
        if not await self.bot.db.settings.find_one({"_id": ctx.guild.id}):
            await self.bot.db.settings.insert_one({"_id": ctx.guild.id})
        if not await self.bot.db.logs.find_one({"_id": ctx.guild.id}):
            await self.bot.db.logs.insert_one({"_id": ctx.guild.id})
        if (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("disabled_mod_modules") and "warn" in (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("disabled_mod_modules"):
            await ctx.send(embed=discord.Embed(title="Warning Disabled", colour=0x3DF270, description="If you are a server administator you can enable the warn command in settings").set_footer(text=f"FinderBot Version {info.version}"))
            return
        await ctx.send(embed=discord.Embed(title="User Warned", colour=0x3DF270).add_field(name="User", value=f"{user.mention} ({user})", inline=False).add_field(name="for reason", value=f"{reason}", inline=False).set_footer(text=f"FinderBot Version {info.version}"))
        await user.send(embed=discord.Embed(title="You Have Been Warned", colour=0x3DF270).add_field(name="Server", value=f"{ctx.guild.name}", inline=False).add_field(name="Reason", value=f"{reason}", inline=False).set_footer(text=f"FinderBot Version {info.version}"))
        await self.bot.db.logs.update_one({"_id": ctx.guild.id}, {"$inc": {f"{user.id}.warns": 1}})
    # ================================

    # ================================
    # ============= Mute =============
    # ================================
    @commands.command(name="mute", aliases=["m"])
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def mute(self, ctx, user: commands.MemberConverter, *, reason="No Reason Specified"):
        if not await self.bot.db.settings.find_one({"_id": ctx.guild.id}):
            await self.bot.db.settings.insert_one({"_id": ctx.guild.id})
        if not await self.bot.db.logs.find_one({"_id": ctx.guild.id}):
            await self.bot.db.logs.insert_one({"_id": ctx.guild.id})
        if (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("disabled_mod_modules") and "mute" in (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("disabled_mod_modules"):
            await ctx.send(embed=discord.Embed(title="Muting Disabled", colour=0x3DF270, description="If you are a server administator you can enable the mute command in settings").set_footer(text=f"FinderBot Version {info.version}"))
            return
        if not (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("muted_role_id") or not discord.utils.get(ctx.guild.roles, id=(await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("muted_role_id")):
            role = await ctx.guild.create_role(name="Muted", colour=discord.colour.Colour.dark_grey(), permissions=discord.permissions.Permissions(send_messages=False, read_messages=True))
            for channel in ctx.guild.text_channels:
                await channel.set_permissions(role, send_messages=False)
            await self.bot.db.settings.update_one({"_id": ctx.guild.id}, {"$set": {"muted_role_id": role.id}})
        if discord.utils.get(ctx.guild.roles, id=(await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("muted_role_id")) in user.roles:
            await ctx.send(embed=discord.Embed(title="User Already Muted", colour=0x3DF270).set_footer(text=f"FinderBot Version {info.version}"))
            return
        await user.add_roles(discord.utils.get(ctx.guild.roles, id=(await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("muted_role_id")))
        if (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("muted_chat") and not (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("muted_chat_id") or (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("muted_chat") and (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("muted_chat_id") and not discord.utils.get(ctx.guild.text_channels, id=(await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("muted_chat_id")):
            await ctx.guild.create_text_channel('Muted Chat', overwrites={ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False), discord.utils.get(ctx.guild.roles, id=(await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("muted_role_id")): discord.PermissionOverwrite(read_messages=True)})
            await self.bot.db.settings.update_one({"_id": ctx.guild.id}, {"$set": {"muted_chat_id": channel.id}})
        await ctx.send(embed=discord.Embed(title="User Muted", colour=0x3DF270).add_field(name="User", value=f"{user.mention} ({user})", inline=False).add_field(name="for reason", value=f"{reason}", inline=False).set_footer(text=f"FinderBot Version {info.version}"))
        await user.send(embed=discord.Embed(title="You Have Been Muted", colour=0x3DF270).add_field(name="Server", value=f"{ctx.guild.name}", inline=False).add_field(name="Reason", value=f"{reason}", inline=False).set_footer(text=f"FinderBot Version {info.version}"))
        await self.bot.db.logs.update_one({"_id": ctx.guild.id}, {"$inc": {f"{user.id}.mutes": 1}})
    # ================================
    # ========= Mute Perms ===========
    # ================================
    @tasks.loop(seconds=5.0)
    async def mute_perms(self):
        for guild in self.bot.guilds:
            if not await self.bot.db.settings.find_one({"_id": guild.id}):
                await self.bot.db.settings.insert_one({"_id": guild.id})
            if (await self.bot.db.settings.find_one({"_id": guild.id})).get("disabled_mod_modules") and not "mute" in (await self.bot.db.settings.find_one({"_id": guild.id})).get("disabled_mod_modules"):
                return
            for channel in guild.text_channels:
                if discord.utils.get(guild.roles, id=(await self.bot.db.settings.find_one({"_id": guild.id})).get("muted_role_id")):
                    await channel.set_permissions(discord.utils.get(guild.roles, id=(await self.bot.db.settings.find_one({"_id": guild.id})).get("muted_role_id")), send_messages=False)
            if (await self.bot.db.settings.find_one({"_id": guild.id})).get("muted_chat"):
                if discord.utils.get(guild.roles, id=(await self.bot.db.settings.find_one({"_id": guild.id})).get("muted_role_id")) and discord.utils.get(guild.text_channels, id=(await self.bot.db.settings.find_one({"_id": guild.id})).get("muted_chat_id")):
                    await discord.utils.get(guild.text_channels, id=(await self.bot.db.settings.find_one({"_id": guild.id})).get("muted_chat_id")).set_permissions(discord.utils.get(guild.roles, id=(await self.bot.db.settings.find_one({"_id": guild.id})).get("muted_role_id")), send_messages=False)
    @mute_perms.before_loop
    async def before_mute_perms(self):
        await self.bot.wait_until_ready()
    # ================================



    # =====================================
    # ============= Temp mute =============
    # =====================================
    @commands.command(name="tempmute", aliases=["tm", "tempm", "tmute", "temporarymute"])
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def tempmute(self, ctx, user: commands.MemberConverter, time, *, reason="No Reason Specified"):
        if not await self.bot.db.settings.find_one({"_id": ctx.guild.id}):
            await self.bot.db.settings.insert_one({"_id": ctx.guild.id})
        if not await self.bot.db.logs.find_one({"_id": ctx.guild.id}):
            await self.bot.db.logs.insert_one({"_id": ctx.guild.id})
        if (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("disabled_mod_modules") and "mute" in (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("disabled_mod_modules"):
            await ctx.send(embed=discord.Embed(title="Muting Disabled", colour=0x3DF270, description="If you are a server administator you can enable the mute command in settings").set_footer(text=f"FinderBot Version {info.version}"))
            return
        if not (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("muted_role_id") or not discord.utils.get(ctx.guild.roles, id=(await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("muted_role_id")):
            role = await ctx.guild.create_role(name="Muted", colour=discord.colour.Colour.dark_grey(), permissions=discord.permissions.Permissions(send_messages=False, read_messages=True))
            for channel in ctx.guild.text_channels:
                await channel.set_permissions(role, send_messages=False)
            await self.bot.db.settings.update_one({"_id": ctx.guild.id}, {"$set": {"muted_role_id": role.id}})
        if discord.utils.get(ctx.guild.roles, id=(await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("muted_role_id")) in user.roles:
            await ctx.send(embed=discord.Embed(title="User Already Muted", colour=0x3DF270).set_footer(text=f"FinderBot Version {info.version}"))
            return
        await user.add_roles(discord.utils.get(ctx.guild.roles, id=(await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("muted_role_id")))
        if (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("muted_chat") and not (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("muted_chat_id") or (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("muted_chat") and (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("muted_chat_id") and not discord.utils.get(ctx.guild.text_channels, id=(await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("muted_chat_id")):
            await ctx.guild.create_text_channel('Muted Chat', overwrites={ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False), discord.utils.get(ctx.guild.roles, id=(await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("muted_role_id")): discord.PermissionOverwrite(read_messages=True)})
            await self.bot.db.settings.update_one({"_id": ctx.guild.id}, {"$set": {"muted_chat_id": channel.id}})
        await ctx.send(embed=discord.Embed(title="User Muted", colour=0x3DF270).add_field(name="User", value=f"{user.mention} ({user})", inline=False).add_field(name="for time", value=f"{humanize_delta(await DurationDelta.convert(self, time))}", inline=False).add_field(name="for reason", value=f"{reason}", inline=False).set_footer(text=f"FinderBot Version {info.version}"))
        await user.send(embed=discord.Embed(title="You Have Been Muted", colour=0x3DF270).add_field(name="Server", value=f"{ctx.guild.name}", inline=False).add_field(name="Time", value=f"{humanize_delta(await DurationDelta.convert(self, time))}", inline=False).add_field(name="Reason", value=f"{reason}", inline=False).set_footer(text=f"FinderBot Version {info.version}"))
        await self.bot.db.logs.update_one({"_id": ctx.guild.id, "users.id": user.id}, {"$inc": {f"{user.id}.mutes": 1}, "$set": {f"{user.id}.unmutes.time": datetime.datetime.now() + await DurationDelta.convert(self, time)}})
    # ================================
    # ========= Mute Check ===========
    # ================================
    @tasks.loop(seconds=5.0)
    async def check_unmute(self):
        for guild in self.bot.guilds:
            if not await self.bot.db.settings.find_one({"_id": guild.id}):
                await self.bot.db.settings.insert_one({"_id": guild.id})
            if (await self.bot.db.settings.find_one({"_id": guild.id})).get("disabled_mod_modules") and not "mute" in (await self.bot.db.settings.find_one({"_id": guild.id})).get("disabled_mod_modules"):
                return
            if await self.bot.db.logs.find_one({"_id": guild.id}):
                for user in await self.bot.db.logs.find_one({"_id": guild.id}):
                    if not user == "_id" and (await self.bot.db.logs.find_one({"_id": guild.id}))[user].get("unmutes") and (await self.bot.db.logs.find_one({"_id": guild.id}))[user].get("unmutes").get("time") and (await self.bot.db.logs.find_one({"_id": guild.id}))[user].get("unmutes").get("time") < datetime.datetime.now():
                        await (guild.get_member(int(user)).remove_roles(discord.utils.get(guild.roles, id=(await self.bot.db.settings.find_one({"_id": guild.id})).get("muted_role_id"))))
                        await self.bot.db.logs.update_one({"_id": guild.id}, {"$unset": {f"{user.id}.unmutes.time": ""}, "$inc": {f"{user.id}.unmutes.unmutes": 1}})
    @check_unmute.before_loop
    async def before_unmute(self):
        await self.bot.wait_until_ready()
    # ================================



    # =================================
    # ============= Unmute =============
    # =================================
    @commands.command(name="unmute", aliases=["unm", "um"])
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def unmute(self, ctx, user: commands.MemberConverter):
        if not await self.bot.db.settings.find_one({"_id": ctx.guild.id}):
            await self.bot.db.settings.insert_one({"_id": ctx.guild.id})
        if not await self.bot.db.logs.find_one({"_id": ctx.guild.id}):
            await self.bot.db.logs.insert_one({"_id": ctx.guild.id})
        if (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("disabled_mod_modules") and "mute" in (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("disabled_mod_modules"):
            await ctx.send(embed=discord.Embed(title="Muting Disabled", colour=0x3DF270, description="If you are a server administator you can enable the mute command in settings").set_footer(text=f"FinderBot Version {info.version}"))
            return
        if (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("muted_role_id") and discord.utils.get(ctx.guild.roles, id=(await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("muted_role_id")) in user.roles:
            await user.remove_roles(discord.utils.get(ctx.guild.roles, id=(await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("muted_role_id")))
            await ctx.send(embed=discord.Embed(title="User Unmuted", colour=0x3DF270).add_field(name="User", value=f"{user.mention} ({user})", inline=False).set_footer(text=f"FinderBot Version {info.version}"))
            await self.bot.db.logs.update_one({"_id": ctx.guild.id}, {"$unset": {f"{user.id}.unmutes.time": ""}, "$inc": {f"{user.id}.unmutes.unmutes": 1}})
        else:
            await ctx.send(embed=discord.Embed(title="User Not Muted", colour=0x3DF270, description=f"{user.name} was unmuted by a moderator or was not muted").add_field(name="User", value=f"{user.mention} ({user})", inline=False).set_footer(text=f"FinderBot Version {info.version}"))
    # =================================

def setup(bot):
    bot.add_cog(Moderation(bot))