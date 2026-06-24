import discord
from discord.ext import commands
import json
import os
import re
import asyncio

BAN_FAJL = "data/bans.json"
INVITE_REGEX = re.compile(
    r'(discord\.gg|discord\.com\/invite|discordapp\.com\/invite)[/\\]([a-zA-Z0-9\-]+)',
    re.IGNORECASE
)

def ucitaj_banove():
    if not os.path.exists(BAN_FAJL):
        return {}
    with open(BAN_FAJL, 'r') as f:
        return json.load(f)

def sacuvaj_banove(podaci):
    os.makedirs("data", exist_ok=True)
    with open(BAN_FAJL, 'w') as f:
        json.dump(podaci, f, indent=2)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        if message.author.guild_permissions.administrator:
            return
        if message.author.guild_permissions.manage_messages:
            return

        if INVITE_REGEX.search(message.content):
            try:
                await message.delete()
                embed = discord.Embed(
                    title="🚫 Invite Link Uklonjen",
                    description=(
                        f"{message.author.mention} slanje invite linkova nije dozvoljeno!\n"
                        f"Ovo upozorenje je zabilježeno."
                    ),
                    color=0xFF0000
                )
                embed.set_footer(text="Ova poruka se briše za 5 sekundi")
                upozorenje = await message.channel.send(embed=embed)
                await asyncio.sleep(5)
                await upozorenje.delete()
            except discord.Forbidden:
                pass

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        podaci = ucitaj_banove()
        kljuc = str(guild.id)
        if kljuc not in podaci:
            podaci[kljuc] = {}

        podaci[kljuc][str(user.id)] = podaci[kljuc].get(str(user.id), 0) + 1
        sacuvaj_banove(podaci)
        ban_br = podaci[kljuc][str(user.id)]

        if ban_br >= 5:
            uloga = discord.utils.get(guild.roles, name="Kažnjen")
            if not uloga:
                try:
                    uloga = await guild.create_role(
                        name="Kažnjen",
                        color=discord.Color.dark_red(),
                        reason="Auto-kreirana za višestruke banove"
                    )
                except discord.Forbidden:
                    pass

            member = guild.get_member(user.id)
            if member and uloga:
                try:
                    for r in member.roles[1:]:
                        if not r.managed:
                            await member.remove_roles(r, reason="5+ banovi")
                    await member.add_roles(uloga, reason="5+ banovi")
                except discord.Forbidden:
                    pass

            log_kanal = discord.utils.get(guild.text_channels, name='mod-log')
            if log_kanal:
                embed = discord.Embed(
                    title="⚠️ Višestruki Ban — Automatska Akcija",
                    color=0xFF0000
                )
                embed.add_field(name="👤 Korisnik", value=f"{user.mention} (`{user}`)", inline=True)
                embed.add_field(name="🔨 Broj Banova", value=f"**{ban_br}**", inline=True)
                embed.add_field(
                    name="⚡ Akcija",
                    value="Sve uloge uklonjene\nDodana uloga **Kažnjen**",
                    inline=False
                )
                embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
                embed.set_footer(text="Automatska moderacija")
                await log_kanal.send(embed=embed)

    @commands.command(name='brojanje')
    async def brojanje(self, ctx):
        guild = ctx.guild
        ukupno = guild.member_count
        clanovi = sum(1 for m in guild.members if not m.bot)
        botovi = sum(1 for m in guild.members if m.bot)
        online = sum(1 for m in guild.members if m.status != discord.Status.offline and not m.bot)
        offline = sum(1 for m in guild.members if m.status == discord.Status.offline and not m.bot)
        dnd = sum(1 for m in guild.members if m.status == discord.Status.dnd and not m.bot)
        idle = sum(1 for m in guild.members if m.status == discord.Status.idle and not m.bot)

        embed = discord.Embed(
            title=f"👥 Statistike Servera",
            description=f"**{guild.name}**",
            color=0x000000
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(name="👤 Ukupno", value=f"**{ukupno:,}**", inline=True)
        embed.add_field(name="🧑 Korisnici", value=f"**{clanovi:,}**", inline=True)
        embed.add_field(name="🤖 Botovi", value=f"**{botovi:,}**", inline=True)
        embed.add_field(name="🟢 Online", value=f"**{online:,}**", inline=True)
        embed.add_field(name="🌙 Idle", value=f"**{idle:,}**", inline=True)
        embed.add_field(name="🔴 Ne uznemiravaj", value=f"**{dnd:,}**", inline=True)
        embed.add_field(name="⚫ Offline", value=f"**{offline:,}**", inline=True)
        embed.set_footer(text=f"Server ID: {guild.id}")
        await ctx.send(embed=embed)

    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, korisnik: discord.Member, *, razlog: str = "Nije naveden razlog"):
        if korisnik == ctx.author:
            await ctx.send("❌ Ne možeš banati samog/samu sebe!")
            return
        if korisnik.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ Ne možeš banati korisnika s višim ili jednakim rangom!")
            return

        try:
            await korisnik.send(
                f"🔨 Banovan/a si sa servera **{ctx.guild.name}**.\nRazlog: **{razlog}**"
            )
        except Exception:
            pass

        await ctx.guild.ban(korisnik, reason=f"{razlog} | Banao: {ctx.author}")
        embed = discord.Embed(title="🔨 Korisnik Banovan", color=0xFF0000)
        embed.set_thumbnail(url=korisnik.avatar.url if korisnik.avatar else None)
        embed.add_field(name="👤 Korisnik", value=f"{korisnik.mention} (`{korisnik}`)", inline=True)
        embed.add_field(name="📝 Razlog", value=razlog, inline=True)
        embed.set_footer(text=f"Moderator: {ctx.author.display_name}")
        await ctx.send(embed=embed)

    @commands.command(name='unban')
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        try:
            await ctx.guild.unban(discord.Object(id=user_id))
            embed = discord.Embed(
                title="✅ Korisnik Odbanovan",
                description=f"Korisnik sa ID `{user_id}` je odbanovan.",
                color=0x2ECC71
            )
            await ctx.send(embed=embed)
        except discord.NotFound:
            await ctx.send(f"❌ Korisnik sa ID `{user_id}` nije pronađen u banovaniima.")

    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, korisnik: discord.Member, *, razlog: str = "Nije naveden razlog"):
        if korisnik == ctx.author:
            await ctx.send("❌ Ne možeš kickati samog/samu sebe!")
            return
        try:
            await korisnik.send(
                f"👢 Izbačen/a si sa servera **{ctx.guild.name}**.\nRazlog: **{razlog}**"
            )
        except Exception:
            pass
        await korisnik.kick(reason=f"{razlog} | Kickao: {ctx.author}")
        embed = discord.Embed(title="👢 Korisnik Izbačen", color=0xFF6600)
        embed.set_thumbnail(url=korisnik.avatar.url if korisnik.avatar else None)
        embed.add_field(name="👤 Korisnik", value=f"{korisnik.mention}", inline=True)
        embed.add_field(name="📝 Razlog", value=razlog, inline=True)
        embed.set_footer(text=f"Moderator: {ctx.author.display_name}")
        await ctx.send(embed=embed)

    @commands.command(name='mute')
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, korisnik: discord.Member, *, razlog: str = "Nije naveden razlog"):
        uloga = discord.utils.get(ctx.guild.roles, name="Ućutao")
        if not uloga:
            try:
                uloga = await ctx.guild.create_role(name="Ućutao", color=discord.Color.dark_gray())
                for kanal in ctx.guild.channels:
                    try:
                        await kanal.set_permissions(uloga, send_messages=False, speak=False, add_reactions=False)
                    except Exception:
                        pass
            except discord.Forbidden:
                await ctx.send("❌ Nemam dozvolu za kreiranje uloge!")
                return

        if uloga in korisnik.roles:
            await ctx.send(f"⚠️ {korisnik.mention} je već ućutat/a!")
            return

        await korisnik.add_roles(uloga, reason=razlog)
        embed = discord.Embed(title="🔇 Korisnik Ućutat", color=0x808080)
        embed.add_field(name="👤 Korisnik", value=korisnik.mention, inline=True)
        embed.add_field(name="📝 Razlog", value=razlog, inline=True)
        embed.set_footer(text=f"Moderator: {ctx.author.display_name}")
        await ctx.send(embed=embed)

    @commands.command(name='unmute')
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, korisnik: discord.Member):
        uloga = discord.utils.get(ctx.guild.roles, name="Ućutao")
        if uloga and uloga in korisnik.roles:
            await korisnik.remove_roles(uloga)
            embed = discord.Embed(
                title="🔊 Korisnik Odućutat",
                description=f"{korisnik.mention} može opet pisati.",
                color=0x2ECC71
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ {korisnik.mention} nije ućutat/a!")

    @commands.command(name='clear')
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, broj: int = 10):
        if not (1 <= broj <= 100):
            await ctx.send("❌ Broj mora biti između **1** i **100**!")
            return
        obrisano = await ctx.channel.purge(limit=broj + 1)
        embed = discord.Embed(
            title="🗑️ Poruke Obrisane",
            description=f"Obrisano **{len(obrisano) - 1}** poruka.",
            color=0x2ECC71
        )
        potvrda = await ctx.send(embed=embed)
        await asyncio.sleep(3)
        await potvrda.delete()

    @commands.command(name='banovi')
    @commands.has_permissions(manage_guild=True)
    async def banovi(self, ctx, korisnik: discord.Member = None):
        podaci = ucitaj_banove()
        kljuc = str(ctx.guild.id)

        if not podaci.get(kljuc):
            await ctx.send("📋 Nema zabilježenih banova na ovom serveru.")
            return

        if korisnik:
            br = podaci[kljuc].get(str(korisnik.id), 0)
            embed = discord.Embed(
                title=f"📋 Banovi — {korisnik.display_name}",
                color=0xFF0000
            )
            embed.set_thumbnail(url=korisnik.avatar.url if korisnik.avatar else None)
            embed.add_field(name="🔨 Broj Banova", value=f"**{br}**", inline=True)
            embed.add_field(
                name="⚠️ Status",
                value="🔴 Opasnost (5+)" if br >= 5 else ("🟡 Upozorenje" if br >= 3 else "🟢 Nizak"),
                inline=True
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="📋 Lista Banova — Top 10", color=0xFF0000)
            opis = ""
            sortirano = sorted(podaci[kljuc].items(), key=lambda x: x[1], reverse=True)[:10]
            for i, (uid, br) in enumerate(sortirano, 1):
                status = "🔴" if br >= 5 else ("🟡" if br >= 3 else "🟢")
                try:
                    user = await self.bot.fetch_user(int(uid))
                    ime = str(user)
                except Exception:
                    ime = f"ID: {uid}"
                opis += f"**{i}.** {status} {ime} — **{br}** banova\n"
            embed.description = opis or "Nema podataka."
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
