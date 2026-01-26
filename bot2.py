
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from discord.ui import View, button

#import main.py

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN_TEMP")

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)

# Track temp channels: {channel_id: owner_id}
temp_channels = {}

# Channel name where users join to create temp voice
CREATE_CHANNEL_NAME = "☎️│Join To Create"
ChannelsGamesNames = [
    "🌳 Minecraft",
    "🆘 ඩmongUs",
    "🔲 RobLox",
    "☠️ FreeFire",
    "🪖 Pubg Mobile",
    "☣️ COD Mobile",
    "🏆 eFootBall",
    "⚽ EA FC",
    "⚜️ Valorant",
    "🔪 CounterStrike",
    "🦺 GTA",
    "♟️ Chess",
    "🏁 SimRacing",
    "🏴‍☠️ DarkSouls Games",
    "🗝️ Completion Games",
]
ChannelsGamesID = [
    1438216357463457934,
    1438238408102379704,
    1438239465540817007,
    1438247916333436998,
    1438251990768549948,
    1438253372644790362,
    1438260543549870090,
    1438261044173738074,
    1438254655401361599,
    1438255592262336634,
    1438250679750758500,
    1438259405786452079,
    1438256507501285498,
    1438257604219502592,
    1438258713986076893,
]
TEMP_CHANNELS_Games = {}

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

