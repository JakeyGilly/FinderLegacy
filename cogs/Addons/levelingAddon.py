import discord, info, random, aiosqlite
from discord.ext import commands
import requests
from PIL import Image, ImageFont, ImageDraw 
import os
def webp2png(path, ID):
    im = Image.open(path).convert("RGBA")
    im.save(f"assets/imageCache/{ID}.png")
    os.remove(path)

class Leveling(commands.Cog):
    """The Leveling Commands"""
    author = "FinderTeam"
    info = "Allows you to level up in your server and compete with others globally and in your server"
    thumbnail = "http://www.rsstrokebkt.com/aset/bootstrap/png/512/arrow-graph-up-right.png"
    def __init__(self, bot):
        self.bot = bot

    # =======================================================
    # ============= Check if addon is installed =============
    # =======================================================
    async def is_addon_server(ctx):
        if not await ctx.bot.db.addons.find_one({"_id": ctx.guild.id}):
            await ctx.bot.db.addons.insert_one({"_id": ctx.guild.id, "addons": []})
        if "leveling" in (await ctx.bot.db.addons.find_one({"_id": ctx.guild.id})).get("addons"):
            return True
        return False

    @commands.Cog.listener()
    async def on_message(self, message):
        if (await self.bot.get_context(message)).valid:
            if not await self.bot.db.addons.find_one({"_id": message.guild.id}):
                await self.bot.db.addons.insert_one({"_id": message.guild.id, "addons": []})
            if not await self.bot.db.leveling.find_one({"_id": message.guild.id}):
                await self.bot.db.leveling.insert_one({"_id": message.guild.id})
            if isinstance(message.channel, discord.channel.DMChannel) or not "leveling" in (await self.bot.db.addons.find_one({"_id": message.guild.id})).get("addons") or message.author.id == self.bot.user.id:
                return
            if not (await self.bot.db.leveling.find_one({"_id": message.guild.id})).get(str(message.author.id)):
                await message.channel.send(f"{message.author.mention}, you are now level 1!")
                await self.bot.db.leveling.update_one({"_id": message.guild.id}, {"$set": {f"{message.author.id}": {"level": 1, "experience": 0}}})
            else:
                await self.bot.db.leveling.update_one({"_id": message.guild.id}, {"$inc": {f"{message.author.id}.experience": 1}}, upsert=True)
                level = (await self.bot.db.leveling.find_one({"_id": message.guild.id})).get(str(message.author.id)).get("level") or 0
                xp2next = (5*(level+1)**2)+(5*(level+1))
                if (await self.bot.db.leveling.find_one({"_id": message.guild.id}))[str(message.author.id)].get("experience") >= xp2next:
                    await self.bot.db.leveling.update_one({"_id": message.guild.id}, {"$inc": {f"{message.author.id}.level": 1}, "$set": {f"{message.author.id}.experience": 0}}, upsert=True)
                    await message.channel.send(f"{message.author.mention}, you are now level "+str((await self.bot.db.leveling.find_one({"_id": message.guild.id})).get(str(message.author.id)).get('level'))+"!")


    @commands.command(name="rank", aliases=["lvl", "level"], hidden=True)
    @commands.guild_only()
    @commands.check(is_addon_server)
    async def rank(self, ctx, user: commands.MemberConverter = None):
        if not user:
            user = ctx.author
        if not user.id == self.bot.user.id:
            level = 0
            experience = 0
            percent = 0
            xp2next = 1
            if await self.bot.db.leveling.find_one({"_id": ctx.guild.id}) and (await self.bot.db.leveling.find_one({"_id": ctx.guild.id})).get(str(user.id)):
                experience = (await self.bot.db.leveling.find_one({"_id": ctx.guild.id}))[str(user.id)].get("experience") or 0
                level = (await self.bot.db.leveling.find_one({"_id": ctx.guild.id}))[str(user.id)].get("level") or 0
                xp2next = (5*(level+1)**2)+(5*(level+1))
                percent = ((await self.bot.db.leveling.find_one({"_id": ctx.guild.id}))[str(user.id)].get("experience")/xp2next) * 100
            tempID = random.randint(1,9999999999999)
            download = requests.get(user.avatar_url, allow_redirects=True)
            open(f'assets/imageCache/{tempID}.webp', 'wb').write(download.content)
            webp2png(f'assets/imageCache/{tempID}.webp', tempID)
            avatar = Image.open(f'assets/imageCache/{tempID}.png')
            avatar = avatar.resize((1024, 1024), Image.ANTIALIAS)
            base_img = Image.open('assets/imageTemplates/bottom.png').convert("RGBA")
            top_img = Image.open('assets/imageTemplates/top.png').convert("RGBA")
            base_img.paste(avatar, (0,0), avatar)
            base_img.paste(top_img, (0,0), top_img)
            ImageDraw.Draw(base_img).text((1124,100), user.name, (255, 255, 255), font=ImageFont.truetype('assets/Fonts/OpenSans-SemiBold.ttf', 200))
            ImageDraw.Draw(base_img).text((1124,350), f"Level {level}", (104,118,114), font=ImageFont.truetype('assets/Fonts/OpenSans-Light.ttf', 200))
            progressBar = Image.new('RGBA', (4096, 1024), color = (70,80,86,255))
            PBMask = Image.open("assets/imageTemplates/barMask.png")
            ImageDraw.Draw(progressBar).rectangle((1200,700,1200+((2700/100)*percent),900), fill=(0, 192, 192), outline=(255, 255, 255))
            base_img.paste(progressBar,(0,0),PBMask)
            if await self.bot.db.leveling.find_one({"_id": ctx.guild.id}) and (await self.bot.db.leveling.find_one({"_id": ctx.guild.id})).get(str(user.id)):
                ImageDraw.Draw(base_img).text((1300,695), f"{experience}/{xp2next}", (36,37,40), font=ImageFont.truetype('assets/Fonts/OpenSans-Regular.ttf', 150))
            try:
                download = requests.get(ctx.guild.icon_url, allow_redirects=True)
                open(f'assets/imageCache/{tempID}.webp', 'wb').write(download.content)
                webp2png(f'assets/imageCache/{tempID}.webp', tempID)
                guild = Image.open(f'assets/imageCache/{tempID}.png')
            except:
                guild = Image.open('assets/imageTemplates/qmod.png')
            guild = guild.resize((512,512), Image.ANTIALIAS)
            mask = Image.open('assets/imageTemplates/guildMask.png')
            base_img.paste(guild,(4096-512,0),mask)
            if await self.bot.db.leveling.find_one({"id_": ctx.guild.id}) and (await self.bot.db.leveling.find_one({"id_": ctx.guild.id})).get(str(user.id)):
                ImageDraw.Draw(base_img).ellipse((4096-512-200, 512-250, 4096-512-200+400, 512-250+400), fill=(36, 37, 40), outline=(0, 0, 0,0))
                ImageDraw.Draw(base_img).text((4096-512-100+100, 512-150+100), f"#{number}", (255,255,255), font = ImageFont.truetype('assets/Fonts/OpenSans-Bold.ttf', 200), anchor="mm")
            base_img.save(f"assets/imageCache/{tempID}result.png")
            avatar.close()
            base_img.close()
            progressBar.close()
            PBMask.close()
            top_img.close()
            await ctx.send(file=discord.File(f"assets/imageCache/{tempID}result.png"))
            os.remove(f"assets/imageCache/{tempID}.png")
            os.remove(f"assets/imageCache/{tempID}result.png")
        else:
            tempID = random.randint(1,9999999999999)
            download = requests.get(user.avatar_url, allow_redirects=True)
            open(f'assets/imageCache/{tempID}.webp', 'wb').write(download.content)
            webp2png(f'assets/imageCache/{tempID}.webp', tempID)
            avatar = Image.open(f'assets/imageCache/{tempID}.png')
            avatar = avatar.resize((1024, 1024), Image.ANTIALIAS)
            base_img = Image.open('assets/imageTemplates/bottom.png').convert("RGBA")
            top_img = Image.open('assets/imageTemplates/top.png').convert("RGBA")
            base_img.paste(avatar, (0,0), avatar)
            base_img.paste(top_img, (0,0), top_img)
            ImageDraw.Draw(base_img).text((1124,100), user.name, (255, 255, 255), font=ImageFont.truetype('assets/Fonts/OpenSans-SemiBold.ttf', 200))
            ImageDraw.Draw(base_img).text((1124,350), f"Level ∞", (104,118,114), font=ImageFont.truetype('assets/Fonts/OpenSans-Light.ttf', 200))
            progressBar = Image.new('RGBA', (4096, 1024), color = (70,80,86,255))
            PBMask = Image.open("assets/imageTemplates/barMask.png")
            ImageDraw.Draw(progressBar).rectangle((1200,700,1200+((2700/100)*100),900), fill=(0, 192, 192), outline=(255, 255, 255))
            base_img.paste(progressBar,(0,0),PBMask)
            ImageDraw.Draw(base_img).text((1300,695), f"∞/∞", (36,37,40), font=ImageFont.truetype('assets/Fonts/OpenSans-Regular.ttf', 150))
            try:
                download = requests.get(ctx.guild.icon_url, allow_redirects=True)
                open(f'assets/imageCache/{tempID}.webp', 'wb').write(download.content)
                webp2png(f'assets/imageCache/{tempID}.webp', tempID)
                guild = Image.open(f'assets/imageCache/{tempID}.png')
            except:
                guild = Image.open('assets/imageTemplates/qmod.png')
            guild = guild.resize((512,512), Image.ANTIALIAS)
            mask = Image.open('assets/imageTemplates/guildMask.png')
            base_img.paste(guild,(4096-512,0),mask)
            ImageDraw.Draw(base_img).ellipse((4096-512-200, 512-250, 4096-512-200+400, 512-250+400), fill=(36, 37, 40), outline=(0, 0, 0,0))
            ImageDraw.Draw(base_img).text((4096-512-100+100, 512-150+100), f"#∞", (255,255,255), font = ImageFont.truetype('assets/Fonts/OpenSans-Bold.ttf', 200), anchor="mm")
            base_img.save(f"assets/imageCache/{tempID}result.png")
            avatar.close()
            base_img.close()
            progressBar.close()
            PBMask.close()
            top_img.close()
            await ctx.send(file=discord.File(f"assets/imageCache/{tempID}result.png"))
            os.remove(f"assets/imageCache/{tempID}.png")
            os.remove(f"assets/imageCache/{tempID}result.png")

    # @commands.group()
    # @commands.guild_only()
    # @commands.check(is_addon_server)
    # async def leaderboard(self, ctx):
    #     if ctx.invoked_subcommand is None:
    #         commands = ""
    #         embed=discord.Embed(title="Addon subcommands", color=0xFFA500).set_footer(text=f"FinderBot {info.version}")
    #         for i in ctx.command.walk_commands():
    #             commands += f"{ctx.prefix}{i}\n"
    #         embed.add_field(name="Subcommands", value=commands, inline=False)
    #         await ctx.send(embed=embed)

    # @leaderboard.command()
    # @commands.guild_only()
    # @commands.check(is_addon_server)
    # async def world(self, ctx):
    #     embed=discord.Embed(title="Leaderboard").set_footer(text=f"FinderBot {info.version}")
    #     number = 0
    #     async for i in self.bot.db.leveling.find({}):
    #         print(i)
    #         for key, _ in i.items():
    #             if not key == "_id":
    #                 number += 1
    #                 embed.add_field(name=f"{number}) {await self.bot.fetch_user(int(key))} in server ```{self.bot.get_guild(int(i['_id']))}```", value=f"Level {i[key].get('level')} - {i[key].get('experience')} xp", inline=False)
    #                 if number == 10:
    #                     await ctx.send(embed=embed)
    #                     return
    #         await ctx.send(embed=embed)
        

    # @leaderboard.command()
    # @commands.guild_only()
    # @commands.check(is_addon_server)
    # async def server(self, ctx):
    #     embed=discord.Embed(title=f"Leaderboard in server {ctx.guild.name}").set_footer(text=f"FinderBot {info.version}")
    #     number = 0
    #     async for i in self.bot.db.leveling.find({"_id": ctx.guild.id}):
    #         for key, _ in i.items():
    #             if not key == "_id":
    #                 number += 1
    #                 embed.add_field(name=f"{number}) {await self.bot.fetch_user(int(key))}", value=f"Level {i[key].get('level')} - {i[key].get('experience')} xp", inline=False)
    #                 if number == 10:
    #                     await ctx.send(embed=embed)
    #                     return
    #         await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Leveling(bot))
