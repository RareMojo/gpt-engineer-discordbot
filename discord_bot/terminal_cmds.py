import json
import logging
import traceback
from typing import TYPE_CHECKING

import discord

from utils.tools import get_boolean_input, update_config

if TYPE_CHECKING:
    from discord_bot.bot import Bot


# Terminal Commands Functions


def toggle_debug_mode(bot: "Bot") -> None:
    """
    Toggles debug mode.
    Args:
      bot (Bot): The bot instance.
    Returns:
      None
    Side Effects:
      Updates the config file.
    Examples:
      >>> toggle_debug_mode(bot)
    """
    config_file = bot.config_file

    with open(config_file, "r") as f:
        config = json.load(f)

    try:
        if config.get("log_level") == "DEBUG":
            bot.log.info("Disabling debug mode...")

            try:
                new_data = {"log_level": "INFO"}
                update_config(config_file, new_data)

            except Exception as e:
                bot.log.debug(f"Failed to update the configuration file: {e}")
                return bot.log.warning("Failed to disable debug mode.")

            bot.log.info("Restarting to apply changes...")

        else:
            bot.log.info("Enabling debug mode...")

            try:
                new_data = {"log_level": "DEBUG"}
                update_config(config_file, new_data)

            except Exception as e:
                bot.log.debug(f"Failed to update the configuration file: {e}")
                return bot.log.warning("Failed to enable debug mode.")

            bot.log.setLevel(logging.DEBUG)
            bot.log.info("Restarting to apply changes...")

        input("Press ENTER to EXIT.")
        bot.stop_bot()

    except FileNotFoundError:
        bot.log.warning(f"Config file {bot.config} not found.")
    except KeyError:
        bot.log.warning(f"Key not found in config file {bot.config}.")
    except Exception as e:
        bot.log.warning(f"An error occurred while toggling debug mode: {e}")
    else:
        bot.log.debug("Debug mode toggled successfully.")


def wipe_config(bot: "Bot") -> None:
    """
    Wipes the config file and shuts down the bot.
    Args:
      bot (Bot): The bot instance.
    Returns:
      None
    Side Effects:
      Wipes the config file and shuts down the bot.
    Examples:
      >>> wipe_config(bot)
    """
    try:
        bot.log.warning("This will wipe the config file and shut down Bot.")
        wipe = get_boolean_input(bot, "Do you want to wipe the config file? (y/n) ")

        if wipe == True:
            wipe_confirm = get_boolean_input(
                bot, "Are you sure you want to wipe config and restart? (y/n) "
            )

            if wipe_confirm == True:
                with open(bot.config_file, "w") as f:
                    f.write("")

                bot.log.info("Config file wiped.")
                bot.log.warning("Bot will now shut down.")
                exit_bot_terminal(bot)

            else:
                bot.log.info("Config file not wiped.")

        else:
            bot.log.info("Config file not wiped.")

    except FileNotFoundError as e:
        bot.log.debug(f"Config file not found: {e}")
    except Exception as e:
        bot.log.error(f"An error occurred while wiping the config file: {e}")


def exit_bot_terminal(bot: "Bot") -> None:
    """
    Shuts down the bot.
    Args:
      bot (Bot): The bot instance.
    Returns:
      None
    Examples:
      >>> exit_bot_terminal(bot)
    """
    try:
        bot.log.debug("Shutting down Bot...")
        bot.stop_bot()
    except Exception as e:
        bot.log.error(f"Error shutting down Bot: {e}")


async def set_bot_name(bot: "Bot") -> None:
    """
    Sets the bot name.
    Args:
      bot (Bot): The bot instance.
    Returns:
      None
    Examples:
      >>> await set_bot_name(bot)
    """
    config_file = bot.config_file

    with open(config_file, "r") as f:
        config = json.load(f)

    try:
        bot.log.debug("Setting bot name...")
        bot.log.info(f"Current name: {config.get('bot_name')}")
        change_bot_name = get_boolean_input(
            bot, "Do you want to change the bot name? (y/n) "
        )

        if change_bot_name == True:
            new_name = input("Enter new bot name: ")

            try:
                await bot.user.edit(username=new_name)
                bot.log.info(
                    "Config change, bot_name: {} -> {}".format(
                        config.get("bot_name"), new_name
                    )
                )

                with open(bot.config_file, "w") as f:
                    config.set("bot_name", new_name)
                    config.write(f)

            except Exception as e:
                bot.log.error("Error: {}".format(e))
                bot.log.warning("Bot name not changed on Discord servers.")
        else:
            bot.log.info("Name not changed.")

    except Exception as e:
        bot.log.error("Error: {}".format(e))
        traceback.print_exc()


