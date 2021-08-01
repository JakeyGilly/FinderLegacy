import re
from discord.ext import commands
import discord, info, discord_components
supported_addons = {'code': 'Code', 'economy': 'Economy', 'tictactoe': 'TicTacToe', 'leveling': 'Leveling', "tickets": 'Ticket', "rockpaperscissors": 'RockPaperScissors'}

class Addons(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        discord_components.DiscordComponents(self.bot)

    @commands.guild_only()
    @commands.group(name="addon", aliases=["addons", "plugin", "mod"])
    @commands.has_permissions(administrator=True)
    async def addon(self, ctx):
        if ctx.invoked_subcommand is None:
            commands = ""
            embed=discord.Embed(title="Addon subcommands", color=0xFFA500).set_footer(text=f"FinderBot {info.version}")
            for i in ctx.command.walk_commands():
                commands += f"{ctx.prefix}{i}\n"
            embed.add_field(name="Subcommands", value=commands, inline=False)
            await ctx.send(embed=embed)


    @commands.guild_only()
    @addon.command(name="install", aliases=["add"])
    @commands.has_permissions(administrator=True)
    async def install(self, ctx, addon):
        if addon in supported_addons.keys():
            if not await self.bot.db.addons.find_one({"_id": ctx.guild.id}):
                await self.bot.db.addons.insert_one({"_id": ctx.guild.id, "addons": []})
            if addon not in (await self.bot.db.addons.find_one({"_id": ctx.guild.id}))['addons']:
                await self.bot.db.addons.update_one({"_id": ctx.guild.id}, {"$push": {"addons": addon}})
            else:
                await ctx.send(embed=discord.Embed(title="Addon installation failed", color=discord.Color.red()).add_field(name=f"`{ctx.guild}` already has {addon} installed", value=f"To uninstall use {ctx.prefix}addon uninstall {addon}").set_footer(text=f"FinderBot {info.version}"))
                return
            await ctx.send(embed=discord.Embed(title="Addon installation successful", color=discord.Color.green()).add_field(name=f"`{ctx.guild}` now has {addon} installed", value=f"To uninstall use {ctx.prefix}addon uninstall {addon}").set_footer(text=f"FinderBot {info.version}"))
        else:
            await ctx.send(embed=discord.Embed(title="Addon installation failed", color=discord.Color.red()).add_field(name=f"{addon} is not supported", value=f"Please use {ctx.prefix}addon list to see available addons").set_footer(text=f"FinderBot {info.version}"))
    
    
    @commands.guild_only()  
    @addon.command(name="uninstall", aliases=["remove", "delete", "rm"])
    @commands.has_permissions(administrator=True)
    async def uninstall(self, ctx, addon):
        if addon in supported_addons.keys():
            if await self.bot.db.addons.find_one({"_id": ctx.guild.id}) and addon in (await self.bot.db.addons.find_one({"_id": ctx.guild.id}))['addons']:
                await self.bot.db.addons.update_one({"_id": ctx.guild.id}, {"$pull": {"addons": addon}})
                await ctx.send(embed=discord.Embed(title="Addon uninstallation successful", color=discord.Color.green()).add_field(name=f"`{ctx.guild}` no longer has {addon} installed", value=f"To install use {ctx.prefix}addon install {addon}").set_footer(text=f"FinderBot {info.version}"))
            else:
                await ctx.send(embed=discord.Embed(title="Addon uninstallation failed", color=discord.Color.red()).add_field(name=f"`{ctx.guild}` does not have {addon} installed", value=f"To install use {ctx.prefix}addon install {addon}").set_footer(text=f"FinderBot {info.version}"))
        else:
            await ctx.send(embed=discord.Embed(title="Addon uninstallation failed", color=discord.Color.red()).add_field(name=f"{addon} is not supported", value=f"Please use {ctx.prefix}addon list to see available addons").set_footer(text=f"FinderBot {info.version}"))    
    
    @commands.guild_only()
    @addon.command(name="list", aliases=["ls"])
    @commands.has_permissions(administrator=True)
    async def list(self, ctx):
        embed=discord.Embed(title="Addon list", color=0xFFA500).set_footer(text=f"FinderBot {info.version}")
        if not await self.bot.db.addons.find_one({"_id": ctx.guild.id}):
            for i in supported_addons.values():
                embed.add_field(name=f"{i}", value="Not installed", inline=False)
            await ctx.send(embed=embed)
            return
        for i in supported_addons.values():
            if i.lower() in (await self.bot.db.addons.find_one({"_id": ctx.guild.id})).get('addons'):
                embed.add_field(name=f"{i}", value="Installed", inline=False)
            else:
                embed.add_field(name=f"{i}", value="Not installed", inline=False)
        await ctx.send(embed=embed)
    
    
    @commands.guild_only()
    @addon.command(name="info", aliases=["i", "infomation", "help", "h"])
    @commands.has_permissions(administrator=True)
    async def info(self, ctx, addon):
        if addon in supported_addons.keys():
            commandstree = ""
            for i in self.bot.commands:
                if i.cog and i.cog.qualified_name == supported_addons[addon]:
                    commandstree += f" - {ctx.prefix}{i}\n"
                    if isinstance(i, commands.Group):
                        for j in i.walk_commands():
                            commandstree += " "*len(str(j).split()) +f"| - {str(j).split()[-1]}\n"
            def check(res):
                return ctx.author == res.user and res.channel == ctx.channel and res.component.id == addon
            message = await ctx.send(embed=discord.Embed(title="Addon Info", color=0xFFA500).add_field(name=f"{addon.capitalize()} info", value=f"{self.bot.get_cog(supported_addons[addon]).info}\n`Author {self.bot.get_cog(supported_addons[addon]).author}`", inline=False).add_field(name=f"{addon.capitalize()} Commands", value=f"```{commandstree}```", inline=False).set_thumbnail(url=self.bot.get_cog(supported_addons[addon]).thumbnail).set_footer(text=f"FinderBot {info.version}"), components=[discord_components.Button(label="Install Addon", id=f"{addon}", style=3)] if addon not in (await self.bot.db.addons.find_one({"_id": ctx.guild.id}))["addons"] else [discord_components.Button(label="Uninstall Addon", id=f"{addon}", style=4)])
            interaction = await self.bot.wait_for("button_click", check=check)
            if addon not in (await self.bot.db.addons.find_one({"_id": ctx.guild.id}))["addons"]:
                await self.bot.db.addons.update_one({"_id": ctx.guild.id}, {"$push": {"addons": addon}})
                await interaction.respond(embed=discord.Embed(title="Addon Installed", color=0x006400).add_field(name="We have successfully installed addon", value=f"{addon} in guild `{ctx.guild}`").set_footer(text=f"FinderBot {info.version}"))
                await message.edit(components=[])
            else:
                await self.bot.db.addons.update_one({"_id": ctx.guild.id}, {"$pull": {"addons": addon}})
                await interaction.respond(embed=discord.Embed(title="Addon Removed", color=0x800000).add_field(name="We have successfully removed addon", value=f"{addon} in guild `{ctx.guild}`").set_footer(text=f"FinderBot {info.version}"))
                await message.edit(components=[])
        else:
            await ctx.send(embed=discord.Embed(title="Not supported addon", color=0x800000).add_field(name="We do not recognise that addon", value=f"use ;addon list to see supported addons").set_footer(text=f"FinderBot {info.version}"))

def setup(bot):
    bot.add_cog(Addons(bot))