import discord, info, random, asyncio
from discord.ext import commands

# =======================================================
# ============= Check if addon is installed =============
# =======================================================
def is_addon__server(addon):
    async def predicate(ctx):
        if not await ctx.bot.db.addons.find_one({"_id": ctx.guild.id}):
            await ctx.bot.db.addons.insert_one({"_id": ctx.guild.id, "addons": []})
        if addon in (await ctx.bot.db.addons.find_one({"_id": ctx.guild.id})).get("addons"):
            return True
        return False
    return commands.check(predicate)

class TicTacToe(commands.Cog):
    author = "FinderTeam"
    info = "Part of the games addon parent. Lets you play Tic-Tac-Toe in your server"
    thumbnail = 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Tic_tac_toe.svg/1200px-Tic_tac_toe.svg.png'
    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @is_addon__server("tictactoe")
    @commands.command(name="tictactoe", aliases=["ttt"], hidden=True)
    async def tictactoe(self, ctx, player: discord.Member=None):
        if player is None:
            await ctx.send(discord.Embed(title="TicTacToe").add_field(name="No player present!", value=f"Please specify a player to play against", inline=False).set_footer(text=f"FinderBot {info.version}"))
            return
        if player.bot:
            await ctx.send(discord.Embed(title="TicTacToe").add_field(name="This game does not support playing with bots!", value=f"Please specify a player to play against", inline=False).set_footer(text=f"FinderBot {info.version}"))
            return
        # admin_role = discord.utils.get(ctx.guild.roles, permissions=discord.permissions.Permissions.manage_channels)
        overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False), ctx.guild.me: discord.PermissionOverwrite(read_messages=True), player: discord.PermissionOverwrite(read_messages=True), ctx.message.author: discord.PermissionOverwrite(read_messages=True)}#admin_role: discord.PermissionOverwrite(read_messages=True)
        channel = await ctx.guild.create_text_channel("tictactoe", overwrites=overwrites)
        await channel.send(f"{ctx.message.author.mention} {player.mention}")
        g1, g2, g3, g4, g5, g6, g7, g8, g9 = "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"
        won, draw, p1OorX = 0, 0, random.choice([u"\u274C", u"\u2B55"])
        grid = f"\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B{g1}\u2B1B\u2B1B\u2B1B{g2}\u2B1B\u2B1B\u2B1B{g3}\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B{g4}\u2B1B\u2B1B\u2B1B{g5}\u2B1B\u2B1B\u2B1B{g6}\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B{g7}\u2B1B\u2B1B\u2B1B{g8}\u2B1B\u2B1B\u2B1B{g9}\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n"
        p2OorX = u"\u2B55" if p1OorX == u"\u274C" else "\u274C"
        reactionTTT, reactList = await channel.send(embed=discord.Embed(title="Tic Tac Toe").add_field(name="The Playing Board", value="Please Wait...").set_footer(text=f"FinderBot {info.version}")), ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
        for i in reactList:
            await reactionTTT.add_reaction(i)
        while won == 0:
            await reactionTTT.edit(embed=discord.Embed(title="Tic Tac Toe", color=0xff0000).add_field(name="The Playing Board", value=grid, inline=True).set_footer(text=f"FinderBot {info.version}"))
            def check_react(_reaction, _user):
                return _reaction.message.id == reactionTTT.id and _user == ctx.message.author and str(_reaction.emoji) in reactList
            try:
                res, user = await self.bot.wait_for('reaction_add', check=check_react, timeout=20.0)
            except asyncio.TimeoutError:
                if draw != 1:
                    await reactionTTT.edit(embed=discord.Embed(title="Your Opponent is AFK!", color=0xff0000).add_field(name=f"{player} Won!", value="Try getting more active friends", inline=True).set_footer(text=f"FinderBot {info.version}"))
                    await channel.send("Closing channel in 10 seconds...")
                    await asyncio.sleep(10)
                    await channel.send("Deleting Channel...")
                    await channel.delete()
            else:
                if '1️⃣' in str(res.emoji):
                    await reactionTTT.clear_reaction("1️⃣")
                    reactList.remove("1️⃣")
                    g1 = p1OorX
                elif '2️⃣' in str(res.emoji):
                    await reactionTTT.clear_reaction("2️⃣")
                    reactList.remove("2️⃣")
                    g2 = p1OorX
                elif '3️⃣' in str(res.emoji):
                    await reactionTTT.clear_reaction("3️⃣")
                    reactList.remove("3️⃣")
                    g3 = p1OorX
                elif '4️⃣' in str(res.emoji):
                    await reactionTTT.clear_reaction("4️⃣")
                    reactList.remove("4️⃣")
                    g4 = p1OorX
                elif '5️⃣' in str(res.emoji):
                    await reactionTTT.clear_reaction("5️⃣")
                    reactList.remove("5️⃣")
                    g5 = p1OorX
                elif '6️⃣' in str(res.emoji):
                    await reactionTTT.clear_reaction("6️⃣")
                    reactList.remove("6️⃣")
                    g6 = p1OorX
                elif '7️⃣' in str(res.emoji):
                    await reactionTTT.clear_reaction("7️⃣")
                    reactList.remove("7️⃣")
                    g7 = p1OorX
                elif '8️⃣' in str(res.emoji):
                    await reactionTTT.clear_reaction("8️⃣")
                    reactList.remove("8️⃣")
                    g8 = p1OorX
                elif '9️⃣' in str(res.emoji):
                    await reactionTTT.clear_reaction("9️⃣")
                    reactList.remove("9️⃣")
                    g9 = p1OorX
                grid = f"\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B{g1}\u2B1B\u2B1B\u2B1B{g2}\u2B1B\u2B1B\u2B1B{g3}\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B{g4}\u2B1B\u2B1B\u2B1B{g5}\u2B1B\u2B1B\u2B1B{g6}\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B{g7}\u2B1B\u2B1B\u2B1B{g8}\u2B1B\u2B1B\u2B1B{g9}\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n"
                await reactionTTT.edit(embed=discord.Embed(title="Tic Tac Toe").add_field(name="The Playing Board", value=grid).set_footer(text=f"FinderBot {info.version}"))
                if g1 == g2 == g3 == p1OorX or g4 == g5 == g6 == p1OorX or g7 == g8 == g9 == p1OorX or g1 == g4 == g7 == p1OorX or g2 == g5 == g8 == p1OorX or g3 == g6 == g9 == p1OorX or g1 == g5 == g9 == p1OorX or g3 == g5 == g7 == p1OorX:
                    await channel.send(f"{ctx.message.author.mention} has Won!")
                    won, winner, loser = 1, ctx.message.author, player
                elif len(reactList) == 0:
                    draw = 1
                    await reactionTTT.edit(embed=discord.Embed(title="No more moves!", color=0xff0000).add_field(name="Draw!", value="⠀", inline=True).set_footer(text=f"FinderBot {info.version}"))
                    await channel.send("Closing channel in 10 seconds...")
                    await asyncio.sleep(10)
                    await channel.send("Deleting Channel...")
                    await channel.delete()
            if won == 0:
                def check_react2(_reaction, _user):
                    return _reaction.message.id == reactionTTT.id and _user == player and str(_reaction.emoji) in reactList
                try:
                    res, user = await self.bot.wait_for('reaction_add', check=check_react2, timeout=20.0)
                except asyncio.TimeoutError:
                    if draw != 1:
                        await reactionTTT.edit(embed=discord.Embed(title="Your Opponent is AFK!", color=0xff0000).add_field(name=f"{ctx.message.author} Won!", value="Try getting more active friends", inline=True).set_footer(text=f"FinderBot {info.version}"))
                        await channel.send("Closing channel in 10 seconds...")
                        await asyncio.sleep(10)
                        await channel.send("Deleting Channel...")
                        await channel.delete()
                else:
                    if '1️⃣' in str(res.emoji):
                        await reactionTTT.clear_reaction("1️⃣")
                        reactList.remove("1️⃣")
                        g1 = p2OorX
                    elif '2️⃣' in str(res.emoji):
                        await reactionTTT.clear_reaction("2️⃣")
                        reactList.remove("2️⃣")
                        g2 = p2OorX
                    elif '3️⃣' in str(res.emoji):
                        await reactionTTT.clear_reaction("3️⃣")
                        reactList.remove("3️⃣")
                        g3 = p2OorX
                    elif '4️⃣' in str(res.emoji):
                        await reactionTTT.clear_reaction("4️⃣")
                        reactList.remove("4️⃣")
                        g4 = p2OorX
                    elif '5️⃣' in str(res.emoji):
                        await reactionTTT.clear_reaction("5️⃣")
                        reactList.remove("5️⃣")
                        g5 = p2OorX
                    elif '6️⃣' in str(res.emoji):
                        await reactionTTT.clear_reaction("6️⃣")
                        reactList.remove("6️⃣")
                        g6 = p2OorX
                    elif '7️⃣' in str(res.emoji):
                        await reactionTTT.clear_reaction("7️⃣")
                        reactList.remove("7️⃣")
                        g7 = p2OorX
                    elif '8️⃣' in str(res.emoji):
                        await reactionTTT.clear_reaction("8️⃣")
                        reactList.remove("8️⃣")
                        g8 = p2OorX
                    elif '9️⃣' in str(res.emoji):
                        await reactionTTT.clear_reaction("9️⃣")
                        reactList.remove("9️⃣")
                        g9 = p2OorX
                    grid = f"\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B{g1}\u2B1B\u2B1B\u2B1B{g2}\u2B1B\u2B1B\u2B1B{g3}\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B{g4}\u2B1B\u2B1B\u2B1B{g5}\u2B1B\u2B1B\u2B1B{g6}\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B{g7}\u2B1B\u2B1B\u2B1B{g8}\u2B1B\u2B1B\u2B1B{g9}\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\u2B1B\n"
                    await reactionTTT.edit(embed=discord.Embed(title="Tic Tac Toe").add_field(name="The Playing Board", value=grid).set_footer(text=f"FinderBot {info.version}"))
                    if g1 == g2 == g3 == p2OorX or g4 == g5 == g6 == p2OorX or g7 == g8 == g9 == p2OorX or g1 == g4 == g7 == p2OorX or g2 == g5 == g8 == p2OorX or g3 == g6 == g9 == p2OorX or g1 == g5 == g9 == p2OorX or g3 == g5 == g7 == p2OorX:
                        await channel.send(f"{player.mention} has Won!")
                        won, winner, loser = 1, player, ctx.message.author
                    elif len(reactList) == 0:
                        draw = 1
                        await reactionTTT.edit(embed=discord.Embed(title="No more moves!", color=0xff0000).add_field(name="Draw!", value="⠀", inline=True).set_footer(text=f"FinderBot {info.version}"))
                        await channel.send("Closing channel in 10 seconds...")
                        await asyncio.sleep(10)
                        await channel.send("Deleting Channel...")
                        await channel.delete()
        else:
            await channel.send(f"Well done, {winner.mention}! Better luck next time, {loser.mention}!\nClosing channel in 10 seconds...")
            await asyncio.sleep(10)
            await channel.send("Deleting Channel...")
            await channel.delete()

    @tictactoe.error
    async def tictactoe_handler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(embed=discord.Embed(title="This command is a addon!", color=0xff0000).add_field(name="This command is for the addon", value="tictactoe", inline=False).add_field(name="To add it this addon use", value=f"{ctx.prefix}addon install tictactoe", inline=False).set_footer(text=f"FinderBot {info.version}"))

