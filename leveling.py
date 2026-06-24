import discord
from discord.ext import commands
import json
import os
import random
import time

DATA_FAJL = "data/leveling.json"

def ucitaj_podatke():
    if not os.path.exists(DATA_FAJL):
        return {}
    with open(DATA_FAJL, 'r') as f:
        return json.load(f)

def sacuvaj_podatke(podaci):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FAJL, 'w') as f:
        json.dump(podaci, f, indent=2)

def xp_za_nivo(nivo):
    return int(100 * (nivo ** 1.5))

def izracunaj_nivo(xp):
    nivo = 0
    preostali = xp
    while preostali >= xp_za_nivo(nivo + 1):
        preostali -= xp_za_nivo(nivo + 1)
        nivo += 1
    return nivo, preostali

def nivo_rang(nivo):
    if nivo >= 50:   return "👑 Legenda"
    elif nivo >= 40: return "💎 Dijamant"
    elif nivo >= 30: return "🥇 Zlatni"
    elif nivo >= 20: return "🥈 Srebrni"
    elif nivo >= 10: return "🥉 Brončani"
    elif nivo >= 5:  return "⚔️ Vitez"
    else:            return "🌱 Početnik"

def rang_boja(nivo):
    if nivo >= 50:   return 0xFFD700
    elif nivo >= 40: return 0x00FFFF
    elif nivo >= 30: return 0xFFD700
    elif nivo >= 20: return 0xC0C0C0
    elif nivo >= 10: return 0xCD7F32
    elif nivo >= 5:  return 0xFF6600
    else:            return 0x2ECC71

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldown = {}

    def uid(self, guild_id, user_id):
        return f"{guild_id}_{user_id}"

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if not message.guild:
            return
        if message.content.startswith('.'):
            return

        uid = self.uid(message.guild.id, message.author.id)
        sada = time.time()

        if uid in self.cooldown and sada - self.cooldown[uid] < 60:
            return
        self.cooldown[uid] = sada

        podaci = ucitaj_podatke()
        if uid not in podaci:
            podaci[uid] = {'xp': 0, 'nivo': 0, 'poruke': 0, 'ime': str(message.author)}

        stari_nivo = podaci[uid]['nivo']
        xp_dobiven = random.randint(15, 35)
        podaci[uid]['xp'] += xp_dobiven
        podaci[uid]['poruke'] = podaci[uid].get('poruke', 0) + 1
        podaci[uid]['ime'] = str(message.author)

        novi_nivo, _ = izracunaj_nivo(podaci[uid]['xp'])
        podaci[uid]['nivo'] = novi_nivo
        sacuvaj_podatke(podaci)

        if novi_nivo > stari_nivo:
            rang = nivo_rang(novi_nivo)
            boja = rang_boja(novi_nivo)
            embed = discord.Embed(
                title="🎉 LEVEL UP!",
                color=boja
            )
            embed.set_author(
                name=message.author.display_name,
                icon_url=message.author.avatar.url if message.author.avatar else None
            )
            embed.add_field(name="📈 Novi Nivo", value=f"**{novi_nivo}**", inline=True)
            embed.add_field(name="🏅 Rang", value=f"**{rang}**", inline=True)
            embed.add_field(name="✨ Ukupno XP", value=f"**{podaci[uid]['xp']:,}**", inline=True)
            embed.set_footer(text="Nastavi pisati da napreduje! • .rang za detalje")
            await message.channel.send(embed=embed)

    @commands.command(name='rang')
    async def rang_cmd(self, ctx, korisnik: discord.Member = None):
        korisnik = korisnik or ctx.author
        uid = self.uid(ctx.guild.id, korisnik.id)
        podaci = ucitaj_podatke()

        if uid not in podaci:
            embed = discord.Embed(
                title="❌ Nema Podataka",
                description=f"{korisnik.mention} nema XP bodova. Počni pisati poruke!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        info = podaci[uid]
        nivo, preostali_xp = izracunaj_nivo(info['xp'])
        sledeci_xp = xp_za_nivo(nivo + 1)
        procenat = int((preostali_xp / sledeci_xp) * 100) if sledeci_xp > 0 else 100

        traka_duzina = 15
        ispunjeno = int(procenat / 100 * traka_duzina)
        traka = "█" * ispunjeno + "░" * (traka_duzina - ispunjeno)

        svi = [(k, v) for k, v in podaci.items() if k.startswith(f"{ctx.guild.id}_")]
        svi.sort(key=lambda x: x[1]['xp'], reverse=True)
        pozicija = next((i + 1 for i, (k, _) in enumerate(svi) if k == uid), "?")

        rang = nivo_rang(nivo)
        boja = rang_boja(nivo)

        embed = discord.Embed(title="📊 Karta Igrača", color=boja)
        embed.set_author(
            name=korisnik.display_name,
            icon_url=korisnik.avatar.url if korisnik.avatar else None
        )
        embed.set_thumbnail(url=korisnik.avatar.url if korisnik.avatar else None)
        embed.add_field(name="🏅 Nivo", value=f"**{nivo}**", inline=True)
        embed.add_field(name="⭐ Rang", value=f"**{rang}**", inline=True)
        embed.add_field(name="🏆 Pozicija", value=f"**#{pozicija}**", inline=True)
        embed.add_field(
            name=f"📈 Progres do Nivoa {nivo + 1}",
            value=(
                f"`[{traka}]` **{procenat}%**\n"
                f"{preostali_xp:,} / {sledeci_xp:,} XP"
            ),
            inline=False
        )
        embed.add_field(name="💬 Poruke", value=f"**{info.get('poruke', 0):,}**", inline=True)
        embed.add_field(name="✨ Ukupno XP", value=f"**{info['xp']:,}**", inline=True)
        embed.set_footer(text="XP se dobija pisanjem poruka • cooldown 60s")
        await ctx.send(embed=embed)

    @commands.command(name='ljestvica')
    async def ljestvica(self, ctx):
        podaci = ucitaj_podatke()
        svi = [(k, v) for k, v in podaci.items() if k.startswith(f"{ctx.guild.id}_")]
        svi.sort(key=lambda x: x[1]['xp'], reverse=True)
        top10 = svi[:10]

        if not top10:
            await ctx.send("❌ Nema podataka za ljestvicu.")
            return

        embed = discord.Embed(
            title="🏆 Ljestvica — Top 10 Igrača",
            color=0xFFD700
        )
        medalje = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
        opis = ""
        for i, (uid, info) in enumerate(top10):
            nivo, _ = izracunaj_nivo(info['xp'])
            rang = nivo_rang(nivo)
            ime = info.get('ime', 'Nepoznat').split('#')[0]
            opis += f"{medalje[i]} **{i+1}.** {ime} — Nivo **{nivo}** | **{info['xp']:,}** XP | {rang}\n"

        embed.description = opis
        embed.set_footer(text=f"Ukupno korisnika: {len(podaci)} • .rang za vlastite statistike")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leveling(bot))
