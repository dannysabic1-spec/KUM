import discord
from discord.ext import commands
import random
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cogs.ekonomija import dodaj_novac, get_balans

RIJECI_5 = [
    "crven", "plava", "bijel", "knjig", "skola",
    "djeca", "kucha", "vrsti", "grada", "polje",
    "zemla", "sunce", "mesec", "vjetr", "kamen",
    "trava", "drvet", "cvjet", "zivot", "radost",
    "sport", "muzik", "slika", "pismo", "gazda",
    "junak", "heroj", "vitez", "banja", "dolac",
    "nokat", "vlasi", "bradi", "usnic", "prsta",
    "torba", "ptica", "drago", "vjera", "sreca",
    "brzin", "misao", "hladi", "toplo", "mirno",
    "svjet", "tamno", "sjajn", "lahor", "struj",
]

ZELENO = "🟩"
ZUTO = "🟨"
SIVO = "⬛"

NAGRADA_PO_POKUSAJU = [1000, 800, 600, 500, 500, 500]

class Wordle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.igre = {}

    def procijeni(self, pogodak, cilj):
        rezultat = [SIVO] * 5
        cilj_lista = list(cilj)
        pogodak_lista = list(pogodak)

        for i in range(5):
            if pogodak_lista[i] == cilj_lista[i]:
                rezultat[i] = ZELENO
                cilj_lista[i] = None
                pogodak_lista[i] = None

        for i in range(5):
            if pogodak_lista[i] is not None and pogodak_lista[i] in cilj_lista:
                rezultat[i] = ZUTO
                cilj_lista[cilj_lista.index(pogodak_lista[i])] = None

        return ''.join(rezultat)

    def napravi_embed(self, igra, naslov="🟩 Wordle", boja=0x000000):
        embed = discord.Embed(title=naslov, color=boja)

        tabela = ""
        for pokusaj, procjena in igra['pokusaji']:
            slova = ' '.join(c.upper() for c in pokusaj)
            tabela += f"`{slova}` {procjena}\n"

        preostalo = 6 - len(igra['pokusaji'])
        for _ in range(preostalo):
            tabela += "`_ _ _ _ _` ⬜⬜⬜⬜⬜\n"

        embed.add_field(name="📋 Pokušaji", value=tabela, inline=False)
        embed.add_field(
            name="📖 Legenda",
            value="🟩 Tačno slovo i pozicija  |  🟨 Slovo postoji  |  ⬛ Slovo ne postoji",
            inline=False
        )

        nagrade_tekst = " | ".join([
            f"1. pokušaj: **$1000**",
            f"2: **$800**",
            f"3: **$600**",
            f"4-6: **$500**"
        ])
        embed.add_field(
            name="💵 Nagrade",
            value=nagrade_tekst,
            inline=False
        )
        embed.add_field(
            name="⏱️ Preostali Pokušaji",
            value=f"**{6 - len(igra['pokusaji'])}** / 6",
            inline=True
        )
        embed.set_footer(text=".pogodi <5-slovna-rijec> za pogađanje")
        return embed

    @commands.command(name='wordle')
    async def wordle(self, ctx):
        cid = ctx.channel.id
        if cid in self.igre:
            embed = self.napravi_embed(self.igre[cid])
            embed.title = "⚠️ Wordle — Igra Već Aktivna!"
            await ctx.send(embed=embed)
            return

        rijec = random.choice(RIJECI_5)
        self.igre[cid] = {
            'rijec': rijec,
            'pokusaji': [],
            'igrac': ctx.author.id
        }

        embed = discord.Embed(
            title="🟩 Wordle — Igra Počela!",
            description=(
                f"🎮 {ctx.author.mention} je pokrenuo/la Wordle!\n\n"
                "Pogodi **5-slovnu bosansku riječ** u **6 pokušaja**!\n"
                "Koristiti `.pogodi <rijec>` za svaki pokušaj.\n\n"
                "🟩 Ispravno slovo i pozicija\n"
                "🟨 Slovo postoji, pogrešna pozicija\n"
                "⬛ Slovo ne postoji"
            ),
            color=0x000000
        )
        embed.set_footer(text=f"💵 Pobjeda donosi do $ 1,000!")
        await ctx.send(embed=embed)

    @commands.command(name='pogodi')
    async def pogodi(self, ctx, pogodak: str = None):
        cid = ctx.channel.id
        if cid not in self.igre:
            await ctx.send("❌ Nema aktivne igre Wordle! Koristiti `.wordle` za početak.")
            return

        if not pogodak:
            await ctx.send("❌ Unesi 5-slovnu riječ! Npr: `.pogodi kamen`")
            return

        pogodak = pogodak.lower().strip()
        if len(pogodak) != 5:
            await ctx.send(f"❌ Riječ mora imati **tačno 5 slova**! Tvoja: `{pogodak}` ({len(pogodak)} slova)")
            return

        igra = self.igre[cid]
        cilj = igra['rijec']
        procjena = self.procijeni(pogodak, cilj)
        igra['pokusaji'].append((pogodak, procjena))

        pokusaj_br = len(igra['pokusaji'])

        if pogodak == cilj:
            nagrada = NAGRADA_PO_POKUSAJU[pokusaj_br - 1]
            novi_balans = dodaj_novac(ctx.author.id, nagrada)
            embed = self.napravi_embed(igra, naslov="🎉 Pobjeda!", boja=0x2ECC71)
            embed.description = (
                f"{ctx.author.mention} Bravo! Pogodio/la si **{cilj.upper()}** u **{pokusaj_br}** pokušaj{'a' if pokusaj_br != 1 else ''}!\n\n"
                f"💵 **Nagrada: +$ {nagrada:,}** | Balans: $ {novi_balans:,}"
            )
            await ctx.send(embed=embed)
            del self.igre[cid]
        elif pokusaj_br >= 6:
            embed = self.napravi_embed(igra, naslov="💀 Izgubio/la si!", boja=0xFF0000)
            embed.description = (
                f"{ctx.author.mention} Potrošio/la si sve pokušaje!\n"
                f"Riječ je bila: **{cilj.upper()}**"
            )
            await ctx.send(embed=embed)
            del self.igre[cid]
        else:
            embed = self.napravi_embed(igra)
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Wordle(bot))
