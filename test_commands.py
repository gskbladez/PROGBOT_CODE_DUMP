import pytest
import pytest_asyncio

from unittest.mock import AsyncMock, MagicMock
from koduck import Koduck, KoduckContext, on_message as send_koduck_message

from pathlib import Path

import mainnb
import mainadvance

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
    expected = expected.read_text()

    result = get_msg_kwarg(test_interaction, 'content')

    assert expected == result
    
# chip

## basic query
@pytest.mark.parametrize("chip_name, chip_title", [
    ['Cannon', '__Cannon (Starter Chip)__'], #Basic Query
    ['StatiCannon', '__StatiCannon (Summer Camp Chip)__'], #Confusable Query
    ['StaticCannon', '__StatiCannon (Summer Camp Chip)__'], #Alias
    ['Zapring, Cannon', '__Cannon (Starter Chip)__'], #Multiple Chips Query
    ])
@pytest.mark.asyncio
async def test_chip_with_query(test_interaction, chip_name, chip_title):
    await mainnb.chip(test_interaction, chip_name)
    
    expected_title = chip_title

    result = get_msg_kwarg(test_interaction, 'embed')
    assert result.title == expected_title


## query the categories
@pytest.mark.parametrize("category_str", ['dark', 'darkchip', 'darkchips'])
@pytest.mark.asyncio
async def test_chip_darkchips(test_interaction, category_str):
    await mainnb.chip(test_interaction, category_str)
    
    expected = test_objs / 'chip_dark.txt'
    expected = expected.read_text()

    result = get_msg_kwarg(test_interaction, 'content')
    assert result == expected

@pytest.mark.parametrize("category_str", ['mega', 'megachip', 'megachips'])
@pytest.mark.asyncio
async def test_chip_megachips(test_interaction, category_str):
    await mainnb.chip(test_interaction, category_str)
    
    expected = test_objs / 'chip_mega.txt'
    expected = expected.read_text()

    result = get_msg_kwarg(test_interaction, 'content')
    assert result == expected

@pytest.mark.parametrize("category_str", ['incident', 'incident chip', 'incident chips'])
@pytest.mark.asyncio
async def test_chip_incidents(test_interaction, category_str):
    await mainnb.chip(test_interaction, category_str)
    
    expected = test_objs / 'chip_incident.txt'
    expected = expected.read_text()

    result = get_msg_kwarg(test_interaction, 'content')
    assert result == expected

@pytest.mark.parametrize("category_str", ['accurate']) # I personally don't want to do every tag but if someone wants to its here
@pytest.mark.asyncio
async def test_chip_tags(test_interaction, category_str):
    await mainnb.chip(test_interaction, category_str)
    
    expected = test_objs / f'chip_{category_str}.txt'
    expected = expected.read_text()

    result = get_msg_kwarg(test_interaction, 'content')
    assert result == expected

@pytest.mark.parametrize("category_str", ['thrown']) # I personally don't want to do every category but if someone wants to its here
@pytest.mark.asyncio
async def test_chip_category(test_interaction, category_str):
    await mainnb.chip(test_interaction, category_str)
    
    expected = test_objs / f'chip_{category_str}.txt'
    expected = expected.read_text()

    result = get_msg_kwarg(test_interaction, 'content')
    assert result == expected

@pytest.mark.parametrize("category_str", ['a-license']) # I personally don't want to do every license but if someone wants to its here
@pytest.mark.asyncio
async def test_chip_license(test_interaction, category_str):
    await mainnb.chip(test_interaction, category_str)
    
    expected = test_objs / f'chip_{category_str}.txt'
    expected = expected.read_text()

    result = get_msg_kwarg(test_interaction, 'content')
    assert result == expected

@pytest.mark.parametrize("category_str, category_txt", [
    ['Chit Chat', 'chip_chit-chat.txt'],
    ['Genso Network', 'chip_genso.txt'] # Treating PMC like CC for simplicity in testing
    ]) # I personally don't want to do every Crossover Content but if someone wants to its here
@pytest.mark.asyncio
async def test_chip_crossover(test_interaction, category_str, category_txt):
    await mainnb.chip(test_interaction, category_str)
    
    expected = test_objs / category_txt
    expected = expected.read_text()

    result = get_msg_kwarg(test_interaction, 'content')
    assert result == expected

@pytest.mark.parametrize("category_str", ['help','rule', 'folder', 'category','tag','navi'])
@pytest.mark.asyncio
async def test_chip_helps(test_interaction, category_str):
    # skipping blank and qq because they're hard coded embeds that worked fine in manual testing
    await mainnb.chip(test_interaction, category_str)
    
    expected = test_objs / f'chip_{category_str}.txt'
    expected = expected.read_text()

    result = get_msg_kwarg(test_interaction, 'content')

    assert result == expected

@pytest.mark.parametrize("category_str", ['help','rule'])
@pytest.mark.asyncio
async def test_power_helps(test_interaction, category_str):
    await mainnb.power(test_interaction, category_str)
    
    expected = test_objs / f'power_{category_str}.txt'
    expected = expected.read_text()

    result = get_msg_kwarg(test_interaction, 'content')

    assert result == expected

