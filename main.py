import datetime, discord, motor.motor_asyncio, info, os
from discord.ext import commands
intents = discord.Intents().default()
intents.members = True

async def update_status(guild_count):
	await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"the screams of humans in {guild_count} server{'s'[:guild_count^1]}"))

async def get_prefix(bot, message):
	if not message.guild:
		return commands.when_mentioned_or(";")(bot, message)
	return commands.when_mentioned_or(";")(bot, message) if not (await bot.db.settings.find_one({"_id": message.guild.id})).get('prefix') else commands.when_mentioned_or((await bot.db.settings.find_one({"_id": message.guild.id}))['prefix'])(bot, message)

bot = commands.Bot(command_prefix=get_prefix, intents=intents)
bot.remove_command("help")
bot.INFO = "\033[93m[INFO]\033[0m"
bot.OK = "\033[92m[OK]\033[0m"
bot.ERROR = "\033[1m\033[91m[ERROR]\033[0m\033[91m"
bot.ENDL = "\033[0m"
print("FinderBot is booting up...")
print(f"\033[96m-------- FinderBot {info.version} --------\033[0m")
print(bot.INFO, "Loading Extensions...")
for filename in os.listdir("./cogs"):
	if filename.endswith(".py"):
		bot.load_extension(f"cogs.{filename[:-3]}")
for filename in os.listdir("./cogs/Addons"):
	if filename.endswith("Addon.py"):
		bot.load_extension(f"cogs.Addons.{filename[:-3]}")
print(bot.OK, "Extentions Loaded successfully")
print(bot.INFO, "Attempting to connect to Discord API...")

@bot.event
async def on_ready():
	print(bot.OK, "Connection Success")
	print(bot.INFO, "Connecting to MangoDB Database")
	bot.db = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get('DB_URL'))[os.environ.get('DB_NAME')]
	guild_count = 0
	for _ in bot.guilds:
		guild_count = guild_count + 1
	await update_status(guild_count)
	print(bot.OK, f"FinderBot is up! at {datetime.datetime.now()} in {guild_count} guild{'s'[:guild_count^1]}.")
	print(bot.INFO,"Welcome to Macintosh")

@bot.event
async def on_guild_join(guild):
	guild_count = 0
	for _ in bot.guilds:
		guild_count+=1
	await update_status(guild_count)

@bot.event
async def on_guild_remove(guild):
	await bot.db.logs.delete_many({"_id": guild.id})
	await bot.db.reactrole.delete_many({"_id": guild.id})
	await bot.db.settings.delete_many({"_id": guild.id})
	await bot.db.addons.delete_many({"_id": guild.id})
	await bot.db.leveling.delete_many({"_id": guild.id})
	await bot.db.giveaways.delete_many({"_id": guild.id})
	await bot.db.economy.delete_many({"_id": guild.id})
	await bot.db.locales.delete_many({"_id": guild.id})
	guild_count = 0
	for _ in bot.guilds:
		guild_count+=1
	await update_status(guild_count)

@bot.event
async def on_message(msg):
	if msg.content == f"<@{bot.user.id}>" or msg.content == f"<@!{bot.user.id}>":
		await msg.channel.send(f"My prefix for this server is `{';' if not (await bot.db.settings.find_one({'_id': msg.guild.id})).get('prefix') else (await bot.db.settings.find_one({'_id': msg.guild.id}))['prefix']}`")
	await bot.process_commands(msg)


bot.run(os.environ.get('BOT_TOKEN'))