import discord
import discord.ext.commands as commands
from discord.ext.commands import Cog, command
import pytest
import pytest_asyncio
import discord.ext.test as dpytest

from unittest.mock import MagicMock, AsyncMock
from koduck import Koduck

from main import refresh_commands

class CogDuck(Cog, Koduck):
    def __init__(self):
        self.add_command("refreshcommands", refresh_commands, "prefix", 3)

@pytest_asyncio.fixture
async def bot():
    # Setup
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    b = commands.Bot(command_prefix="!",
                     intents=intents)
    await b._async_setup_hook()  # setup the loop
    await b.add_cog(CogDuck())

    dpytest.configure(b)

    yield b

    # Teardown
    await dpytest.empty_queue() # empty the global message queue as test teardown

@pytest.mark.asyncio
async def test_ping(bot):
    await dpytest.message("!help me")
    assert dpytest.verify().message().content("Pong !")
