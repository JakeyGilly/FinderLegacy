import discord, info, random, datetime, re
from dateutil.relativedelta import relativedelta
from discord.ext import commands
def humanize_delta(delta: relativedelta) -> str:
    time_strings = []
    for unit, value in ((f"year{'s'[:delta.years^1]}", delta.years),(f"month{'s'[:delta.months^1]}", delta.months),(f"day{'s'[:delta.days^1]}", delta.days),(f"hour{'s'[:delta.hours^1]}", delta.hours),(f"minute{'s'[:delta.minutes^1]}", delta.minutes),(f"second{'s'[:delta.seconds^1]}", delta.seconds)):
        if value:
            time_strings.append(f"{value} {unit}")
    if len(time_strings) > 1:
        time_strings[-1] = f"{time_strings[-2]} and {time_strings[-1]}"
        del time_strings[-2]
    return ", ".join(time_strings)
class Economy(commands.Cog):
    author = "FinderTeam"
    info = "A Economy addon that implements currency and ways to earn money."
    thumbnail = 'https://www.iconpacks.net/icons/1/free-coin-icon-794-thumb.png'
    def __init__(self, bot):
        self.bot = bot



    # =======================================================
    # ============= Check if addon is installed =============
    # =======================================================
    async def is_addon_server(ctx):
        if not await ctx.bot.db.addons.find_one({"_id": ctx.guild.id}):
            await ctx.bot.db.addons.insert_one({"_id": ctx.guild.id, "addons": []})
        if "economy" in (await ctx.bot.db.addons.find_one({"_id": ctx.guild.id})).get("addons"):
            return True
        return False

    @commands.command(name="bal", aliases=["balance", "money", "bank", "account", "moneybag", "wallet"])
    @commands.guild_only()
    @commands.check(is_addon_server)
    async def money(self, ctx, user: discord.Member = None):
        if not await self.bot.db.settings.find_one({"_id": ctx.guild.id}):
            await self.bot.db.settings.insert_one({"_id": ctx.guild.id})
        if not await self.bot.db.economy.find_one({"_id": ctx.guild.id}):
            await self.bot.db.economy.insert_one({"_id": ctx.guild.id})
        bank = 0
        wallet = 0
        if await self.bot.db.economy.find_one({"_id": ctx.guild.id}) and (await self.bot.db.economy.find_one({"_id": ctx.guild.id})).get(str(ctx.author.id) if not user else str(user.id)):
            bank = (await self.bot.db.economy.find_one({"_id": ctx.guild.id}))[str(ctx.author.id) if not user else str(user.id)].get("bank") or 0
            wallet = (await self.bot.db.economy.find_one({"_id": ctx.guild.id}))[str(ctx.author.id) if not user else str(user.id)].get("wallet") or 0
        EcoSymbol = (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("economy_symbol") or "$"
        await ctx.send(embed=discord.Embed(title=f"{ctx.author.name if not user else user.name}'s money", color=0xffff00).add_field(name="Bank", value=f"{EcoSymbol}{bank}", inline=False).add_field(name="Wallet", value=f"{EcoSymbol}{wallet}", inline=False).set_footer(text=f"FinderBot {info.version}"))
        
    @commands.command(name="ecosymbol", aliases=["changeecosymbol", "changeeco"])
    @commands.guild_only()
    @commands.check(is_addon_server)
    @commands.has_permissions(manage_guild=True)
    async def changeecosymbol(self, ctx, symbol):
        if not await self.bot.db.settings.find_one({"_id": ctx.guild.id}):
            await self.bot.db.settings.insert_one({"_id": ctx.guild.id})
        await self.bot.db.settings.update_one({"_id": ctx.guild.id}, {"$set": {"economy_symbol": symbol}}, upsert=True)
        await ctx.send(embed=discord.Embed(title="Success", color=0x008000).add_field(name="Prefix changed to", value=symbol, inline=False).set_footer(text=f"FinderBot {info.version}"))
        
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.command(name="beg", aliases=["plead"])
    @commands.guild_only()
    @commands.check(is_addon_server)
    async def beg(self, ctx):
        if not await self.bot.db.settings.find_one({"_id": ctx.guild.id}):
            await self.bot.db.settings.insert_one({"_id": ctx.guild.id})
        if not await self.bot.db.economy.find_one({"_id": ctx.guild.id}):
            await self.bot.db.economy.insert_one({"_id": ctx.guild.id})
        EcoSymbol = (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("economy_symbol") or "$"
        beggers = ["a homeless man", "Justin Bieber", "Steve Jobs", "a caterpillar", "Donald Trump", "FinderBot","David Attenborough", "Gregg Wallace", "Your future self", "Minecraft Steve", "Minecraft Alex","Jesus", "God", "your mum", "your dad", "your baby", "your child", "your teenager", "the queen","FinderBot's evil twin", "someone over the rainbow", "Tim Cook", "the wall", "the door", "yourself","no-one", "your shadow", "the sun", "the moon", "the stars", "your landlord", "Simon the gorilla", "Alex the budgie", "Professor Sir Dr Drew FinderBot the seconds of scotland the third MBE Jr. Snr. Jr."]
        money = random.randint(0, 100)
        self.bot.db.economy.update_one({"_id": ctx.guild.id}, {"$inc": {f"{ctx.author.id}.wallet": money}}, upsert=True)
        await ctx.send(embed=discord.Embed(title=f"Beg", color=0xffff00).add_field(name=f"You have begged to {random.choice(beggers)}", value=f"and received {EcoSymbol}{money}", inline=True).set_footer(text=f"FinderBot {info.version}"))

    @commands.command(name="daily")
    @commands.guild_only()
    @commands.check(is_addon_server)
    async def daily(self, ctx):
        if not await self.bot.db.settings.find_one({"_id": ctx.guild.id}):
            await self.bot.db.settings.insert_one({"_id": ctx.guild.id})
        if not await self.bot.db.economy.find_one({"_id": ctx.guild.id}):
            await self.bot.db.economy.insert_one({"_id": ctx.guild.id})
        if (await self.bot.db.economy.find_one({"_id": ctx.guild.id})).get(str(ctx.author.id)) and (await self.bot.db.economy.find_one({"_id": ctx.guild.id})).get(str(ctx.author.id)).get("dailyCooldown") or await self.bot.db.economy.find_one({"_id": ctx.guild.id, str(ctx.author.id)+".dailyCooldown": {"$gt": datetime.datetime.now()}}):
            time = (await self.bot.db.economy.find_one({"_id": ctx.guild.id})).get(str(ctx.author.id)).get("dailyCooldown")
            await ctx.send(embed=discord.Embed(title=f"Daily", color=0xff0000).add_field(name="You have already used your daily.", value=f"Please wait {humanize_delta(relativedelta(time, datetime.datetime.now()))}.", inline=False).set_footer(text=f"FinderBot {info.version}"))
            return
        EcoSymbol = (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("economy_symbol") or "$"
        money = random.randint(500, 5000)
        await self.bot.db.economy.update_one({"_id": ctx.guild.id}, {"$set": {str(ctx.author.id)+".dailyCooldown": datetime.datetime.now()+datetime.timedelta(days=1)}, "$inc": {str(ctx.author.id)+".wallet": money}})
        await ctx.send(embed=discord.Embed(title=f"Daily", color=0xffff00).add_field(name=f"You have received {EcoSymbol}{money}", value=f"You can use your daily again in {humanize_delta(relativedelta(datetime.datetime.now()+datetime.timedelta(days=1), datetime.datetime.now()))}.", inline=False).set_footer(text=f"FinderBot {info.version}"))
    
    @commands.command(name="deposit")
    @commands.guild_only()
    @commands.check(is_addon_server)
    async def deposit(self, ctx, amount):
        if not await self.bot.db.settings.find_one({"_id": ctx.guild.id}):
            await self.bot.db.settings.insert_one({"_id": ctx.guild.id})
        if not await self.bot.db.economy.find_one({"_id": ctx.guild.id}):
            await self.bot.db.economy.insert_one({"_id": ctx.guild.id})
        EcoSymbol = (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("economy_symbol") or "$"
        wallet = 0
        if not await self.bot.db.economy.find_one({"_id": ctx.guild.id, str(ctx.author.id)+".wallet": {"$gte": int(amount)}}):
            if (await self.bot.db.economy.find_one({"_id": ctx.guild.id})).get(str(ctx.author.id)):
                wallet = (await self.bot.db.economy.find_one({"_id": ctx.guild.id}))[str(ctx.author.id)].get('wallet') or 0
            await ctx.send(embed=discord.Embed(title=f"Deposit", color=0xff0000).add_field(name=f"You do not have enough money to deposit {EcoSymbol}{amount}.", value=f"You have {EcoSymbol}{wallet} in your wallet.", inline=False).set_footer(text=f"FinderBot {info.version}"))
            return
        await self.bot.db.economy.update_one({"_id": ctx.guild.id}, {"$inc" : {str(ctx.author.id)+".wallet": -int(amount), str(ctx.author.id)+".bank": int(amount)}})
        if (await self.bot.db.economy.find_one({"_id": ctx.guild.id})).get(str(ctx.author.id)):
            wallet = (await self.bot.db.economy.find_one({"_id": ctx.guild.id}))[str(ctx.author.id)].get('wallet') or 0
        await ctx.send(embed=discord.Embed(title=f"Deposit", color=0xffff00).add_field(name=f"You have deposited {EcoSymbol}{amount}.", value=f"You now have {EcoSymbol}{wallet} in your wallet.", inline=False).set_footer(text=f"FinderBot {info.version}"))
    
    @commands.command(name="withdraw", aliases=["withdrawal"])
    @commands.guild_only()
    @commands.check(is_addon_server)
    async def withdraw(self, ctx, amount):
        if not await self.bot.db.settings.find_one({"_id": ctx.guild.id}):
            await self.bot.db.settings.insert_one({"_id": ctx.guild.id})
        if not await self.bot.db.economy.find_one({"_id": ctx.guild.id}):
            await self.bot.db.economy.insert_one({"_id": ctx.guild.id})
        EcoSymbol = (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("economy_symbol") or "$"
        bank = 0
        if not await self.bot.db.economy.find_one({"_id": ctx.guild.id, str(ctx.author.id)+".bank": {"$gte": int(amount)}}):
            if (await self.bot.db.economy.find_one({"_id": ctx.guild.id})).get(str(ctx.author.id)):
                bank = (await self.bot.db.economy.find_one({"_id": ctx.guild.id}))[str(ctx.author.id)].get('bank') or 0
            await ctx.send(embed=discord.Embed(title=f"Withdraw", color=0xff0000).add_field(name=f"You do not have enough money to withdraw {EcoSymbol}{amount}.", value=f"You have {EcoSymbol}{bank} in your bank.", inline=False).set_footer(text=f"FinderBot {info.version}"))
            return
        await self.bot.db.economy.update_one({"_id": ctx.guild.id}, {"$inc" : {str(ctx.author.id)+".wallet": int(amount), str(ctx.author.id)+".bank": -int(amount)}})
        if (await self.bot.db.economy.find_one({"_id": ctx.guild.id})).get(str(ctx.author.id)):
            bank = (await self.bot.db.economy.find_one({"_id": ctx.guild.id}))[str(ctx.author.id)].get('bank') or 0
        await ctx.send(embed=discord.Embed(title=f"Deposit", color=0xffff00).add_field(name=f"You have withdrawn {EcoSymbol}{amount}.", value=f"You now have {EcoSymbol}{bank} in your bank.", inline=False).set_footer(text=f"FinderBot {info.version}"))


    # @commands.command()
    # @commands.guild_only()
    # @commands.check(is_addon_server)
    # async def rob(self, ctx, user: discord.User):
    #     if not await self.bot.db.settings.find_one({"_id": ctx.guild.id}):
    #         await self.bot.db.settings.insert_one({"_id": ctx.guild.id})
    #     if not await self.bot.db.economy.find_one({"_id": ctx.guild.id}):
    #         await self.bot.db.economy.insert_one({"_id": ctx.guild.id})
    #     EcoSymbol = (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("economy_symbol") or "$"
    #     print("hi")
    #     if user.id == ctx.author.id:
    #         await ctx.send(embed=discord.Embed(title=f"Rob", color=0xff0000).add_field(name=f"You cannot rob yourself.", value=f"Try rob someone else.", inline=False).set_footer(text=f"FinderBot {info.version}"))
    #         return
    #     print("hi")
    #     if (not await self.bot.db.economy.find_one({"_id": ctx.guild.id})).get(str(ctx.author.id)).get("dailyCooldown") or await self.bot.db.economy.find_one({"_id": ctx.guild.id, str(ctx.author.id)+".dailyCooldown": {"$gt": datetime.datetime.now()}}):
    #         print("hi")
    #         if await self.bot.db.economy.find_one({"_id": ctx.guild.id, str(user.id)+".wallet": {"$lt": 100}}):
    #             await ctx.send(embed=discord.Embed(title="Rob").add_field(name=f"{user.name} has not enough money", value="Try rob someone else", inline=False).set_footer(text=f"FinderBot {info.version}"))
    #         else:
    #             robbed = False
    #             while not robbed:
    #                 amount = random.randint(100, 1000)
    #                 if await self.bot.db.economy.find_one({"_id": ctx.guild.id, str(user.id)+".wallet": {"$lt": amount}}):
    #                     robbed = True
    #             await ctx.send(embed=discord.Embed(title="Rob").add_field(name=f"You successfully robbed {user.name}", value=f"You gained {EcoSymbol}{amount}", inline=False).set_footer(text=f"FinderBot {info.version}"))
    #             await self.bot.db.economy.update_one({"_id": ctx.guild.id}, {"$inc" : {str(ctx.author.id)+".wallet": int(amount), str(user.id)+".wallet": -int(amount)}})
    #             await self.bot.db.economy.update_one({"_id": ctx.guild.id}, {"$set": {str(ctx.author.id)+".robCooldown": datetime.datetime.now()+datetime.timedelta(days=1)}, "$inc": {str(ctx.author.id)+".wallet": amount}})
    #     else:
    #         await ctx.send(embed=discord.Embed(title="You already robbed recently!", color=discord.colour.Colour.blue()).add_field(name="Command is on cooldown", value=f"Come back in {humanize_delta(relativedelta(datetime.datetime.now()+datetime.timedelta(days=1)))} mins", inline=True).set_footer(text=f"FinderBot {info.version}"))

    
    @commands.command(name="gamble", aliases=["casino"])
    @commands.guild_only()
    @commands.check(is_addon_server)
    async def gamble(self, ctx, amount=100):
        if not await self.bot.db.settings.find_one({"_id": ctx.guild.id}):
            await self.bot.db.settings.insert_one({"_id": ctx.guild.id})
        if not await self.bot.db.economy.find_one({"_id": ctx.guild.id}):
            await self.bot.db.economy.insert_one({"_id": ctx.guild.id})
        EcoSymbol = (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("economy_symbol") or "$"
        if not await self.bot.db.economy.find_one({"_id": ctx.guild.id, str(ctx.author.id)+".wallet": {"$gte": int(amount)}}) or amount < 100:
            await ctx.send(embed=discord.Embed(title="Gamble", color=0xff0000).add_field(name=f"You don't have enough money", value=f"Minimum betting amount is {EcoSymbol}100", inline=False).set_footer(text=f"FinderBot {info.version}"))
            return
        else:
            reward = random.randint(-amount, amount*2)
            if reward > 0:
                await ctx.send(embed=discord.Embed(title="Gamble", color=0x00ff00).add_field(name=f"You won {EcoSymbol}{reward}", value=f"You now have {EcoSymbol}"+str(((await self.bot.db.economy.find_one({"_id": ctx.guild.id}))[str(ctx.author.id)].get("wallet") or 0)+(reward-int(amount))), inline=False).set_footer(text=f"FinderBot {info.version}"))
            else:
                await ctx.send(embed=discord.Embed(title="Gamble", color=0xff0000).add_field(name=f"You lost {EcoSymbol}{-reward}", value=f"You now have {EcoSymbol}"+str(((await self.bot.db.economy.find_one({"_id": ctx.guild.id}))[str(ctx.author.id)].get("wallet") or 0)+(reward-int(amount))), inline=False).set_footer(text=f"FinderBot {info.version}"))
            await self.bot.db.economy.update_one({"_id": ctx.guild.id}, {"$inc" : {str(ctx.author.id)+".wallet": reward-int(amount)}})

    @commands.command(name="pay", aliases=["gift", "give"])
    @commands.guild_only()
    @commands.check(is_addon_server)
    async def pay(self, ctx, user: discord.Member, amount):
        if not await self.bot.db.settings.find_one({"_id": ctx.guild.id}):
            await self.bot.db.settings.insert_one({"_id": ctx.guild.id})
        if not await self.bot.db.economy.find_one({"_id": ctx.guild.id}):
            await self.bot.db.economy.insert_one({"_id": ctx.guild.id})
        EcoSymbol = (await self.bot.db.settings.find_one({"_id": ctx.guild.id})).get("economy_symbol") or "$"
        if int(amount) < 0:
            await ctx.send(embed=discord.Embed(title="Pay", color=0xff0000).add_field(name=f"Amount cannot be negative", value=f"Amount: {amount}", inline=False).set_footer(text=f"FinderBot {info.version}"))
            return
        if int(amount) == 0:
            wallet = (await self.bot.db.economy.find_one({"_id": ctx.guild.id})).get(str(ctx.author.id)).get("wallet") or 0 if (await self.bot.db.economy.find_one({"_id": ctx.guild.id})).get(str(ctx.author.id)) else 0
            await ctx.send(embed=discord.Embed(title="Pay", color=0x00ff00).add_field(name=f"You paid {EcoSymbol}{amount}", value=f"{user.mention} now has {EcoSymbol}{wallet}", inline=False).set_footer(text=f"FinderBot {info.version}"))
            return
        wallet = 0
        if not await self.bot.db.economy.find_one({"_id": ctx.guild.id, str(ctx.author.id)+".wallet": {"$gte": int(amount)}}):
            if (await self.bot.db.economy.find_one({"_id": ctx.guild.id})).get(str(ctx.author.id)):
               wallet = (await self.bot.db.economy.find_one({"_id": ctx.guild.id}))[str(ctx.author.id)].get("wallet") or 0
            await ctx.send(embed=discord.Embed(title="Pay", color=0xff0000).add_field(name=f"You don't have enough money", value=f"You have {wallet} in your wallet", inline=False).set_footer(text=f"FinderBot {info.version}"))
            return
        await self.bot.db.economy.update_one({"_id": ctx.guild.id}, {"$inc" : {str(ctx.author.id)+".wallet": -int(amount), str(user.id)+".wallet": int(amount)}}, upsert=True)
        if (await self.bot.db.economy.find_one({"_id": ctx.guild.id})).get(str(user.id)):
            wallet = (await self.bot.db.economy.find_one({"_id": ctx.guild.id}))[str(user.id)].get("wallet") or 0
        await ctx.send(embed=discord.Embed(title="Pay", color=0x00ff00).add_field(name=f"You paid {EcoSymbol}{amount}", value=f"{user.mention} now has {EcoSymbol}{wallet}", inline=False).set_footer(text=f"FinderBot {info.version}"))
    
    
    # implement a shopping system
    # shop items
    # finder token | price 1m coins | completely useless
    


    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(embed=discord.Embed(title="This command is a addon!", color=0xff0000).add_field(name="This command is for the addon", value="economy", inline=False).add_field(name="To add it this addon use", value=f"{ctx.prefix}addon install economy", inline=False).set_footer(text=f"FinderBot {info.version}"))

def setup(bot):
    bot.add_cog(Economy(bot))
