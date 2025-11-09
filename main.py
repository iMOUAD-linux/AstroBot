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



#    Events

#    COMMANDS
#Server Stats
@bot.command()
async def stats(ctx):
    guild = ctx.guild

    name = guild.name
    owner = guild.owner
    member_count = guild.member_count
    text_channels = len(guild.text_channels)
    voice_channels = len(guild.voice_channels)
    created_at = guild.created_at.strftime("%Y-%m-%d")

    embed = discord.Embed(title=f"Server Stats: {name}", color=discord.Color.blue())
    embed.add_field(name="Owner", value=str(owner), inline=False)
    embed.add_field(name="Members", value=member_count, inline=True)
    embed.add_field(name="Text Channels", value=text_channels, inline=True)
    embed.add_field(name="Voice Channels", value=voice_channels, inline=True)
    embed.set_footer(text=f"Created at: {created_at}")

    await ctx.send(embed=embed)

webserver.keep_alive()
bot.run(token, log_handler=handler, log_level=logging.DEBUG)


