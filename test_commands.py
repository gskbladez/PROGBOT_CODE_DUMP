import discord
import discord.ext.commands as commands
from discord.ext.commands import Cog, command
import pytest
import pytest_asyncio
import discord.ext.test as dpytest
from discord.ext.test.backend import make_message

from unittest.mock import AsyncMock
from koduck import Koduck, KoduckContext, on_message as send_koduck_message

from main import refresh_commands

from pathlib import Path

test_objs = Path('.') / 'test_objects'
help_objs = test_objs / 'help'

def make_koduck_message(content):
    config = dpytest.get_config()
    return make_message(
        content,
        config.members[0],
        config.channels[0]
        )

@pytest_asyncio.fixture
async def bot():
    # Setup
    context = KoduckContext()
    _koduck = Koduck()
    _intents = discord.Intents.default()
    _intents.members = True
    _intents.message_content = True
    
    context.koduck = _koduck
    context.koduck.client = commands.Bot(
        command_prefix="!",
        intents = _intents
        )
    
    await context.koduck.client._async_setup_hook()
    await refresh_commands(context, test_mode = True)
    
    dpytest.configure(context.koduck.client)
    
    yield _koduck

    # Teardown
    await dpytest.empty_queue() # empty the global message queue as test teardown

@pytest.mark.asyncio
async def test_ping(bot):
    test_msg = make_koduck_message("!help")
    await send_koduck_message(test_msg)
    
    result = dpytest.get_message().content
    
    expected = help_objs / 'no_category.txt'
    expected = expected.read_text()

    assert expected == result