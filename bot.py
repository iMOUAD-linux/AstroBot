from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import os
# Minimal server to satisfy Koyeb health check
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')

def run_server():
    port = int(os.getenv("PORT", 8000))
    HTTPServer(('', port), Handler).serve_forever()

threading.Thread(target=run_server, daemon=True).start()

from http.server import BaseHTTPRequestHandler, HTTPServer

# --- Tiny Web Server so Koyeb Free Plan doesn't sleep ---
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_web():
    port = int(os.getenv("PORT", 8000))
    server = HTTPServer(("", port), Handler)
    server.serve_forever()

threading.Thread(target=run_web, daemon=True).start()

import threading, time, requests
def keep_alive():
    url = "https://" + os.getenv("KOYEB_APP_NAME") + ".koyeb.app"
    while True:
        try:
            requests.get(url)
        except:
            pass
        time.sleep(240)
threading.Thread(target=keep_alive, daemon=True).start()


import discord
from discord.ext import commands, tasks
import logging
from dotenv import load_dotenv
#import asyncio
import os
from datetime import timezone, datetime


load_dotenv()
token = os.getenv('TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='Astro ', intents=intents)
GUILD_ID = discord.Object(id=1422702521432014878)


#---------------------Slash Commands---------------------
@bot.tree.command(name="serverstats", description="Show server statistics", guild=GUILD_ID)
async def serverstats(interaction: discord.Interaction):
    guild = interaction.guild

    embed = discord.Embed(title=f"Server Stats: {guild.name}", color=discord.Color.blue())
    embed.add_field(name="Owner", value=str(guild.owner), inline=False)
    embed.add_field(name="Members", value=guild.member_count, inline=True)
    embed.add_field(name="Text Channels", value=len(guild.text_channels), inline=True)
    embed.add_field(name="Voice Channels", value=len(guild.voice_channels), inline=True)
    embed.add_field(name="Roles", value=len(guild.roles), inline=True)
    embed.set_footer(text=f"Created: {guild.created_at.strftime('%Y-%m-%d')}")

    await interaction.response.send_message(embed=embed)

#---------------------Slash Commands---------------------
@bot.tree.command(name="verifie", description="Show server statistics", guild=GUILD_ID)
async def serverstats(interaction: discord.Interaction):
    guild = interaction.guild

    embed = discord.Embed(title=f"Server Stats: {guild.name}", color=discord.Color.blue())
    embed.add_field(name="Owner", value=str(guild.owner), inline=False)
    embed.add_field(name="Members", value=guild.member_count, inline=True)
    embed.add_field(name="Text Channels", value=len(guild.text_channels), inline=True)
    embed.add_field(name="Voice Channels", value=len(guild.voice_channels), inline=True)
    embed.add_field(name="Roles", value=len(guild.roles), inline=True)
    embed.set_footer(text=f"Created: {guild.created_at.strftime('%Y-%m-%d')}")

    await interaction.response.send_message(embed=embed)



#---------------------Events---------------------

# READY
invite_cache = {}
@bot.event
async def on_ready():
    print(f"Done, {bot.user.name}")
    try:
        guild = discord.Object(id=1422702521432014878)
        synced = await bot.tree.sync(guild=guild)
        print(f"Synced {len(synced)} commands to guild {guild.id}")
    except Exception as e:
        print(f"Error syncing commands: {e}")
        # Load all invites for all guilds
    for guild in bot.guilds:
        invite_cache[guild.id] = await guild.invites()

# HELLO
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.lower() in ["hello", "hi", "hey"]:
        await message.channel.send(f"hi {message.author.mention}")

    await bot.process_commands(message)
#message
@bot.command()
@commands.has_permissions(administrator=True)
async def say(ctx, *, message: str):
    await ctx.message.delete()
    await ctx.send(message)
@bot.command()
@commands.has_permissions(administrator=True)
async def announce(ctx, *, message: str):
    await ctx.message.delete()
    await ctx.send(f"📢 ✦ @everyone : {message}")


#Verification
# === CONFIG ===
VERIFY_ROLE_ID = 1438555128725635174        # Verified role ID
UNVERIFIED_ROLE_ID = 1438548824867082323    # Unverified role ID
LOG_CHANNEL_ID = 1440328152969773097        # Logs channel ID
ALLOWED_ROLES = [
    1438551255554326609,   # Staff/Admin role 1
    1438551255554326609,   # Staff/Admin role 2
    1438551255554326609    # Staff/Admin role 3
]
@bot.command()
async def verifie(ctx, member: discord.Member):
    author = ctx.author
    # ----- Permission Check -----
    if not any(role.id in ALLOWED_ROLES for role in author.roles):
        return await ctx.reply("❌ You don't have permission to use this command.")
    # ----- Get roles -----
    verified_role = ctx.guild.get_role(VERIFY_ROLE_ID)
    unverified_role = ctx.guild.get_role(UNVERIFIED_ROLE_ID)
    if verified_role is None or unverified_role is None:
        return await ctx.reply("❌ One of the roles is missing. Check IDs.")
    # ----- Already verified? -----
    if verified_role in member.roles:
        return await ctx.reply(f"⚠️ {member.mention} is already verified.")
    # ----- Remove unverified -----
    if unverified_role in member.roles:
        await member.remove_roles(unverified_role)
    # ----- Add verified -----
    await member.add_roles(verified_role)
    await ctx.reply(f"✔ {member.mention} has been **verified successfully!**")
    # ----- LOG ACTION -----
    log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(
            title="🔰 Member Verified",
            color=discord.Color.green()
        )
        embed.add_field(name="👤 Verified Member", value=member.mention, inline=False)
        embed.add_field(name="🛡 Verified By", value=author.mention, inline=False)
        embed.add_field(name="📅 Date", value=f"<t:{int(ctx.message.created_at.timestamp())}:f>", inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)

        await log_channel.send(embed=embed)


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.lower() == "a":
        embed = discord.Embed(color=0x2f3136)
        embed.set_author(name=f"{message.author.name}'s Avatar")
        embed.set_image(url=message.author.display_avatar.url)

        await message.channel.send(embed=embed)

    await bot.process_commands(message)



#Welcome
@bot.event
async def on_member_join(member):
    guild = member.guild
    channel = member.guild.get_channel(1439637073966399603)
    # Fetch invites again
    new_invites = await guild.invites()
    old_invites = invite_cache[guild.id]
    inviter = None
    # Compare old invites with new invites
    found = False
    for old in old_invites:
        for new in new_invites:
            if old.code == new.code and new.uses > old.uses:
                inviter = old.inviter
                found = True
                break
        if found:
            break
    # Update cache
    invite_cache[guild.id] = new_invites
    if channel is None:
        return
    embed = discord.Embed(
        title="--Welcome To ⚔️«  𝗔𝗿𝗲𝗻𝗮 𝟮𝟭𝟮  »⚔️ community--",
        description=f"\nHey {member.mention}! Welcome to **{member.guild.name}** 🎊\n\nWe’re happy to have you here! and We wish you a wonderful adventure, Also forming beautiful long-lasting friendships.",
        color=0x8B0000
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_image(url="https://i.ibb.co/5xnX7RKR/212-8-Copy.jpg")
    embed.set_footer(text=f"Member #{member.guild.member_count} - 𝕸 𝕺 𝖀 𝕬 𝕯's Style")
    from datetime import timezone
    join_date = member.joined_at.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    embed.add_field(name="✚ Joined On", value=join_date, inline=False)
    # Add inviter info
    if inviter:
        embed.add_field(
            name="✔ Invited By",
            value=f"{inviter.mention}",
            inline=False
        )
    else:
        embed.add_field(
            name="✔✚ Invited By",
            value="Unknown Member :(",
            inline=False
        )
    await channel.send(content=f"✦ **Everyone welcome {member.mention}!**", embed=embed)


# Booster

import io
import aiohttp
from PIL import Image, ImageDraw, ImageFont

BACKGROUND_URL = "https://i.ibb.co/VW52nqdk/Aren-1.png"
BOOST_ICON_URL = "https://cdn.iconscout.com/icon/free/png-256/free-level-3-discord-boost-icon-svg-download-png-5582634.png"

async def generate_booster_card(display_name: str, booster: discord.Member, boosts: int = 1):
    # --- Download background ---
    async with aiohttp.ClientSession() as session:
        async with session.get(BACKGROUND_URL) as resp:
            bg_data = await resp.read()

        async with session.get(BOOST_ICON_URL) as resp:
            boost_icon_data = await resp.read()

        async with session.get(str(booster.display_avatar.url)) as resp:
            avatar_data = await resp.read()

    bg = Image.open(io.BytesIO(bg_data)).convert("RGBA")
    boost_icon = Image.open(io.BytesIO(boost_icon_data)).convert("RGBA")
    avatar = Image.open(io.BytesIO(avatar_data)).convert("RGBA")

    # --- Resize images ---
    boost_icon = boost_icon.resize((140, 140))
    avatar = avatar.resize((230, 230))

    # --- Circular avatar ---
    mask = Image.new("L", (230, 230), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 230, 230), fill=255)
    avatar_circle = Image.new("RGBA", (230, 230))
    avatar_circle.paste(avatar, (0, 0), mask)

    draw = ImageDraw.Draw(bg)

    # --- Fonts ---
    title_font = ImageFont.truetype("arial.ttf", 60)
    medium_font = ImageFont.truetype("arial.ttf", 45)
    small_font = ImageFont.truetype("arial.ttf", 38)

    # --- Text ---
    draw.text((400, 40), "ARENA BOOSTERS", fill="white", font=title_font, anchor="mm")
    draw.text((400, 300), "The server was successfully boosted By", fill="white", font=medium_font, anchor="mm")
    draw.text((400, 360), f"“{display_name}”", fill="white", font=title_font, anchor="mm")
    draw.text((400, 500), f"+ “{boosts}” The Number Of Boosts", fill="white", font=medium_font, anchor="mm")
    draw.text((400, 690), "You can claim now 3000xp and @Bourgeois role, thank you for boosting",
              fill="white", font=small_font, anchor="mm")

    # --- Place images ---
    bg.paste(avatar_circle, (285, 120), avatar_circle)
    bg.paste(boost_icon, (330, 380), boost_icon)
    # --- Output as PNG ---
    buffer = io.BytesIO()
    bg.save(buffer, "PNG")
    buffer.seek(0)
    return discord.File(buffer, filename="booster_card.png")

@bot.event
async def on_member_update(before, after):
    # Detect new booster
    if before.premium_since is None and after.premium_since is not None:

        booster_log_channel = after.guild.get_channel(1436708798227025970)

        from booster_card import generate_booster_card  # or skip if in same file

        file = await generate_booster_card(
            display_name=after.display_name,
            booster=after,
            boosts=len(after.guild.premium_subscribers)
        )
        await booster_log_channel.send(file=file)



#---------------------Bot commands---------------------


# =============================
#   Daily Stats Task
# =============================
STATS_CHANNEL_ID = 1441146001250582558  # Channel where stats are posted daily
@tasks.loop(hours=24)
async def send_daily_stats():
    await bot.wait_until_ready()
    channel = bot.get_channel(STATS_CHANNEL_ID)
    guild = channel.guild
    # ---- COUNT MEMBERS ----
    total_members = guild.member_count
    online = sum(1 for m in guild.members if m.status == discord.Status.online)
    idle = sum(1 for m in guild.members if m.status == discord.Status.idle)
    dnd = sum(1 for m in guild.members if m.status == discord.Status.dnd)
    offline = sum(1 for m in guild.members if m.status == discord.Status.offline)
    # ---- COUNT BOTS ----
    bot_count = sum(1 for m in guild.members if m.bot)
    # ---- CHANNEL COUNTS ----
    text_channels = len(guild.text_channels)
    voice_channels = len(guild.voice_channels)
    categories = len(guild.categories)
    # ---- SERVER AGE ----
    age_days = (datetime.now(timezone.utc) - guild.created_at).days
    # ---- BOOST INFO ----
    boosts = guild.premium_subscription_count
    boost_level = guild.premium_tier
    # ---- OWNER ----
    owner = guild.owner
    # =============================
    #       MODERN EMBED
    # =============================
    embed = discord.Embed(
        title="**Daily Server Status Report**",
        description=f"Daily stats generated for **{guild.name}**",
        color=0xFFFFFF,
        timestamp=datetime.now(timezone.utc)
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(
        name="👥・Members",
        value=(
            f"**Total:** {total_members}\n"
            f"🟢 Online: {online}\n"
            f"🟡 Idle: {idle}\n"
            f"🔴 DND: {dnd}\n"
            f"⚫ Offline: {offline}"
        ),
        inline=True
    )
    embed.add_field(
        name="➤ 🤖・Bots",
        value=f"{bot_count}",
        inline=True
    )
    embed.add_field(
        name="➤ 📂・Channels",
        value=(
            f" 💬 Text: {text_channels}\n"
            f" 🔊 Voice: {voice_channels}\n"
            f" 📁 Categories: {categories}"
        ),
        inline=False
    )
    embed.add_field(
        name="➤ 🔮・Boosts",
        value=(
            f"Boosts: **{boosts}**\n"
            f"Level: **{boost_level}**"
        ),
        inline=True
    )
    embed.add_field(
        name="➤ 📅・Server Age",
        value=f"{age_days} days old",
        inline=False
    )
    embed.set_footer(text="Arena 212 • Daily System Report • 𝕸 𝕺 𝖀 𝕬 𝕯's Style")
    await channel.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def startstats(ctx):
    send_daily_stats.start()
    await ctx.reply("📊 Daily server stats have been **activated**!")



# GameRoles
channel_id = 1441172659714134151   # Channel to send the embed
log_channel_id = 1438590055206748161  # (optional) logs channel
game_roles = [
    {"name": "<:VALO:1441524219677638838>",    "role_id": 1438565538132529396},
    {"name": "<:CS:1441524217639079949>", "role_id": 1438565647176044567},
    {"name": "<:GTA:1441524213793161216>",    "role_id": 1438565733616320542},
    {"name": "<:CHESS:1441524800932675725>",        "role_id": 1438565828143353947},
    {"name": "<:DS:1441524184969642137>",    "role_id": 1438566033811046604},
    {"name": "<:RACING:1441524110936113204>",    "role_id": 1438565921240387675},
    {"name": "<:PES:1441524114958454940>",    "role_id": 1438566565732679802},
    {"name": "<:Mc:1441524225340080298>",    "role_id": 1438566111250485390},
    {"name": "<:AMONGUS:1441524118166966282>",    "role_id": 1438566163587272725},
    {"name": "<:PM:1441524221653159996>",    "role_id": 1438566405325721610},
    {"name": "<:FF:1441524223305580624>",    "role_id": 1438566302343102484},
    {"name": "<:ROBLOX:1441524112681078786>",    "role_id": 1438566220403314768},
    {"name": "<:COD:1441524143940964485>",    "role_id": 1438566481507127498},
    {"name": "<:FC:1441524151872393417>",    "role_id": 1438566633038676068},
    {"name": "<:REPO:1441524141416124578>",    "role_id": 1438566961054351564},

]
class GameRoleButton(discord.ui.Button):
    def __init__(self, label, role_id, emoji):
        super().__init__(label=label, emoji=emoji, style=discord.ButtonStyle.secondary)
        self.role_id = role_id
    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        if role is None:
            return await interaction.response.send_message(
                "❌ Role not found.", ephemeral=True
            )
        user = interaction.user
        # TOGGLE SYSTEM
        if role in user.roles:
            # REMOVE IF USER ALREADY HAS IT
            await user.remove_roles(role)
            msg = f"❎ Removed role **{role.name}**"
        else:
            # GIVE IF USER DOES NOT HAVE IT
            await user.add_roles(role)
            msg = f"✅ Added role **{role.name}**"
        # Send small private message
        await interaction.response.send_message(msg, ephemeral=True)
        # Log system
        log_channel = interaction.guild.get_channel(log_channel_id)
        if log_channel:
            await log_channel.send(f"**{user}** → {msg}")
class GameRoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for game in game_roles:
            self.add_item(GameRoleButton(label="", emoji=game["name"], role_id=game["role_id"]))
@bot.command()
@commands.has_permissions(administrator=True)
async def gameroles(ctx):

    embed = discord.Embed(
        title="🎮 Choose Your Game Roles",
        description=(
            "Click on the buttons below to claim or remove a role.\n\n"
            "**Choose the games you play!**"
        ),
        color=0xFFFFFF
    )
    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
    # List roles in embed
    text = ""
    for game in game_roles:
        role = ctx.guild.get_role(game["role_id"])
        text += f"{game['name']} → {role.mention if role else '`Unknown role`'}\n"
    embed.add_field(name="Available Game Roles", value=text, inline=False)
    await ctx.send(embed=embed, view=GameRoleView())




# AVATARS
import json
import os
from datetime import datetime, timedelta
# 🟦 SET THIS — The channel where +givexp commands will be sent
XP_CHANNEL_ID = 1437487204019601519   # <── replace
XP_VALUES = {
    "1️⃣": 10,   # 1 star
    "2️⃣": 20,   # 2 stars
    "3️⃣": 30,   # 3 stars
    "4️⃣": 40,   # 4 stars
    "5️⃣": 50,   # 5 stars
}
ALLOWED_REACTIONS = list(XP_VALUES.keys())
if not os.path.exists("avatar_data.json"):
    with open("avatar_data.json", "w") as f:
        json.dump({"posts": {}, "cooldowns": {}}, f, indent=4)
# Load & Save
def load_data():
    with open("avatar_data.json", "r") as f:
        return json.load(f)
def save_data(data):
    with open("avatar_data.json", "w") as f:
        json.dump(data, f, indent=4)
#  Trigger: "a" or "avatar"
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    content = message.content.lower().strip()
    if content in ["a", "avatar"]:
        embed = discord.Embed(
            title=f"{message.author.display_name}'s Avatar",
            description="Rating this avatar will earn you XP",
            color=0xFFFFFF
        )
        embed.add_field(name="1️⃣", value="**10xp**", inline=False)
        embed.add_field(name="2️⃣", value="**20xp**", inline=True)
        embed.add_field(name="3️⃣", value="**30xp**", inline=False)
        embed.add_field(name="4️⃣", value="**40xp**", inline=True)
        embed.add_field(name="5️⃣", value="**50xp**", inline=False)
        embed.set_image(url=message.author.display_avatar.url)
        embed.set_thumbnail(url=message.author.display_avatar.url)
        embed.set_footer(text="✦ 𝕸 𝕺 𝖀 𝕬 𝕯'Style")
        avatar_msg = await message.channel.send(embed=embed)
        # Add 1★ → 5★ reactions
        for reaction in ALLOWED_REACTIONS:
            await avatar_msg.add_reaction(reaction)
        # Save message → owner
        data = load_data()
        data["posts"][str(avatar_msg.id)] = {
            "author": message.author.id,
            "timestamp": datetime.utcnow().isoformat()
        }
        save_data(data)
    await bot.process_commands(message)
#  Reaction Handler
@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return
    msg = reaction.message
    data = load_data()
    # Not an avatar message → ignore
    if str(msg.id) not in data["posts"]:
        return
    post_info = data["posts"][str(msg.id)]
    owner_id = post_info["author"]
    # Invalid reaction
    if reaction.emoji not in ALLOWED_REACTIONS:
        await reaction.remove(user)
        return
    # They cannot react to themselves
    if user.id == owner_id:
        await reaction.remove(user)
        return
    # Anti-spam: 1 reaction per week per user-pair
    pair_key = f"{owner_id}:{user.id}"
    if pair_key in data["cooldowns"]:
        last_time = datetime.fromisoformat(data["cooldowns"][pair_key])
        if datetime.utcnow() < last_time + timedelta(days=7):
            return  # still on cooldown
    # XP amount
    xp_amount = XP_VALUES[reaction.emoji]
    owner = msg.guild.get_member(owner_id)
    # 🟦 SEND XP COMMAND TO SPECIFIC CHANNEL
    xp_channel = bot.get_channel(XP_CHANNEL_ID)
    if xp_channel is not None:
        await xp_channel.send(f"+givexp {owner.mention} {xp_amount}")
    # Update cooldown
    data["cooldowns"][pair_key] = datetime.utcnow().isoformat()
    save_data(data)

bot.run(token)
