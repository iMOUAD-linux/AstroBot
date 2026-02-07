

import discord
from discord.ext import commands, tasks
from discord import app_commands
from dotenv import load_dotenv
import json
import os
import time
import asyncio

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

RANKS = {
    "Bronze": 0,
    "Silver": 1000,
    "Gold": 3000,
    "Diamond": 10000,
    "Aura": 100000
}
ROLE_IDS = {
    "Bronze":    1438574028175577200,
    "Silver":    1438573344780718274,
    "Gold":      1438332003131985960,
    "Diamond":   1438565410109784124,
    "Aura":      1438565618235216066
}

# ------------------------------
# Load or create XP/Rank storage
# ------------------------------
if not os.path.exists("ranks.json"):
    with open("ranks.json", "w") as f:
        json.dump({}, f)

def load_ranks():
    with open("ranks.json", "r") as f:
        return json.load(f)

def save_ranks(data):
    with open("ranks.json", "w") as f:
        json.dump(data, f, indent=4)

# ------------------------------
# Determine rank from XP
# ------------------------------
def get_rank_from_xp(xp: int):
    current_rank = "Bronze"
    for rank, req_xp in RANKS.items():
        if xp >= req_xp:
            current_rank = rank
    return current_rank

# ------------------------------
# Bot Setup
# ------------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True
intents.messages = True


bot = commands.Bot(command_prefix="+", intents=intents, partials=["MESSAGE", "CHANNEL", "REACTION"] )
GUILD_ID = discord.Object(id=1422702521432014878)


# ------------------------------
# Update member's rank role
# ------------------------------
async def update_member_rank(member, xp):
    # --- Prevent owners from receiving ANY rank ---
    if any(role.id == 1438551255554326609 for role in member.roles):
        # Save XP only, force rank = "Owner"
        data = load_ranks()
        uid = str(member.id)
        data[uid] = {"xp": xp, "rank": "Owner"}
        save_ranks(data)
        return  # STOP here → no roles changed
    # Normal rank processing continues here
    data = load_ranks()
    uid = str(member.id)
    guild = member.guild
    new_rank = get_rank_from_xp(xp)
    old_rank = data.get(uid, {}).get("rank", "Bronze")
    # Rank changed → update roles
    if new_rank != old_rank:
        # Remove old rank roles
        for rank_name in ROLE_IDS.keys():
            role_id = ROLE_IDS[rank_name]
            role = guild.get_role(role_id)
            if role and role in member.roles:
                await member.remove_roles(role)
        # Add new role
        new_role = guild.get_role(ROLE_IDS[new_rank])
        if new_role:
            await member.add_roles(new_role)
        print(f"[RANK UP] {member} → {new_rank}")
    # Save data
    data[uid] = {"xp": xp, "rank": new_rank}
    save_ranks(data)

