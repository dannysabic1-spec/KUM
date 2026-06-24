import sys
import os

# Promijeni radni direktorij na folder bota da bi discord.py mogao naći 'cogs'
_BOT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(_BOT_DIR)
if _BOT_DIR not in sys.path:
    sys.path.insert(0, _BOT_DIR)

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.bans = True

bot = commands.Bot(command_prefix='.', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'✅ Bot spreman! Prijavljen kao {bot.user}')
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.playing,
        name=".help | 💵 Ekonomija & Igre"
    ))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="🚫 Zabranjen Pristup",
            description="Nemaš dozvolu za ovu komandu!",
            color=0xFF0000
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Korisnik nije pronađen!")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Pogrešan argument! Provjeri komandu sa `.help`")

@bot.command(name='help')
async def help_cmd(ctx):
    embed = discord.Embed(
        title="📋 Lista Svih Komandi",
        description="Kompletan bosanski Discord bot | Prefix: **`.`**",
        color=0x000000
    )
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)

    embed.add_field(
        name="🎮 Igre",
        value=(
            "`.kaladont` — Pokreni Kaladont igru\n"
            "`.kaladont stop` — Zaustavi Kaladont\n"
            "`.vjesalo` — Pokreni Vješalo\n"
            "`.slovo <x>` — Pogodi slovo u Vješalu\n"
            "`.slots [ulog]` — Zavrtiaj bankomat 🎰\n"
            "`.slotinfo` — Tablica dobitaka Slotsa\n"
            "`.wordle` — Pokreni Wordle igru\n"
            "`.pogodi <rijec>` — Pogodi riječ u Wordleu"
        ),
        inline=False
    )
    embed.add_field(
        name="💵 Ekonomija",
        value=(
            "`.novac` — Pogledaj svoj balans\n"
            "`.novac @korisnik` — Balans drugog korisnika\n"
            "`.prenos @korisnik <iznos>` — Pošalji novac\n"
            "`.bogatasi` — Lista najbogatijih\n"
            "`.daj @korisnik <iznos>` — *(samo vlasnik)*\n"
            "`.uzmi @korisnik <iznos>` — *(samo vlasnik)*\n"
            "`.resetnovac @korisnik` — *(samo vlasnik)*"
        ),
        inline=False
    )
    embed.add_field(
        name="📊 Level Sistem",
        value=(
            "`.rang` — Tvoj nivo i XP\n"
            "`.rang @korisnik` — Nivo drugog korisnika\n"
            "`.ljestvica` — Top 10 po XP-u"
        ),
        inline=False
    )
    embed.add_field(
        name="👥 Server Info",
        value="`.brojanje` — Broji članove servera",
        inline=False
    )
    embed.add_field(
        name="🔧 Moderacija",
        value=(
            "`.ban @korisnik [razlog]` — Banuj\n"
            "`.unban <ID>` — Odbanuj\n"
            "`.kick @korisnik [razlog]` — Kickaj\n"
            "`.mute @korisnik` — Ućutaj\n"
            "`.unmute @korisnik` — Odućutaj\n"
            "`.clear <1-100>` — Briši poruke\n"
            "`.banovi` — Lista banova"
        ),
        inline=False
    )
    embed.add_field(
        name="🤖 Automatske Funkcije",
        value=(
            "🚫 Anti-Invite — briše invite linkove\n"
            "📈 XP po poruci — 15-35 XP svakih 60s\n"
            "🎉 Level Up — automatska obavijest\n"
            "⚠️ 5 Banova — uklanjanje uloga"
        ),
        inline=False
    )
    embed.add_field(
        name="💰 Nagrade u Igrama",
        value=(
            "🎰 Slots: do **$ 5,000** (jackpot)\n"
            "🪢 Vješalo: **$ 500** za pobjedu\n"
            "🟩 Wordle: **$ 500–1,000** za pobjedu\n"
            "🔤 Kaladont: **$ 10** po tačnoj riječi"
        ),
        inline=False
    )
    embed.set_footer(text="🇧🇦 Bosanski Discord Bot • Sve na bosanskom!")
    await ctx.send(embed=embed)

async def load_extensions():
    import importlib.util
    import types

    moduli = ['ekonomija', 'kaladont', 'vjesalo', 'slots', 'wordle', 'leveling', 'moderation']
    _cogs_dir = os.path.join(_BOT_DIR, 'cogs')

    # Registriraj 'cogs' kao paket u sys.modules da bi međusobni importi radili
    if 'cogs' not in sys.modules:
        pkg = types.ModuleType('cogs')
        pkg.__path__ = [_cogs_dir]
        pkg.__package__ = 'cogs'
        pkg.__file__ = os.path.join(_cogs_dir, '__init__.py')
        sys.modules['cogs'] = pkg

    for filename in moduli:
        filepath = os.path.join(_cogs_dir, f'{filename}.py')
        mod_name = f'cogs.{filename}'

        spec = importlib.util.spec_from_file_location(mod_name, filepath)
        module = importlib.util.module_from_spec(spec)
        module.__package__ = 'cogs'
        sys.modules[mod_name] = module
        spec.loader.exec_module(module)

        # Pozovi setup() funkciju kao što discord.py to radi
        await module.setup(bot)
        print(f'  ✔ Učitan modul: {filename}')

async def main():
    async with bot:
        print("🔄 Učitavam module...")
        await load_extensions()
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            print("❌ GREŠKA: DISCORD_TOKEN nije postavljen u .env fajlu!")
            return
        await bot.start(token)

import asyncio
asyncio.run(main())
