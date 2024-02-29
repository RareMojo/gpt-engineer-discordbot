from discord.ext import commands
from utils.tools import update_with_discord
from discord_bot.terminal import welcome_to_bot
from discord_bot.logger import log_debug, log_error, log_info

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord_bot.bot import Bot


class CoreCog(commands.Cog, name="Core Cog", description="The core cog for the bot."):
    """Core Cog that handles the bot's core functionality."""

    def __init__(self, bot: "Bot"):
        """
        Initializes the CoreCog class.
        Args:
          bot (Bot): The bot instance.
        """
        self.bot = bot

    @commands.Cog.listener()
    async def on_connect(self):
        """Called when bot connects to Discord."""
        try:
            # Update Bot's status and activity, if applicable.
            await update_with_discord(self.bot)
            log_debug(self.bot, "Bot connected to Discord.")
        except Exception as e:
            log_error(self.bot, f"Error updating Bot: {e}")

    @commands.Cog.listener()
    async def on_ready(self):
        """Called when Bot is ready and connected to Discord."""
        try:
            await welcome_to_bot(self.bot)
            await self.bot.start_terminal_command_loop()
            log_debug(self.bot, "Bot is ready and connected to Discord.")
        except Exception as e:
            log_error(self.bot, f"Error welcoming Bot: {e}")

    @commands.Cog.listener()
    async def block_dms(self, ctx: commands.Context) -> bool:
        """
        Blocks DMs from the bot.
        Args:
          ctx (commands.Context): The context of the command.
        Returns:
          bool: True if the command is in a guild, False otherwise.
        """
        return ctx.guild is not None


async def setup(bot: "Bot") -> None:
    """Loads the cog."""
    try:
        await bot.add_cog(CoreCog(bot))
        log_debug(bot, "CoreCog loaded.")
    except Exception as e:
        log_error(bot, f"Error loading CoreCog: {e}")