class TempVoiceControl(discord.ui.View):
    def __init__(self, owner_id):
        super().__init__(timeout=None)
        self.owner_id = owner_id

    # 🔒 Lock / Unlock
    @button(emoji="<:verrouiller:1439630169726783529>", style=discord.ButtonStyle.secondary)
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message("❌ Only the channel owner can use this.", ephemeral=True)
        vc = interaction.user.voice.channel if interaction.user.voice else None
        if vc:
            await vc.set_permissions(interaction.guild.default_role, connect=False)
            await interaction.response.send_message("<:verrouiller:1439630169726783529> Channel locked.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ You're not in your voice channel.", ephemeral=True)

    @button(emoji="<:symboledeverrouillage:1439630167994535998>", style=discord.ButtonStyle.secondary)
    async def unlock(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message("❌ Only the channel owner can use this.", ephemeral=True)
        vc = interaction.user.voice.channel if interaction.user.voice else None
        if vc:
            await vc.set_permissions(interaction.guild.default_role, connect=True)
            await interaction.response.send_message("<:symboledeverrouillage:1439630167994535998> Channel unlocked.", ephemeral=True)

    # 🙈 Hide / 👁 Show
    @button(emoji="<:visible1:1439630164802932838>", style=discord.ButtonStyle.secondary)
    async def hide(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message("❌ Only the owner can hide.", ephemeral=True)
        vc = interaction.user.voice.channel if interaction.user.voice else None
        if vc:
            await vc.set_permissions(interaction.guild.default_role, view_channel=False)
            await interaction.response.send_message("<:visible1:1439630164802932838> Channel hidden.", ephemeral=True)

    @button(emoji="<:visible:1439630166560080084>", style=discord.ButtonStyle.secondary)
    async def show(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message("❌ Only the owner can show.", ephemeral=True)
        vc = interaction.user.voice.channel if interaction.user.voice else None
        if vc:
            await vc.set_permissions(interaction.guild.default_role, view_channel=True)
            await interaction.response.send_message("<:visible:1439630166560080084> Channel visible.", ephemeral=True)

    # ✏️ Rename
    @button(emoji="<:editer:1439630171446575275>", style=discord.ButtonStyle.secondary)
    async def rename(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message("❌ Only the owner can rename.", ephemeral=True)
        modal = RenameModal()
        await interaction.response.send_modal(modal)

    # 🚪 Limit Members
    @button(emoji="<:pasdarret:1439630163057967236>", style=discord.ButtonStyle.secondary)
    async def limit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message("❌ Only the owner can limit members.", ephemeral=True)
        modal = LimitModal()
        await interaction.response.send_modal(modal)

    # ➕ Invite Member
    @button(emoji="<:plussymbolenoir:1439630161745150083>", style=discord.ButtonStyle.secondary)
    async def invite(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message("❌ Only the owner can invite.", ephemeral=True)
        await interaction.response.send_message("Mention the user to invite:", ephemeral=True)

    # ❌ Reject Member
    @button(emoji="<:signemoins:1439630160298250260>", style=discord.ButtonStyle.secondary)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message("❌ Only the owner can reject members.", ephemeral=True)
        await interaction.response.send_message("Mention the user to remove from channel:", ephemeral=True)

    # 🎯 Claim Ownership
    @button(emoji="<:couronne:1439630158549094521>", style=discord.ButtonStyle.secondary)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.voice and interaction.user.voice.channel:
            vc = interaction.user.voice.channel
            self.owner_id = interaction.user.id
            await interaction.response.send_message("<:couronne:1439630158549094521> You are now the owner of this temp voice!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Join a voice first.", ephemeral=True)

    # 🔐 Unlock for Specific Member
    @button(emoji="<:faireundon:1439630156787486772>", style=discord.ButtonStyle.secondary)
    async def unlock_for_one(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message("❌ Only the owner can use this.", ephemeral=True)
        await interaction.response.send_message("Mention the user to unlock for:", ephemeral=True)


class RenameModal(discord.ui.Modal, title="Rename Voice Channel"):
    new_name = discord.ui.TextInput(label="New name", placeholder="Enter the new channel name")

    async def on_submit(self, interaction: discord.Interaction):
        vc = interaction.user.voice.channel if interaction.user.voice else None
        if vc:
            await vc.edit(name=self.new_name.value)
            await interaction.response.send_message(f"✅ Renamed to **{self.new_name.value}**", ephemeral=True)


class LimitModal(discord.ui.Modal, title="Set Member Limit"):
    limit = discord.ui.TextInput(label="Member limit", placeholder="e.g. 5", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        vc = interaction.user.voice.channel if interaction.user.voice else None
        if vc:
            await vc.edit(user_limit=int(self.limit.value))
            await interaction.response.send_message(f"🚪 Limit set to {self.limit.value} members.", ephemeral=True)


# Event to send the embed when a temp voice is created
async def send_temp_voice_panel(channel: discord.VoiceChannel, text_channel: discord.TextChannel, owner: discord.Member):
    embed = discord.Embed(
        title="⏭︎ 𝐂𝐨𝐧𝐭𝐫𝐨𝐥 𝐲𝐨𝐮𝐫 𝐯𝐨𝐢𝐜𝐞 𝐜𝐡𝐚𝐧𝐧𝐞𝐥",
        description="Use the buttons below to **manage** your temporary voice channel.",
        color=discord.Color.dark_red()
    )
    embed.add_field(name="Help Command", value="**.v help** to check all commands to manage your TempVoice", inline=False)
    embed.set_image(url="https://i.ibb.co/NnZcQ4c4/212-9.jpg")
    embed.set_author(name="Arena Temp Voice", icon_url=owner.display_avatar.url)
    embed.set_footer(text="Temporary Voice Controls • M O U A D's Style")

    view = TempVoiceControl(owner.id)
    await text_channel.send(embed=embed, view=view)


# Event: user joins/leaves voice
@bot.event
async def on_voice_state_update(member, before, after):
    # 1️⃣ Create temp channel
    if after.channel and after.channel.id == 1437496385435078799:
        guild = member.guild
        category = after.channel.category
        channel_name = f"{member.display_name}'s channel"

        VERIFIED_ROLE_ID = 1438555128725635174
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False, connect=False),  # hide for everyone
            member: discord.PermissionOverwrite(view_channel=True, connect=True, manage_channels=True, use_voice_activation=True, send_messages=True, read_message_history=True)
        }

        # allow staff/verified role to see all temp voices
        if VERIFIED_ROLE_ID:
            verified_role = guild.get_role(VERIFIED_ROLE_ID)
            if verified_role:
                overwrites[verified_role] = discord.PermissionOverwrite(view_channel=True, connect=True)

        # Create temp channel
        temp_channel = await guild.create_voice_channel(
            name=channel_name,
            category=category,
            user_limit=20,  # default limit, can edit later
            overwrites=overwrites,
            bitrate=64000  # default bitrate, can edit later
        )

        # Store owner
        temp_channels[temp_channel.id] = member.id

        # Move user into their temp channel
        await member.move_to(temp_channel)
        print(f"✅ Temp voice created: {temp_channel.name} for {member.display_name}")
        voice_chat = temp_channel  # VoiceChannel object
        if hasattr(voice_chat, "guild"):
            try:
                # Each voice channel has an attached "voice text chat" channel (same ID)
                voice_text_channel = await voice_chat.fetch_channel()
            except:
                # fallback for older versions
                voice_text_channel = await voice_chat.guild.fetch_channel(voice_chat.id)

        # Send the control embed directly into that voice channel's text chat
        await send_temp_voice_panel(temp_channel, voice_text_channel, member)

    # 2️⃣ Delete temp channel if empty
    if before.channel and before.channel.id in temp_channels:
        if len(before.channel.members) == 0:
            await before.channel.delete()
            del temp_channels[before.channel.id]
            print(f"🗑 Deleted empty temp channel: {before.channel.name}")

    if after.channel and after.channel.id in ChannelsGamesID:
        index = ChannelsGamesID.index(after.channel.id)
        generator = after.channel
        guild = member.guild

        # Check limit
        if len(TEMP_CHANNELS_Games) >= 7:
            await member.move_to(None)
            await member.send("🚫 The temporary voice channel limit has been reached.")
            return
            
        VERIFIED_ROLE_ID = 1438555128725635174
        # Create temp voice
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False, connect=False),  # hide for everyone
            member: discord.PermissionOverwrite(view_channel=True, connect=True, manage_channels=True, use_voice_activation=True, send_messages=True, read_message_history=True)
        }
        # allow staff/verified role to see all temp voices
        if VERIFIED_ROLE_ID:
            verified_role = guild.get_role(VERIFIED_ROLE_ID)
            if verified_role:
                overwrites[verified_role] = discord.PermissionOverwrite(view_channel=True, connect=True)
        temp_channel = await guild.create_voice_channel(
            name=f"{ChannelsGamesNames[index]} • {member.display_name}",
            category=generator.category,
            position=generator.position + 1,
            overwrites=overwrites,
            user_limit=15,
            reason=f"Temporary voice for {member.display_name}"
        )
        TEMP_CHANNELS_Games[temp_channel.id] = member.id
        await member.move_to(temp_channel)

    # Delete temp when empty
    if before.channel and before.channel.id in TEMP_CHANNELS_Games:
        if len(before.channel.members) == 0:
            await before.channel.delete(reason="Temporary channel empty")
            del TEMP_CHANNELS_Games[before.channel.id]



@commands.command(name="v")
async def voice_command(ctx, action: str = None, *, value: str = None):
    """Command format: .v <action> [value]"""
    member = ctx.author
    vc = member.voice.channel if member.voice else None

    if not vc:
        return await ctx.send("❌ You must be in your temp voice channel.")

    # make sure this user is the owner of the temp channel
    # if you stored owner IDs in a dict like temp_channels = {channel_id: owner_id}
    # check it like this:
    if vc.id in temp_channels and temp_channels[vc.id] != member.id:
        return await ctx.send("❌ Only the owner can manage this voice channel.")

    if not action:
        return await ctx.send("⚙️ Usage: `.v <action>` — actions: rename, limit, lock, unlock, hide, show, invite, reject")

    action = action.lower()

    # --- ✏️ Rename
    if action == "name" and value and ctx.author:
        await vc.edit(name=value)
        return await ctx.send(f"{ctx.author.mention} : <:editer:1439630171446575275> Renamed to **{value}**")
    if action == "rename" and value and ctx.author:
        await vc.edit(name=value)
        return await ctx.send(f"{ctx.author.mention} : <:editer:1439630171446575275> Renamed to **{value}**")

    # --- 🚪 Limit Members
    if action == "limit" and value and value.isdigit():
        await vc.edit(user_limit=int(value))
        return await ctx.send(f"🚪 Limit set to **{value}** members")

    # --- 🔒 Lock
    if action == "lock" and ctx.author:
        await vc.set_permissions(ctx.guild.default_role, connect=False)
        return await ctx.send(f"{ctx.author.mention} : <:verrouiller:1439630169726783529> Channel locked.")

    # --- 🔓 Unlock
    if action == "unlock" and ctx.author:
        await vc.set_permissions(ctx.guild.default_role, connect=True)
        return await ctx.send(f"{ctx.author.mention} : <:verrouiller:1439630169726783529> Channel unlocked.")

    # --- 🙈 Hide
    if action == "hide":
        await vc.set_permissions(ctx.guild.default_role, view_channel=False)
        return await ctx.send("🙈 Channel hidden.")

    # --- 👁 Show
    if action == "show":
        await vc.set_permissions(ctx.guild.default_role, view_channel=True)
        return await ctx.send("👁 Channel visible.")

    # --- ➕ Invite
    if action == "invite" and ctx.message.mentions and ctx.author:
        target = ctx.message.mentions[0]
        await vc.set_permissions(target, connect=True, view_channel=True)
        return await ctx.send(f"{ctx.author.mention} : ➕ Invited {target.mention} to the channel.")

    # --- ❌ Reject
    if action == "reject" and ctx.message.mentions and ctx.author:
        target = ctx.message.mentions[0]
        await vc.set_permissions(target, connect=False, view_channel=False)
        if target.voice and target.voice.channel == vc:
            await target.move_to(None)
        return await ctx.send(f"{ctx.author.mention} : ❌ {target.mention} has been removed from the channel.")

    # --- 🎯 Claim Ownership
    if action == "claim":
        voice = ctx.author.voice
        if not voice or not voice.channel:
            return await ctx.send("❌ You must be inside the TempVoice to claim it.")
        channel = voice.channel
        if channel.id not in temp_voice_owners:
            return await ctx.send("❌ This is not a TempVoice.")
        current_owner_id = temp_voice_owners[channel.id]
        if current_owner_id == ctx.author.id:
            return await ctx.send("🔹 You already own this channel.")
        current_owner = ctx.guild.get_member(current_owner_id)
        if current_owner and current_owner in channel.members:
            return await ctx.send("❌ You cannot claim this channel while the owner is still inside.")
        temp_voice_owners[channel.id] = ctx.author.id
        await channel.set_permissions(
            ctx.author,
            manage_channels=True,
            move_members=True,
            mute_members=True,
            deafen_members=True,
            connect=True,
            speak=True
        )
        if current_owner:
            await channel.set_permissions(current_owner, overwrite=None)
            return await ctx.send(f"✅ {ctx.author.mention} is now the owner of **{channel.name}**!")

    # --- 🔐 Unlock for specific member
    if action == "allow" and ctx.message.mentions:
        target = ctx.message.mentions[0]
        await vc.set_permissions(target, connect=True, view_channel=True)
        return await ctx.send(f"🔐 {target.mention.mention} can now join your voice channel.")

    if action == "help" and ctx.author:
        return await ctx.send(f"*{ctx.author.mention} this is some commands to manage your TempVoice :\n"
                              "**.v name <Name>** \n --- to rename your TempVoice \n"
                              "**.v limit <Number>** \n --- to control your TempVoice limit member\n"
                              "**.v lock** \n --- to lock your TempVoice\n"
                              "**.v unlock** \n --- to unlock your TempVoice\n"
                              "**.v hide** \n --- to hide your voice from everyone\n"
                              "**.v show** \n --- to make your voice showing to everyone\n"
                              "**.v invite <Member>** \n --- to invite your friends into your TempVoice\n"
                              "**.v reject <Member>** \n --- to block someone from your tempVoice\n"
                              "**.v claim** \n --- to be the new TempVoice Owner\n"
                              "**.v allow <Member>** \n --- to allowed someone join"
                              )

    # --- Unknown
    await ctx.send("❌ Unknown action. Try: rename, limit, lock, unlock, hide, show, invite, reject, claim, allow.")


# Slash command: edit your temp channel
@bot.tree.command(name="edit_tempvoice", description="Edit your temporary voice channel")
@app_commands.describe(new_name="New channel name", user_limit="Max users (0 = unlimited)",
                       bitrate="Bitrate in bits/sec")
async def edit_tempvoice(interaction: discord.Interaction,
                         new_name: str = None,
                         user_limit: int = None,
                         bitrate: int = None):
    # Find user's temp channel
    user_channel = None
    for cid, owner_id in temp_channels.items():
        if owner_id == interaction.user.id:
            user_channel = interaction.guild.get_channel(cid)
            break
    if not user_channel:
        return await interaction.response.send_message("❌ You don't own any temp voice channel.", ephemeral=True)

    # Apply edits
    kwargs = {}
    if new_name:
        kwargs["name"] = new_name
    if user_limit is not None:
        kwargs["user_limit"] = user_limit if user_limit > 0 else 0
    if bitrate is not None:
        kwargs["bitrate"] = bitrate

    if not kwargs:
        return await interaction.response.send_message("⚠️ No changes provided.", ephemeral=True)

    await user_channel.edit(**kwargs)
    await interaction.response.send_message(f"✅ TempVoice updated!", ephemeral=True)


# Optional: debug command to list active temp voices
@bot.tree.command(name="list_tempvoices", description="List all active temp voices (debug)")
async def list_tempvoices(interaction: discord.Interaction):
    if not temp_channels:
        return await interaction.response.send_message("No active temp channels.", ephemeral=True)
    lines = []
    for cid, owner_id in temp_channels.items():
        ch = interaction.guild.get_channel(cid)
        lines.append(f"{ch.name if ch else 'Unknown'} — owner <@{owner_id}>")
    await interaction.response.send_message("\n".join(lines), ephemeral=True)





bot.add_command(voice_command)
bot.run(TOKEN)
