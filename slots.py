import discord
from discord.ext import commands
import random
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cogs.ekonomija import get_balans, dodaj_novac

SIMBOLI = ["🍒", "🍋", "🍊", "🍇", "⭐", "💎", "7️⃣", "🔔", "🍀", "💰"]
SPIN_SIMBOLI = ["🌀", "❓", "🔄"]

DOBITCI = {
    ("7️⃣", "7️⃣", "7️⃣"): ("🏆 JACKPOT! TRI SEDMICE!", 5000, 0xFF0000),
    ("💎", "💎", "💎"): ("💎 TRI DIJAMANTA!", 3000, 0x00FFFF),
    ("💰", "💰", "💰"): ("💰 TRI NOVČANIKA!", 2000, 0xFFD700),
    ("⭐", "⭐", "⭐"): ("⭐ TRI ZVIJEZDE!", 1500, 0xFFFF00),
    ("🍀", "🍀", "🍀"): ("🍀 TRI DJETELINE!", 1000, 0x00FF00),
    ("🔔", "🔔", "🔔"): ("🔔 TRI ZVONA!", 750, 0xFFA500),
    ("🍇", "🍇", "🍇"): ("🍇 TRI GROŽĐA!", 600, 0x800080),
    ("🍊", "🍊", "🍊"): ("🍊 TRI NARANDŽE!", 500, 0xFF6600),
    ("🍋", "🍋", "🍋"): ("🍋 TRI LIMUNA!", 500, 0xFFFF00),
    ("🍒", "🍒", "🍒"): ("🍒 TRI TREŠNJE!", 500, 0xFF0000),
}

def slots_box(r1, r2, r3, naslov="___SLOTS___", status=""):
    return (
        f"```\n"
        f"╔══════════════════╗\n"
        f"║   {naslov}   ║\n"
        f"╠══════════════════╣\n"
        f"║                  ║\n"
        f"║   {r1}  │  {r2}  │  {r3}   ║\n"
        f"║                  ║\n"
        f"╚══════════════════╝\n"
        f"```"
        + (f"\n{status}" if status else "")
    )

class Slots(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.na_cekanju = set()

    @commands.command(name='slots')
    async def slots(self, ctx, ulog: int = 100):
        if ctx.author.id in self.na_cekanju:
            await ctx.send(f"⏳ {ctx.author.mention} Čekaj da završi prethodni okret!")
            return

        if ulog < 10:
            await ctx.send("❌ Minimalni ulog je **$ 10**!")
            return

        if ulog > 10000:
            await ctx.send("❌ Maksimalni ulog je **$ 10,000**!")
            return

        balans = get_balans(ctx.author.id)
        if balans < ulog:
            embed = discord.Embed(
                title="❌ Nedovoljno Sredstava",
                description=(
                    f"Imaš samo **$ {balans:,}**!\n"
                    f"Koristiti `.daj` za dobijanje novca."
                ),
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        self.na_cekanju.add(ctx.author.id)
        dodaj_novac(ctx.author.id, -ulog)

        try:
            spin1 = random.choice(SIMBOLI)
            spin2 = random.choice(SIMBOLI)
            spin3 = random.choice(SIMBOLI)

            jackpot_sansa = random.randint(1, 150)
            if jackpot_sansa == 1:
                spin1 = spin2 = spin3 = "7️⃣"

            embed = discord.Embed(
                title="🎰 Slots",
                description=slots_box("🌀", "🌀", "🌀", status=f"💵 Ulog: **$ {ulog:,}** | 🔄 Okretanje..."),
                color=0xFFD700
            )
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
            msg = await ctx.send(embed=embed)

            await asyncio.sleep(0.7)
            embed.description = slots_box(spin1, "🌀", "🌀", status=f"💵 Ulog: **$ {ulog:,}** | ⏳ Okretanje...")
            await msg.edit(embed=embed)

            await asyncio.sleep(0.7)
            embed.description = slots_box(spin1, spin2, "🌀", status=f"💵 Ulog: **$ {ulog:,}** | ⏳ Okretanje...")
            await msg.edit(embed=embed)

            await asyncio.sleep(0.7)

            rezultat = (spin1, spin2, spin3)

            if rezultat in DOBITCI:
                poruka, dobitak, boja = DOBITCI[rezultat]
                novi_balans = dodaj_novac(ctx.author.id, dobitak)
                embed.color = boja
                opis_status = (
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"💵 **Ulog:** $ {ulog:,}\n"
                    f"🏆 **Dobitak:** $ {dobitak:,}\n"
                    f"💰 **Balans:** $ {novi_balans:,}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"✅ {poruka}"
                )
                embed.description = slots_box(spin1, spin2, spin3, status=opis_status)
                embed.set_footer(text="🎰 Koristiti .slots <ulog> za novi okret")
            else:
                dva_ista = (spin1 == spin2 or spin2 == spin3 or spin1 == spin3)
                novi_balans = get_balans(ctx.author.id)

                if dva_ista:
                    embed.color = 0xFFA500
                    opis_status = (
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"💵 **Ulog:** $ {ulog:,}\n"
                        f"😅 **Skoro!** Dva ista simbola!\n"
                        f"💰 **Balans:** $ {novi_balans:,}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"and won nothing... :c"
                    )
                else:
                    embed.color = 0x555555
                    opis_status = (
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"💵 **Kum bet** 💵 {ulog:,}\n"
                        f"💰 **Balans:** $ {novi_balans:,}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"and won nothing... :c"
                    )
                embed.description = slots_box(spin1, spin2, spin3, status=opis_status)
                embed.set_footer(text="🎰 Koristiti .slots <ulog> za novi okret")

            await msg.edit(embed=embed)

        finally:
            self.na_cekanju.discard(ctx.author.id)

    @commands.command(name='slotinfo')
    async def slotinfo(self, ctx):
        embed = discord.Embed(
            title="🎰 Slots — Tablica Dobitaka",
            color=0xFFD700
        )
        opis = "```\n"
        for simboli, (poruka, bodovi, _) in DOBITCI.items():
            s1, s2, s3 = simboli
            opis += f"$ {bodovi:>6,}  →  {s1} {s2} {s3}\n"
        opis += "```"
        embed.description = opis
        embed.add_field(
            name="ℹ️ Info",
            value=(
                "• Koristiti: `.slots <ulog>` (min. $ 10)\n"
                "• Maksimalni ulog: **$ 10,000**\n"
                "• Jackpot šansa: **7️⃣7️⃣7️⃣** je rijedak!\n"
                "• Gubiš ulog ako nema tri ista"
            ),
            inline=False
        )
        embed.set_footer(text="💵 Zarađuj novac igranjem igara")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Slots(bot))
