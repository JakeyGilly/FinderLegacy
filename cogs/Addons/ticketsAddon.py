import discord, info, random, datetime, asyncio
from discord.ext import commands
class Ticket(commands.Cog):
    author = "FinderTeam"
    thumbnail = 'https://icons.iconarchive.com/icons/custom-icon-design/flatastic-2/512/ticket-icon.png'
    info = 'Get help from members of the server and ask questions'
    def __init__(self, bot):
        self.bot = bot

    # =======================================================
    # ============= Check if addon is installed =============
    # =======================================================
    async def is_addon_server(ctx):
        if not await ctx.bot.db.addons.find_one({"_id": ctx.guild.id}):
            await ctx.bot.db.addons.insert_one({"_id": ctx.guild.id, "addons": []})
        if "tickets" in (await ctx.bot.db.addons.find_one({"_id": ctx.guild.id})).get("addons"):
            return True
        return False

    # =====================================
    # ============= Ticketing =============
    # =====================================
    @commands.command(name='ticket', aliases=['tickets', "question"])
    @commands.guild_only()
    @commands.check(is_addon_server)
    async def ticket(self, ctx):
        msg = await ctx.send(embed=discord.Embed(title="FinderBot Technical Support", color=0x2f2fd0).add_field(name="Would you like to create a ticket?", value="If you have a question or concern, please create a ticket by reacting with the 📩 emoji.", inline=True).set_thumbnail(url="https://cdn.discordapp.com/attachments/726725834261397545/816730090837639191/FinderBotHelp.png").set_footer(text=f"FinderBot {info.version}"))
        await msg.add_reaction("📩")
        await ctx.message.delete()
        def check(_reaction, _user):
            return _user == ctx.message.author and str(_reaction.emoji) == '📩' and _reaction.message.id == msg.id
        def check2(_reaction, _user):
            return _user == ctx.message.author and str(_reaction.emoji) == '🔒' and _reaction.message.id == msg2.id
        def check3(_reaction, _user):
            return _user == user and (str(_reaction.emoji) == '✅' or str(_reaction.emoji) == '❌') and _reaction.message.id == msg2.id
        try:
            reaction, user = await ctx.bot.wait_for('reaction_add', timeout=10.0, check=check)
        except asyncio.TimeoutError:
            await msg.edit(embed=discord.Embed(title="Timed Out", color=0xFF0000).add_field(name=f"{ctx.author.name}, You took too long to respond!", value="Try running the command again").set_footer(text=f"FinderBot Version {info.version}"))
        else:
            await reaction.message.delete()
            overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False), ctx.message.author: discord.PermissionOverwrite(read_messages=True, send_messages=True)} # support_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)}
            ticket_num = random.randint(100000, 999999)
            channel_ticket = await ctx.guild.create_text_channel(f'ticket-#{ticket_num}', overwrites=overwrites)   
            msg2 = await channel_ticket.send(embed=discord.Embed(title="How can we help you?", description="A staff member will take care of you as soon as possible. In the meantime please describe your problem\n\n🔒 - Close the ticket", color=0x0000ff).set_footer(text=f"FinderBot {info.version}").set_thumbnail(url="https://cdn.discordapp.com/attachments/726725834261397545/816730090837639191/FinderBotHelp.png"))
            await msg2.add_reaction("🔒")
            while True:
                reaction, user = await ctx.bot.wait_for('reaction_add', check=check2)
                await msg2.add_reaction("✅")
                await msg2.add_reaction("❌")
                reaction2, _ = await ctx.bot.wait_for('reaction_add', check=check3)
                if '✅' in str(reaction2.emoji):
                    await channel_ticket.send("Closing Ticket...")
                    await channel_ticket.delete()
                if '❌' in str(reaction2.emoji):
                    await msg2.clear_reactions()
                    await msg2.add_reaction("🔒")
            #TODO: add buttons

def setup(bot):
    bot.add_cog(Ticket(bot))