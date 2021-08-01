import discord
import info
import random
from discord.ext import commands

class Fun(commands.Cog):
    """Fun commands."""
    def __init__(self, bot):
        self.bot = bot
    


    # ================================
    # ============= Pong =============
    # ================================
    @commands.command(name="ping", aliases=["pong"], help="Ping!")
    async def ping(self, ctx):
        await ctx.send("Pong!")
    # ================================

    # ==================================
    # ============= 8 Ball =============
    # ==================================
    @commands.command(name="8ball", aliases=["8", "eightball", "8-ball", "eight-ball"], help="Ask the 8 Ball a question!")
    async def eight_ball(self, ctx, arg):
        ballList = ["will occur on the 14th day after the 7th saturday of your 273rd year.", "is on the horizon of fate", "is within the realm of possibilities", "will never happen, you dumb dumb", ". Don't count on it", ". It is decidedly so!", ". Without a doubt", "has already occurred"]
        await ctx.send(embed=discord.Embed(title="8ball").add_field(name=f"The desire you seek {random.choice(ballList)}!", value="⠀").set_footer(text=f"FinderBot {info.version}"))
    # ==================================



    # =================================
    # ============= Quote =============
    # =================================
    @commands.command(name="quote", aliases=["inspiration", "inspire"], help="Get inspired!")
    async def quote(self, ctx):
        await ctx.send(embed=discord.Embed(title="Inspiration Quotes").add_field(name=random.choice(["Rome was not built in a day, it was built in a 2 days", "42", "If life gives you lemons, I'll burn your house down!!", "The alphabet has no need to be in order", "If the lads ask you to voice chat, you better join.", "Reading the TOS of a website will not give you enlightenment.", "Error: FinderBot.app raised exception : 404 quote not found \nFinderBot.quotes.errors.doneAll: You have done it. You have seen all the quotes. There are no more.\nGo outside and do something else with your sad, sad life.", "The cake is a lie"]), value="⠀").set_footer(text=f"FinderBot {info.version}"))
    # =================================

def setup(bot):
    bot.add_cog(Fun(bot))
