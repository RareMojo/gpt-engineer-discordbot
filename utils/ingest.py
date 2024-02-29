import asyncio
import tempfile
from typing import TYPE_CHECKING
from urllib.parse import urljoin
import aiohttp

import pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders.recursive_url_loader import RecursiveUrlLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Pinecone
from bs4 import BeautifulSoup as Soup

from utils.tools import download_file
from discord_bot.logger import log_debug, log_error, log_info

if TYPE_CHECKING:
    from discord_bot.bot import Bot



async def ingestAny(bot: "Bot", url: str, namespace: str):
    """
    Ingests documents from a given URL into Pinecone.
    Args:
      bot (Bot): The bot instance.
      url (str): The URL of the documents to ingest.
      namespace (str): The namespace to ingest the documents into.
    Side Effects:
      Ingests documents into Pinecone.
    Examples:
      >>> ingest_db(bot, 'https://example.com/db', 'my_namespace')
    """
    base_url = url

    loader = RecursiveUrlLoader(url=base_url)
    
    db = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000, chunk_overlap=100
    )
    texts = text_splitter.split_documents(db)

    pinecone.init(api_key=bot.pinecone_api_key, environment=bot.pinecone_env)
    embeddings = OpenAIEmbeddings(
        model="text-embedding-ada-002", openai_api_key=bot.openai_api_key
    )
    Pinecone.from_documents(
        texts, embeddings, index_name=bot.pinecone_index, namespace=namespace
    )
    log_debug(
        bot,
        f"Successfully ingested {len(texts)} documents into Pinecone index {bot.pinecone_index} in namespace {namespace}.",
    )
    
    
async def ingestRTD(bot: "Bot", url: str, namespace: str):
    """
    Ingests documents from a given URL into Pinecone.
    Args:
      bot (Bot): The bot instance.
      url (str): The URL of the documents to ingest.
      namespace (str): The namespace to ingest the documents into.
    Side Effects:
      Ingests documents into Pinecone.
    Examples:
      >>> ingest_db(bot, 'https://example.com/db', 'my_namespace')
    """
    base_url = url

    with tempfile.TemporaryDirectory() as temp_dir:
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url) as response:
                if response.status == 200:
                    soup = Soup(await response.text(), "html.parser")
                    tasks = []

                    for link in soup.find_all("a", {"class": "reference internal"}):
                        file_url = urljoin(base_url, link["href"])
                        if file_url.endswith(".html"):
                            tasks.append(
                                download_file(bot, session, file_url, temp_dir)
                            )

                    await asyncio.gather(*tasks)
                else:
                    log_error(bot, f"Failed to download: {base_url}")

        from langchain.document_loaders.readthedocs import ReadTheDocsLoader

        class DBLoader(ReadTheDocsLoader):
            """My custom ReadThedbLoader."""

            def _clean_data(self, data: str) -> str:
                """
                Cleans the data from a given HTML string.
                Args:
                  data (str): The HTML string to clean.
                Returns:
                  str: The cleaned string.
                Examples:
                  >>> MDBLoader._clean_data('<html><body>Hello World!</body></html>')
                  'Hello World!'
                """
                from bs4 import BeautifulSoup

                soup = BeautifulSoup(data, **self.bs_kwargs)

                html_tags = [
                    ("div", {"role": "main"}),
                    ("main", {"id": "main-content"}),
                    ("body", {}),
                ]

                text = None

                for tag, attrs in html_tags[::-1]:
                    text = soup.find(tag, attrs)
                    if text is not None:
                        break

                if text is not None:
                    text = text.get_text()
                else:
                    text = ""

                return "\n".join([t for t in text.split("\n") if t])

        loader = DBLoader(temp_dir, features="html.parser", encoding="utf-8")
        db = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000, chunk_overlap=100
        )
        texts = text_splitter.split_documents(db)

        pinecone.init(api_key=bot.pinecone_api_key, environment=bot.pinecone_env)
        embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002", openai_api_key=bot.openai_api_key
        )
        Pinecone.from_documents(
            texts, embeddings, index_name=bot.pinecone_index, namespace=namespace
        )
        log_debug(
            bot,
            f"Successfully ingested {len(texts)} documents into Pinecone index {bot.pinecone_index} in namespace {namespace}.",
        )