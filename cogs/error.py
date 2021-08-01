from discord.ext import commands
import traceback, discord, info

class Error(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        error = getattr(error, 'original', error)
        ignored = (commands.CommandNotFound, )
        if isinstance(error, ignored):
            return
        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} has been disabled.')

        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(embed=discord.Embed(color=0x800000).add_field(name=f'Member Not Found', value=f"{error.args[0]}").set_footer(text=f"FinderBot {info.version}"))
        elif isinstance(error, commands.UserNotFound):
            await ctx.send(embed=discord.Embed(color=0x800000).add_field(name=f'User not found in ban list', value=error.args[0].split("\"")[1]+" was unbanned by a moderator or was not banned").set_footer(text=f"FinderBot {info.version}"))
        elif isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
            await ctx.send(embed=discord.Embed(description=error.args[0], color=0x800000).add_field(name=f'Usage for command: {ctx.command}', value=f"`{ctx.prefix}{ctx.command} {ctx.command.signature}`\n<> -> Required\n[] -> Optional").set_footer(text=f"FinderBot {info.version}"))
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=discord.Embed(color=0x800000).add_field(name=f'Missing permissions', value=f"{error.args[0]}").set_footer(text=f"FinderBot {info.version}"))
        else:
            print(self.bot.ERROR, traceback.format_exception(type(error), error, error.__traceback__), self.bot.ENDL)

def setup(bot):
    bot.add_cog(Error(bot))

    