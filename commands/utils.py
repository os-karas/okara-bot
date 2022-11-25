import discord

from discord.ext import commands
from discord.embeds import Embed
from typing import Optional, Union

from contexts.all import GuildContext


class Utils(commands.Cog):
    """utilities Commands"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    async def ping(self, ctx: commands.Context):
        """Test bot latency"""
        await ctx.send(embed=Embed(
            title="pong",
            description=f"{self.bot.latency*1000:.0f}ms",
            color=discord.Color.dark_grey(),
        ))

    @commands.command(name="calc", aliases=["calculate", "calculator"])
    async def calculate(self, ctx: commands.Context, *, calc: str):
        """calculate math expressions"""

        if calc.__len__() > 50:
            raise commands.RangeError(calc, 1, 50)

        await ctx.send(embed=Embed(
            title=calc,
            description=eval(calc),
            color=discord.Color.dark_green()
        ))

    @calculate.error
    async def calculate_error(self, ctx: commands.Context, err: commands.CommandError):
        if isinstance(err, commands.CommandInvokeError):
            ctx.command_failed = False
            return await ctx.message.reply("Invalid calculation, enter a valid calculation.")

    @commands.command()
    @commands.guild_only()
    async def invite(self, ctx: GuildContext):
        """Create instant invite"""
        link = await ctx.channel.create_invite(max_uses=0, max_age=60 * 60)

        await ctx.send(f"{link}",
                       embed=Embed(title="obs.:",
                                   description="this invitation is only valid for 1 hour",
                                   color=discord.Color.yellow()))

    @commands.command(name="whoami", aliases=["who"])
    async def who_am_i(self, ctx: commands.Context, author: Optional[Union[discord.User, discord.Member]] = None):
        """Describes user"""
        author = author or ctx.author

        embed = Embed(color=author.color,
                      title=author)
        embed.set_image(url=author.banner)
        embed.set_thumbnail(
            url=author.display_avatar.url)

        embed.add_field(
            name="\U00002139 User Info",
            value=f"""
                **User Id:** {author.id}
                **Name:** {author.name}
                **Created:** {author.created_at.strftime('%d/%m/%Y %H:%M')}

            """,
            inline=False
        )

        if isinstance(author, discord.member.Member):
            embed.add_field(
                name="\U0001F464 Member Info",
                value=f"""
                    {f"**Joined:** {author.joined_at.strftime('%d/%m/%Y %H:%M')}" if author.joined_at else ""}
                    {f"**Nick:** {author.nick}" if author.nick else ""}
                    **Top Role:** {author.top_role.name if author.top_role.name.startswith("@") else author.top_role.mention}
                    **Roles:**
                    {", ".join(
                        map(
                            lambda role: role.name if role.name.startswith("@") else role.mention,
                            author.roles
                            ))}

                """,
                inline=False
            )

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Utils(bot))