class RockPaperScissors(commands.Cog):
    author = "FinderTeam"
    info = "Part of the games addon parent. Lets you play Rock Paper Scissors in your server"
    thumbnail = 'https://aguirre.github.io/RPS-Multiplayer/assets/images/rps.png'
    def __init__(self, bot):
        self.bot = bot


    @is_addon__server("rockpaperscissors")
    @commands.guild_only()
    @commands.command(name="rockpaperscissors", aliases=["rps"], hidden=True)
    async def rockpaperscissors(self, ctx, user: discord.Member=None):
        if user is None:
            await ctx.send(embed=discord.Embed(title="Rock Paper Scissors").add_field(name="No player present!", value=f"Please specify a player to play against", inline=False).set_footer(text=f"FinderBot {info.version}"))
            return
        won = 0
        channel1 = await ctx.guild.create_text_channel("Rock Paper Scissors-p1", overwrites={ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False), ctx.guild.me: discord.PermissionOverwrite(read_messages=True), ctx.message.author: discord.PermissionOverwrite(read_messages=True)})
        await channel1.send(f"{ctx.author.mention}! you have challenged {user.mention}")
        p1msg = await channel1.send(embed=discord.Embed(title="Rock Paper Scissors").add_field(name=f"Loading...", value="Please wait...").set_footer(text=f"FinderBot {info.version}"))
        await p1msg.add_reaction("🪨")
        await p1msg.add_reaction("📄")
        await p1msg.add_reaction("✂")
        if not user.bot:
            channel2 = await ctx.guild.create_text_channel("Rock Paper Scissors-p2", overwrites={ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False), ctx.guild.me: discord.PermissionOverwrite(read_messages=True), user: discord.PermissionOverwrite(read_messages=True)})
            await channel2.send(f"{user.mention}! {ctx.author.mention} challenged you")
            p2msg = await channel2.send(embed=discord.Embed(title="Rock Paper Scissors").add_field(name=f"Loading...", value="Please wait...").set_footer(text=f"FinderBot {info.version}"))
            await p2msg.add_reaction("🪨")
            await p2msg.add_reaction("📄")
            await p2msg.add_reaction("✂")
            await p1msg.edit(embed=discord.Embed(title="Rock Paper Scissors").add_field(name=f"{ctx.author.name} Would you like to pick Rock, Paper or Scissors?", value="Select from the reactions below").set_footer(text=f"FinderBot {info.version}"))
            if not user.bot:
                await p2msg.edit(embed=discord.Embed(title="Rock Paper Scissors").add_field(name=f"{user.name} Would you like to pick Rock, Paper or Scissors?", value="Select from the reactions below").set_footer(text=f"FinderBot {info.version}"))
        while won == 0:
            reactList = ["🪨", "📄", "✂"]
            async def react_handler(player: discord.User, opponent: discord.User, message: discord.Message=None):
                if player.bot:
                    return random.choice(reactList)
                try:
                    reaction, _ = await self.bot.wait_for('reaction_add', check=lambda r, u: r.emoji in reactList and r.message.id == message.id and u == player, timeout=60)
                except asyncio.TimeoutError:
                    return None
                return reaction.emoji
            author_helper = react_handler(ctx.author, user, p1msg)
            if not user.bot:
                opponent_helper = react_handler(user, ctx.author, p2msg)
            else:
                opponent_helper = react_handler(user, ctx.author)
            author_emoji, opponent_emoji = await asyncio.gather(author_helper, opponent_helper)
            if author_emoji != opponent_emoji:
                won = 1
            else:
                await p1msg.edit(embed=discord.Embed(title="Rock Paper Scissors").add_field(name=f"You Drew", value=f"You chose {author_emoji} and {user.name} chose {opponent_emoji}\nTry Again.").set_footer(text=f"FinderBot {info.version}"))
                await p1msg.clear_reaction(author_emoji)
                await p1msg.add_reaction(author_emoji)
                if not user.bot:
                    await p2msg.edit(embed=discord.Embed(title="Rock Paper Scissors").add_field(name=f"You Drew", value=f"You chose {opponent_emoji} and {ctx.author.name} chose {author_emoji}\nTry Again.").set_footer(text=f"FinderBot {info.version}"))
                    await p2msg.clear_reaction(opponent_emoji)
                    await p2msg.add_reaction(opponent_emoji)
        if author_emoji == "📄" and opponent_emoji == '✂'  or author_emoji == "✂" and opponent_emoji == "🪨" or author_emoji == "🪨" and opponent_emoji == "📄": 
            winner = user
            loser = ctx.author
        elif author_emoji == '📄' and opponent_emoji == "🪨" or author_emoji == "✂" and opponent_emoji == "📄" or author_emoji == "🪨" and opponent_emoji == "✂": 
            winner = ctx.author
            loser = user
        await p1msg.edit(embed=discord.Embed(title="Rock Paper Scissors").add_field(name=f"{winner} Won", value=f"You chose {author_emoji} and {user.name} chose {opponent_emoji}").set_footer(text=f"FinderBot {info.version}"))
        if not user.bot:
            await p2msg.edit(embed=discord.Embed(title="Rock Paper Scissors").add_field(name=f"{winner} Won", value=f"You chose {opponent_emoji} and {ctx.author.name} chose {author_emoji}").set_footer(text=f"FinderBot {info.version}"))
        await channel1.send("Closing channel in 10 seconds...")
        if not user.bot:
            await channel2.send("Closing channel in 10 seconds...")
        await asyncio.sleep(10)
        await channel1.send("Deleting Channel...")
        await channel1.delete()
        if not user.bot:
            await channel2.send("Deleting Channel...")
            await channel2.delete()

    @rockpaperscissors.error
    async def rps_handler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(embed=discord.Embed(title="This command is a addon!", color=0xff0000).add_field(name="This command is for the addon", value="rockpaperscissors", inline=False).add_field(name="To add it this addon use", value=f"{ctx.prefix}addon install rockpaperscissors", inline=False).set_footer(text=f"FinderBot {info.version}"))


def setup(bot):
    bot.add_cog(TicTacToe(bot))
    bot.add_cog(RockPaperScissors(bot))