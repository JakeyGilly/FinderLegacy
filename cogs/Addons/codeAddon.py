import discord, info, re, aiohttp, json
from discord.ext import commands

class Code(commands.Cog):
    author = "FinderTeam"
    info = "Executes programming code in discord. This uses the Piston API found at `https://github.com/engineer-man/piston`"
    thumbnail = "https://img.icons8.com/ios/452/source-code.png"
    def __init__(self, bot):
        self.bot = bot



    # =======================================================
    # ============= Check if addon is installed =============
    # =======================================================
    async def is_addon_server(ctx):
        if not await ctx.bot.db.addons.find_one({"_id": ctx.guild.id}):
            await ctx.bot.db.addons.insert_one({"_id": ctx.guild.id, "addons": []})
        if "code" in (await ctx.bot.db.addons.find_one({"_id": ctx.guild.id})).get("addons"):
            return True
        return False
        


    # ========================================
    # ============= Code Command =============
    # ========================================
    @commands.command(name="code", aliases=["program", "execute", "run", "compile"], hidden=True)
    @commands.check(is_addon_server)
    async def code(self, ctx, language, *, code):
        if re.match(re.compile(f"(?s){ctx.prefix}(?:edit_last_)?code(?: +(?P<language>\S*)\s*|\s*)(?:\n(?P<args>(?:[^\n\r\f\v]*\n)*?)\s*|\s*)```(?:(?P<syntax>\S+)\n\s*|\s*)(?P<source>.*)```(?:\n?(?P<stdin>(?:[^\n\r\f\v]\n?)+)+|)"), ctx.message.content):
            async with aiohttp.ClientSession() as session:
                async with session.post('https://emkc.org/api/v1/piston/execute', data={"language": language, "source": code.strip("`")}) as response:
                    json_data = json.loads(await response.text())
                    if list(json_data.values())[3] == "":
                        await ctx.send(embed=discord.Embed(title=" 👨‍💻 Code").add_field(name=f"The code \n{code}\n in language {language} returned ", value=f"no result").set_footer(text=f"FinderBot {info.version}")) 
                    await ctx.send(embed=discord.Embed(title=" 👨‍💻 Code").add_field(name=f"The code \n{code}\n in language {language} returned", value=f"```{list(json_data.values())[3]}```").set_footer(text=f"FinderBot {info.version}"))
        else:
            await ctx.send(embed=discord.Embed(title=" 👨‍💻 Code").add_field(name=f"The code \n{code}\n in language {language} is not valid", value=f"```{ctx.message.content}```").set_footer(text=f"FinderBot {info.version}"))
    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(embed=discord.Embed(title="This command is a addon!", color=0xff0000).add_field(name="This command is for the addon", value="code", inline=False).add_field(name="To add it this addon use", value=f"{ctx.prefix}addon install code", inline=False).set_footer(text=f"FinderBot {info.version}"))
def setup(bot):
    bot.add_cog(Code(bot))