@pytest.mark.parametrize("query_str", ['virus passive','cost', 'speed', 'sense roll'])
@pytest.mark.asyncio
async def test_power_query(test_interaction, query_str):
    await mainnb.power(test_interaction, query_str)
    
    expected = test_objs / f'power_{query_str}.txt'
    expected = expected.read_text()

    result = get_msg_kwarg(test_interaction, 'content')

    assert result == expected
    
# power: lookup multiple powers

@pytest.mark.parametrize("category_str", ['help','rule'])
@pytest.mark.asyncio
async def test_ncp_helps(test_interaction, category_str):
    await mainnb.ncp(test_interaction, category_str)
    
    expected = test_objs / f'ncp_{category_str}.txt'
    expected = expected.read_text()

    result = get_msg_kwarg(test_interaction, 'content')

    assert result == expected

@pytest.mark.parametrize("query_str", ['1eb', 'chitchat', 'minus'])
@pytest.mark.asyncio
async def test_ncp_query(test_interaction, query_str):
    await mainnb.ncp(test_interaction, query_str)
    
    expected = test_objs / f'ncp_{query_str}.txt'
    expected = expected.read_text()

    result = get_msg_kwarg(test_interaction, 'content')

    assert result == expected

# - ncp: lookup multiple NCPs

@pytest.mark.parametrize("category_str", ['help','rule'])
@pytest.mark.asyncio
async def test_virus_helps(test_interaction, category_str):
    await mainnb.virus(test_interaction, category_str)
    
    expected = test_objs / f'virus_{category_str}.txt'
    expected = expected.read_text()

    result = get_msg_kwarg(test_interaction, 'content')

    assert result == expected

@pytest.mark.parametrize("query_str", ['category', 'tags'])
@pytest.mark.asyncio
async def test_virus_query(test_interaction, query_str):
    await mainnb.virus(test_interaction, query_str)
    
    expected = test_objs / f'virus_{query_str}.txt'
    expected = expected.read_text()

    result = get_msg_kwarg(test_interaction, 'content')

    assert result == expected

# - virus: lookup multiple viruses (simple), lookup multiple viruses (detailed), lookup omega virus, lookup mega virus

@pytest.mark.parametrize("query_str", ['mystic lilies','night drifters','shot', '1eb', 'npu'])
@pytest.mark.asyncio
@pytest.mark.skip
async def test_generic_query(test_interaction, query_str):
    await mainnb.virus(test_interaction, query_str)
    
    expected = test_objs / f'query_{query_str}.txt'
    expected = expected.read_text()

    result = get_msg_kwarg(test_interaction, 'content')

    assert result == expected

# - query: mystic lilies (chips + ncps), night drifters (virus only), chip category, ncp EB, npu, powers by skill, daemon, network mod, weather, bond powers, heart home (no chips, NCPs, or viruses)

@pytest.mark.parametrize("category_str", ['help','rule'])
@pytest.mark.asyncio
async def test_bond_helps(test_interaction, category_str):
    await mainnb.bond(test_interaction, category_str)
    
    expected = test_objs / f'bond_{category_str}.txt'
    expected = expected.read_text()

    result = get_msg_kwarg(test_interaction, 'content')

    assert result == expected

# - bondpower: lookup multiple bond powers

@pytest.mark.parametrize("category_str", ['help','list'])
@pytest.mark.asyncio
async def test_networkmod_helps(test_interaction, category_str):
    await mainadvance.networkmod(test_interaction, category_str)
    
    expected = test_objs / f'networkmod_{category_str}.txt'
    expected = expected.read_text()

    result = get_msg_kwarg(test_interaction, 'content')

    assert result == expected

# - networkmod: lookup multiple

@pytest.mark.parametrize("category_str", ['help','rule','list'])
@pytest.mark.asyncio
async def test_weather_helps(test_interaction, category_str):
    await mainadvance.weather(test_interaction, category_str)
    
    expected = test_objs / f'weather_{category_str}.txt'
    expected = expected.read_text()

    result = get_msg_kwarg(test_interaction, 'content')

    assert result == expected

# - weather: lookup 4 LiquidTime DiamondDust ChromaticFlux MementoBorealis

# - mysterydata: roll common, uncommon, rare, sunny, violet, sapphire, mystery reward

# - rulebook: send, lookup beta 4 advance 3, lookup beta 7 mobile
# - element: roll a number, roll a number in a category

@pytest.mark.parametrize("category_str", ['help','rule','list'])
@pytest.mark.asyncio
async def test_daemon_helps(test_interaction, category_str):
    await mainadvance.daemon(test_interaction, category_str)
    
    expected = test_objs / f'daemon_{category_str}.txt'
    expected = expected.read_text()

    result = get_msg_kwarg(test_interaction, 'content')

    assert result == expected
# - daemon: list a name

@pytest.mark.parametrize("category_str", ['help','rule','noclip'])
@pytest.mark.asyncio
async def test_npu_messages(test_interaction, category_str):
    await mainnb.upgrade(test_interaction, category_str)
    
    expected = test_objs / f'npu_{category_str}.txt'
    expected = expected.read_text()

    result = get_msg_kwarg(test_interaction, 'content')

    assert result == expected

# - npu: lookup npus
# - crimsonnoise: roll uncommon, common, rare