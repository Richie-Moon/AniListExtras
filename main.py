from os import environ
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import pymongo
import anilist

load_dotenv()
TOKEN = environ["TOKEN"]

db_client = pymongo.MongoClient(f"mongodb+srv://richiemoon:{environ['PASSWORD']}@anilistextras.fxhup5u.mongodb.net/?retryWrites=true&w=majority")


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=".", intents=discord.Intents.all(), application_id=1110130569326641204)

    async def setup_hook(self) -> None:
        for command in c:
            bot.tree.add_command(command)

    async def on_ready(self):
        print(f"Logged in as {self.user}")


bot = Bot()


@bot.command()
async def sync(ctx):
    synced = await ctx.bot.tree.sync()
    for c in synced:
        print(c)
    await ctx.send(f"Synced {len(synced)} commands.")


@app_commands.command(description="Displays client latency.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"{round(bot.latency * 1000, 1)}ms.")


@app_commands.command(description="Gets your Plan to Rewatch list. ")
async def rw(interaction: discord.Interaction):
    db = db_client["rewatch"]
    collection = db[str(interaction.user.id)]

    embed = discord.Embed(title="Plan to Rewatch", colour=discord.Color.from_rgb(147, 112, 219), timestamp=interaction.created_at)
    embed.set_author(name=interaction.user.name)
    text = ""

    for anime in collection.find():
        if anime["name_english"] is None:
            text += f"[{anime['name_romaji']}]({anime['link']})\n"
        else:
            text += f"[{anime['name_romaji']} ({anime['name_english']})]({anime['link']})\n"

    embed.add_field(name="", value=text)

    await interaction.response.send_message(embed=embed)


@app_commands.command(description="Add an anime to your plan to rewatch list. ")
async def add_rw(interaction: discord.Interaction, name: str, anime_id: int = None):

    anime = anilist.get_multiple(name=name, anime_id=anime_id)

    db = db_client["rewatch"]
    collection = db[str(interaction.user.id)]

    print(anime)

c = [ping, rw, add_rw]

bot.run(TOKEN)