async def set_bot_avatar(bot: "Bot") -> None:
    """
    Sets the bot avatar.
    Args:
      bot (Bot): The bot instance.
    Returns:
      None
    Examples:
      >>> await set_bot_avatar(bot)
    """
    try:
        config_file = bot.config_file
        bot.log.debug("Setting bot avatar...")
        bot.log.info(
            "This sets the avatar to the image at ../resources/images/avatar.png"
        )
        change_avatar = get_boolean_input(
            bot, "Do you want to change the avatar? (y/n) "
        )
        successful = True

        with open(bot.avatar_file, "rb") as f:
            new_avatar = f.read()

        if change_avatar == True:
            try:
                await bot.user.edit(avatar=new_avatar)
            except Exception as e:
                bot.log.error("Error: {}".format(e))
                bot.log.warning("Avatar not changed on Discord servers.")
                bot.log.warning("It will automatically be changed on the next startup.")
                successful = False

            if successful == True:
                try:
                    new_data = {"update_bot": True}
                    update_config(config_file, new_data)
                except Exception as e:
                    bot.log.debug(f"Failed to update the configuration file: {e}")
                    return bot.log.warning("Failed to set update flag.")

            if successful == True:
                bot.log.info("Avatar changed.")
        else:
            bot.log.info("Avatar not changed.")

    except Exception as e:
        bot.log.error("Error: {}".format(e))


async def set_bot_presence(bot: "Bot") -> None:
    """
    Sets the bot presence.
    Args:
      bot (Bot): The bot instance.
    Returns:
      None
    Examples:
      >>> await set_bot_presence(bot)
    """
    try:
        config_file = bot.config_file
        with open(config_file, "r") as f:
            config = json.load(f)

        bot.log.info("Current presence: {}".format(config.get("presence")))
        update_presence = get_boolean_input(
            bot, "Do you want to change the presence? (y/n) "
        )

        if update_presence == True:
            new_presence = input("Enter new presence: ")

            try:
                new_data = {"update_bot": True, "presence": new_presence}
                update_config(config_file, new_data)

            except Exception as e:
                bot.log.debug(f"Failed to update the configuration file: {e}")
                return bot.log.warning("Failed to set update flag.")

            try:
                await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=new_presence))
                bot.log.info(
                    "Config change, presence: {} -> {}".format(
                        config.get("presence"), new_presence
                    )
                )

            except Exception as e:
                bot.log.error("Error: {}".format(e))
                bot.log.warning("Presence not changed.")
        else:
            bot.log.info("Presence not changed.")

    except Exception as e:
        bot.log.debug(f"Error in set_bot_presence: {traceback.format_exc()}")
        bot.log.error(f"Error in set_bot_presence: {e}")


async def sync_commands(bot: "Bot") -> None:
    """
    Synchronizes commands with Discord.
    Args:
      bot (Bot): The bot instance.
    Returns:
      None
    Examples:
      >>> await sync_commands(bot)
    """
    bot.log.debug("Synchronizing commands...")

    try:
        config = bot.config
        bot.log.debug("Synchronizing commands...")
        synchronize = get_boolean_input(
            bot, "Do you want to synchronize commands? (y/n) "
        )

        if synchronize == True:
            # Try to update commands on Discord servers.
            bot.log.debug("Updating commands on Discord servers...")
            sync_list = await bot.tree.sync()
            bot.log.info(f"{len(sync_list)} commands synchronized.")
            config["update_bot"] = True
        else:
            bot.log.info("Commands not synchronized.")

    except Exception as e:
        bot.log.error(f"Error in sync_commands: {e}")
        bot.log.error("Commands not synchronized.")


