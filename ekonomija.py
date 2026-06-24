import discord
from discord.ext import commands
import json
import os

EKONOMIJA_FAJL = "data/ekonomija.json"
POCETNI_NOVAC = 0

def ucitaj():
    if not os.path.exists(EKONOMIJA_FAJL):
        return {}
    with open(EKONOMIJA_FAJL, 'r') as f:
        return json.load(f)

def sacuvaj(podaci):
    os.makedirs("data", exist_ok=True)
    with open(EKONOMIJA_FAJL, 'w') as f:
        json.dump(podaci, f, indent=2)

def get_balans(user_id: str):
    podaci = ucitaj()
    return podaci.get(str(user_id), 0)

def dodaj_novac(user_id: str, iznos: int, ime: str = None):
    podaci = ucitaj()
    uid = str(user_id)
    if uid not in podaci:
        podaci[uid] = 0
    podaci[uid] += iznos
    if podaci[uid] < 0:
        podaci[uid] = 0
    sacuvaj(podaci)
    return podaci[uid]

def postavi_novac(user_id: str, iznos: int):
    podaci = ucitaj()
    podaci[str(user_id)] = max(0, iznos)
    sacuvaj(podaci)
    return podaci[str(user_id)]

NOVAC_EMOJI = "💵"

class Ekonomija(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def napravi_novac_embed(self, korisnik, balans, naslov="💵 Novčanik", boja=0x2ECC71):
        embed = discord.Embed(title=naslov, color=boja)
        embed.set_author(name=korisnik.display_name, icon_url=korisnik.avatar.url if korisnik.avatar else None)
        embed.add_field(
            name="💰 Balans",
            value=f"```\n$ {balans:,}\n```",
            inline=False
        )
        embed.set_footer(text="💵 Bosanski Bot Ekonomija")
        return embed

    @commands.command(name='novac', aliases=['wallet', 'balans', 'pare'])
    async def novac(self, ctx, korisnik: discord.Member = None):
        korisnik = korisnik or ctx.author
        balans = get_balans(korisnik.id)

        embed = discord.Embed(
            title="💵 Novčanik",
            color=0x2ECC71
        )
        embed.set_author(
            name=korisnik.display_name,
            icon_url=korisnik.avatar.url if korisnik.avatar else None
        )
        embed.add_field(
            name="💰 Balans",
            value=f"```\n$ {balans:,}\n```",
            inline=False
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/💵")
        embed.set_footer(text="Igraj igre i zarađuj • .help za komande")
        await ctx.send(embed=embed)

    @commands.command(name='daj')
    async def daj(self, ctx, korisnik: discord.Member = None, iznos: int = None):
        if ctx.author.id != ctx.guild.owner_id:
            embed = discord.Embed(
                title="🚫 Zabranjen Pristup",
                description="Samo **vlasnik servera** može davati novac!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        if not korisnik or iznos is None:
            embed = discord.Embed(
                title="❌ Pogrešna Komanda",
                description="Koristi: `.daj @korisnik <iznos>`\nPrimjer: `.daj @Pero 5000`",
                color=0xFF6600
            )
            await ctx.send(embed=embed)
            return

        if iznos <= 0:
            await ctx.send("❌ Iznos mora biti pozitivan broj!")
            return

        novi_balans = dodaj_novac(korisnik.id, iznos)

        embed = discord.Embed(
            title="💵 Novac Dodan!",
            color=0x2ECC71
        )
        embed.add_field(name="👤 Korisnik", value=korisnik.mention, inline=True)
        embed.add_field(name="💰 Dato", value=f"**$ {iznos:,}**", inline=True)
        embed.add_field(name="📊 Novi Balans", value=f"**$ {novi_balans:,}**", inline=True)
        embed.set_footer(text=f"Dato od: {ctx.author.display_name} (vlasnik)")
        await ctx.send(embed=embed)

    @commands.command(name='uzmi')
    async def uzmi(self, ctx, korisnik: discord.Member = None, iznos: int = None):
        if ctx.author.id != ctx.guild.owner_id:
            embed = discord.Embed(
                title="🚫 Zabranjen Pristup",
                description="Samo **vlasnik servera** može uzimati novac!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        if not korisnik or iznos is None:
            await ctx.send("❌ Koristi: `.uzmi @korisnik <iznos>`")
            return

        novi_balans = dodaj_novac(korisnik.id, -iznos)
        embed = discord.Embed(
            title="💸 Novac Uklonjen",
            color=0xFF6600
        )
        embed.add_field(name="👤 Korisnik", value=korisnik.mention, inline=True)
        embed.add_field(name="💰 Uzeto", value=f"**$ {iznos:,}**", inline=True)
        embed.add_field(name="📊 Novi Balans", value=f"**$ {novi_balans:,}**", inline=True)
        await ctx.send(embed=embed)

    @commands.command(name='prenos', aliases=['posalji'])
    async def prenos(self, ctx, korisnik: discord.Member = None, iznos: int = None):
        if not korisnik or iznos is None:
            embed = discord.Embed(
                title="❌ Pogrešna Komanda",
                description="Koristi: `.prenos @korisnik <iznos>`\nPrimjer: `.prenos @Pero 1000`",
                color=0xFF6600
            )
            await ctx.send(embed=embed)
            return

        if korisnik == ctx.author:
            await ctx.send("❌ Ne možeš slati novac samom sebi!")
            return

        if iznos <= 0:
            await ctx.send("❌ Iznos mora biti pozitivan!")
            return

        moj_balans = get_balans(ctx.author.id)
        if moj_balans < iznos:
            embed = discord.Embed(
                title="❌ Nedovoljno Sredstava",
                description=f"Imaš samo **$ {moj_balans:,}** a pokušavaš poslati **$ {iznos:,}**!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        dodaj_novac(ctx.author.id, -iznos)
        novi_balans_primaoca = dodaj_novac(korisnik.id, iznos)
        moj_novi_balans = get_balans(ctx.author.id)

        embed = discord.Embed(
            title="💸 Prenos Uspješan!",
            color=0x2ECC71
        )
        embed.add_field(name="📤 Pošiljalac", value=f"{ctx.author.mention}\n`$ {moj_novi_balans:,}`", inline=True)
        embed.add_field(name="💵 Iznos", value=f"**$ {iznos:,}**", inline=True)
        embed.add_field(name="📥 Primalac", value=f"{korisnik.mention}\n`$ {novi_balans_primaoca:,}`", inline=True)
        embed.set_footer(text="💵 Bosanski Bot Ekonomija")
        await ctx.send(embed=embed)

    @commands.command(name='bogatasi', aliases=['topnovac', 'richlista'])
    async def bogatasi(self, ctx):
        podaci = ucitaj()
        if not podaci:
            await ctx.send("❌ Niko još nema novac!")
            return

        sortirano = sorted(podaci.items(), key=lambda x: x[1], reverse=True)[:10]

        embed = discord.Embed(
            title="💰 Lista Najbogatijih",
            description="Top 10 najbogatijih korisnika",
            color=0xFFD700
        )

        medalje = ["🥇", "🥈", "🥉"] + ["💵"] * 7
        opis = ""
        for i, (uid, balans) in enumerate(sortirano):
            try:
                user = await self.bot.fetch_user(int(uid))
                ime = user.display_name
            except:
                ime = f"Korisnik #{uid[:6]}"
            opis += f"{medalje[i]} **{i+1}.** {ime} — **$ {balans:,}**\n"

        embed.description = opis
        embed.set_footer(text="Zarađuj novac igranjem igara!")
        await ctx.send(embed=embed)

    @commands.command(name='resetnovac')
    async def resetnovac(self, ctx, korisnik: discord.Member = None):
        if ctx.author.id != ctx.guild.owner_id:
            await ctx.send("🚫 Samo vlasnik servera može resetovati novac!")
            return
        if not korisnik:
            await ctx.send("❌ Navedi korisnika: `.resetnovac @korisnik`")
            return
        postavi_novac(korisnik.id, 0)
        await ctx.send(f"✅ Balans korisnika {korisnik.mention} je resetovan na **$ 0**.")

async def setup(bot):
    await bot.add_cog(Ekonomija(bot))
