from discord.ext import commands
from dateutil.relativedelta import relativedelta
import discord, info, datetime

def humanize_delta(delta: relativedelta) -> str:
    time_strings = []
    for unit, value in (("years", delta.years),("months", delta.months),("days", delta.days),("hours", delta.hours),("minutes", delta.minutes),("seconds", delta.seconds)):
        if value:
            time_strings.append(f"{value} {unit}")
    if len(time_strings) > 1:
        time_strings[-1] = f"{time_strings[-2]} and {time_strings[-1]}"
        del time_strings[-2]
    return ", ".join(time_strings)

start_time = datetime.datetime.now()

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.group(name="owner", aliases=["dev"], hidden=True)
    @commands.is_owner()
    async def owner(self, ctx):
        if ctx.invoked_subcommand is None:
            commands = ""
            embed=discord.Embed(title="Addon subcommands", color=0xFFA500)
            for i in ctx.command.walk_commands():
                commands += f"{ctx.prefix}{i}\n"
            embed.add_field(name="Subcommands", value=commands, inline=False)
            await ctx.send(embed=embed)

    @owner.command(name="stats", aliases=["info", "i"], hidden=True)
    @commands.is_owner()
    async def stats(self, ctx):
        await ctx.send(embed=discord.Embed(title="Owner Stats Dashboard", color=0xFFA50).add_field(name="Bot in", value=f"{len(self.bot.guilds)} servers", inline=False).add_field(name="Users", value=f"{sum([len(guild.members) for guild in self.bot.guilds])} members", inline=False).add_field(name="Unique members", value=f"{len(set([member.id for guild in self.bot.guilds for member in guild.members]))} unique", inline=False).add_field(name="Average users per server", value=f"{round(sum([len(guild.members) for guild in self.bot.guilds]) / len(self.bot.guilds), 2)} users", inline=False).set_footer(text=f"FinderBot {info.version}"))

    @owner.command(name="uptime", aliases=["running", "run"], hidden=True)
    @commands.is_owner()
    async def uptime(self, ctx):
        await ctx.send(embed=discord.Embed(title="Owner Uptime", color=0xFFA500).add_field(name="Uptime", value=f"{humanize_delta(relativedelta(datetime.datetime.now(), start_time))}", inline=False).set_footer(text=f"FinderBot {info.version}"))

# TODO
# add command stats commands per day/hour counter
# add owner options
def setup(bot):
    bot.add_cog(Owner(bot))