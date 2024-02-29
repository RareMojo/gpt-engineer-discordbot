import asyncio
import json
import os
from typing import TYPE_CHECKING

from discord.ext import commands
from dotenv import load_dotenv

from discord_bot.terminal import terminal_command_loop

load_dotenv()

CHATBOT_CATEGORY_ID = int(os.getenv("CHATBOT_CATEGORY_ID", 0))
CHATBOT_THREADS_ID = int(os.getenv("CHATBOT_THREADS_ID", 0))
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")
GUILD_ID = os.getenv("DISCORD_GUILD_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")


if TYPE_CHECKING:
    from discord import Intents
    from discord_bot.logger import Logger


class Bot(commands.Bot):
    """Main Bot class that handles the bot's initialization and startup.

    Attributes:
        intents (discord.Intents): The bot's intents.
        logger (Logger): The bot's logger.
    """

    def __init__(self, intents: "Intents", paths: dict, logger: "Logger"):
        """
        Initializes the Bot class.
        Args:
          intents (discord.Intents): The bot's intents.
          paths (dict): A dictionary of paths.
          logger (Logger): The bot's logger.
        Side Effects:
          Sets the bot's logger, paths, config file, avatar file, cogs directory, guild ID, owner ID, chatbot category ID, chatbot threads ID, Discord token, OpenAI API key, OpenAI model, Pinecone API key, Pinecone environment, and Pinecone index.
          Loads the config file.
          Sets the bot's display name.
          Sets self.running to True.
        Examples:
          >>> bot = Bot(intents, paths, logger)
          Bot built.
          Bot initialized.
        """
        self.log = logger
        self.log.debug("Bot built.")
        self.paths = paths
        self.config_file = self.paths["configs"] / "config.json"
        self.avatar_file = self.paths["assets"] / "images" / "avatar.png"
        self.cogs_dir = self.paths["cogs"]
        self.guild_id = int(GUILD_ID) if GUILD_ID else None
        self.owner_id = int(OWNER_ID) if OWNER_ID else None
        self.chatbot_category_id = CHATBOT_CATEGORY_ID
        self.chatbot_threads_id = CHATBOT_THREADS_ID
        self.discord_token = str(DISCORD_TOKEN)
        self.openai_api_key = str(OPENAI_API_KEY)
        self.openai_model = str(OPENAI_MODEL)
        self.pinecone_api_key = str(PINECONE_API_KEY)
        self.pinecone_env = str(PINECONE_ENV)
        self.pinecone_index = str(PINECONE_INDEX)
        self.google_search_api_key = str(GOOGLE_SEARCH_API_KEY)
        
        with open(self.config_file, "r") as f:
            self.config = json.load(f)

        self.default_db_id = self.config.get("default_db_id")
        self.display_name = self.config.get("bot_name")
        self.show_source_documents = self.config.get("show_source_documents")

        super().__init__(command_prefix=self.config.get("prefix"), intents=intents)
        self.log.debug("Bot initialized.")
        self.running = True

    async def start_bot(self):
        """Starts bot."""
        self.log.info("Bot starting...")
        await self.load_cogs()

        bot_task = asyncio.create_task(self.start(self.discord_token), name="bot")

        try:
            while self.running:
                await asyncio.sleep(0)

        except Exception as e:
            self.log.error(f"Bot encountered an error: {e}")

        finally:
            bot_task.cancel()
            
    async def start_terminal_command_loop(self):
        """Starts the terminal command loop."""
        self.log.debug("Starting terminal command loop...")
        
        terminal_task = asyncio.create_task(terminal_command_loop(self), name="terminal")
        
        try:
            while self.running:
                await asyncio.sleep(0)
        
        except Exception as e:
            self.log.error(f"Terminal encountered an error: {e}")
        
        finally:
            terminal_task.cancel()

    def stop_bot(self):
        """Stops bot."""
        self.log.info("Bot stopping...")
        self.running = False

    async def load_cogs(self):
        """Loads all cogs in the cogs directory and its subdirectories."""
        self.log.debug("Loading cogs...")
        num_loaded_cogs = 0
        try:
            for dirpath, dirnames, filenames in os.walk(self.cogs_dir):
                loaded_extensions = []
                cog_name = None
                
                for filename in filenames:
                    
                    if filename.endswith("cog.py"):
                        rel_path = os.path.relpath(dirpath, self.cogs_dir)
                        
                        if rel_path == '.':
                            cog_name = f"cogs.{filename[:-3]}"
                        else:
                            cog_name = f"cogs.{rel_path.replace(os.sep, '.')}.{filename[:-3]}"
                            
                        if cog_name in self.extensions:
                            continue
                        
                        await self.load_extension(cog_name)
                        loaded_extensions.append(filename[:-3])
                        num_loaded_cogs += 1
                        
                if loaded_extensions:
                    package_name = "Standalone Cogs" if dirpath == self.cogs_dir else os.path.basename(dirpath)
                    self.log.info("Loaded:")
                    self.log.info(f"Package Name: {package_name}")
                    self.log.info(f"Extensions: {', '.join(loaded_extensions)}")
        except Exception as e:
            self.log.error(f"Failed to load extension: {e}")
        self.log.info(f"Loaded total {num_loaded_cogs} cogs.")