# -----------------LeaderBoard------------------------
import datetime
# Channel where the leaderboard is sent DAILY
LEADERBOARD_CHANNEL_ID = 1447963554618544271  # <-- PUT YOUR CHANNEL ID HERE
# Background task for daily leaderboard
async def daily_leaderboard_loop():
    await bot.wait_until_ready()

    while not bot.is_closed():
        now = datetime.datetime.now()
        # Next midnight
        next_run = (now + datetime.timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        wait_seconds = (next_run - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        # When time hits → send leaderboard
        try:
            channel = bot.get_channel(LEADERBOARD_CHANNEL_ID)
            if channel:
                await send_leaderboard(channel)
        except Exception as e:
            print("[ERROR sending leaderboard]", e)



import unicodedata
def text_width(text: str) -> int:
    """Calculate how many monospace cells a string visually occupies in Discord."""
    width = 0
    for char in text:
        ea = unicodedata.east_asian_width(char)
        if ea in ("W", "F"):   # Wide/Fullwidth characters take 2 cells
            width += 2
        else:
            width += 1
    return width
def pad_to_width(text: str, target_width: int) -> str:
    """Pad using real display width."""
    current = text_width(text)
    return text + " " * max(0, (target_width - current))
async def send_leaderboard(channel):
    guild = channel.guild
    data = load_ranks()
    # Sort & take top 10
    top10 = sorted(data.items(), key=lambda x: x[1]["xp"], reverse=True)[:10]
    embed = discord.Embed(
        title="🏆 Daily XP Leaderboard",
        description="Top 10 Members (XP Ranking)",
        color=0xf1c40f
    )
    header_cols = ["#", "Name", "XP", "Rank", "Role"]
    rows = []
    for position, (uid, info) in enumerate(top10, start=1):
        xp = info.get("xp", 0)
        rank = info.get("rank", "Bronze")
        member = guild.get_member(int(uid))
        if member:
            name = member.name
            role = (
                member.top_role.name
                if member.top_role != guild.default_role
                else "None"
            )
        else:
            name = "Unknown"
            role = "Unknown"
        # limit name length visually
        if text_width(name) > 18:
            name = name[:15] + "…"
        rows.append([str(position), name, str(xp), rank, role])
    # compute column widths using visual width
    col_widths = []
    for col in range(len(header_cols)):
        max_w = text_width(header_cols[col])
        for row in rows:
            max_w = max(max_w, text_width(row[col]))
        col_widths.append(max_w)
    # Build table
    table = "```\n"
    header_line = " | ".join(
        pad_to_width(header_cols[i], col_widths[i]) for i in range(len(header_cols))
    )
    table += header_line + "\n"
    table += "-+-".join("-" * w for w in col_widths) + "\n"
    for row in rows:
        line = " | ".join(
            pad_to_width(row[i], col_widths[i]) for i in range(len(row))
        )
        table += line + "\n"
    table += "```"
    embed.add_field(name="Leaderboard", value=table, inline=False)
    embed.set_footer(text="ArenaLeveling Leaderboard • 𝕸 𝕺 𝖀 𝕬 𝕯's Style")
    await channel.send(embed=embed)


# ------------------------------
# On Ready
# ------------------------------
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Developed by : M O U A D"))
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

    # Start the daily leaderboard task
    bot.loop.create_task(daily_leaderboard_loop())


#LeaderBoardCommand
@bot.command(name="leaderboard")
async def leaderboard_cmd(ctx):
    await send_leaderboard(ctx.channel)

@bot.tree.command(name="xp", description="Show the XP and Rank of a member.")
async def xp(interaction: discord.Interaction, member: discord.Member = None):
    # Default: show own xp
    if member is None:
        member = interaction.user
    data = load_ranks()
    uid = str(member.id)
    if uid not in data:
        xp = 0
    else:
        xp = data[uid]["xp"]
    rank = get_rank_from_xp(xp)
    embed = discord.Embed(
        title=f"{member.name}'s XP",
        description=f"**Rank:** {rank}\n**XP:** {xp}",
        color=0xfffff
    )
    embed.set_thumbnail(url=member.display_avatar.url)

    await interaction.response.send_message(embed=embed)


#Ranks Event
@bot.event
async def on_member_join(member):
    # Give Bronze role
    bronze_role = member.guild.get_role(ROLE_IDS["Bronze"])
    if bronze_role:
        await member.add_roles(bronze_role)
    # Create XP entry for the new member
    data = load_ranks()
    uid = str(member.id)
    data[uid] = {"xp": 0, "rank": "Bronze"}
    save_ranks(data)
@bot.event
async def update_member_rank(member, xp):
    guild = member.guild
    data = load_ranks()
    uid = str(member.id)
    new_rank = get_rank_from_xp(xp)
    old_rank = data.get(uid, {}).get("rank", "Bronze")
    if new_rank != old_rank:
        # Remove all rank roles
        for rname, rid in ROLE_IDS.items():
            role = guild.get_role(rid)
            if role and role in member.roles:
                await member.remove_roles(role)
        # Give new role
        new_role = guild.get_role(ROLE_IDS[new_rank])
        if new_role:
            await member.add_roles(new_role)
        print(f"[RANK UP] {member} → {new_rank}")
    # Special 1000 XP role
    reward_role = member.guild.get_role(1438574168269525105)
    if xp >= 1000 and reward_role and reward_role not in member.roles:
        await member.add_roles(reward_role)
        await member.remove_roles(member.guild.get_role(1438581142394503189))

    # Save
    data[uid] = {"xp": xp, "rank": new_rank}
    save_ranks(data)


# ------------------------------
# Placeholder for XP update
# (You will tell me how you want XP added)
# ------------------------------
async def add_xp(member, amount):
    data = load_ranks()
    uid = str(member.id)
    # Create if not exists
    if uid not in data:
        data[uid] = {"xp": 0, "rank": "Bronze"}
    # Add XP
    new_xp = data[uid]["xp"] + amount
    # Save + update role
    await update_member_rank(member, new_xp)


# ------------------------------
# Example message event (no XP yet)
# XP system will be added when you want
# ------------------------------
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    # Later → add XP here
    # await add_xp(message.author, 5)
    await bot.process_commands(message)

# ------------------------------
# Admin Command: Give XP
# ------------------------------
@bot.command()
@commands.has_permissions(administrator=True)
async def addxp(ctx, member: discord.Member, amount: int):
    await add_xp(member, amount)
    data = load_ranks()
    uid = str(member.id)
    new_xp = data[uid]["xp"]
    await ctx.send(f"✚ Added **{amount} XP** to **{member.display_name}**  (now: **{new_xp} XP**)")
@addxp.error
async def addxp_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    else:
        await ctx.send("❌ Error: Invalid syntax. Use: `+givexp @user <amount>`")

@bot.command(name="removexp")
@commands.has_permissions(administrator=True)
async def removexp(ctx, member: discord.Member, amount: int):
    data = load_ranks()
    uid = str(member.id)
    if uid not in data:
        data[uid] = {"xp": 0}
    # Remove XP (cannot go below 0)
    data[uid]["xp"] = max(0, data[uid]["xp"] - amount)
    new_xp = data[uid]["xp"]
    save_ranks(data)
    # Fix roles & rank
    await update_member_rank(member, new_xp)
    await ctx.send(
        f"✘ Removed **{amount} XP** from **{member.mention}** (now: **{new_xp} XP**)"
    )


@bot.command(name="xp")
async def xp(ctx, member: discord.Member = None):
    # If no member is provided → show XP of the author
    if member is None:
        member = ctx.author
    data = load_ranks()
    uid = str(member.id)
    xp = data.get(uid, {}).get("xp", 0)
    rank = get_rank_from_xp(xp)
    embed = discord.Embed(
        title=f"{member.display_name}'s XP",
        description=f"**Rank:** {rank}\n**XP:** {xp}",
        color=0xFFFFFF
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot:  # only react to bot messages
        content = message.content.lower()
        if content.startswith("+givexp"):
            parts = content.split()
            if len(parts) != 3:
                return
            raw = parts[1]
            # If it's a mention like <@123> or <@!123>
            if raw.startswith("<@") and raw.endswith(">"):
                raw = raw.replace("<@", "").replace("<@!", "").replace(">", "")
            user_id = int(raw)
            amount = int(parts[2])
            member = message.guild.get_member(user_id)
            data = load_ranks()
            uid = str(member.id)
            new_xp = data[uid]["xp"]
            if member:
                xp = await add_xp(member, amount)
                await message.channel.send(
                    f"✚ Added **{amount} XP** to **{member.display_name}**  (now: **{new_xp} XP**)"
                )
        if content.startswith("+removexp"):
            parts = content.split()
            if len(parts) != 3:
                return
            raw = parts[1]
            # If it's a mention like <@123> or <@!123>
            if raw.startswith("<@") and raw.endswith(">"):
                raw = raw.replace("<@", "").replace("<@!", "").replace(">", "")
            user_id = int(raw)
            amount = int(parts[2])
            member = message.guild.get_member(user_id)
            if member:
                xp = await removexp(member, amount)
                await message.channel.send(
                    f"✘ Removed **{amount} XP** from **{member.mention}** (now: **{new_xp} XP**)"
                )
    # don’t forget to process other commands
    await bot.process_commands(message)


#-----------------------・Tasks・-----------------------#

# A C T I V I T I E S

last_message_time = {}
COOLDOWN_SECONDS = 10
# 1) Normal message = +10 XP (with cooldown)
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    user_id = message.author.id
    now = time.time()
    if user_id in last_message_time:
        if now - last_message_time[user_id] < COOLDOWN_SECONDS:
            return
    last_message_time[user_id] = now
    await add_xp(message.author, 10)
    await bot.process_commands(message)
# 2) Reaction added = +5 XP
@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return
    await add_xp(user, 5)
# 3) Enter voice channel = +15 XP
@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        await add_xp(member, 15)

# ---------------------------------------------------------------------
# 4) Member invited using your invite link = +300 XP
# ---------------------------------------------------------------------
invite_cache = {}
async def update_invites():
    for guild in bot.guilds:
        invite_cache[guild.id] = await guild.invites()
@bot.event
async def on_ready():
    await update_invites()
    print(f"[ONLINE] Logged in as {bot.user}")
@bot.event
async def on_member_join(member):
    guild = member.guild
    old_invites = invite_cache.get(guild.id, [])
    new_invites = await guild.invites()
    for new_inv in new_invites:
        for old_inv in old_invites:
            if new_inv.code == old_inv.code and new_inv.uses > old_inv.uses:
                inviter = new_inv.inviter
                if inviter and not inviter.bot:
                    await add_xp(inviter, 300)
                break
    invite_cache[guild.id] = new_invites
# ---------------------------------------------------------------------
# 5) Create Temp Voice = +20 XP
# ---------------------------------------------------------------------
@bot.event
async def on_voice_state_update(member, before, after):
    # user joins a voice channel
    if before.channel is None and after.channel is not None:
        # check if it's the specific voice channel
        if after.channel.id == 1437496385435078799:
            data = load_ranks()
            uid = str(member.id)
            if uid not in data:
                data[uid] = {"xp": 0}
            data[uid]["xp"] += 20  # give XP
            save_ranks(data)
# ---------------------------------------------------------------------
# 5) Server Boost = +10,000 XP
# ---------------------------------------------------------------------
@bot.event
async def on_member_update(before, after):
    # boost added
    if before.premium_since is None and after.premium_since is not None:
        await add_xp(after, 3000)


bot.run(token)
