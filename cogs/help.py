import discord, info
from discord.ext import commands
from discord.errors import Forbidden


class Help(commands.Cog):
    """Sends this help message"""
    def __init__(self, bot):
        self.bot = bot

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


def setup(bot):
    bot.add_cog(Help(bot))