async def set_owner(bot: "Bot") -> None:
    """
    Sets the owner of the bot.
    Args:
      bot (Bot): The bot instance.
    Returns:
      None
    Examples:
      >>> await set_owner(bot)
    """
    try:
        config_file = bot.config_file

        with open(config_file, "r") as f:
            config = json.load(f)

        bot.log.info(
            f"Current owner: {config.get('owner_name')}"
        )
        change_owner_name = get_boolean_input(
            bot, "Do you want to change bot owner? (y/n) "
        )

        if change_owner_name == True:
            new_owner_name = input("Enter new owner name: ")

            try:
                new_data = {
                    "update_bot": True,
                    "owner_name": new_owner_name,
                }
                update_config(config_file, new_data)

            except Exception as e:
                bot.log.debug(f"Failed to update the configuration file: {e}")
                return bot.log.warning("Failed to set update flag.")

            bot.log.info(
                "Config change, owner_name: {} -> {}".format(
                    config.get("owner_name"), new_owner_name
                )
            )
        else:
            bot.log.info("Owner not changed.")

    except Exception as e:
        bot.log.error(f"Error in set_owner function: {e}")


async def set_persona(bot: "Bot") -> None:
    """
    Sets the persona of the bot.
    Args:
      bot (Bot): The bot instance.
    Returns:
      None
    Examples:
      >>> await set_persona(bot)
    """
    try:
        config_file = bot.config_file

        with open(config_file, "r") as f:
            config = json.load(f)

        bot.log.info(
            f"Current persona: {config.get('persona')}"
        )
        change_persona = get_boolean_input(
            bot, "Do you want to change bot persona? (y/n) "
        )

        if change_persona == True:
            new_persona = input("Enter new persona name: ")

            try:
                new_data = {
                    "persona": new_persona,
                }
                update_config(config_file, new_data)

            except Exception as e:
                bot.log.debug(f"Failed to update the configuration file: {e}")
                return bot.log.warning("Failed to set update flag.")

            bot.log.info(
                "Config change, persona: {} -> {}".format(
                    config.get("persona"), new_persona
                )
            )
        else:
            bot.log.info("Persona not changed.")

    except Exception as e:
        bot.log.error(f"Error in set_persona function: {e}")


def show_help(bot: "Bot") -> None:
    """
    Displays a list of available commands.
    Args:
      bot (Bot): The bot instance.
    Returns:
      None
    Examples:
      >>> show_help(bot)
    """
    black = "\u001b[30m"
    cyan = "\u001b[36m"
    green = "\u001b[32m"
    purple = "\u001b[35m"
    bold = "\u001b[1m"
    reset = "\u001b[0m"
    commands = {
        "exit": "Shuts Bot and the script down.",
        "help": "Displays this message.",
        "ping": "Pongs.",
        "setbotname": "Changes the current Bot name.",
        "setpresence": "Changes the current Bot presence.",
        "setavatar": "Changes the current Bot avatar.",
        "setowner": "Sets the owner of the bot.",
        "setpersona": "Sets the persona of the bot.",
        "reload": "Synchronizes commands with Discord.",
        "wipebot": 'Wipes the bot"s configuration files.',
        "aliases": "Lists all command aliases.",
        "debug": "Toggles debug mode.",
        "setdb": "Sets the default DB ID for AskDB.",
        "showsource": "Toggles showing source documents.",
    }

    try:
        bot.log.debug("Starting show_help function...")
        bot.log.info(
            f"{black}{'-' * 24}[ {purple}{bold}Available commands{reset}{black} ]{'-' * 24}{reset}"
        )
        bot.log.info("")
        bot.log.info(
            f"{cyan}Simply type the command you want to execute and press enter.{reset}"
        )
        bot.log.info(
            f"{cyan}A brief description of the command will be displayed below.{reset}"
        )
        bot.log.info("")

        for command, description in commands.items():
            bot.log.info(
                f"{green}{command}{' ' * (30 - len(command))}{black}- {description}{' ' * (45 - len(description))}{reset}"
            )
        bot.log.info("")
        bot.log.info(
            f"{black}{'-' * 22}[ {purple}{bold}End available commands{reset}{black} ]{'-' * 22}{reset}"
        )
        bot.log.debug("Exiting show_help function...")

    except Exception as e:
        bot.log.error(f"Error in show_help function: {e}")
        traceback.print_exc()


