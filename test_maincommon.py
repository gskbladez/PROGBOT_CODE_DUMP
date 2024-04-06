from maincommon import find_value_in_table
import pytest
from unittest.mock import MagicMock, AsyncMock

@pytest.mark.asyncio
async def test_find_value_in_table():
    expected = "Cannon"
    result = await find_value_in_table(None, "Chip", "Chip", "Cannon")
    assert expected == result["Chip"]

@pytest.mark.asyncio
async def test_find_value_in_table_alias():
    expected = "DataDaggers"
    result = await find_value_in_table(None, "Chip", "Chip", "DataDagger")
    assert expected == result["Chip"]


@pytest.mark.asyncio
async def test_find_value_in_table_fail():
    mock_interaction = MagicMock()
    mock_send_message = AsyncMock()

    mock_interaction.command.koduck.send_message = mock_send_message

    await find_value_in_table(mock_interaction, "Chip", "Chip", "KillRoyWasHere")

    expected = "I can't find `KillRoyWasHere`!"
    mock_send_message.assert_called_once_with(mock_interaction, content=expected, ephemeral=True)
