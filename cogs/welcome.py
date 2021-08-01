import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if await self.bot.db.settings.find_one({'_id': member.guild.id}):
            for role in (await self.bot.db.settings.find_one({'_id': member.guild.id})).get('joinroleid'):
                await member.add_roles(discord.utils.get(member.guild.roles, id=int(role)))
            locales = await self.bot.db.locales.find_one({'_id': member.guild.id, 'locale': (await self.bot.db.settings.find_one({'_id': member.guild.id})).get('locales')}) if (await self.bot.db.settings.find_one({'_id': member.guild.id})).get('locales') else await self.bot.db.locales.find_one({'_id': member.guild.id, 'locale': "en-gb"})
            if (await self.bot.db.settings.find_one({'_id': member.guild.id})).get('welcome'):
                if (await self.bot.db.settings.find_one({'_id': member.guild.id})).get('welcome_DM'):
                    await member.send(locales['DMWelcomeMessage']) if locales else await member.send("Welcome to the server")
                if (await self.bot.db.settings.find_one({'_id': member.guild.id})).get('welcome_channel') and (await self.bot.db.settings.find_one({'_id': member.guild.id})).get('welcome_channel_id'):
                        await discord.utils.get(member.guild.channels, id=(await self.bot.db.settings.find_one({'_id': member.guild.id})).get('welcome_channel_id')).send(locales['ChannelWelcomeMessage']) if locales else await discord.utils.get(member.guild.channels, id=(await self.bot.db.settings.find_one({'_id': member.guild.id})).get('welcome_channel_id')).send("Someone joined the server")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        locales = await self.bot.db.locales.find_one({'_id': member.guild.id, 'locale': (await self.bot.db.settings.find_one({'_id': member.guild.id})).get('locales')}) if (await self.bot.db.settings.find_one({'_id': member.guild.id})).get('locales') else await self.bot.db.locales.find_one({'_id': member.guild.id, 'locale': "en-gb"})
        if (await self.bot.db.settings.find_one({'_id': member.guild.id})).get('leave'):
            if (await self.bot.db.settings.find_one({'_id': member.guild.id})).get('leave_DM'):
                await member.send(locales['DMLeaveMessage']) if locales else await member.send("You left the server")
            if (await self.bot.db.settings.find_one({'_id': member.guild.id})).get('leave_channel') and (await self.bot.db.settings.find_one({'_id': member.guild.id})).get('leave_channel_id'):
                    await discord.utils.get(member.guild.channels, id=(await self.bot.db.settings.find_one({'_id': member.guild.id})).get('leave_channel_id')).send(locales['ChannelLeaveMessage']) if locales else await discord.utils.get(member.guild.channels, id=(await self.bot.db.settings.find_one({'_id': member.guild.id})).get('leave_channel_id')).send("Someone left the server")

# add way to inject code into messages:

def setup(bot):
    bot.add_cog(Welcome(bot))