def show_aliases(bot: "Bot") -> None:
    """
    Prints a list of command aliases.
    Args:
      bot (Bot): The bot instance.
    Side Effects:
      Prints a list of command aliases to the console.
    Examples:
      >>> show_aliases(bot)
    """
    black = "\u001b[30m"
    purple = "\u001b[35m"
    green = "\u001b[32m"
    bold = "\u001b[1m"
    reset = "\u001b[0m"
    aliases = {
        "exit": ["quit", "shutdown"],
        "help": ["h", "?"],
        "ping": ["p"],
        "setbotname": ["setbot", "sbn"],
        "setpresence": ["setbotpres", "sbp"],
        "setavatar": ["setava", "sba"],
        "setowner": ["setown"],
        "setpersona": ["setper", "persona", "sp"],
        "reload": ["sync", "r"],
        "wipebot": ["wipeconfig", "wipe", "wb"],
        "alias": ["aliases", "a"],
        "debug": ["d"],
        "setdb": ["defaultdb", "dbd", "dbid"],
        "showsource": ["showsrc", "src"],
    }

    try:
        bot.log.debug("Starting show_aliases function...")
        bot.log.info(
            f"{black}{'-' * 24}[ {purple}{bold}Command Aliases{reset}{black} ]{'-' * 24}{reset}"
        )
        bot.log.info("")

        for command, alias_list in aliases.items():
            aliases_str = ", ".join(alias_list)
            bot.log.info(
                f"{green}{command}{' ' * (30 - len(command))}{black}- {aliases_str}{' ' * (45 - len(aliases_str))}{reset}"
            )
        bot.log.info("")
        bot.log.info(
            f"{black}{'-' * 22}[ {purple}{bold}End command aliases{reset}{black} ]{'-' * 22}{reset}"
        )
        bot.log.debug("Exiting show_aliases function...")

    except Exception as e:
        bot.log.error(f"Error in show_aliases function: {e}")
        traceback.print_exc()


def ping(bot: "Bot") -> None:
    """
    Prints 'Pong!' to the console.
    Args:
      bot (Bot): The bot instance.
    Side Effects:
      Prints 'Pong!' to the console.
    Examples:
      >>> ping(bot)
      Pong!
    """
    try:
        bot.log.info("Pong!")
    except Exception as e:
        bot.log.error(f"Error in ping function: {e}")
        

def set_default_db_id(bot: "Bot") -> None:
    """
    Sets the default DB ID for AskDB.

    Args:
        bot (Bot): The bot instance.
    """
    
    config_file = bot.config_file

    with open(config_file, "r") as f:
        config = json.load(f)

    bot.log.info("Current default DB ID: {}".format(bot.default_db_id))
    change_default_db_id = get_boolean_input(bot, "Would you like to change the default DB ID? (y/n) ")
            
    try:
        if change_default_db_id == True:
            new_db_id = input("Enter new default DB ID: ")
            bot.default_db_id = new_db_id
            new_data = {"default_db_id": new_db_id}
            update_config(config, new_data)
            bot.log.info("Default DB ID changed.")
            
        else:
            bot.log.info("Default DB ID not changed.")
    except Exception as e:
        bot.log.error(f"Error in set_default_db_id function: {e}")
        
        
def toggle_show_source_documents(bot: "Bot") -> None:
    """
    Toggle whether or not to show source documents.
    
    Args:
        bot (Bot): The bot instance.
    """
    
    config_file = bot.config_file

    bot.log.info("Current show source documents: {}".format(bot.show_source_documents))
    change_show_source_documents = get_boolean_input(bot, "Would you like to toggle show source documents? (y/n) ")
    
    try:
        if change_show_source_documents == True:
            bot.show_source_documents = not bot.show_source_documents
            new_data = {"show_source_documents": bot.show_source_documents}
            update_config(config_file, new_data)
            bot.log.info("Show source documents changed.")
            
        else:
            bot.log.info("Show source documents not changed.")
    except Exception as e:
        bot.log.error(f"Error in toggle_show_source_documents function: {e}")