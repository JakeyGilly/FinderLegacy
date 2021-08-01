from discord.ext import commands
import discord, info, asyncio

class Admin(commands.Cog):
    """Admin commands that help manage the server."""
    def __init__(self, bot):
        self.bot = bot


    # =========================================
    # ============= Change Prefix =============
    # =========================================
    @commands.command(name='prefix', aliases=['prefixes', "changeprefix"], help="Change the prefix of the bot.")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def changeprefix(self, ctx, symbol):
        await self.bot.db.settings.update_one({"_id": ctx.guild.id}, {"$set": {"prefix": symbol}}, upsert=True)
        await ctx.send(embed=discord.Embed(title="Prefix Changed", color=0x00FF00).add_field(name=f"{ctx.guild.name}'s prefix changed to **{symbol}**", value="This will be used to prefix all commands.").set_footer(text=f"FinderBot Version {info.version}"))
    # =========================================



    # ===========================================
    # ============= Delete Messages =============
    # ===========================================
    @commands.command(name='purge', aliases=['delete', 'clear', 'deletemessage', 'deletemessages'], help="Delete messages from the channel.")
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def clear(self, ctx, messagenum: int, user: commands.MemberConverter=None):
        def is_user(m):
            return m.author == user
        if messagenum > 1000:
            messagenum = 1000
        confirm = await ctx.send(embed=discord.Embed(title="Message Deletion").add_field(name=f"Are you sure you want to delete {messagenum} message{'s'[:messagenum^1]}?", value="React with :white_check_mark: to confirm, :negative_squared_cross_mark: to cancel.").set_footer(text=f"FinderBot Version {info.version}"))
        await confirm.add_reaction("\N{WHITE HEAVY CHECK MARK}")
        await confirm.add_reaction("\N{NEGATIVE SQUARED CROSS MARK}")
        def check(r, u):
            return u == ctx.author and str(r.emoji) in ["\N{WHITE HEAVY CHECK MARK}", "\N{NEGATIVE SQUARED CROSS MARK}"]
        try:
            reaction, u = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send(embed=discord.Embed(title="Timed Out", color=0xFF0000).add_field(name=f"{ctx.author.name}, You took too long to respond!", value="Try running the command again").set_footer(text=f"FinderBot Version {info.version}"))
            return
        if str(reaction.emoji) == "\N{NEGATIVE SQUARED CROSS MARK}":
            confirm.delete()
            return
        if str(reaction.emoji) == "\N{WHITE HEAVY CHECK MARK}":
            await ctx.channel.purge(limit=messagenum, check=is_user) if user else await ctx.message.channel.purge(limit=int(messagenum+2))
    # ===========================================



    # ====================================
    # ============= Slowmode =============
    # ====================================
    @commands.command(name='slowmode', aliases=['slow', 'delay'], help="Change the slowmode speed of the channel.")
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds:int=None):
        if seconds == None or not isinstance(seconds, int) or seconds < 0:
            seconds = 5
        await ctx.channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            await ctx.send(embed=discord.Embed(title="Slowmode Disabled", color=0x00FF00).add_field(name=f"{ctx.guild.name}'s slowmode disabled", value=f"Slowmode is now disabled by {ctx.author}.").set_footer(text=f"FinderBot Version {info.version}"))
        elif seconds > 0:
            await ctx.send(embed=discord.Embed(title="Slowmode Enabled", color=0x00FF00).add_field(name=f"{ctx.guild.name}'s slowmode enabled", value=f"Slowmode is now enabled for {seconds} second{'s'[:seconds^1]} by {ctx.author}.").set_footer(text=f"FinderBot Version {info.version}"))
    # ====================================



    # =======================================
    # ============= Voting/Poll =============
    # =======================================
    @commands.command(name='poll', aliases=['vote', 'polls', 'polling', 'voting'], help="Create a poll that users can vote on.")
    @commands.guild_only()
    async def vote(self, ctx, question: str, options: str):
        emojis=["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟", "🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬"]
        options = options.split("|")
        if len(options) < 2:
            await ctx.send(embed=discord.Embed(title="Invalid Number of Options", color=0xFF0000).add_field(name=f"{ctx.author.name}", value="Please provide at least 2 options to create a poll seperated by '|'.").set_footer(text=f"FinderBot Version {info.version}"))
            return
        if len(options) > 17:
            await ctx.send(embed=discord.Embed(title="Too Many Options", color=0xFF0000).add_field(name=f"{ctx.author.name}", value="Please provide less than 17 options to create a poll seperated by '|'.").set_footer(text=f"FinderBot Version {info.version}"))
            return
        embed=discord.Embed(title=f"{ctx.author.name}'s poll", color=0x00FF00).add_field(name=f"{question}", value="\n".join(options)).set_footer(text=f"FinderBot Version {info.version}")
        poll = await ctx.send(embed=embed)
        for option in options:
            await poll.add_reaction(emojis[option])
    # =======================================


    # # TODO
    # # ======================================================
    # # ============= Locking/Unlocking channels =============
    # # ======================================================
    # @commands.command()
    # @commands.guild_only()
    # @commands.has_permissions(manage_channels=True)
    # async def lock(self, ctx):
    #     overwrite = ctx.channel.overwrites_for([role for role in ctx.guild.roles if not role.permissions.administrator])
    #     overwrite.send_messages = None
    #     await ctx.channel.set_permissions([role for role in ctx.guild.roles if not role.permissions.administrator], overwrite=overwrite)
    #     await ctx.send(embed=discord.Embed(title="Channel Locked", color=0x00FF00).add_field(name="Sending messages has been disabled", value=f"Channel locked by {ctx.author}").set_footer(text=f"FinderBot Version {info.version}"))
    # @commands.command()
    # @commands.guild_only()
    # @commands.has_permissions(manage_channels=True)
    # async def unlock(self, ctx):
    #     overwrite = ctx.channel.overwrites_for([role for role in ctx.guild.roles if not role.permissions.administrator])
    #     overwrite.send_messages = None
    #     await ctx.channel.set_permissions([role for role in ctx.guild.roles if not role.permissions.administrator], overwrite=overwrite)
    #     await ctx.send(embed=discord.Embed(title="Channel Unlocked", color=0x00FF00).add_field(name="Sending messages has been enabled", value=f"Channel unlocked by {ctx.author}").set_footer(text=f"FinderBot Version {info.version}"))
    # # ======================================================

def setup(bot):
    bot.add_cog(Admin(bot))
