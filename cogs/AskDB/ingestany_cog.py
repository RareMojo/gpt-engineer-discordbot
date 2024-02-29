import sys
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from utils.ingest import ingestAny
from utils.mongo_db import MongoDBHandler
from discord_bot.logger import log_debug, log_error, log_info

if TYPE_CHECKING:
    from discord_bot.bot import Bot

embed_color_pending = 0xFD7C42
embed_color_success = discord.Color.brand_green()
embed_color_failure = discord.Color.brand_red()

sys.path.append("../")
handler = MongoDBHandler("askdb")


class IngestAnyCog(commands.Cog):
    """
    Cog for ingesting URLs.
    """

    def __init__(self, bot: "Bot"):
        """
        Initializes the IngestDBCog class.
        Args:
          bot (Bot): The Bot instance.
        """
        self.bot = bot

    @commands.hybrid_command()
    async def ingestany(self, ctx: commands.Context, url: str, db_name: str):
        """
        Ingests a URL.
        Args:
        ctx (commands.Context): The context of the command.
        url (str): The URL to ingest.
        db_name (str): The name of the db.
        Returns:
        discord.Embed: An embed containing the result of the ingestion.
        Examples:
        >>> await ctx.send(embed=await ingestdb(ctx, 'https://example.com', 'Example db'))
        Embed containing the result of the ingestion.
        """
        channel = ctx.channel
        allowed_roles = ["Contributor", "Moderator", "Administrator", "Developer", "Head Developer", "Super Admin", "BOT"]
        author_roles = [role.name for role in ctx.author.roles]
        
        if not any(role in allowed_roles for role in author_roles):
            await ctx.send(embed=discord.Embed(title="Error", color=embed_color_failure, description="You do not have permission to use this command."), ephemeral=True)
            return
        
        if channel.category.id != self.bot.chatbot_category_id:
            await ctx.send(embed=discord.Embed(title="Error", color=embed_color_failure, description="Please use this command in the 'AI' text-chat category."), ephemeral=True)
            return

        await ctx.defer(ephemeral=True)
        try:
            try:
                random_uuid = str(uuid.uuid4())
                embed = discord.Embed(
                    title="Ingesting URL",
                    type="rich",
                    description=f"\n *This might take a while*",
                    color=embed_color_pending,
                )
                await ctx.send(embed=embed, ephemeral=True)
                log_debug(
                    self.bot, f"Ingesting {url} as {db_name} for {ctx.author.name}"
                )
                await ingestAny(self.bot, url=url, namespace=random_uuid)
                current_time = datetime.now()
                handler.handle_data(
                    user_id=str(ctx.author.id),
                    user_name=str(ctx.author.name),
                    db_name=db_name,
                    db_id=random_uuid,
                    ingest_url=url,
                    ingested_time=current_time,
                )
                embed = discord.Embed(
                    title="Success",
                    description=f"{url}\n**DB Name:** `{db_name}`\n**DB ID:** `{random_uuid}`",
                    timestamp=current_time,
                    color=embed_color_success,
                )
                await ctx.send(embed=embed, ephemeral=True)
            except Exception as e:
                log_error(
                    self.bot,
                    f"Error ingesting {url} as {db_name} for {ctx.author.name}: {e}",
                )
                embed = discord.Embed(
                    title="Error", description=f"Error: {e}", color=embed_color_failure
                )
            else:
                pass
        except Exception as e:
            log_error(
                self.bot,
                f"Error ingesting {url} as {db_name} for {ctx.author.name}: {e}",
            )
            embed = discord.Embed(
                title="Error", description=f"Error: {e}", color=embed_color_failure
            )
            await ctx.send(embed=embed, ephemeral=True)


async def setup(bot: "Bot") -> None:
    """Loads the cog."""
    try:
        await bot.add_cog(IngestAnyCog(bot))
        log_debug(bot, "IngestAnyCog loaded.")
    except Exception as e:
        log_error(bot, f"Error loading IngestAnyCog: {e}")
