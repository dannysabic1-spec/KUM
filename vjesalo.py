import discord
from discord.ext import commands
import random
from cogs.ekonomija import dodaj_novac, get_balans

RIJECI = [
    "automobil", "knjiga", "planina", "rijeka", "more", "sunce", "mjesec",
    "zvijezda", "kuca", "skola", "prijatelj", "porodica", "muzika", "film",
    "sport", "fudbal", "kosarka", "tenis", "plivanje", "trening", "putovanje",
    "avion", "voz", "brod", "bicikl", "motor", "kompjuter", "telefon",
    "internet", "muzej", "pozoriste", "restoran", "kafana", "pijaca", "park",
    "suma", "livada", "polje", "jezero", "ocean", "pusinja", "snijeg",
    "kisa", "vjetar", "grmljavina", "munja", "duga", "oblak", "nebo",
    "zemlja", "vatra", "voda", "zrak", "kamen", "drvo", "cvijece", "trava",
    "zivotinja", "pas", "macka", "konj", "krava", "ovca", "ptica", "riba",
    "zmija", "lav", "tigar", "slon", "majmun", "panda", "vuk", "medvjed"
]

NAGRADA = 500

VJESALO = [
    "```\n  +---+\n  |   |\n      |\n      |\n      |\n      |\n=========\n  0/6 ❤️❤️❤️❤️❤️❤️```",
    "```\n  +---+\n  |   |\n  O   |\n      |\n      |\n      |\n=========\n  1/6 ❤️❤️❤️❤️❤️🖤```",
    "```\n  +---+\n  |   |\n  O   |\n  |   |\n      |\n      |\n=========\n  2/6 ❤️❤️❤️❤️🖤🖤```",
    "```\n  +---+\n  |   |\n  O   |\n /|   |\n      |\n      |\n=========\n  3/6 ❤️❤️❤️🖤🖤🖤```",
    "```\n  +---+\n  |   |\n  O   |\n /|\\  |\n      |\n      |\n=========\n  4/6 ❤️❤️🖤🖤🖤🖤```",
    "```\n  +---+\n  |   |\n  O   |\n /|\\  |\n /    |\n      |\n=========\n  5/6 ❤️🖤🖤🖤🖤🖤```",
    "```\n  +---+\n  |   |\n  O   |\n /|\\  |\n / \\  |\n      |\n=========\n  6/6 💀💀💀💀💀💀```",
]

class Vjesalo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.igre = {}

    def prikaz_rijeci(self, rijec, pogodjena):
        return ' '.join([f'**{c.upper()}**' if c in pogodjena else '`_`' for c in rijec])

    def napravi_embed(self, igra, naslov="🪢 Vješalo", boja=0x000000):
        rijec = igra['rijec']
        pogodjena = igra['pogodjena']
        pogresna = igra['pogresna']
        pogresno_br = len(pogresna)
        slika = VJESALO[min(pogresno_br, 6)]
        prikaz = self.prikaz_rijeci(rijec, pogodjena)
        slova = ' '.join([chr(i) for i in range(ord('a'), ord('z')+1) if chr(i) not in pogodjena and chr(i) not in pogresna])

        embed = discord.Embed(title=naslov, color=boja)
        embed.add_field(name="🎪 Vješalo", value=slika, inline=False)
        embed.add_field(name="🔤 Riječ", value=prikaz, inline=False)
        embed.add_field(
            name="❌ Pogrešna Slova",
            value=f"`{', '.join(p.upper() for p in pogresna)}`" if pogresna else "`Nema`",
            inline=True
        )
        embed.add_field(
            name="✅ Preostali Pokušaji",
            value=f"**{6 - pogresno_br}**",
            inline=True
        )
        embed.add_field(
            name="🔡 Dostupna Slova",
            value=f"`{slova.upper()}`" if slova else "`Sva probana`",
            inline=False
        )
        embed.set_footer(text=f"💵 Pobjeda donosi $ {NAGRADA:,} • .slovo <x> za pogađanje")
        return embed

    @commands.command(name='vjesalo')
    async def vjesalo(self, ctx):
        cid = ctx.channel.id
        if cid in self.igre:
            embed = self.napravi_embed(self.igre[cid])
            embed.title = "⚠️ Igra Već Aktivna!"
            await ctx.send(embed=embed)
            return

        rijec = random.choice(RIJECI)
        self.igre[cid] = {
            'rijec': rijec,
            'pogodjena': set(),
            'pogresna': [],
            'igrac': ctx.author.id
        }
        embed = self.napravi_embed(self.igre[cid])
        embed.description = f"🎮 {ctx.author.mention} je pokrenuo/la igru!\nPogodi slova pomoću komande `.slovo <x>`"
        await ctx.send(embed=embed)

    @commands.command(name='slovo')
    async def slovo(self, ctx, slovo: str = None):
        cid = ctx.channel.id
        if cid not in self.igre:
            await ctx.send("❌ Nema aktivne igre Vješalo! Koristiti `.vjesalo` za početak.")
            return

        if not slovo or len(slovo) != 1 or not slovo.isalpha():
            await ctx.send("❌ Molimo unesi jedno slovo! Npr: `.slovo a`")
            return

        igra = self.igre[cid]
        slovo = slovo.lower()
        rijec = igra['rijec']

        if slovo in igra['pogodjena'] or slovo in igra['pogresna']:
            await ctx.send(f"⚠️ Slovo **{slovo.upper()}** je već pokušano! Probaj drugo.")
            return

        if slovo in rijec:
            igra['pogodjena'].add(slovo)
            if all(c in igra['pogodjena'] for c in rijec):
                embed = self.napravi_embed(igra, naslov="🎉 Pobjeda!", boja=0x2ECC71)
                novi_balans = dodaj_novac(ctx.author.id, NAGRADA)
                embed.add_field(
                    name="💵 Nagrada",
                    value=f"**+$ {NAGRADA:,}** | Balans: $ {novi_balans:,}",
                    inline=False
                )
                embed.description = f"{ctx.author.mention} je pogodio/la riječ **{rijec.upper()}**! Bravo! 🏆"
                await ctx.send(embed=embed)
                del self.igre[cid]
            else:
                embed = self.napravi_embed(igra, naslov=f"✅ Tačno! Slovo `{slovo.upper()}`", boja=0x2ECC71)
                await ctx.send(embed=embed)
        else:
            igra['pogresna'].append(slovo)
            if len(igra['pogresna']) >= 6:
                embed = self.napravi_embed(igra, naslov="💀 Izgubio/la si!", boja=0xFF0000)
                embed.description = f"{ctx.author.mention} Nisi pogodio/la. Riječ je bila: **{rijec.upper()}**"
                await ctx.send(embed=embed)
                del self.igre[cid]
            else:
                embed = self.napravi_embed(igra, naslov=f"❌ Pogrešno! Slovo `{slovo.upper()}`", boja=0xFF6600)
                await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Vjesalo(bot))
