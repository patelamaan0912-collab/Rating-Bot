print("Bot file loaded")
card_cache = {}
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()
import discord
from discord.ext import commands
from discord.ui import View, Button
import json, os, io, requests
from PIL import Image, ImageDraw, ImageFont
from PIL import ImageFilter  # make sure at top

import os
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "data.json"

# =========================
# DATA
# =========================
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

def get_guild(gid):
    gid = str(gid)
    if gid not in data:
        data[gid] = {"users": {}, "config": {}}
    if "users" not in data[gid]:
        data[gid]["users"] = {}
    return data[gid]

# =========================
# CARD GENERATOR
# =========================
def generate_card(member, user_data):
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    import requests, io, os

    WIDTH, HEIGHT = 1024, 683
    frames = []

    frame_i = 0 
    base = Image.open("card_bg.png").resize((WIDTH, HEIGHT)).convert("RGBA")
    draw = ImageDraw.Draw(base)

    # DARKEN BACKGROUND
    dark = Image.new("RGBA", base.size, (0,0,0,140))
    base = Image.alpha_composite(base, dark)
    draw = ImageDraw.Draw(base)

    # =========================
    # FONTS (Orbitron Setup)
    # =========================
    import os

    def load_font(name, size):
        path = os.path.join(os.getcwd(), name)
        if not os.path.exists(path):
            print(f"[FONT ERROR] Missing: {name}")
            return ImageFont.load_default()
        return ImageFont.truetype(path, size)

    font_name   = load_font("Orbitron-Black.otf", 60)
    font_medium = load_font("Orbitron-Medium.otf", 30)
    font_small  = load_font("Orbitron-Light.otf", 20)

    # =========================
    # DATA
    # =========================
    up = user_data.get("up", 0)
    down = user_data.get("down", 0)
    score = up - down
    total = max(up + down, 1)

    # =========================
    # DYNAMIC COLOR THEME
    # =========================
    if score > 0:
        main_color = "#00ff88"   # green
    elif score < 0:
        main_color = "#ff3c3c"   # red
    else:
        main_color = "#00eaff"   # cyan

    # =========================
    # POSITIONS (LOCKED)
    # =========================
    avatar_pos = (80, 120)
    username_box = (220, 90, 780, 230)
    score_box = (820, 90, 980, 260)
    up_box = (220, 260, 480, 360)
    down_box = (520, 260, 780, 360)
    stats_box = (80, 450, 980, 630)
    logo_pos = (820, 460)

    progress_y = 410

    # =========================
    # NEON BOX (CLEAN VERSION)
    # =========================
    def neon_box(coords, color, radius=25):
        x1, y1, x2, y2 = coords
        base_rgb = tuple(int(color[i:i+2], 16) for i in (1,3,5))

        glow = Image.new("RGBA", base.size, (0,0,0,0))
        g = ImageDraw.Draw(glow)

        # 🔥 OUTER GLOW (soft aura)
        for i in range(20):
            g.rounded_rectangle(
                (x1-i, y1-i, x2+i, y2+i),
                radius=radius+i,
                outline=(*base_rgb, 25),
                width=3
            )

        # 🔥 CORE GLOW (strong)
        for i in range(10):
            g.rounded_rectangle(
                (x1-i, y1-i, x2+i, y2+i),
                radius=radius+i,
                outline=(*base_rgb, 180 - i*15),
                width=4
            )

        glow = glow.filter(ImageFilter.GaussianBlur(10))
        base.alpha_composite(glow)

        # ⚡ MAIN LIGHTSABER LINE
        draw.rounded_rectangle(coords, radius, outline=color, width=5)

        # ⚡ INNER CORE (sharp glow line)
        draw.rounded_rectangle(
            (x1+2, y1+2, x2-2, y2-2),
            radius,
            outline=(255,255,255,180),
            width=1
        )
        
    # =========================
    # DRAW BOXES
    # =========================
    neon_box(username_box, main_color)
    neon_box(score_box, main_color)
    neon_box(up_box, "#00ff88")
    neon_box(down_box, "#ff3c3c")
    neon_box(stats_box, "#b266ff")

    def add_shine_line_animated(y):
        shine = Image.new("RGBA", base.size, (0,0,0,0))
        s = ImageDraw.Draw(shine)

        x_offset = (frame_i * 100) % WIDTH

        s.line((x_offset, y, x_offset+200, y), fill=(255,255,255,180), width=13)

        shine = shine.filter(ImageFilter.GaussianBlur(8))
        base.alpha_composite(shine)

    # =========================
    # AVATAR + STRONG AURA (FIXED)
    # =========================
    try:
        r = requests.get(member.display_avatar.url)
        avatar = Image.open(io.BytesIO(r.content)).resize((120,120)).convert("RGBA")

        mask = Image.new("L", (120,120), 0)
        ImageDraw.Draw(mask).ellipse((0,0,120,120), fill=255)

        ax, ay = avatar_pos
        rgb = tuple(int(main_color[i:i+2],16) for i in (1,3,5))

        aura = Image.new("RGBA", base.size, (0,0,0,0))
        a = ImageDraw.Draw(aura)

        # 🔥 CORE GLOW (STRONG)
        for i in range(12):
            a.ellipse(
                (ax-i, ay-i, ax+120+i, ay+120+i),
                outline=(*rgb, 220 - i*10),
                width=6
            )

        # 🔥 OUTER SOFT GLOW
        for i in range(20):
            a.ellipse(
                (ax-i-5, ay-i-5, ax+125+i, ay+125+i),
                outline=(*rgb, 40),
                width=3
            )

        aura = aura.filter(ImageFilter.GaussianBlur(4))  # 🔥 reduced blur
        base.alpha_composite(aura)

        # white ring (lightsaber core)
        draw.ellipse((ax-2, ay-2, ax+122, ay+122), outline=(255,255,255), width=2)

        base.paste(avatar, avatar_pos, mask)

    except Exception as e:
        print("Avatar error:", e)

    
    # =========================
    # USERNAME (FIXED)
    # =========================

    nx1, ny1, nx2, ny2 = username_box   # ✅ THIS LINE WAS MISSING

    def fit_text(draw, text, font_path, max_width, start_size):
        size = start_size
        while size > 10:
            font = ImageFont.truetype(font_path, size)
            bbox = draw.textbbox((0,0), text, font=font)
            width = bbox[2] - bbox[0]
            if width <= max_width:
                return font
            size -= 2
        return ImageFont.truetype(font_path, size)

    name_text = member.display_name.upper()
    max_width = nx2 - nx1 - 40

    font_name_dynamic = fit_text(draw, name_text, "Orbitron-Black.otf", max_width, 70)

    # NAME
    draw.text((nx1+20, ny1+25), name_text, font=font_name_dynamic, fill="#ffe082")

    # REAL USERNAME (below)
    draw.text((nx1+20, ny1+95), member.name, font=font_small, fill="#ffd166")

    # =========================
    # SCORE BOX (CENTERED)
    # =========================
    sx1, sy1, sx2, sy2 = score_box
    cx = (sx1 + sx2) // 2

    draw.text((cx, sy1+35), "SCORE", font=font_small, fill="#00eaff", anchor="mm")
    draw.text((cx+2, sy1+102), str(score), font=font_name, fill=(0,0,0), anchor="mm")
    
    # glow layer
    glow = Image.new("RGBA", base.size, (0,0,0,0))
    g = ImageDraw.Draw(glow)

    rgb = tuple(int(main_color[i:i+2],16) for i in (1,3,5))

    for i in range(6):
        g.text((cx, sy1+100), str(score),
            font=font_name,
            fill=(*rgb, 60),
            anchor="mm")

    glow = glow.filter(ImageFilter.GaussianBlur(4))
    base.alpha_composite(glow)

    # main text
    draw.text((cx, sy1+100), str(score), font=font_name, fill=main_color, anchor="mm")

    status = "NEUTRAL" if score == 0 else ("POSITIVE" if score > 0 else "NEGATIVE")
    draw.text((cx, sy1+150), status, font=font_small, fill="#ffd166", anchor="mm")

    # =========================
    # UP / DOWN BOXES
    # =========================
    def centered_box_text(box, label, value, color):
        x1, y1, x2, y2 = box
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        draw.text((cx, y1 + 20), label, font=font_small, fill=color, anchor="mm")
        # shadow
        draw.text((cx+2, cy+12), str(value), font=font_name, fill=(0,0,0), anchor="mm")
        # main
        draw.text((cx, cy+10), str(value), font=font_name, fill=color, anchor="mm")

    centered_box_text(up_box, "UPVOTES", up, "#00ff88")
    centered_box_text(down_box, "DOWNVOTES", down, "#ff3c3c")
  
    # =========================
    # PROGRESS BAR (REAL)
    # =========================
    bars = 40

    # calculate real progress
    progress = int((up / max(up + down, 1)) * bars)

    for i in range(bars):
        x = 200 + i * 14

        if i < progress:
            # glow
            glow = Image.new("RGBA", base.size, (0,0,0,0))
            g = ImageDraw.Draw(glow)

            g.rectangle((x-2, progress_y-2, x+12, progress_y+16),
                        fill=tuple(int(main_color[i:i+2],16) for i in (1,3,5)) + (120,))

            glow = glow.filter(ImageFilter.GaussianBlur(6))
            base.alpha_composite(glow)

            draw.rectangle((x, progress_y, x+10, progress_y+14), fill=main_color)
        else:
            draw.rectangle((x, progress_y, x+10, progress_y+14), fill="#111")

    draw.text((150, progress_y), "0%", font=font_small, fill=main_color)
    draw.text((775, progress_y), "100%", font=font_small, fill="#00eaff")
    draw.text((WIDTH//2, 385), "REPUTATION PROGRESS", font=font_small, fill="#00eaff", anchor="mm")

    # =========================
    # STATS BOX (FIXED CLEAN)
    # =========================

    x1, y1, x2, y2 = stats_box
    section_width = (x2 - x1) // 4

    # vertical dividers
    def glow_line(x):
        glow = Image.new("RGBA", base.size, (0,0,0,0))
        g = ImageDraw.Draw(glow)

        for i in range(15):
            g.line(
                (x, y1-i, x, y2+i),
                fill=(178,102,255, int(255/(i+1))),
                width=3
            )

        glow = glow.filter(ImageFilter.GaussianBlur(10))
        base.alpha_composite(glow)

        draw.line((x, y1+10, x, y2-10), fill="#d580ff", width=2)

    # APPLY
    for i in range(1, 4):
        glow_line(x1 + section_width * i)

    total_votes = up + down
    activity = total_votes * 2
    joined = member.joined_at.strftime("%d %b %Y").upper() if member.joined_at else "--"

    centers = [
        x1 + section_width//2,
        x1 + section_width + section_width//2,
        x1 + section_width*2 + section_width//2,
        x1 + section_width*3 + section_width//2
    ]

    # =========================
    # WRAP FUNCTION
    # =========================
    def draw_wrapped_text(draw, text, font, max_width, center_x, y, color):
        words = text.split()
        lines = []
        current = ""

        for word in words:
            test = current + " " + word if current else word
            w = draw.textbbox((0,0), test, font=font)[2]

            if w <= max_width:
                current = test
            else:
                lines.append(current)
                current = word

        if current:
            lines.append(current)

        for i, line in enumerate(lines):
            draw.text((center_x, y + i*28), line, font=font, fill=color, anchor="mm")

    # =========================
    # LABELS
    # =========================
    labels = ["TOTAL VOTES", "ACTIVITY SCORE", "JOINED DISCORD", "SERVER"]

    for i in range(4):
        draw.text((centers[i], y1+30), labels[i], font=font_small, fill="#e6f7ff", anchor="mm")

    # =========================
    # VALUES (NO DUPLICATION)
    # =========================

    # Total Votes
    draw.text((centers[0], y1+102), str(total_votes), font=font_medium, fill=(0,0,0), anchor="mm")
    draw.text((centers[0], y1+100), str(total_votes), font=font_medium, fill="white", anchor="mm")

    # Activity
    draw.text((centers[1], y1+102), str(activity), font=font_medium, fill=(0,0,0), anchor="mm")
    draw.text((centers[1], y1+100), str(activity), font=font_medium, fill="white", anchor="mm")

    # Joined (WRAPPED ONLY ONCE)
    draw_wrapped_text(draw, joined, font_medium, 220, centers[2], y1+90, "white")

    def draw_icon_text(x, y, text, icon, font, color):
        draw.text((x-20, y), icon, font=font, fill=color, anchor="mm")
        draw.text((x+10, y), text, font=font, fill=color, anchor="mm")
    # =========================
    # LOGO
    # =========================
    try:
        if member.guild.icon:
            r = requests.get(member.guild.icon.url)
            guild_icon = Image.open(io.BytesIO(r.content)).resize((100,100)).convert("RGBA")

            mask = Image.new("L", (100,100), 0)
            ImageDraw.Draw(mask).ellipse((0,0,100,100), fill=255)

            icon_x = centers[3] - 50
            icon_y = y1 + 40

            # 🔥 SAME AURA AS AVATAR
            rgb = tuple(int(main_color[i:i+2],16) for i in (1,3,5))

            aura = Image.new("RGBA", base.size, (0,0,0,0))
            a = ImageDraw.Draw(aura)

            # core glow
            for i in range(10):
                a.ellipse(
                    (icon_x-i, icon_y-i, icon_x+100+i, icon_y+100+i),
                    outline=(*rgb, 200 - i*12),
                    width=4
                )

            # soft glow
            for i in range(15):
                a.ellipse(
                    (icon_x-i-3, icon_y-i-3, icon_x+103+i, icon_y+103+i),
                    outline=(*rgb, 40),
                    width=2
                )

            aura = aura.filter(ImageFilter.GaussianBlur(5))
            base.alpha_composite(aura)

            # white ring
            draw.ellipse((icon_x-2, icon_y-2, icon_x+102, icon_y+102), outline=(255,255,255), width=2)

            # paste icon
            base.paste(guild_icon, (icon_x, icon_y), mask)

    except Exception as e:
        print("Guild icon error:", e)


    # =========================
    # SAVE BUFFER
    # =========================
    buffer = io.BytesIO()
    base.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer
# =========================
# BUTTON
# =========================
class VoteButton(Button):
    def __init__(self, uid, vote):
        super().__init__(
            label="🔼" if vote=="up" else "🔽",
            style=discord.ButtonStyle.success if vote=="up" else discord.ButtonStyle.danger
        )
        self.uid = str(uid)
        self.vote = vote

    async def callback(self, interaction):
        await interaction.response.send_message("⏳ Processing your vote...", ephemeral=True)
    
        uid = self.uid  # ✅ FIXED

        if uid in card_cache:
            del card_cache[uid]
            
        g = get_guild(interaction.guild.id)
        users = g["users"]
        
        voter = str(interaction.user.id)
        target = self.uid

        users.setdefault(target, {"up":0,"down":0,"voters":{}})

        if voter == target:
            return await interaction.followup.send("No self voting", ephemeral=True)

        if voter in users[target]["voters"]:
            prev = users[target]["voters"][voter]

            if prev == self.vote:
                return await interaction.followup.send("Already voted", ephemeral=True)

            if prev == "up":
                users[target]["up"] -= 1
            else:
                users[target]["down"] -= 1

        users[target]["voters"][voter] = self.vote

        if self.vote == "up":
            users[target]["up"] += 1
        else:
            users[target]["down"] += 1

        save_data()
        await update_message(interaction.guild, target)

        await interaction.edit_original_response(content="✅ Vote counted")

def create_view(uid):
    v = View(timeout=None)
    v.add_item(VoteButton(uid, "up"))
    v.add_item(VoteButton(uid, "down"))
    return v
# =========================
# UPDATE MESSAGE
# =========================
async def update_message(guild, uid):
    g = get_guild(guild.id)
    user = g["users"].get(uid)

    if not user:
        return

    try:
        channel = bot.get_channel(user.get("channel_id"))
        if not channel:
            return

        msg = await channel.fetch_message(user.get("message_id"))

    except:
        # 🔥 MESSAGE DOESN'T EXIST → RECREATE IT
        member = guild.get_member(int(uid))
        if member:
            await create_profile(guild, member)
        return

    member = guild.get_member(int(uid))
    if not member:
        return

    img = generate_card(member, user)
    file = discord.File(img, filename="card.png")

    embed = discord.Embed()
    embed.set_image(url="attachment://card.png")
    embed.set_footer(text=uid)

    await msg.edit(embed=embed, attachments=[file], view=create_view(uid))

# =========================
# CREATE PROFILE
# =========================
async def create_profile(guild, member):
    g = get_guild(guild.id)

    if "channel" not in g["config"]:
        return

    channel = bot.get_channel(g["config"]["channel"])
    uid = str(member.id)

    if member.bot:
        return

    g["users"].setdefault(uid, {"up":0,"down":0,"voters":{}})

    img = generate_card(member, g["users"][uid])
    file = discord.File(img, filename="card.png")

    embed = discord.Embed()
    embed.set_image(url="attachment://card.png")
    embed.set_footer(text=uid)

    msg = await channel.send(embed=embed, file=file, view=create_view(uid))

    g["users"][uid]["channel_id"] = channel.id
    g["users"][uid]["message_id"] = msg.id

    save_data()

# =========================
# COMMANDS
# =========================
@bot.command()
async def config(ctx, channel: discord.TextChannel):
    g = get_guild(ctx.guild.id)
    g["config"]["channel"] = channel.id
    save_data()
    await ctx.send("Channel set")

@bot.command()
async def setup(ctx):
    msg = await ctx.send("⚙️ Setting up profiles... please wait")

    guild = ctx.guild
    g = get_guild(guild.id)

    count = 0

    for member in guild.members:
        if member.bot:
            continue

        uid = str(member.id)
        user = g["users"].get(uid)

        if user and "message_id" in user:
            await update_message(guild, uid)
        else:
            await create_profile(guild, member)

        count += 1

    await msg.edit(content=f"✅ Setup complete for {count} users")

# =========================
# EVENTS
# =========================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    if member.bot:
        return

    guild = member.guild
    g = get_guild(guild.id)
    uid = str(member.id)

    if uid in g["users"] and "message_id" in g["users"][uid]:
        try:
            await update_message(guild, uid)
            return
        except:
            pass

    await create_profile(guild, member)

@bot.event
async def on_member_remove(member):
    guild = member.guild
    g = get_guild(guild.id)
    uid = str(member.id)

    user = g["users"].get(uid)
    if not user:
        return

    try:
        channel = bot.get_channel(user.get("channel_id"))
        if channel:
            msg = await channel.fetch_message(user.get("message_id"))
            await msg.delete()
    except:
        pass

    # Optional: remove from data
    del g["users"][uid]
    save_data()

# =========================
# RUN
# =========================
import time
import os
keep_alive()  # you can keep this (harmless on Railway)
while True:
    try:
        print("🚀 Starting bot...")
        bot.run(TOKEN)
    except Exception as e:
        print(f"⚠️ Bot crashed: {e}")
        time.sleep(10)
