import pytest
import pytest_asyncio

from unittest.mock import AsyncMock
from koduck import Koduck, KoduckContext, on_message as send_koduck_message

from pathlib import Path

import mainnb

test_objs = Path('.') / 'test_objects'
help_objs = test_objs / 'help'

@pytest.mark.asyncio
async def test_help():
    test_interaction = AsyncMock()
    test_interaction.command.koduck.send_message = AsyncMock()
    await mainnb.help_cmd(test_interaction, None)
    
    expected = help_objs / 'no_query.txt'
    expected = expected.read_text()

    test_interaction.command.koduck.send_message.assert_awaited_with(test_interaction, content=expected)

@pytest.mark.asyncio
async def test_help_with_query():
    test_interaction = AsyncMock()
    test_interaction.command.koduck.send_message = AsyncMock()
    await mainnb.help_cmd(test_interaction, "you")
    
    expected = help_objs / 'no_category.txt'
    expected = expected.read_text().encode('unicode_escape').decode('utf8')

    test_interaction.command.koduck.send_message.assert_awaited_with(test_interaction, content=expected)