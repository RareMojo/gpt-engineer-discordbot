from __future__ import annotations

import time
from typing import TYPE_CHECKING, Optional

import discord
from discord.ext import commands

from utils.ai import ChatAgent
from discord_bot.logger import log_debug, log_error, log_info
from utils.tools import split_chat

if TYPE_CHECKING:
    from discord_bot.bot import Bot


class ChatbotCog(
    commands.Cog, name="Chatbot Cog", description="LangChain + ChatGPT integration."
):
    """
    Be sure to set above to your .env file. Don't share these keys.
    Simply type in the apropriate channel to talk to the bot.
    There is a built in rate limiter.

    WARNING: BEWARE OF ANY POSSIBLE OUTPUTS, AND MONITOR API USAGE. WE ARE NOT RESPONSIBLE FOR YOUR ACTIONS. BE SAFE.
    """

    def __init__(self, bot: "Bot"):
        """
        Initializes the ChatbotCog class.
        Args:
          bot (Bot): The Bot object.
        Side Effects:
          Sets the guild_id, chatbot_threads_id, category_id, _cd, and embed_color attributes.
        Notes:
          Be sure to set the appropriate environment variables.
        Examples:
          >>> ChatbotCog(bot)
          Initializes the ChatbotCog class.
        """
        self.bot = bot
        self.guild_id = self.bot.guild_id
        self.chatbot_threads_id = bot.chatbot_threads_id
        self.category_id = bot.chatbot_category_id
        self._cd = commands.CooldownMapping.from_cooldown(
            1, 3.0, commands.BucketType.member
        )
        self.embed_color = discord.Color.brand_green()

    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread):
        """Called when a thread is created."""
        time.sleep(0.25)
        persona = self.bot.config.get("persona")

        if thread.parent.id == self.bot.chatbot_threads_id:
            reply = (
                f"Hello {thread.owner.mention}, please stay in this thread. "
                f"\nDo not ping people in `{thread.name}` and do not make duplicates. "
                f"\n\nIf `{persona}` does not respond to your thread within 1 minute or has an error, try again. "
                f"\n\nPlease **do not spam** the bot. If it still does not work ping an `Admin`. "
            )
            embeds = discord.Embed(
                title=f"{persona}Bot", description=reply, color=self.embed_color
            )
            await thread.send(embed=embeds)
            log_debug(self.bot, f"Chatbot thread created: {thread.name}")

    @commands.Cog.listener()
    async def on_message(self, ctx: discord.Message):
        """
        Listens for messages and responds with a Chat-GPT response.
        Args:
          ctx (discord.Message): The message context.
        Side Effects:
          Sets the channel_id attribute of the ChatbotCog instance.
        Notes:
          There is a built in rate limiter.
        Examples:
          >>> on_message(ctx)
        """
        chat_agents = {}
        chatbot = self.bot.user
        prompt = str(ctx.content)
        user = str(ctx.author.display_name)

        channel = ctx.channel
        self.channel_id = channel.id
        mentioned = False

        if prompt.startswith(self.bot.config.get("prefix")):
            return

        if ctx.guild != self.guild_id:
            ratelimit = self.get_ratelimit(ctx)
            supported_channel = self.category_id
            self.channel_id = (
                ctx.channel.category_id
                if isinstance(ctx.channel, discord.Thread)
                else ctx.channel.id
            )

            if chatbot in ctx.mentions:
                mentioned = True

            if self.channel_id != supported_channel or mentioned:
                return

            if not (ctx.author.bot):
                waiting = True

                if ratelimit is None or ratelimit < 0:
                    log_debug(self.bot, "Sending message to Chat-GPT...")

                    async with channel.typing():
                        while waiting:
                            if self.channel_id not in chat_agents:
                                chat_agents[self.channel_id] = ChatAgent(
                                    self.bot, self.channel_id
                                )

                            chat_agent = chat_agents[self.channel_id]
                            log_debug(self.bot, f"Prompt: {prompt}, User: {user}, Channel: {channel}")
                            messages = chat_agent.predict(prompt)

                            if not messages:
                                raise ValueError("No response received from the agent.")

                            log_debug(self.bot, "Received response from OpenAI.")

                            response = messages
                            response_chunks = split_chat(response)

                            if response_chunks is None:
                                waiting = False
                                log_debug(self.bot, "No response from Chat-GPT API.")
                                return

                            for chunk in response_chunks:
                                if channel is not None:
                                    await channel.send(chunk)
                                    time.sleep(0.33)
                            else:
                                waiting = False
                else:
                    rate_response = f"You are talking too fast, {user}"
                    waiting = False
                    log_debug(
                        self.bot,
                        f"User {user} is talking too fast. Rate limit: {ratelimit}",
                    )
                    await channel.send(rate_response)
                    return

    def get_ratelimit(self, message: discord.Message) -> Optional[float]:
        """
        Gets the rate limit for a given message.
        Args:
          message (discord.Message): The message context.
        Returns:
          Optional[float]: The rate limit for the given message.
        Examples:
          >>> get_ratelimit(message)
          0.5
        """
        bucket = self._cd.get_bucket(message)
        if bucket is None:
            return
        return bucket.update_rate_limit()


async def setup(bot: "Bot") -> None:
    """Loads the cog."""
    try:
        await bot.add_cog(ChatbotCog(bot))
        log_debug(bot, "ChatbotCog loaded.")
    except Exception as e:
        log_error(bot, f"Error loading ChatbotCog: {e}")
