import asyncio
from typing import TYPE_CHECKING

from discord_bot.terminal_cmds import (exit_bot_terminal, ping, set_bot_avatar,
                                       set_bot_name, set_bot_presence,
                                       set_default_db_id, set_owner,
                                       set_persona, show_aliases, show_help,
                                       sync_commands, toggle_debug_mode,
                                       wipe_config, toggle_show_source_documents)

if TYPE_CHECKING:
    from discord_bot.bot import Bot


async def welcome_to_bot(bot: "Bot") -> None:
    """
    Prints bot instance details and a welcome message.
    Args:
      bot (Bot): The bot instance.
    Returns:
      None
    Examples:
      >>> welcome_to_bot(bot)
      Bot Instance Details:
      Display name: BotName
      Presence: Playing a game
      Linked with Guild | ID: 123456789
      Bot is online and ready.
      Welcome to BotName!
      Be sure to check out the documentation at the GitHub repository.
      Type 'help' for a list of terminal commands.
    """
    bot_name = bot.config.get("bot_name")
    presence = bot.config.get("presence")
    owner_name = bot.config.get("owner_name")

    try:
        bot.log.debug("Starting welcome_to_bot function...")
        bot.log.info("Bot Instance Details:")
        bot.log.info(f"Display name: {bot_name}")
        bot.log.info(f"Presence: {presence}")

        for guild in bot.guilds:
            bot.log.info(f"Linked with {guild} | ID: {guild.id}")

        bot.log.info("Bot is online and ready.")

        if bot.config.get("update_bot") == False:
            bot.log.info(f"Welcome back to {bot_name}, {owner_name}!")
            bot.log.info("Type 'help' for a list of terminal commands.")
        else:
            bot.log.info(f"Welcome to {bot_name}!")
            bot.log.info(
                "Be sure to check out the documentation at the GitHub repository."
            )
            bot.log.info("Type 'help' for a list of terminal commands.")

    except Exception as e:
        bot.log.error(f"Error in welcome_to_bot function: {e}")
        

async def terminal_command_loop(bot: "Bot"):
    """
    Runs a loop to handle terminal commands.
    Args:
      bot (Bot): The bot instance.
    Returns:
      None
    Examples:
      >>> await terminal_command_loop(bot)
    """
    owner_name = bot.config.get("owner_name")
    bot_name = bot.config.get("bot_name")
    loop = asyncio.get_event_loop()
    delay = 0.25
    black = "\x1b[30m"
    red = "\x1b[31m"
    purple = "\x1b[35m"
    cyan = "\x1b[36m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    gray = "\x1b[38m"
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    while bot.running:
        await asyncio.sleep(delay)
        terminal_format = f"{bold}{green}{owner_name}{reset}{bold}{black}@{reset}{bold}{purple}{bot_name}{reset}"
        terminal_prompt = f"{terminal_format}{black}{bold}: > {reset}"

        terminal_command = loop.run_in_executor(None, input, terminal_prompt)

        command_handler = TerminalCommands(bot, await terminal_command)
        await command_handler.handle_terminal_command()

class TerminalCommands:
    """
    Initializes the TerminalCommands class.
    Args:
      bot (Bot): The bot instance.
      terminal_command (str): The terminal command to handle.
    """

    def __init__(self, bot: "Bot", terminal_command: str):
        """
        Initializes the TerminalCommands class.
        Args:
          bot (Bot): The bot instance.
          terminal_command (str): The terminal command to handle.
        """
        self.bot = bot
        self.terminal_command = terminal_command

    async def handle_terminal_command(self):
        """
        Handles the terminal command.
        Returns:
          None
        Side Effects:
          Executes the command specified by the terminal command.
        Examples:
          >>> handle_terminal_command("ping")
          Pinging...
        """
        user_command = self.terminal_command.lower()
        self.bot.log.info("Received command: {}".format(user_command))

        if user_command in ["exit", "quit", "shutdown"]:
            self.bot.log.debug("Exiting bot terminal...")
            exit_bot_terminal(self.bot)

        elif user_command in ["help", "h", "?"]:
            self.bot.log.debug("Showing help...")
            show_help(self.bot)

        elif user_command in ["ping", "p"]:
            self.bot.log.debug("Pinging...")
            ping(self.bot)

        elif user_command in ["setbotname", "setbot", "sbn"]:
            self.bot.log.debug("Setting bot name...")
            await set_bot_name(self.bot)

        elif user_command in ["setpresence", "setpres", "sp"]:
            self.bot.log.debug("Setting bot presence...")
            await set_bot_presence(self.bot)

        elif user_command in ["setavatar", "setava", "sa"]:
            self.bot.log.debug("Setting bot avatar...")
            await set_bot_avatar(self.bot)

        elif user_command in ["setowner", "setown"]:
            self.bot.log.debug("Setting owner...")
            await set_owner(self.bot)
            
        elif user_command in ["setpersona", "persona", "setper", "sp"]:
            self.bot.log.debug("Setting bot persona...")
            await set_persona(self.bot)
        
        elif user_command in ["reload", "sync", "r"]:
            self.bot.log.debug("Syncing commands...")
            await sync_commands(self.bot)

        elif user_command in ["wipebot", "wipeconfig", "wipe", "wb"]:
            self.bot.log.debug("Wiping bot config...")
            wipe_config(self.bot)

        elif user_command in ["alias", "aliases", "a"]:
            self.bot.log.debug("Showing aliases...")
            show_aliases(self.bot)

        elif user_command in ["debug", "d"]:
            self.bot.log.debug("Toggling debug mode...")
            toggle_debug_mode(self.bot)
            
        elif user_command in ["setdb", "defaultdb", "dbd", "dbid"]:
            self.bot.log.debug("Setting default DB ID...")
            set_default_db_id(self.bot)
            
        elif user_command in ["showsource", "showsrc", "src"]:
            self.bot.log.debug("Toggling show source documents...")
            toggle_show_source_documents(self.bot)

        else:
            self.bot.log.info(f"{user_command} is not a recognized command.")
