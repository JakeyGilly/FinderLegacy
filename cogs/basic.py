import discord, info, random, re, datetime
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

class Basic(commands.Cog):
    """Some basic commands."""
    def __init__(self, bot):
        self.bot = bot
        self.giveaway_check.start()

    #! Add Calculator command
    # # ================================
    # # ============= Help =============
    # # ================================
    # @commands.command(name="help", aliases=["h"])
    # async def help(self, ctx):
    #     await ctx.send(embed=discord.Embed(title="FinderBot Help").add_field(name="To get help with FinderBot Bot go to", value=f"https://github.com/FinderDiscord/FinderDocs").set_footer(text=f"FinderBot {info.version}"))
    # # ================================
    
    
    # ================================
    # ============= Help =============
    # ================================
    @commands.command(name='help', aliases=['h'], help='Sends this help message')
    async def help(self, ctx, input=None):
        if not input:
            emb = discord.Embed(title='FinderBot Help', description=f'Commands and Modules\nUse `{ctx.prefix}help <module>` to gain more information about that module').set_footer(text=f"FinderBot {info.version}")
            cogs_desc = ''
            for cog in self.bot.cogs:
                i = 0
                for command in self.bot.get_cog(cog).get_commands():
                    if not command.hidden:
                        i += 1
                if i > 0:
                    cogs_desc += f'`{cog}` {self.bot.cogs[cog].__doc__}\n'
            emb.add_field(name='Modules', value=cogs_desc, inline=False)
            commands_desc = ''
            for command in self.bot.walk_commands():
                if not command.cog_name and not command.hidden:
                    commands_desc += f'{command.name} - {command.help}\n'
            if commands_desc:
                emb.add_field(name='Not belonging to a module', value=commands_desc, inline=False)
        else:
            for cog in self.bot.cogs:
                if cog.lower() == input.lower():
                    emb = discord.Embed(title=f'FinderBot Help', description=f"{cog} - Commands\n**{self.bot.cogs[cog].__doc__}**")
                    h = 0
                    for command in self.bot.get_cog(cog).get_commands():
                        commandss = ""
                        aliases = ""
                        if not command.hidden:
                            h += 1
                            if isinstance(command, commands.Group):
                                for j in command.walk_commands():
                                    commandss += f"{ctx.prefix}{j}\n"
                            for i in command.aliases:
                                aliases += f"{i}, "
                            aliases = aliases[:-2]
                        if h != 0:
                            if not commandss:        
                                emb.add_field(name=f"`{ctx.prefix}{command.name}` Aliases: {aliases}", value=f"{command.help}", inline=False)
                            else:
                                emb.add_field(name=f"`{ctx.prefix}{command.name}` Aliases: {aliases}", value=f"{command.help}\n\nSubcommands\n`{commandss}`", inline=False)
                        else:
                            emb = discord.Embed(title=f'{input} - Commands', description=f'No such module exists', color=discord.Color.red())
                    break
            else:
                emb = discord.Embed(title=f'{input} - Commands', description=f'No such module exists', color=discord.Color.red())
        await ctx.send(embed=emb)

    # ==========================================
    # ============= Reaction Roles =============
    # ==========================================
    @commands.command(name="reactionroles", aliases=["rr, reactrole", "reactroles", "reactionrole"], help="Create a reaction role so users can add roles.")
    @commands.guild_only()
    async def reactrole(self, ctx, role: discord.Role, emoji):
        if ctx.guild.me.top_role > role:
            if not await self.bot.db.reactrole.find_one({'role_id': role.id}):
                message = await ctx.send(embed=discord.Embed(title="Reaction Role", description=f"React to this message with {emoji} to get the `{role.name}` role").set_footer(text=f"FinderBot {info.version}"))
                await self.bot.db.reactrole.insert_one({'_id': message.id, 'emoji': emoji, "role_id": role.id})
                await message.add_reaction(emoji)
            else:
                await ctx.send(embed=discord.Embed(title="Reaction Role failed", color=0xff0000).add_field(name="Role already setup", value=f"{role.name} already has a reaction role setup.").set_footer(text=f"FinderBot {info.version}"))
        else:
            await ctx.send(embed=discord.Embed(title="Reaction Role failed", color=0xff0000).add_field(name="Role too high", value=f"You can't give a role that is higher than my top role.").set_footer(text=f"FinderBot {info.version}"))
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if not payload.user_id == self.bot.user.id and (await self.bot.db.reactrole.find_one({'_id': payload.message_id})) and payload.emoji.name == (await self.bot.db.reactrole.find_one({'_id': payload.message_id}))['emoji'] and discord.utils.get(self.bot.get_guild(payload.guild_id).roles, id=(await self.bot.db.reactrole.find_one({'_id': payload.message_id}))['role_id']):
            await self.bot.get_guild(payload.guild_id).get_member(payload.user_id).add_roles(discord.utils.get(self.bot.get_guild(payload.guild_id).roles, id=(await self.bot.db.reactrole.find_one({'_id': payload.message_id}))['role_id']))
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if not payload.user_id == self.bot.user.id and (await self.bot.db.reactrole.find_one({'_id': payload.message_id})) and payload.emoji.name == (await self.bot.db.reactrole.find_one({'_id': payload.message_id}))['emoji'] and discord.utils.get(self.bot.get_guild(payload.guild_id).roles, id=(await self.bot.db.reactrole.find_one({'_id': payload.message_id}))['role_id']):
            await self.bot.get_guild(payload.guild_id).get_member(payload.user_id).remove_roles(discord.utils.get(self.bot.get_guild(payload.guild_id).roles, id=(await self.bot.db.reactrole.find_one({'_id': payload.message_id}))['role_id']))
    # ==========================================

   
    # =================================
    # ============= About =============
    # =================================
    @commands.command(name="about", aliases=["info", "information", "i"], help="Get information about FinderBot.")
    async def about(self, ctx):
        await ctx.send(embed=discord.Embed(title="FinderBot", color=0x1D93FF).set_author(name="About FinderBot").set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/c/c9/FinderBot_Icon_macOS_Big_Sur.png").add_field(name="The Macintosh Desktop Experience", value="Created by FinderTeam").set_footer(text=f"FinderBot {info.version}\n{info.web}"))
    # =================================



    # ====================================
    # ============= Giveaway =============
    # ====================================
    @commands.command(name="giveaway", help="Create a giveaway that users can enter into.")
    async def giveaway(self, ctx, time, winners: int, prize):
        if datetime.datetime.now() + await DurationDelta.convert(self, time) > datetime.datetime.now()+relativedelta(days=90):
            await ctx.send(embed=discord.Embed(title="Giveaway", color=0xff0000).add_field(name="Too long", value="The giveaway has to be shorter than 90 days.").set_footer(text=f"FinderBot {info.version}"))
            return
        message = await ctx.send(embed=discord.Embed(title="Giveaway", color=0x1D93FF).add_field(name=f"{winners} winners with a prize of {prize}\nEnding in {humanize_delta(await DurationDelta.convert(self, time))}", value=f"To enter the giveaway, react to this message with 🎁").set_footer(text=f"FinderBot {info.version}"))
        await self.bot.db.giveaways.insert_one({'_id': message.id, 'guild_id': ctx.guild.id, 'channel_id': ctx.channel.id, 'time': datetime.datetime.now() + await DurationDelta.convert(self, time), 'winners': winners, 'prize': prize})
        await message.add_reaction("🎁")
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if await self.bot.db.giveaways.find_one({'_id': message.id}):
            await self.bot.db.giveaways.delete_one({'_id': message.id})
    # =======================================
    # ============= Giveaway Check ==========
    # =======================================
    @tasks.loop(seconds=5)
    async def giveaway_check(self):
        async for giveaway in self.bot.db.giveaways.find({}):
            await (await (discord.utils.get(self.bot.get_guild(giveaway['guild_id']).channels, id=giveaway['channel_id'])).fetch_message(giveaway['_id'])).edit(embed=discord.Embed(title="Giveaway", color=0x1D93FF).add_field(name=f"{(await self.bot.db.giveaways.find_one({'_id': giveaway['_id']}))['winners']} winners with a prize of {(await self.bot.db.giveaways.find_one({'_id': giveaway['_id']}))['prize']}\nEnding in {humanize_delta(relativedelta((await self.bot.db.giveaways.find_one({'_id': giveaway['_id']}))['time'], datetime.datetime.now()))}", value=f"To enter the giveaway, react to this message with 🎁").set_footer(text=f"FinderBot {info.version}"))
            if giveaway['time'] < datetime.datetime.now():
                users = []
                for reaction in (await (discord.utils.get(self.bot.get_guild(giveaway['guild_id']).channels, id=giveaway['channel_id'])).fetch_message(giveaway["_id"])).reactions:
                    async for user in reaction.users():
                        users.append(user)
                users.pop(0)
                if len(users) == 0:
                    await (await (discord.utils.get(self.bot.get_guild(giveaway['guild_id']).channels, id=giveaway['channel_id'])).fetch_message(giveaway["_id"])).edit(embed=discord.Embed(title="Giveaway", color=0xff0000).add_field(name="No winners", value="No one has won the giveaway.").set_footer(text=f"FinderBot {info.version}"))
                    await self.bot.db.giveaways.delete_one({'time': {"$lt": datetime.datetime.now()}})
                    return
                winners = ""
                try:
                    for _ in range(int(giveaway['winners'])):
                        winner = random.choice(users)
                        users.remove(winner)
                        winners += winner.name + "\n"
                except IndexError:
                    pass
                await (await (discord.utils.get(self.bot.get_guild(giveaway['guild_id']).channels, id=giveaway['channel_id'])).fetch_message(giveaway["_id"])).edit(embed=discord.Embed(title="Giveaway", color=0x1D93FF).add_field(name="Giveaway has ended", value=f"{winners} has won the giveaway.\nThe prize was {giveaway['prize']}").set_footer(text=f"FinderBot {info.version}"))
        await self.bot.db.giveaways.delete_many({'time': {"$lt": datetime.datetime.now()}})
    @giveaway_check.before_loop
    async def before_giveaway_check(self):
        await self.bot.wait_until_ready()
    # ====================================



    # ========================================
    # ============= Dice Rolling =============
    # ========================================
    @commands.command(name="roll", aliases=["dice", "diceroll"], help="Roll a dice.")
    async def diceroll(self, ctx, rolls: int = 1):
        if rolls < 100:
            roll1, roll2, roll3, roll4, roll5, roll6, total = 0, 0, 0, 0, 0, 0, 0
            for i in range(rolls):
                roll = random.randint(1, 6)
                if roll == 1:
                    roll1 += 1
                elif roll == 2:
                    roll2 += 1
                elif roll == 3:
                    roll3 += 1
                elif roll == 4:
                    roll4 += 1
                elif roll == 5:
                    roll5 += 1
                elif roll == 6:
                    roll6 += 1
                total += roll
            if rolls > 1:
                await ctx.send(embed=discord.Embed(title="Dice rolling").add_field(name=f"Your total is {total}", value=f"You rolled {roll1} 1's\nYou rolled {roll2} 2's\nYou rolled {roll3} 3's\nYou rolled {roll4} 4's\nYou rolled {roll5} 5's\nYou rolled {roll6} 6's").set_footer(text=f"FinderBot {info.version}"))
            else:
                await ctx.send(embed=discord.Embed(title="Dice rolling").add_field(name=f"Your total is {total}", value=f"You rolled {roll}").set_footer(text=f"FinderBot {info.version}"))      
        else:
            await ctx.send(embed=discord.Embed(title="Dice rolling").add_field(name=f"You can only roll up to 100 dice", value=f"Please try again").set_footer(text=f"FinderBot {info.version}"))
    # ========================================

    # ==================================
    # ============= Donate =============
    # ==================================
    @commands.command(name="donate", aliases=["support"], help="Donate to the bot.")
    async def donate(self,ctx):
        link = 'https://paypal.com/donate?hosted_button_id=8ZP8UT4W634G8'
        await ctx.send(embed=discord.Embed(title="Donate").add_field(name="Donate to FinderBot", value=f"You can donate to FinderBot here: {link}").set_footer(text=f"FinderBot {info.version}"))
    # ============================================

    # ===================================
    # ============= Version =============
    # ===================================
    @commands.command(name="version", aliases=["changelog"], help="Check the changelog.")
    async def version(self,ctx):
        f = open('CHANGELOG', 'r')
        await ctx.send(embed=discord.Embed(title="Version", color=0x8FCB95).add_field(name=f"Latest Changelog for FinderBot {info.version}", value=f'```{f.read()}```', inline=True).set_footer(text=f"FinderBot {info.version}"))
    # ============================================



    # =======================================
    # ============= Flip a coin =============
    # =======================================
    @commands.command(name="flip", aliases=["coin", "flipcoin", "headsortails", "coinflip"], help="Flip a coin.")
    async def coinflip(self, ctx, flips: int = 1):
        heads = 0
        tails = 0
        if flips == 1:
            flips = random.choice(["heads", "tails"])
            await ctx.send(f"You fliped {flips}")
        elif flips < 100:
            for i in range(flips):
                flip = random.choice(["heads", "tails"])
                if flip == "heads":
                    heads+=1
                else:
                    tails+=1
            await ctx.send(embed=discord.Embed(title="Coin Flipping").add_field(name=f"You flipped the coin {flips} times", value=f"You flipped heads {heads} times\nYou flipped tails {tails} times").set_footer(text=f"FinderBot {info.version}"))
        else:
            await ctx.send("Please flip less than 100 times")
    # =======================================

def setup(bot):
    bot.add_cog(Basic(bot))
