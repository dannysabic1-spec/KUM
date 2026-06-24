import discord
from discord.ext import commands
from cogs.ekonomija import dodaj_novac, get_balans

NAGRADA_PO_RIJECI = 10

class Kaladont(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.igre = {}

    def get_nastavak(self, rijec):
        rijec = rijec.lower().strip()
        return rijec[-2:] if len(rijec) >= 2 else rijec

    def normalize(self, rijec):
        return rijec.lower().strip()

    @commands.command(name='kaladont')
    async def kaladont(self, ctx, akcija: str = None):
        cid = ctx.channel.id

        if akcija and akcija.lower() == 'stop':
            if cid in self.igre:
                igra = self.igre[cid]
                ukupno = len(igra['koristene_rijeci'])
                del self.igre[cid]
                embed = discord.Embed(
                    title="🛑 Kaladont Završen",
                    description=f"Igra je završena.\nUkupno izgovorenih riječi: **{ukupno}**",
                    color=0x555555
                )
                embed.set_footer(text="Pokreni novu igru sa .kaladont")
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Nema aktivne igre Kaladont u ovom kanalu.")
            return

        if cid in self.igre:
            igra = self.igre[cid]
            if igra['zadnja_rijec']:
                sljedeci = self.get_nastavak(igra['zadnja_rijec'])
                embed = discord.Embed(
                    title="⚠️ Igra Već Aktivna!",
                    description=(
                        f"Kaladont je već u toku!\n"
                        f"Zadnja riječ: **{igra['zadnja_rijec'].capitalize()}**\n"
                        f"Sljedeća mora početi s: **{sljedeci.upper()}**"
                    ),
                    color=0xFF6600
                )
                await ctx.send(embed=embed)
            return

        self.igre[cid] = {
            'zadnja_rijec': None,
            'koristene_rijeci': [],
            'zadnji_igrac': None,
            'rezultati': {}
        }

        embed = discord.Embed(
            title="🎮 Kaladont — Igra Počela!",
            color=0x000000
        )
        embed.add_field(
            name="📜 Pravila",
            value=(
                "• Svaka nova riječ mora početi s **posljednja 2 slova** prethodne\n"
                "• Ne smiješ ponoviti već korištenu riječ\n"
                "• Ne smiješ igrati dva puta zaredom\n"
                f"• Svaka tačna riječ donosi **💵 $ {NAGRADA_PO_RIJECI}**"
            ),
            inline=False
        )
        embed.add_field(
            name="📝 Primjer",
            value="`Motika` → **KA**men → **EN**ergija → **JA**buka...",
            inline=False
        )
        embed.add_field(
            name="▶️ Počni",
            value="Napiši prvu riječ u chat!",
            inline=False
        )
        embed.set_footer(text=".kaladont stop — za završetak igre")
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.content.startswith('.'):
            return

        cid = message.channel.id
        if cid not in self.igre:
            return

        igra = self.igre[cid]
        rijec = message.content.strip()

        if len(rijec.split()) > 1 or not rijec.isalpha():
            return

        rijec_norm = self.normalize(rijec)

        if igra['zadnji_igrac'] == message.author.id:
            embed = discord.Embed(
                title="❌ Ne Možeš Igrati Dvaput!",
                description=f"{message.author.mention} Čekaj da neko drugi odigra.",
                color=0xFF0000
            )
            await message.channel.send(embed=embed)
            return

        if rijec_norm in igra['koristene_rijeci']:
            uid = str(message.author.id)
            zarade = igra['rezultati']
            embed = discord.Embed(
                title="💀 Ponovljena Riječ — Gubitak!",
                description=f"{message.author.mention} je rekao/la već korištenu riječ **{rijec.capitalize()}**!",
                color=0xFF0000
            )
            if zarade:
                opis_zarade = "\n".join([f"• Zaradio/la **$ {v:,}**" for k, v in zarade.items()])
                embed.add_field(name="💰 Zarade u igri", value=opis_zarade, inline=False)
            embed.set_footer(text="Pokreni novu igru sa .kaladont")
            await message.channel.send(embed=embed)
            del self.igre[cid]
            return

        if igra['zadnja_rijec'] is not None:
            ocekivani_pocetak = self.get_nastavak(igra['zadnja_rijec'])
            if not rijec_norm.startswith(ocekivani_pocetak):
                embed = discord.Embed(
                    title="❌ Pogrešan Početak — Gubitak!",
                    description=(
                        f"{message.author.mention} je izgubio/la!\n"
                        f"Trebalo je početi s **{ocekivani_pocetak.upper()}**\n"
                        f"Napisano: **{rijec.capitalize()}**"
                    ),
                    color=0xFF0000
                )
                embed.set_footer(text="Pokreni novu igru sa .kaladont")
                await message.channel.send(embed=embed)
                del self.igre[cid]
                return

        igra['koristene_rijeci'].append(rijec_norm)
        igra['zadnja_rijec'] = rijec_norm
        igra['zadnji_igrac'] = message.author.id

        uid = str(message.author.id)
        igra['rezultati'][uid] = igra['rezultati'].get(uid, 0) + NAGRADA_PO_RIJECI
        novi_balans = dodaj_novac(message.author.id, NAGRADA_PO_RIJECI)

        sljedeci = self.get_nastavak(rijec_norm)
        embed = discord.Embed(
            title="✅ Tačno!",
            color=0x2ECC71
        )
        embed.add_field(
            name="📝 Riječ",
            value=f"**{message.author.display_name}** → `{rijec.capitalize()}`",
            inline=True
        )
        embed.add_field(
            name="➡️ Sljedeća počinje s",
            value=f"**`{sljedeci.upper()}`**",
            inline=True
        )
        embed.add_field(
            name="💵 Zarada",
            value=f"+$ {NAGRADA_PO_RIJECI} | Ukupno: $ {novi_balans:,}",
            inline=False
        )
        embed.set_footer(text=f"Ukupno riječi: {len(igra['koristene_rijeci'])}")
        await message.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Kaladont(bot))
