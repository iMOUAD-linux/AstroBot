import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import webserver

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='Astro ', intents=intents)

@bot.event
async def on_ready():
    print(f"Done, {bot.user.name}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    badWords = ('w9', 'qhaab', 'zaml')
    for badWord in badWords:
        if badWord in message.content.lower():
            await message.delete()
            await message.channel.send(f"{message.author.mention} - 🤫 Dont say that again!")

    await bot.process_commands(message)


@bot.command()
async def salam(ctx):
    await ctx.send(f"salam o3alaykom {ctx.author.mention}!")

webserver.keep_alive()
bot.run(token, log_handler=handler, log_level=logging.DEBUG)


