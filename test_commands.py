import pytest
import pytest_asyncio

from unittest.mock import AsyncMock, MagicMock
from koduck import Koduck, KoduckContext, on_message as send_koduck_message

from pathlib import Path

import mainnb

test_objs = Path('.') / 'test_objects'

def get_msg_kwarg(_interaction, _kwarg):
    return _interaction.command.koduck.send_message.await_args.kwargs[_kwarg]

@pytest.fixture
def test_interaction():
    _interaction = AsyncMock()
    _interaction.command.koduck.send_message = AsyncMock()
    return _interaction


# - help: send a query
@pytest.mark.asyncio
async def test_help(test_interaction):
    # I think this is actually impossible to reach now due to how slash commands work
    await mainnb.help_cmd(test_interaction, None)
    
    expected = test_objs / 'help_none.txt'
    expected = expected.read_text()

    result = get_msg_kwarg(test_interaction, 'content')

    assert expected == result

@pytest.mark.asyncio
async def test_help_with_query(test_interaction):
    await mainnb.help_cmd(test_interaction, "you")
    
    expected = test_objs / 'help_you.txt'
    expected = expected.read_text().encode('unicode_escape').decode('utf8')

    result = get_msg_kwarg(test_interaction, 'content')

    assert expected == result
    
# chip

## help
@pytest.mark.asyncio
async def test_chip_none(test_interaction):
    await mainnb.chip(test_interaction, 'help')
    
    expected = test_objs / 'chip_none.txt'
    expected = expected.read_text()

    result = get_msg_kwarg(test_interaction, 'content')

    assert expected == result

## basic query
@pytest.mark.parametrize("chip_name, chip_title", [
    ['Cannon', '__Cannon (Starter Chip)__'], #Basic Query
    ['StatiCannon', '__StatiCannon (Summer Camp Chip)__'], #Confusable Query
    ['StaticCannon', '__StatiCannon (Summer Camp Chip)__'] #Alias
    ])
@pytest.mark.asyncio
async def test_chip_with_query(test_interaction, chip_name, chip_title):
    await mainnb.chip(test_interaction, chip_name)
    
    expected_title = chip_title

    result = get_msg_kwarg(test_interaction, 'embed')
    assert result.title == expected_title

# rule, folder, ??, blank, category, tag, navi, lookup multiple, query a tag, query a category, query megachips, query incident chips, query by license, query by crossover content, query by Genso Network
## query a category
@pytest.mark.parametrize("dark_str", ['dark', 'darkchip', 'darkchips'])
@pytest.mark.asyncio
async def test_chip_darkchips(test_interaction, dark_str):
    await mainnb.chip(test_interaction, dark_str)
    
    expected = test_objs / 'chip_dark.txt'
    expected = expected.read_text()

    result = get_msg_kwarg(test_interaction, 'content')
    assert result == expected
    
# - power: help, rule, query by virus passive powers, query by cost powers, query by speed powers, query by sense roll powers, lookup multiple powers
# - ncp: help, rule, query by 1EB, query by crossover content, query by Genso Minus Cust, lookup multiple NCPs
# - virus: help, rule, query category, query virus tags, lookup multiple viruses (simple), lookup multiple viruses (detailed), lookup omega virus, lookup mega virus
# - tag: lookup battlechip tag, lookup virus category, lookup virus tag, lookup chip category
# - query: mystic lilies (chips + ncps), night drifters (virus only), chip category, ncp EB, npu, powers by skill, daemon, network mod, weather, bond powers, heart home (no chips, NCPs, or viruses)
# - bondpower: help, rule, lookup multiple bond powers
# - mysterydata: roll common, uncommon, rare, sunny, violet, sapphire, mystery reward
# - rulebook: send, lookup beta 4 advance 3, lookup beta 7 mobile
# - element: roll a number, roll a number in a category
# - daemon: list all, list a name
# - npu: query a power for its NPUs, lookup npus
# - crimsonnoise: roll uncommon, common, rare
# - networkmod: help, list, lookup multiple
# - weather: rule, help, list, lookup 4 LiquidTime DiamondDust ChromaticFlux MementoBorealis