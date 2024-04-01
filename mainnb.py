import typing
import discord
import random
import settings
import pandas as pd
import numpy as np
import re
import mainadvance
from maincommon import clean_args, send_query_msg, find_value_in_table, roll_row_from_table
from maincommon import cc_color_dictionary, playermade_list, rulebook_df, help_df
from maincommon import nyx_link, grid_link
import koduck

MAX_POWER_QUERY = 5
MAX_NCP_QUERY = 5
MAX_CHIP_QUERY = 5
MAX_VIRUS_QUERY = 5
MAX_ELEMENT_ROLL = 12
MAX_MOD_QUERY = 5
MAX_BOND_QUERY = 4
MAX_NPU_QUERY = MAX_NCP_QUERY
PROBABLY_INFINITE = 99
MAX_RANDOM_VIRUSES = 6
MAX_ELEMENT_QUERY = 12
MAX_MD_BONUS = 20

skill_list = [
    'Sense', 'Info', 'Coding',
    'Strength', 'Speed', 'Stamina',
    'Charm', 'Bravery', 'Affinity']
skill_color_dictionary = {"Mind": 0x81A7C6,
                          "Body": 0xDF8F8D,
                          "Soul": 0xF8E580}
help_categories = {
    "Lookups": ':mag: **Lookups**',
    "Rollers": ':game_die: **Rollers**',
    "Helpers": ':thumbsup: **Helpers**',
    "Reminders (Base)": ':information_source: **Reminders (Base)**',
    "Reminders (Advanced Content)": ':trophy: **Reminders (Advanced Content)**',
    "Reminders (Liberation)": ':map: **Reminders (Liberation)**',
    "Reminders (DarkChips)": ':smiling_imp: **Reminders (DarkChips)**',
    "Safety Tools": ':shield: **Safety Tools**'}

cc_dict = {
    "ChitChat": "Chit Chat", "Radical Spin": "RadicalSpin", "Skateboard Dog": "SkateboardDog",
    "Night Drifters": "NightDrifters", "Underground Broadcast": "UndergroundBroadcast",
    "Mystic Lilies": "MysticLilies", "Genso Network": "GensoNetwork, Genso", "Leximancy": "",
    "New Connections": "NewConnections", "Silicon Skin": "SiliconSkin",
    "The Walls Will Swallow You": "TWWSY, TheWallsWillSwallowYou, The Walls, TheWalls, Walls",
    "MUDSLURP": "MUD",
    "Tarot": "",
    "Summer Camp": "Summber Camp, SummerCamp, Summer, Sunmer Camp",
    "Nyx": "", "Cast the Dice": "CasttheDice, CastDice, Cast Dice", "Neko Virus": "Neko Virus Infection, NekoVirus"}
cc_list = list(cc_dict.keys())
cc_df = pd.DataFrame.from_dict({"Source": cc_list, "Alias": list(cc_dict.values())})

virus_colors = {"Virus": 0x7c00ff,
                "MegaVirus": 0xA8E8E8,
                "OmegaVirus": 0xA8E8E8}

mysterydata_dict = {"common": {"color": 0x48C800,
                               "image": settings.common_md_image},
                    "uncommon": {"color": 0x00E1DF,
                                 "image": settings.uncommon_md_image},
                    "rare": {"color": 0xD8E100,
                             "image": settings.rare_md_image},
                    "gold": {"color": 0xFFD541,
                             "image": settings.gold_md_image},
                    "violet": {"color": 0x895EFF,
                             "image": settings.violet_md_image},
                    "sapphire": {"color": 0x3659FE,
                             "image": settings.sapphire_md_image},
                    "sunny": {"color": cc_color_dictionary["Summber Camp"],
                              "image": settings.sunny_md_image}}

chip_df = pd.read_csv(settings.chipfile, sep="\t").fillna('')
chip_known_aliases = chip_df[chip_df["Alias"] != ""].copy()
chip_tag_list = chip_df["Tags"].str.split(",", expand=True) \
    .stack() \
    .str.strip() \
    .str.lower() \
    .unique()
chip_tag_list = [i for i in chip_tag_list if i]
chip_category_list = pd.unique(chip_df["Category"])
chip_category_list = [i for i in chip_category_list if i]
chip_license_list = pd.unique(chip_df["License"].str.lower())
chip_from_list = pd.unique(chip_df["From?"].str.lower())

power_df = pd.read_csv(settings.powerfile, sep="\t").fillna('')
virus_df = pd.read_csv(settings.virusfile, sep="\t").fillna('')
virus_df = virus_df[virus_df["Name"] != ""]
virus_tag_list = virus_df["Tags"].str.split(";|,", expand=True) \
    .stack() \
    .str.strip() \
    .str.lower() \
    .unique()
virus_tag_list = [i for i in virus_tag_list if i]
[virus_tag_list.remove(i) for i in ["none", "None"] if i in virus_tag_list]
virus_category_list = pd.unique(virus_df["Category"].str.strip())
virus_category_list = [i for i in virus_category_list if i]

bond_df = pd.read_csv(settings.bondfile, sep="\t").fillna('').dropna(subset=['BondPower'])
tag_df = pd.read_csv(settings.tagfile, sep="\t").fillna('')
mysterydata_df = pd.read_csv(settings.mysterydatafile, sep="\t").fillna('')

element_df = pd.read_csv(settings.elementfile, sep="\t").fillna('')
element_category_list = pd.unique(element_df["category"].dropna())

adventure_df = pd.read_csv(settings.adventurefile, sep="\t").fillna('')
fight_df = pd.read_csv(settings.fightfile, sep="\t").fillna('')
glossary_df = pd.read_csv(settings.glossaryfile, sep="\t").fillna('')

nyx_chip_df = pd.read_csv(settings.nyx_chipfile, sep="\t").fillna('')
nyx_power_df = pd.read_csv(settings.nyx_ncpfile, sep="\t").fillna('')
pmc_chip_df = pd.read_csv(settings.pmc_chipfile, sep="\t").fillna('')
pmc_power_df = pd.read_csv(settings.pmc_powerfile, sep="\t").fillna('')
pmc_virus_df = pd.read_csv(settings.pmc_virusfile, sep="\t").fillna('')

chip_drops = chip_df.merge(virus_df[["Name", "Drops1"]], left_on="Chip", right_on="Drops1", how="left")
chip_drops = chip_drops.merge(virus_df[["Name", "Drops2"]], left_on="Chip", right_on="Drops2", how="left")
chip_drops["Dropped By"] = chip_drops["Name_x"].combine_first(chip_drops['Name_y'])
chip_df["Dropped By"] = chip_drops["Name_x"].combine_first(chip_drops['Name_y']).fillna('')

async def help_cmd(interaction: discord.Interaction, query: str):
    # Default message if no parameter is given
    if query is None:
        message_help = "Hi, I'm **ProgBot**, a bot made for *NetBattlers*, the Unofficial MMBN RPG! \n" + \
                       "My prefix for commands here is ``. You can also DM me using slash commands!" + \
                       "To see a list of all commands you can use, type `commands`. " + \
                       "You can type `help` and any other command for more info on that command!\n" + \
                       "I can also pull up info on some rules and descriptions! Check `help all` for the list of details I can help with!"
        return await interaction.command.koduck.send_message(interaction, content=message_help)

    cleaned_args = clean_args([query])
    if cleaned_args[0] in ['list', 'all']:
        sub_df = help_df[help_df["Hidden?"] == False]
        help_groups = sub_df.groupby(["Type"])
        return_msgs = ["%s\n*%s*" % (name, ", ".join(help_group["Command"].values)) for name, help_group in help_groups if name]
        return await interaction.command.koduck.send_message(interaction, content="\n\n".join(return_msgs))
    elif re.match("help(help)+", cleaned_args[0]):
        cleaned_args = ["helphelp"]  # assuming direct control

    funkyarg = ''.join(cleaned_args)
    help_msg = await find_value_in_table(interaction, help_df, "Command", funkyarg, suppress_notfound=True, allow_duplicate=True)
    if help_msg is None:
        help_response = help_df[help_df["Command"] == "unknowncommand"].iloc[0]["Response"]
    else:
        help_response = help_msg["Response"]
        if help_msg["Ruling?"]:
            ruling_msg = await find_value_in_table(interaction, help_df, "Command", help_msg["Ruling?"], suppress_notfound=True)
            if ruling_msg is None:
                return await interaction.command.koduck.send_message(interaction,
                                    content="Couldn't pull up additional ruling information for %s! You should probably let the devs know..." % help_msg["Ruling?"], ephemeral=True)
            help_response = help_response + "\n\n" + ruling_msg["Response"]

        # determines custom emojis
        unique_emojis = np.unique(np.array(re.findall(r"<:(\S+):>", help_response)))
        for cust_emoji in unique_emojis:
            if (koduck.client.get_guild(settings.source_guild_id)) and (cust_emoji in settings.custom_emojis):
                help_response = re.sub(r"<:%s:>" % cust_emoji, settings.custom_emojis[cust_emoji], help_response)
            else:
                help_response = re.sub(r"(^\s*)?<:%s:>(\s*$|\s)?" % cust_emoji, "", help_response)

    return await interaction.command.koduck.send_message(interaction, content=help_response)


async def tag(interaction: discord.Interaction, category: str):
    cleaned_args = category.strip().lower()
    if cleaned_args == 'help':
        return await interaction.command.koduck.send_message(interaction, 
                                        content="Give me a BattleChip tag or Virus/Chip category, and I can pull up its info for you!")
    
    tag_info = await find_value_in_table(interaction, tag_df, "Tag", cleaned_args)
    if tag_info is None:
        return

    tag_title = tag_info["Tag"]
    tag_description = tag_info["Description"]
    tag_alt = tag_info["AltName"]
    tag_description = tag_description.replace("\\n", "\n")

    if tag_alt:
        tag_title += " (%s)" % tag_alt

    embed = discord.Embed(
        title="__%s__" % tag_title,
        description=tag_description,
        color=0x24ff00)
    return await interaction.command.koduck.send_message(interaction, embed=embed)


def query_chip(args):
    arg_lower = ' '.join(args)

    alias_check = cc_df[
        cc_df["Alias"].str.contains("(?:^|,|;)\s*%s\s*(?:$|,|;)" % re.escape(arg_lower), flags=re.IGNORECASE)]
    if alias_check.shape[0] > 0:
        arg_lower = alias_check.iloc[0]["Source"].lower()

    if arg_lower in ['dark', 'darkchip', 'darkchips']:
        return_title = "Pulling up all `DarkChips`..."
        subdf = chip_df[chip_df["Tags"].str.contains("Dark|dark")]
        return_msg = ", ".join(subdf["Chip"])
    elif arg_lower in ['mega', 'megachip', 'megachips']:
        return_title = "Pulling up all `MegaChips` (excluding DarkChips and Incident Chips)..."
        subdf = chip_df[chip_df["Tags"].str.contains("Mega|mega")]
        return_msg = ", ".join(subdf["Chip"])
    elif arg_lower in ['incident', 'incident chip', 'incident chips']:
        return_title = "Pulling up all `Incident` Chips..."
        subdf = chip_df[chip_df["Tags"].str.contains("Incident", flags=re.IGNORECASE)]
        return_msg = ", ".join(subdf["Chip"])
    elif arg_lower in arg_lower in chip_tag_list:
        subdf = chip_df[chip_df["Tags"].str.contains(re.escape(arg_lower), flags=re.IGNORECASE) &
                        ~chip_df["Tags"].str.contains("dark|incident|mega", flags=re.IGNORECASE)]
        return_title = "Pulling up all BattleChips with the `%s` tag (excluding MegaChips)..." % re.escape(
            arg_lower).capitalize()
        return_msg = ", ".join(subdf["Chip"])
    elif arg_lower in [i.lower() for i in chip_category_list]:
        subdf = chip_df[(chip_df["Category"].str.contains(re.escape(arg_lower), flags=re.IGNORECASE)) &
                        ~chip_df["Tags"].str.contains("dark|incident|mega", flags=re.IGNORECASE)]
        if subdf.shape[0] == 0:
            return False, "", ""
        return_title = "Pulling up all chips in the `%s` category (excluding MegaChips)..." % subdf.iloc[0]["Category"]
        return_msg = ", ".join(subdf["Chip"])
    elif arg_lower in chip_license_list:
        subdf = chip_df[chip_df["License"].str.contains(re.escape(arg_lower), flags=re.IGNORECASE)]
        if subdf.shape[0] == 0:
            return False, "", ""
        return_title = "Pulling up all `%s` BattleChips..." % subdf.iloc[0]["License"]
        return_msg = ", ".join(subdf["Chip"])
    elif arg_lower in ["nyx"]:
        subdf = nyx_chip_df
        if subdf.shape[0] == 0:
            return False, "", ""
        return_title = "Pulling up all BattleChips from the `%s` Advance Content..." % subdf.iloc[0]["From?"]
        return_msg = ", ".join(subdf["Chip"])
    elif arg_lower not in ["core"] and arg_lower in chip_from_list:
        subdf = chip_df[chip_df["From?"].str.contains(re.escape(arg_lower), flags=re.IGNORECASE)]
        if subdf.shape[0] == 0:
            return False, "", ""
        return_title = "Pulling up all BattleChips from the `%s` Advance Content..." % subdf.iloc[0]["From?"]
        return_msg = ", ".join(subdf["Chip"])
    elif arg_lower in [i.lower() for i in playermade_list]:
        subdf = pmc_chip_df[pmc_chip_df["From?"].str.contains(re.escape(arg_lower), flags=re.IGNORECASE)]
        if subdf.shape[0] == 0:
            return False, "", ""
        return_title = "Pulling up all BattleChips from the unofficial `%s` Player-Made Content..." % subdf.iloc[0]["From?"]
        return_msg = ", ".join(subdf["Chip"])
    else:
        return False, "", ""

    return True, return_title, return_msg


def pity_cc_check(arg):
    alias_check = cc_df[
        cc_df["Alias"].str.contains("(?:^|,|;)\s*%s\s*(?:$|,|;)" % re.escape(arg), flags=re.IGNORECASE)]
    if alias_check.shape[0] > 0:
        arg = alias_check.iloc[0]["Source"]
        return arg
    try:
        would_be_valid = next(i for i in cc_list if re.match(r"^%s$" % re.escape(arg), i, flags=re.IGNORECASE))
        return would_be_valid
    except StopIteration:
        return None


async def chip(interaction: discord.Interaction, query: str):
    cleaned_args = clean_args([query])
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await interaction.command.koduck.send_message(interaction, content=
                                                             f"Give me the name of 1-{MAX_CHIP_QUERY} **BattleChips** and I can pull up their info for you!\n\n" +
                                                        "I can also query chips by **Category**, **Tag**, **License**, and **Advance Content**! \n" +
                                                        "I can also list all current chip categories with `chip category`, and all current chip tags with `chip tag`. To pull up details on a specific Category or Tag, use `tag` instead. (i.e. `tag blade`)"\
                                        )
    if cleaned_args[0] in ['rule', 'ruling', 'rules']:
        ruling_msg = await find_value_in_table(interaction, help_df, "Command", "chipruling", suppress_notfound=True)
        if ruling_msg is None:
            return await interaction.command.koduck.send_message(interaction, content="Couldn't find the rules for this command! (You should probably let the devs know...)", ephemeral=True)
        return await interaction.command.koduck.send_message(interaction, content=ruling_msg["Response"])
    
    if cleaned_args[0] in ['folder', 'folders']:
        ruling_msg = await find_value_in_table(interaction, help_df, "Command", "folder", suppress_notfound=True)
        if ruling_msg is None:
            return await interaction.command.koduck.send_message(interaction, content="Couldn't find the rules for this command! (You should probably let the devs know...)", ephemeral=True)
        return await interaction.command.koduck.send_message(interaction, content=ruling_msg["Response"])
    if 'blank' in cleaned_args[0]:
        embed = discord.Embed(
            title="__Blank BattleChip__",
            description="*Slot into your PET to download the attack data of defeated Viruses or other entities mid-battle." +
                        "\nBlank chips do not need to be in a Folder to use." +
                        "\nUnless the GM says otherwise, NetOps always have plenty of blank chips available.*",
            color=cc_color_dictionary["Item"])
        return await interaction.command.koduck.send_message(interaction, embed=embed)

    if '??' in cleaned_args[0]:
        embed = discord.Embed(
            title="__?????__",
            color=cc_color_dictionary["Mystery"])

        embed.add_field(name="[???/???/???]",
            value="*An unknown chip was slotted in!*")
        return await interaction.command.koduck.send_message(interaction, embed=embed)

    if cleaned_args[0] in ['category', 'categories']:
        result_title = "Displaying all known BattleChip Categories..."
        result_text = ", ".join(chip_category_list)
        return await send_query_msg(interaction, result_title, result_text)
    elif cleaned_args[0] in ['tag', 'tags']:
        result_title = "Displaying all known BattleChip Tags..."
        result_text = ", ".join([i.capitalize() for i in chip_tag_list])
        return await send_query_msg(interaction, result_title, result_text)
    elif cleaned_args[0] in ['navi', 'navichip']:
        return await interaction.command.koduck.send_message(interaction, 
                                        content="NaviChips are **MegaChips** that store attack data from defeated Navis! Each NaviChip is unique, based off the Navi it was downloaded from. NaviChips are determined by the GM.")
    arg_combined = ' '.join(cleaned_args)
    is_query, return_title, return_msg = query_chip(cleaned_args)
    if is_query:
        return await send_query_msg(interaction, return_title, return_msg)

    would_be_valid = pity_cc_check(arg_combined)
    if would_be_valid:
        return await interaction.command.koduck.send_message(interaction, 
                                        content="`%s` has no Advance Content BattleChips!" % would_be_valid, ephemeral=True)

    if len(cleaned_args) > MAX_CHIP_QUERY:
        return await interaction.command.koduck.send_message(interaction, content=f"Too many chips, no more than {MAX_CHIP_QUERY}!", ephemeral=True)

    for arg in cleaned_args:
        if not arg:
            continue
        chip_title, subtitle_trimmed, chip_description, color, _ = await chipfinder(interaction, arg)
        if chip_title is None:
            continue
        embed = discord.Embed(
            title="__%s__" % chip_title,
            color=color)
        embed.add_field(name="[%s]" % subtitle_trimmed,
                        value="_%s_" % chip_description)
        await interaction.command.koduck.send_message(interaction, embed=embed)


async def chipfinder(interaction: discord.Interaction, arg, suppress_err_msg=False):
    chip_info = await find_value_in_table(interaction, chip_df, "Chip", arg, suppress_notfound=True, alias_message=True)
    if chip_info is None:
        chip_info = await find_value_in_table(interaction, pmc_chip_df, "Chip", arg, suppress_notfound=True,
                                              alias_message=True)
        if chip_info is None:
            chip_info = await find_value_in_table(interaction, nyx_chip_df, "Chip", arg, suppress_notfound=suppress_err_msg,
                                                  alias_message=True)
            if chip_info is None:
                return None, None, None, None, None

    chip_name = chip_info["Chip"]

    chip_damage = chip_info["Dmg"]
    if chip_damage:
        chip_damage += " Damage"
    else:
        chip_damage = "-"
    chip_range = chip_info["Range"]
    chip_description = chip_info["Effect"]
    chip_category = chip_info["Category"]
    chip_tags = chip_info["Tags"]
    chip_crossover = chip_info["From?"]
    chip_license = chip_info["License"]

    chip_tags_list = [i.strip() for i in chip_tags.split(",")]

    chip_title = chip_name
    if chip_crossover in playermade_list:
        chip_title_sub = "%s Unofficial " % chip_crossover
    elif chip_crossover != "Core" and chip_crossover != "DarkChips":
        chip_title_sub = "%s " % chip_crossover
    elif chip_license:
        chip_title_sub = chip_license + " "
    else:
        chip_title_sub = chip_license

    if chip_crossover == "Nyx":
        msg_time = interaction["message"].created_at
        if msg_time.month == 4 and msg_time.day == 1:
            chip_title_sub = "%s Legal!! Crossover " % chip_crossover
        else:
            chip_title_sub = "%s Illegal Crossover " % chip_crossover

    # this determines embed colors
    color = cc_color_dictionary["Chip"]
    if chip_tags_list:
        if 'Dark' in chip_tags:
            color = cc_color_dictionary['Dark']
            chip_tags_list.remove("Dark")
            chip_title_sub += "Dark"
        elif 'Mega' in chip_tags:
            color = cc_color_dictionary['MegaChip']
            chip_tags_list.remove("Mega")
            chip_title_sub += "Mega"
        elif 'Incident' in chip_tags:
            color = cc_color_dictionary['Mystic Lilies']
            chip_tags_list.remove("Incident")
            chip_title_sub += "Incident "
    if chip_title_sub:
        chip_title += " (%sChip)" % chip_title_sub

    if chip_category == 'Item':
        color = cc_color_dictionary["Item"]
    if chip_crossover in cc_color_dictionary:
        color = cc_color_dictionary[chip_crossover]

    subtitle = [chip_damage, chip_range, chip_category, ", ".join(chip_tags_list)]
    subtitle_trimmed = [i for i in subtitle if i and i[0] != '-']

    return chip_title, "/".join(subtitle_trimmed), chip_description, color, ""


def find_skill_color(skill_key):
    if skill_key in ["Sense", "Info", "Coding"]:
        color = skill_color_dictionary["Mind"]
    elif skill_key in ["Strength", "Speed", "Stamina"]:
        color = skill_color_dictionary["Body"]
    elif skill_key in ["Charm", "Bravery", "Affinity"]:
        color = skill_color_dictionary["Soul"]
    elif "Daemon" in skill_key:
        color = cc_color_dictionary["Dark"]
    else:
        color = -1  # error code
    return color


async def power_ncp(interaction: discord.Interaction, arg, force_power=False, ncp_only=False, suppress_err_msg=False):
    if ncp_only:
        local_power_df = power_df[power_df["Sort"] != "Virus Power"]
        local_pmc_df = pmc_power_df[pmc_power_df["Sort"] != "Virus Power"]
    else:
        local_power_df = power_df
        local_pmc_df = pmc_power_df

    power_info = await find_value_in_table(interaction, local_power_df, "Power/NCP", arg, suppress_notfound=True,
                                           alias_message=True)

    if power_info is None:
        power_info = await find_value_in_table(interaction, local_pmc_df, "Power/NCP", arg, suppress_notfound=True,
                                               alias_message=True)
        if power_info is None:
            power_info = await find_value_in_table(interaction, nyx_power_df, "Power/NCP", arg, suppress_notfound=suppress_err_msg,
                                                   alias_message=True)
            if power_info is None:
                return None, None, None, None, None

    power_name = power_info["Power/NCP"]

    if ncp_only and any(power_df["Power/NCP"].str.contains(re.escape("%sncp" % power_name), flags=re.IGNORECASE)):
        power_info = await find_value_in_table(interaction, local_power_df, "Power/NCP", power_name+"ncp",
                                               suppress_notfound=True, alias_message=False)
        power_name = power_info["Power/NCP"]

    power_skill = power_info["Skill"]
    power_type = power_info["Type"]
    power_description = power_info["Effect"]
    power_eb = power_info["EB"]
    power_source = power_info["From?"]
    power_tag = ""
    if "[Instant]" in power_description:
        power_description = re.sub(r"\s*%s\s*" % re.escape("[Instant]"), "", power_description, flags=re.IGNORECASE)
        power_tag += "Instant"

    # this determines embed colors
    power_color = find_skill_color(power_skill)
    if power_color < 0:
        if power_source in cc_color_dictionary:
            power_color = cc_color_dictionary[power_source]
        elif (power_color < 0) and any(local_power_df["Power/NCP"].str.contains("^%s$" % re.escape(power_skill), flags=re.IGNORECASE)):
            power_true_info = await find_value_in_table(interaction, local_power_df, "Power/NCP", power_skill)
            power_color = find_skill_color(power_true_info["Skill"])
        else:
            power_color = 0xffffff
    field_footer = ""

    # determines custom emojis
    if koduck.client.get_guild(settings.source_guild_id):
        emojis_available = True
        if power_tag in ['Instant']:
            emoji_tag = settings.custom_emojis["instant"]
        if power_type in ['Cost']:
            emoji_type = settings.custom_emojis["cost"]
        elif power_type in ['Roll']:
            emoji_type = settings.custom_emojis["roll"]
        else:
            emoji_type = ""
        emoji_tag = ""
    else:
        emojis_available = False
        emoji_type = ""
        emoji_tag = ""

    if power_eb == '-' or force_power:  # display as power, rather than ncp
        if power_type in ['Passive', '-', 'Upgrade']:
            field_title = 'Passive Power'
        elif power_type in ['Minus']:
            field_title = 'MinusCust Passive Power'
        elif emojis_available:
            field_title = "%s Power/%s%s" % (power_skill, emoji_type, power_type)
            if power_tag:
                field_title += "/%s%s" % (emoji_tag, power_tag)
        else:
            field_title = "%s Power/%s" % (power_skill, power_type)
            if power_tag:
                field_title += "/%s" % power_tag

        field_description = power_description

        if 'Upgrade' in power_type:
            field_description = "(%s Upgrade) %s" % (power_skill, field_description)

        # Unused Source description line
        if False:
            if power_source in playermade_list:
                field_footer = "Source: %s (Unofficial)" % power_source
            elif power_source in cc_list:
                field_footer = "Source: %s (Advance Content)" % power_source

    else:
        field_title = '%s EB' % power_eb

        if power_source == "Navi Power Upgrades":
            field_title += "/%s Power Upgrade NCP" % power_skill
        elif power_type == "Minus":
            power_name += " (%s Unofficial MinusCust Program)" % power_source
            field_title = "+" + field_title
        elif power_source in playermade_list:
            power_name += " (%s Unofficial NCP)" % power_source
        elif power_source == "Nyx":
            msg_time = interaction.created_at
            if msg_time.month == 4 and msg_time.day == 1:
                power_name += (" (%s Legal!! Crossover NCP) " % power_source)
            else:
                power_name += (" (%s Illegal Crossover NCP) " % power_source)
        elif power_source != "Core":
            power_name += " (%s Advance NCP)" % power_source

        if power_type in ['Passive', '-', 'Upgrade', 'Minus']:
            field_description = power_description
        elif power_tag and emojis_available:
            field_description = "(%s/%s%s/%s%s) %s" % (power_skill, emoji_type, power_type, emoji_tag, power_tag, power_description)
        elif power_tag:
            field_description = "(%s/%s/%s) %s" % (power_skill, power_type, power_tag, power_description)
        elif emojis_available:
            field_description = "(%s/%s%s) %s" % (power_skill, emoji_type, power_type, power_description)
        else:
            field_description = "(%s/%s) %s" % (power_skill, power_type, power_description)

    return power_name, field_title, field_description, power_color, field_footer


def query_power(args):
    sub_df = power_df
    is_default = True
    search_tag_list = []

    for arg in args:
        arg_capital = arg.capitalize()
        if arg in [i.lower() for i in skill_list]:
            sub_df = sub_df[(sub_df["Skill"] == arg_capital)]
            search_tag_list.append(arg_capital)
        elif arg in ['cost', 'roll', 'passive']:
            sub_df = sub_df[(sub_df["Type"] == arg_capital)]
            search_tag_list.append(arg_capital)
        elif arg == 'virus':
            is_default = False

    if not search_tag_list:
        return False, "", ""

    if is_default:
        sub_df = sub_df[sub_df["Sort"] == "Power"]
        search_tag_list.append('Navi')
    else:
        sub_df = sub_df[(sub_df["Sort"] == "Virus Power") & (sub_df["From?"] != "Mega Viruses") & (sub_df["From?"] != "The Walls Will Swallow You")]
        search_tag_list.append('Virus (excluding Mega)')
    results_title = "Searching for `%s` Powers..." % "` `".join(search_tag_list)
    results_msg = ", ".join(sub_df["Power/NCP"])

    return True, results_title, results_msg


async def power(interaction: discord.Interaction, query: str):
    cleaned_args = clean_args([query])
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await interaction.command.koduck.send_message(interaction, 
                                        content=f"Give me the name of 1-{MAX_POWER_QUERY} **Powers** and I can pull up their info for you!\n\n" +
                                                    "I can also query Powers by **Skill**, **Type**, and whether or not it is **Virus**-exclusive! " +
                                                    "Try giving me multiple queries at once, i.e. `power sense cost` or `power virus passive`!")
    if cleaned_args[0] in ['rule', 'ruling', 'rules']:
        ruling_msg = await find_value_in_table(interaction, help_df, "Command", "powerruling", suppress_notfound=True)
        if ruling_msg is None:
            return await interaction.command.koduck.send_message(interaction, 
                                        content="Couldn't find the rules for this command! (You should probably let the devs know...)", ephemeral=True)
        return await interaction.command.koduck.send_message(interaction, 
                                    content=ruling_msg["Response"])

    if len(cleaned_args) > MAX_POWER_QUERY:
        return await interaction.command.koduck.send_message(interaction, 
                                        content=f"Too many powers, no more than {MAX_POWER_QUERY}!", ephemeral=True)

    is_query, results_title, results_msg = query_power(cleaned_args)
    if is_query:
        if not results_msg:
            return await interaction.command.koduck.send_message(interaction,content="No powers found with that query!", ephemeral=True)
        return await send_query_msg(interaction, results_title, results_msg)

    for arg in cleaned_args:
        if not arg:
            continue
        is_power_ncp = re.match(r"^(\S+)\s*ncp$", re.escape(arg), flags=re.IGNORECASE)
        if is_power_ncp:
            arg = is_power_ncp.group(1)
        power_name, field_title, field_description, power_color, field_footer = await power_ncp(interaction, arg, force_power=True)
        if power_name is None:
            continue

        embed = discord.Embed(title="__{}__".format(power_name),
                              color=power_color)
        embed.add_field(name="**[{}]**".format(field_title),
                        value="_{}_".format(field_description))
        if field_footer:
            embed.set_footer(text=field_footer)
        await interaction.command.koduck.send_message(interaction, embed=embed)
    return


def query_ncp(arg_lower):
    alias_check = cc_df[
        cc_df["Alias"].str.contains("(?:^|,|;)\s*%s\s*(?:$|,|;)" % re.escape(arg_lower), flags=re.IGNORECASE)]
    if alias_check.shape[0] > 0:
        arg_lower = alias_check.iloc[0]["Source"].lower()

    ncp_df = power_df[power_df["Sort"] != "Virus Power"]
    valid_cc_list = list(pd.unique(ncp_df["From?"].str.lower().str.strip()))
    [valid_cc_list.remove(i) for i in ["core", "navi power upgrades"]]
    eb_match = re.match(r"^(\d+)(?:\s*EB)?$", arg_lower, flags=re.IGNORECASE)

    if eb_match:
        eb_search = eb_match.group(1)
        #Exclude npus from ncp query
        subdf = ncp_df[(ncp_df["EB"] == eb_search) & (ncp_df["Type"] != "Upgrade")]
        results_title = "Finding all `%s` EB NCPs (excluding NPUs)..." % eb_search
        results_msg = ", ".join(subdf["Power/NCP"])
        return True, results_title, results_msg
    elif arg_lower in ["nyx"]:
        subdf = nyx_power_df
        results_title = "Pulling up all NCPs from the `%s` Advance Content..." % subdf.iloc[0]["From?"]
        results_msg = ", ".join(subdf["Power/NCP"])
    elif arg_lower in valid_cc_list:
        subdf = ncp_df[ncp_df["From?"].str.contains(re.escape(arg_lower), flags=re.IGNORECASE)]
        results_title = "Pulling up all NCPs from the `%s` Advance Content..." % subdf.iloc[0]["From?"]
        results_msg = ", ".join(subdf["Power/NCP"])
    elif arg_lower in [i.lower() for i in playermade_list]:
        subdf = pmc_power_df[(pmc_power_df["From?"].str.contains(re.escape(arg_lower), flags=re.IGNORECASE)) &
                             (pmc_power_df["Sort"] != "Virus Power")]
        results_title = "Pulling up all NCPs from the unofficial `%s` Player-Made Content..." % subdf.iloc[0]["From?"]
        results_msg = ", ".join(subdf["Power/NCP"])
    elif arg_lower in ["minus", "minus cust", "minuscust"]:
        subdf = pmc_power_df[pmc_power_df["Type"] == "Minus"]
        results_title = "Pulling up all `MinusCust` Programs from the unofficial Genso Network Player-Made Content..."
        results_msg = ", ".join(subdf["Power/NCP"])
    else:
        return False, "", ""

    return True, results_title, results_msg


async def ncp(interaction: discord.Interaction, query:str):
    cleaned_args = clean_args([query])
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await interaction.command.koduck.send_message(interaction, 
                                        content="Give me the names of 1-%d **NaviCust Parts** (NCPs) and I can pull up their info for you!\n\n" % MAX_POWER_QUERY +
                                                    "I can also query NCPs by **EB** and **Advance Content!**")

    if cleaned_args[0] in ['rule', 'ruling', 'rules']:
        ruling_msg = await find_value_in_table(interaction, help_df, "Command", "ncpruling", suppress_notfound=True)
        if ruling_msg is None:
            return await interaction.command.koduck.send_message(interaction, 
                                        content="Couldn't find the rules for this command! (You should probably let the devs know...)", ephemeral=True)
        return await interaction.command.koduck.send_message(interaction, 
                                    content=ruling_msg["Response"])

    arg_combined = " ".join(cleaned_args)
    is_query, results_title, results_msg = query_ncp(arg_combined)
    if is_query:
        return await send_query_msg(interaction, results_title, results_msg)
    would_be_valid = pity_cc_check(arg_combined)
    if would_be_valid:
        return await interaction.command.koduck.send_message(interaction, 
                                        content="`%s` has no Advance Content NCPs!" % would_be_valid, ephemeral=True)

    if len(cleaned_args) > MAX_NCP_QUERY:
        return await interaction.command.koduck.send_message(interaction, 
                                        content=f"Too many NCPs, no more than {MAX_NCP_QUERY}!", ephemeral=True)

    for arg in cleaned_args:
        if not arg:
            continue

        power_name, field_title, field_description, power_color, _ = await power_ncp(interaction, arg, force_power=False,
                                                                                     ncp_only=True)
        if power_name is None:
            continue

        embed = discord.Embed(title="__{}__".format(power_name),
                              color=power_color)
        embed.add_field(name="**[{}]**".format(field_title),
                        value="_{}_".format(field_description))
        await interaction.command.koduck.send_message(interaction,  embed=embed)
    return


def query_npu(arg):
    if arg.capitalize() in skill_list:
        return False, "", ""

    eb_match = re.match(r"^(\d+)(?:\s*EB)?$", re.escape(arg), flags=re.IGNORECASE)
    if eb_match:
        eb_search = eb_match.group(1)
        result_ncps = power_df[(power_df["Type"] == "Upgrade") & (power_df["EB"] == eb_search)]
        if result_ncps.shape[0] == 0:
            return False, "", ""
        result_msg = ", ".join(result_ncps["Power/NCP"])
        result_title = "Finding all `%sEB` Navi Power Upgrades..." % eb_search
        return True, result_title, result_msg

    result_npu = power_df[power_df["Skill"].str.contains("^%s$" % re.escape(arg), flags=re.IGNORECASE)]
    if result_npu.shape[0] == 0:
        return False, "", ""
    result_title = "Finding all Navi Power Upgrades for `%s`..." % result_npu.iloc[0]["Skill"]
    result_string = ", ".join(result_npu["Power/NCP"])
    return True, result_title, result_string


async def upgrade(interaction: discord.Interaction, query: str):
    cleaned_args = clean_args([query])
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await interaction.command.koduck.send_message(interaction, 
                                        content="Give me the name of 1-%d default Navi Powers and I can find its **upgrades** for you!" % MAX_NPU_QUERY)
    if len(cleaned_args) > MAX_NPU_QUERY:
        return await interaction.command.koduck.send_message(interaction, 
                                        content="I can't pull up more than %d Navi Power Upgrades at a time!" % MAX_NPU_QUERY, ephemeral=True)

    if cleaned_args[0] in ['rule', 'ruling', 'rules']:
        ruling_msg = await find_value_in_table(interaction, help_df, "Command", "npuruling", suppress_notfound=True)
        if ruling_msg is None:
            return await interaction.command.koduck.send_message(interaction, 
                                        content="Couldn't find the rules for this command! (You should probably let the devs know...)", ephemeral=True)
        return await interaction.command.koduck.send_message(interaction, 
                                    content=ruling_msg["Response"])

    for arg in cleaned_args:
        arg = arg.lower()

        is_upgrade, result_title, result_msg = query_npu(arg)
        if is_upgrade:
            await send_query_msg(interaction, result_title, result_msg)
            continue
        if any((power_df["Type"] == "Upgrade") & power_df["Power/NCP"].str.contains("^%s$" % re.escape(arg), flags=re.IGNORECASE)):
            await ncp(interaction, arg)
            continue
        await interaction.command.koduck.send_message(interaction, 
                                 content="Couldn't find any Navi Power Upgrades for `%s`!" % arg, ephemeral=True)
    return


async def virus_master(interaction: discord.Interaction, arg, simplified=True):
    virus_info = await find_value_in_table(interaction, virus_df, "Name", arg, suppress_notfound=True, alias_message=True)

    if virus_info is None:
        virus_info = await find_value_in_table(interaction, pmc_virus_df, "Name", arg)
        if virus_info is None:
            return None, None, None, None, None, None

    virus_name = virus_info["Name"]
    virus_description = virus_info["Description"]
    virus_category = virus_info["Category"]
    virus_image = virus_info["Image URL"]
    virus_artist = virus_info["Image Artist"]
    virus_source = virus_info["From?"]
    virus_hp = virus_info["HP"]
    virus_element = virus_info["Element"]
    virus_tags = virus_info["Tags"]
    virus_stats = [int(virus_info["Mind"]), int(virus_info["Body"]), int(virus_info["Soul"])]
    virus_skills = {'Sense': virus_info["Sense"], 'Info': virus_info["Info"], 'Coding': virus_info["Coding"],
                    'Strength': virus_info["Strength"], 'Speed': virus_info["Speed"], 'Stamina': virus_info["Stamina"],
                    'Charm': virus_info["Charm"], 'Bravery': virus_info["Bravery"], 'Affinity': virus_info["Affinity"]}
    virus_powers = [virus_info["Powers1"], virus_info["Powers2"], virus_info["Powers3"], virus_info["Powers4"]]
    virus_drops = [virus_info["Drops1"], virus_info["Drops2"]]

    virus_footer = "Category: %s" % virus_category

    if 'Mega' in virus_tags:
        virus_footer_bit = "MegaVirus"
    else:
        virus_footer_bit = "Virus"
    if virus_source in playermade_list:
        virus_footer += " (%s Unofficial %s)" % (virus_source, virus_footer_bit)
    elif virus_source in cc_list:
        virus_footer += " (%s Advance %s)" % (virus_source, virus_footer_bit)
    if virus_artist:
        if " (Provided)" in virus_artist:
            virus_footer += "\n(Artwork provided by %s)" % virus_artist.replace(" (Provided)", "")
        else:
            virus_footer += "\n(Artwork by %s)" % virus_artist

    if virus_source in cc_color_dictionary:
        virus_color = cc_color_dictionary[virus_source]
    elif 'Mega' in virus_tags:
        if 'Ω' in virus_name:
            virus_color = virus_colors["OmegaVirus"]
        else:
            virus_color = virus_colors["MegaVirus"]
    else:
        virus_color = virus_colors["Virus"]

    virus_descript_block = ""
    virus_title = ""

    virus_skills = [(key, int(val)) for key, val in virus_skills.items() if val and int(val) != 0]

    if not simplified:
        try:
            hp_int = int(virus_hp)
            if hp_int > PROBABLY_INFINITE:
                virus_hp = "∞"
            else:
                virus_hp = "%d" % hp_int
        except ValueError:
            pass
        virus_title = "HP %s" % virus_hp
        virus_descript_block = "**Element: %s**" % virus_element + \
                               "\nMind %d, Body %d, Soul %d" % (*virus_stats,)
        if virus_skills:
            virus_descript_block += "\n%s" % ", ".join(["%s %s" % (key, val) for key, val in virus_skills])
        if virus_powers:
            virus_descript_block += "\nPowers: %s" % ", ".join([i for i in virus_powers if i])
        if virus_drops:
            virus_descript_block += "\nDrops: %s" % ", ".join([i for i in virus_drops if i])
        virus_descript_block += "\n"

    if simplified:
        virus_descript_block += "*%s*\n" % virus_description

    if not virus_tags:
        virus_tags = "None"
    virus_descript_block += "**__Tags: %s__**" % virus_tags

    if not simplified:
        virus_descript_block += "\n*%s*" % virus_description

    return virus_name, virus_title, virus_descript_block, virus_footer, virus_image, virus_color


def query_virus(arg_lower):
    alias_check = cc_df[
        cc_df["Alias"].str.contains("(?:^|,|;)\s*%s\s*(?:$|,|;)" % re.escape(arg_lower), flags=re.IGNORECASE)]
    if alias_check.shape[0] > 0:
        arg_lower = alias_check.iloc[0]["Source"].lower()

    valid_cc_list = list(pd.unique(virus_df["From?"].str.lower().str.strip()))
    [valid_cc_list.remove(i) for i in ["core"]]
    if arg_lower in [i.lower() for i in virus_category_list]:
        sub_df = virus_df[virus_df["Category"].str.contains(re.escape(arg_lower), flags=re.IGNORECASE)]
        result_title = "Viruses in the `%s` category..." % sub_df.iloc[0]["Category"]
        result_msg = ", ".join(sub_df["Name"])
    elif arg_lower in virus_tag_list:
        sub_df = virus_df[virus_df["Tags"].str.contains(re.escape(arg_lower), flags=re.IGNORECASE)]
        result_title = "Viruses with the `%s` tag..." % arg_lower.capitalize()
        result_msg = ", ".join(sub_df["Name"])
    elif arg_lower in valid_cc_list:
        sub_df = virus_df[virus_df["From?"].str.contains(re.escape(arg_lower), flags=re.IGNORECASE)]
        result_title = "Viruses from the `%s` Advance Content..." % sub_df.iloc[0]["From?"]
        result_msg = ", ".join(sub_df["Name"])
    elif arg_lower in [i.lower() for i in playermade_list]:
        subdf = pmc_virus_df[pmc_virus_df["From?"].str.contains(re.escape(arg_lower), flags=re.IGNORECASE)]
        if subdf.shape[0] == 0:
            return False, "", ""
        result_title = "Pulling up all Viruses from unofficial `%s` Player-Made Content..." % subdf.iloc[0]["From?"]
        result_msg = ", ".join(subdf["Name"])
    else:
        return False, "", ""
    return True, result_title, result_msg


async def virus(interaction: discord.Interaction, query:str, detailed:bool=False):
    cleaned_args = clean_args([query])
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await interaction.command.koduck.send_message(interaction,
                                        content=f"Give me the name of 1-{MAX_VIRUS_QUERY} **Viruses** and I can pull up their info for you!\n\n" +
                                                    "I can query Viruses by **Category**, **Tag**, or **Advance Content**, and pull up the list of Virus categories with `virus category`!\n" +
                                                    "For a list of all Virus categories, use `virus category`, and all current Virus tags with `virus tag`. To pull up details on a specific Category or Tag, use `tag` instead. (i.e. `tag artillery`)")
    elif cleaned_args[0] in ['category', 'categories']:
        result_title = "Displaying all known Virus Categories..."
        result_text = ", ".join(virus_category_list)
        return await send_query_msg(interaction, result_title, result_text)
    elif cleaned_args[0] in ['tag', 'tags']:
        result_title = "Displaying all known Virus Tags..."
        result_text = ", ".join([i.capitalize() for i in virus_tag_list])
        return await send_query_msg(interaction, result_title, result_text)
    elif cleaned_args[0] in ['rule', 'ruling', 'rules']:
        ruling_msg = await find_value_in_table(interaction, help_df, "Command", "virusruling", suppress_notfound=True)
        if ruling_msg is None:
            return await interaction.command.koduck.send_message(interaction,
                                        content="Couldn't find the rules for this command! (You should probably let the devs know...)", ephemeral=True)
        return await interaction.command.koduck.send_message(interaction,
                                    content=ruling_msg["Response"])
    elif len(cleaned_args) > MAX_VIRUS_QUERY:
        return await interaction.command.koduck.send_message(interaction,
                                        content=f"Too many viruses, no more than {MAX_VIRUS_QUERY}!", ephemeral=True)

    arg_combined = " ".join(cleaned_args)
    is_query, result_title, result_msg = query_virus(arg_combined)
    if is_query:
        return await send_query_msg(interaction, result_title, result_msg)

    for arg in cleaned_args:
        if not arg:
            continue
        virus_name, virus_hp, virus_description, virus_footer, virus_image, virus_color = await virus_master(interaction, arg, simplified=not detailed)
        if virus_name is None:
            continue
        if detailed:
            embed = discord.Embed(title=virus_name, color=virus_color)
            embed.add_field(name=virus_hp,
                            value=virus_description, inline=True)
        else:
            embed = discord.Embed(title=virus_name,
                                description=virus_description,
                                color=virus_color)
        embed.set_thumbnail(url=virus_image)
        embed.set_footer(text=virus_footer)
        await interaction.command.koduck.send_message(interaction, embed=embed)

    return


async def query_func(interaction: discord.Interaction, query: str):
    cleaned_args = clean_args([query])
    if len(cleaned_args) < 1:
        return await interaction.command.koduck.send_message(interaction, 
                                                 content="This command can sort battlechips, NCPs, and powers by Category, and single out Advance Content chips! " +
                                                 "Please type `help query` for more information.")
    arg = cleaned_args[0]
    arg_combined = " ".join(cleaned_args)

    is_chip_query, chip_title, chip_msg = query_chip(cleaned_args)
    is_ncp_query, ncp_title, ncp_msg = query_ncp(arg_combined)
    if is_chip_query and is_ncp_query:
        result_title = "Pulling up all BattleChips and NCPs from %s..." % re.match(r".*(`.+`).*", chip_title).group(1)
        ncp_addon = ["%s(NCP)" % i for i in ncp_msg.split(", ")]
        result_msg = chip_msg + ", " + ", ".join(ncp_addon)
        return await send_query_msg(interaction, result_title, result_msg)
    elif is_chip_query:
        return await send_query_msg(interaction, chip_title, chip_msg)
    elif is_ncp_query:
        return await send_query_msg(interaction, ncp_title, ncp_msg)

    is_virus_query, result_title, result_msg = query_virus(arg_combined)
    if is_virus_query:
        return await send_query_msg(interaction, result_title, result_msg)

    is_npu_query, result_title, result_msg = query_npu(arg_combined)
    if is_npu_query:
        return await send_query_msg(interaction, result_title, result_msg)

    is_power_query, result_title, result_msg = query_power(cleaned_args)
    if is_power_query:
        return await send_query_msg(interaction, result_title, result_msg)

    if arg in ['daemon', 'daemons']:
        _, result_title, result_msg = mainadvance.query_daemon()
        return await send_query_msg(interaction, result_title, result_msg)

    if arg_combined in ['networkmod', 'mod', 'new connections', 'newconnections']:
        _, result_title, result_msg = mainadvance.query_network()
        return await send_query_msg(interaction, result_title, result_msg)

    if arg_combined in ['weather', 'cyberweather']:
        _, result_title, result_msg = mainadvance.query_weather()
        return await send_query_msg(interaction, result_title, result_msg)

    if arg_combined in ['bond', 'bondpower', 'bondpowers', 'bonds']:
        result_title = "Pulling up all Bond Powers..."
        result_msg = ', '.join(bond_df["BondPower"])
        return await send_query_msg(interaction, result_title, result_msg)

    would_be_valid = pity_cc_check(arg_combined)
    if would_be_valid:
        return await interaction.command.koduck.send_message(interaction, 
                                        content="`%s` has no queryable Advance Content!" % would_be_valid, ephemeral=True)

    return await interaction.command.koduck.send_message(interaction, 
                                    content="`%s` is not a valid query!" % query, ephemeral=True)


async def mysterydata(interaction: discord.Interaction, md_type: typing.Literal["Common", "Uncommon", "Rare", "Gold", "Violet", "Sapphire"], chip_ncps_only: bool = False):
    arg = md_type.lower().strip()
    force_reward = chip_ncps_only

    mysterydata_type = mysterydata_df[mysterydata_df["MysteryData"].str.contains("^%s$" % re.escape(arg), flags=re.IGNORECASE)]

    if mysterydata_type.shape[0] == 0:
        return await interaction.command.koduck.send_message(interaction, 
                                                             content=f"{md_type} isn't a valid type of Mystery Data!", 
                                                             ephemeral=True)

    bonus_count = 0
    bonus_limit = 1

    results_list = []
    while bonus_count < bonus_limit:
        if bonus_count >= MAX_MD_BONUS:
            break

        roll_probabilities = mysterydata_type[mysterydata_type["Type"] == "Info"]
        if force_reward:
            roll_probabilities = roll_probabilities[
                roll_probabilities["Value"].str.contains("^BattleChip|NCP|NPU$", flags=re.IGNORECASE)]
        roll_category = roll_row_from_table(roll_probabilities)["Value"]

        #temporary bonus roll shenanigans
        if "Bonus Roll" in roll_category:
            bonus_limit += 1
            continue

        df_sub = mysterydata_type[mysterydata_type["Type"] == roll_category]
        result_chip = roll_row_from_table(df_sub)["Value"]

        if not re.match(r"\w+\s\w+", result_chip): # is not a sentence
            results_list.append(result_chip + " " + roll_category)
        else:
            results_list = [re.sub(r"\s*(\.|!|\?)+\s*$", '', result_chip)]  # removes last punctuation marks!
            break

        if roll_category == "Zenny":
            results_list = [f"{int(result_chip) * (random.randint(1, 6) + random.randint(1, 6))} Zenny"]
            break

        bonus_count += 1

    if arg in mysterydata_dict:
        md_color = mysterydata_dict[arg]["color"]
        md_image_url = mysterydata_dict[arg]["image"]
    else:
        md_color = 0xffffff
        md_image_url = ""

    if len(results_list) > 1:
        result_text = f"{', '.join(results_list[0:-1])} and {results_list[-1]}"  # proper grammar, darnit
    else:
        result_text = results_list[0]
    result_text += "!"

    arg = arg.capitalize()
    embed = discord.Embed(title=f"__{arg} MysteryData__",
                          description=f"_{interaction.user.mention} accessed the {arg} MysteryData..._\n\nGot: **{result_text}**",
                          color=md_color)
    embed.set_thumbnail(url=md_image_url)
    return await interaction.command.koduck.send_message(interaction, embed=embed)


async def bond(interaction: discord.Interaction, query: str):
    cleaned_args = [q.strip().lower() for q in query.split(",") if q]
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await interaction.command.koduck.send_message(interaction, 
                                        content="Give me a **Bond Power** and I can pull up its info for you!\nFor a list of all Bond Powers, use `bond all`!")
    elif cleaned_args[0] in ['rule', 'ruling', 'rules']:
        ruling_msg = await find_value_in_table(interaction, help_df, "Command", "bondruling", suppress_notfound=True)
        if ruling_msg is None:
            return await interaction.command.koduck.send_message(interaction, 
                                        content="Couldn't find the rules for this command! (You should probably let the devs know...)", ephemeral=True)
        return await interaction.command.koduck.send_message(interaction, 
                                    content=ruling_msg["Response"])
    elif len(cleaned_args) > MAX_BOND_QUERY:
        return await interaction.command.koduck.send_message(interaction, 
                                        content="Too many Bond Powers; no more than %d!\nBesides, there's only four Bond Powers in the game!" % MAX_BOND_QUERY, ephemeral=True)
    if cleaned_args[0] in ['all', 'list']:
        result_title = "Pulling up all Bond Powers..."
        result_msg = ', '.join(bond_df["BondPower"])
        return await send_query_msg(interaction, result_title, result_msg)

    for arg in cleaned_args:
        bond_info = await find_value_in_table(interaction, bond_df, "BondPower", arg)
        if bond_info is None:
            continue

        bond_title = bond_info["BondPower"]
        bond_cost = bond_info["Cost"]
        bond_description = bond_info["Description"]

        embed = discord.Embed(
            title="__%s__" % bond_title,
            color=0x24ff00)
        embed.add_field(name="**({})**".format(bond_cost),
                        value="_{}_".format(bond_description))

        await interaction.command.koduck.send_message(interaction,  embed=embed)
    return


async def element(interaction: discord.Interaction, number: int, category: typing.Literal['All','Nature','Fantasy','Science','Actions','Art','???']='All'):
    element_return_number = number
    element_category = category
    
    if element_category != 'All':
        sub_element_df = element_df[element_df["category"].str.contains(f"^\s*{category}\s*$", flags=re.IGNORECASE)]
        if sub_element_df.shape[0] == 0:
          return await interaction.command.koduck.send_message(interaction, content="Invalid category provided!\n" +
                                                        "Categories: **%s**" % ", ".join(element_category_list), ephemeral=True)
        
        element_flavor_title = f"Picked {element_return_number} random element(s) from the {element_category} category..."
    else:
        sub_element_df = element_df
        element_flavor_title = f"Picked {element_return_number} random element(s)..."
    if element_return_number < 1:
        return await interaction.command.koduck.send_message(interaction, content="The number of elements can't be 0 or negative!", ephemeral=True)
    if element_return_number > MAX_ELEMENT_QUERY:
        return await interaction.command.koduck.send_message(interaction, content=f"That's too many elements! Are you sure you need more than {MAX_ELEMENT_ROLL}?", ephemeral=True)

    elements_selected = random.sample(range(sub_element_df.shape[0]), element_return_number)
    elements_name = [sub_element_df.iloc[i]["element"] for i in elements_selected]

    element_color = 0x48C800
    elements_list = ", ".join(elements_name)

    embed = discord.Embed(title=element_flavor_title,
                          color=element_color,
                          description=elements_list)
    return await interaction.command.koduck.send_message(interaction, embed=embed)


async def rulebook(interaction: discord.Interaction, query:str=""):
    split_args = [re.sub(r"([a-z])(\d)",r"\1 \2", query, flags=re.IGNORECASE)]
    cleaned_args = clean_args([" ".join(split_args)])
    errmsg = []

    if query:
        is_get_latest = cleaned_args[0] in ["all", "latest", "new"]
    else:
        is_get_latest = True

    if is_get_latest:
        rulebook_df["BiggNumber"] = pd.to_numeric(rulebook_df["Version"])
        ret_books = rulebook_df.loc[rulebook_df.groupby(["Name"])["BiggNumber"].idxmax()]
        book_names = ["**%s %s %s**: <%s>" % (book["Name"], book["Release"], book["Version"], book["Link"]) for _, book in
                      ret_books.iterrows()]
    elif cleaned_args[0] == "help":
        return await interaction.command.koduck.send_message(interaction, 
                                        content="Links the **rulebooks** for NetBattlers! You can also look for a specific rulebook version! (i.e. `rulebook beta 7 adv 6`)")
    elif cleaned_args[0] in ['nyx', 'cc', 'crossover']:
        book_names = ["**Nyx Crossover Content**(?): <%s>" % nyx_link]
    elif cleaned_args[0] in ['grid', 'gridbased', 'grid-based', 'gridbasedcombat', 'grid-basedcombat']:
        book_names = ["**Grid-Based Combat Rules**(?): <%s>" % grid_link]
    else:
        book_names = []

    if not book_names:
        errmsg = []
        book_query = {"Name": "", "Type": "All", "Version": None, "Release": ""}
        book_queries = []
        in_progress = False
        for arg in cleaned_args:
            try:
                # if arg.isdigit():
                float(arg)
                version_str = arg
                if book_query["Version"] is not None:
                    await interaction.command.koduck.send_message(interaction, content="Going with Version `%s`!" % version_str)
                book_query["Version"] = version_str
                continue
            except ValueError:
                pass

            if arg in (['beta', 'netbattlers', 'netbattler', 'nb', 'b'] + ['advance', 'advanced', 'nba', 'adv', 'a'] + ['alpha']+['pre-alpha', 'prealpha']):
                if in_progress:
                    book_queries.append(book_query)
                    book_query = {"Name": "", "Type": "All", "Version": None, "Release": ""}
                if arg in (['beta', 'netbattlers', 'netbattler', 'nb', 'b']+['alpha']+['pre-alpha', 'prealpha']):
                    book_query["Name"] = "NetBattlers"
                    if arg in ['alpha']:
                        book_query["Release"] = "Alpha"
                    elif arg in ['pre-alpha', 'prealpha']:
                        book_query["Release"] = "Pre-Alpha"
                    else:
                        book_query["Release"] = "Beta"
                else:
                    book_query["Name"] = "NetBattlers Advance"
                in_progress = True

            if arg in ['all', 'list']:
                book_query["Version"] = "All"
                in_progress = True

            if arg in (['full', 'fullres', 'full-res'] + ['mobile']):
                if arg in ['full', 'fullres']:
                    book_query["Type"] = "Full Res"
                else:
                    book_query["Type"] = "Mobile"
                in_progress = True

        if in_progress:
            book_queries.append(book_query)

        ret_book = pd.Series(False, index=rulebook_df.index)
        for book_query in book_queries:
            bookname = book_query["Name"]
            booktype = book_query["Type"]
            book_version = book_query["Version"]
            book_release = book_query["Release"]

            if not bookname:
                await interaction.command.koduck.send_message(interaction, 
                                         content="Don't know which book you want! Please specify either 'Beta', 'Advance', or 'Alpha'!'", ephemeral=True)
                continue
            elif bookname == 'Unknown':
                continue

            subfilt = (rulebook_df["Name"] == bookname)
            if booktype != "All":
                subfilt = subfilt & (rulebook_df["Type"] == booktype)
                book_type_str = " (`%s`)" % booktype
            else:
                book_type_str = ""

            if book_release:
                subfilt = subfilt & (rulebook_df["Release"]==book_release)

            if book_version is None:
                subfilt = subfilt.index == pd.to_numeric(rulebook_df[subfilt]["Version"]).idxmax()
                book_version_str = " (Most recent)"
            elif book_version == "All":
                book_version_str = ""
            else:
                subfilt = subfilt & (rulebook_df["Version"].str.contains("^" + book_version))
                book_version_str = " `%s`" % book_version

            if not any(subfilt):
                msg404 = "Couldn't find `%s`%s!%s" % (bookname, book_version_str, book_type_str)
                errmsg.append(msg404)

            ret_book = ret_book | subfilt

        ret_books = rulebook_df.loc[ret_book]
        book_names = [
            "**%s %s %s** (%s): <%s>" % (book["Name"], book["Release"], book["Version"], book["Type"], book["Link"])
            for _, book in ret_books.iterrows()]

    book_names += errmsg
    if not book_names:
        return await interaction.command.koduck.send_message(interaction, content=f"Couldn't find any rulebooks for `{query}`!")
    return await interaction.command.koduck.send_message(interaction, content="\n".join(book_names))


async def virusr(interaction: discord.Interaction, number: int=1, 
                 artillery:int=0, disruption:int=0, striker: int=0, support:int=0, wrecker:int=0, 
                 mega:bool=False, omega:bool=False):

    virus_nums = [number, artillery, disruption, striker, support, wrecker]
    virus_pairs = zip(["any", "artillery", "disruption", "striker", "support", "wrecker"], virus_nums)

    total_v = sum(virus_nums)
   
    if total_v > MAX_RANDOM_VIRUSES:
        return await interaction.command.koduck.send_message(interaction, content=f"Rolling too many Viruses! (Only up to {MAX_RANDOM_VIRUSES}!)", ephemeral=True)
    elif total_v == 0:
        return await interaction.command.koduck.send_message(interaction, content="Rolling... no Viruses? Huh?", ephemeral=True)
    elif total_v == 1:
        virus_keyword = "Virus"
    else:
        virus_keyword = "Viruses"

    virus_roll_titles = []
    viruses_names = []

    df_filt = np.zeros(virus_df.shape[0], dtype=bool)
    if not mega:
        df_filt = df_filt | (virus_df["Tags"].str.contains(r"Mega", flags=re.IGNORECASE) & ~virus_df["Name"].str.contains(r"Ω"))
    if not omega:
        df_filt = df_filt | (virus_df["Tags"].str.contains(r"Mega", flags=re.IGNORECASE) & virus_df["Name"].str.contains(r"Ω")) # MettaurOmega, pls

    v_df = virus_df[~df_filt]
    
    for virus_type, virus_num in virus_pairs:
        sub_df = v_df
        if virus_num == 0:
            continue
        if virus_type != "any":
            sub_df = sub_df[sub_df["Category"].str.contains(r"^%s$" % re.escape(virus_type), flags=re.IGNORECASE)]
            virus_cat = sub_df["Category"].iloc[0]
        else:
            virus_cat = "Random"
        if sub_df.shape[0] < virus_num:
            search_query = virus_type
            await interaction.command.koduck.send_message(interaction, 
                                                          content=f"There's only {sub_df} `{search_query}` Viruses! Limiting it to {sub_df.shape[0]}...", ephemeral=True)
            virus_num = sub_df.shape[0]

        virus_roll_titles.append(f"{virus_num} {virus_cat}")
        viruses_rolled = random.sample(range(sub_df.shape[0]), virus_num)
        viruses_names += [sub_df.iloc[i]["Name"] for i in viruses_rolled]

    virus_title = ", ".join(virus_roll_titles)
    virus_list = ", ".join(viruses_names)
    embed = discord.Embed(title="Rolling %s %s..." % (virus_title, virus_keyword),
                          color=virus_colors["Virus"],
                          description=virus_list)
    return await interaction.command.koduck.send_message(interaction, embed=embed)

# TODO: merge with the fight generator?
async def adventure(interaction: discord.Interaction, adv_type: str="Core"):
    if not adv_type:
        arg = "core"
    else:
        arg = adv_type.lower().strip()

    if arg == 'core':
        adventure_df_use = adventure_df[adventure_df["Sort"] == "Core"]
    else:
        adventure_df_use = adventure_df
# -----------------------------------------------------------------------
# ADVENTURE HEADERS
    # The "Sort" column controls how the data is sorted between the option presets.
    # The "Definition" column controls the filtering rules for grammar correction.
    # All of the randomization is done initially for the Chaos preset.

    # The following sorting mechanisms have been removed until more options have been created for them.
    # Atmosphere, NPC last names, vulnerability header, some sort/definition rules that are needed in later iterations
# -----------------------------------------------------------------------
# Adventure headers
# Corresponds to the header table in the book. Extended for customization.

    advheaddf_sub = adventure_df[adventure_df["Type"] == "AdvHeader"]
    advhead_row = roll_row_from_table(adventure_df_use, df_filters={"Type": "AdvHeader"})
    define_advheader = [advhead_row["Definition"]]
    adv_header = advhead_row["Result"]

# -----------------------------------------------------------------------
# Header results
# Corresponds to the results table in the book.

    headresultdf_row = roll_row_from_table(adventure_df_use, df_filters={"Type": "HeaderResult"})
    define_headresult = [headresultdf_row["Definition"]]
    header_result = headresultdf_row["Result"]


# -----------------------------------------------------------------------
# Conflict generators. Headers for conflicts and vulnerabilities primarily exist for homebrew tables.

    conflict_result = roll_row_from_table(adventure_df_use, df_filters={"Type": "ConflictResult"})["Result"]
    vuln_result = roll_row_from_table(adventure_df_use, df_filters={"Type": "VulnResult"})["Result"]

# -----------------------------------------------------------------------
# Generators for human beings.
# Although with the NBC you never know, it might be for ghosts instead.
# First name generator corresponds to the first names in the Core book. Last names are homebrew.
# Maybe to-do navi names too?
    npc_firstname = roll_row_from_table(adventure_df_use, df_filters={"Type": "NPCFirstName"})["Result"]

# -----------------------------------------------------------------------
# these use the same tables, just need individual results
    npc_personality = roll_row_from_table(adventure_df_use, df_filters={"Type": "Personality"})["Result"]

# -----------------------------------------------------------------------

    npc_occupation = roll_row_from_table(adventure_df_use, df_filters={"Type": "Occupation"})["Result"]
    npc_feature = roll_row_from_table(adventure_df_use, df_filters={"Type": "Feature"})["Result"]

    if arg == 'core':
        generated_msg = f"The adventure starts with the kids {adv_header} {header_result} " + \
                        f"But an evildoer is there to {conflict_result} " + \
                        f"Their name is **{npc_firstname}**, and they are {npc_personality} {npc_occupation}, notable for {npc_feature}. " + \
                        f"Their vulnerability is {vuln_result}\n"
        return await interaction.command.koduck.send_message(interaction, content=generated_msg)

    # Classification headers (for the type of adventure the generator sorts from)
    # These three work together (Except core rulebook doesn't really care about ClassHeader, for now.)

    class_header = roll_row_from_table(adventure_df_use, df_filters={"Type": "ClassHeader"})["Result"]
    conflict_header = roll_row_from_table(adventure_df_use, df_filters={"Type": "ConflictHeader"})["Result"]
    navi_personality = roll_row_from_table(adventure_df_use, df_filters={"Type": "Personality"})["Result"]
    navi_hostility = roll_row_from_table(adventure_df_use, df_filters={"Type": "NaviHostility"})["Result"]

    # -----------------------------------------------------------------------
    # Element generation. Just borrowed the element picker code for this.
    navi_element = roll_row_from_table(element_df)["element"]

    # -----------------------------------------------------------------------
    # Extended generator tables.
    conflict_type = roll_row_from_table(adventure_df_use, df_filters={"Type": "ConflictType"})["Result"]

#   TODO: if (arg == 'extended'):
    if arg == 'chaos':
        generated_msg = f"The adventure starts with {class_header} {adv_header} {header_result} " + \
                        f"But {conflict_header} {conflict_result} Their vulnerability is {vuln_result}\n" + \
                        f"**{npc_firstname}** is {npc_personality} {npc_occupation}, notable for {npc_feature}.\n" + \
                        f"Next, {class_header} meet {navi_personality} navi with the element of {navi_element} that greets them with {navi_hostility}.\n" + \
                        f"The primary conflict is {conflict_type}"
        return await interaction.command.koduck.send_message(interaction, content=generated_msg)
    else:
        return await interaction.command.koduck.send_message(interaction, content="Please specify either Core or Chaos.")


async def fight(interaction: discord.Interaction):
    # element
    navi_element = roll_row_from_table(element_df)["element"]
    # skills
    bestskill = roll_row_from_table(fight_df, df_filters={"Type": "Skill"})["Result"]
    trainedskill = roll_row_from_table(fight_df, df_filters={"Type": "Skill"})["Result"]
    # secret weapon
    secret_weapon = roll_row_from_table(fight_df, df_filters={"Type": "SecretWeapon"})["Result"]
    # weakness
    weakness = roll_row_from_table(fight_df, df_filters={"Type": "Weakness"})["Result"]

    # arena
    arena = roll_row_from_table(fight_df, df_filters={"Type": "Arena"})["Result"]
    # element manifest
    element_manifest = roll_row_from_table(fight_df, df_filters={"Type": "ElementManifest"})["Result"]
    # navi start
    navi_start = roll_row_from_table(fight_df, df_filters={"Type": "NaviStart"})["Result"]
    # trouble type
    trouble_type = roll_row_from_table(fight_df, df_filters={"Type": "TroubleType"})["Result"]
    # fight objective
    fight_objective = roll_row_from_table(fight_df, df_filters={"Type": "FightObjective"})["Result"]
    # real world assist
    real_world_assist = roll_row_from_table(fight_df, df_filters={"Type": "RealWorldAssist"})["Result"]

    generated_msg = f"For this fight, this Navi has the element **{navi_element}**, and is proficient in **{bestskill}**. They are also trained in **{trainedskill}**. " + \
                    f"**{secret_weapon}**, but their weakness is **{weakness}**.\n" + \
                    f"The arena is **{arena}**, and the Navi's element manifests as **{element_manifest}**. The Navi is **{navi_start}**!\n" + \
                    f"{trouble_type}, and the NetOps need to **{fight_objective}**! However, in the real world, **{real_world_assist}** is there to help!"
    return await interaction.command.koduck.send_message(interaction, content=generated_msg)


async def sheet(interaction: discord.Interaction):
    msg_txt = f"**Official NetBattlers Character Sheet:** <{settings.character_sheet}>\nFor player-made character sheets, search for sheets in the Player-Made Repository using `playermaderepo character sheet`!"
    return await interaction.command.koduck.send_message(interaction, content=msg_txt)


async def glossary(interaction: discord.Interaction, term: str):
    if not term:
        return await interaction.command.koduck.send_message(interaction, 
                                        content="Use me to pull up a **Glossary** term in ProgBot! I can also try to search for a term if you know the first few letters!")
    cleaned_arg = term.strip().lower()

    glossary_info = await find_value_in_table(interaction, glossary_df, "Name", cleaned_arg, suppress_notfound=True) # exact match

    if glossary_info is None: # fuzzier match
        match_candidates = glossary_df[glossary_df["Name"].str.contains("^" + re.escape(cleaned_arg), flags=re.IGNORECASE)]

        if match_candidates.shape[0] < 1:
            return await interaction.command.koduck.send_message(interaction,  content="Didn't find any matches for `%s` in the glossary!" % term, ephemeral=True)
        if match_candidates.shape[0] > 1:
            progbot_list = ["> **%s**: `%s`" % (nam, cmd)
                            for nam, cmd in zip(match_candidates['Name'], match_candidates['ProgBot Command'])]
            return await interaction.command.koduck.send_message(interaction, content="Found multiple matches under `%s` in the glossary!\n%s" %
                                                                            (term, "\n".join(progbot_list)), ephemeral=True)
        glossary_info = match_candidates.iloc[0]
        
    if glossary_info["ProgBot Function"] not in globals():
        return await  interaction.command.koduck.send_message(interaction,
                                        content="Don't recognize the function `%s`! (You should probably let the devs know...)" % glossary_info["ProgBot Function"], ephemeral=True)

    #spotlight needs to be moved to interaction...
    progbot_func = globals()[glossary_info["ProgBot Function"]]
    return await progbot_func(interaction, glossary_info["ProgBot Argument"])


async def find_chip_ncp_power(interaction: discord.Interaction, query: str):
    cleaned_args = clean_args([query])

    if not query or (cleaned_args[0] in ["help"]):
        return await interaction.command.koduck.send_message(interaction, 
                                        content=f"I can search through **Chips**, **Powers**, and **NCPs**! Give me 1-{MAX_CHIP_QUERY} terms and I'll try to find them!")

    if len(cleaned_args) > MAX_CHIP_QUERY:
        return await interaction.command.koduck.send_message(interaction,  content=f"Too many items, no more than {MAX_CHIP_QUERY}!", ephemeral=True)

    for arg in cleaned_args:
        item_title, item_trimmed, item_description, item_color, item_footer = await chipfinder(interaction, arg, suppress_err_msg=True)

        if item_title is None:
            item_title, item_trimmed, item_description, item_color, item_footer = await power_ncp(interaction, arg, force_power=False,
                                                                                      ncp_only=False, suppress_err_msg=True)
            if item_title is None:
                item_title, item_trimmed, item_description, item_color, item_footer = await power_ncp(interaction, arg, force_power=False,
                                                                                         ncp_only=True, suppress_err_msg=True)
                if item_title is None:
                    await interaction.command.koduck.send_message(interaction,  content="Unable to find `%s`!" % arg, ephemeral=True)
                    continue
        embed = discord.Embed(
            title="__%s__" % item_title,
            color=item_color)
        embed.add_field(name=f"[{item_trimmed}]", 
                        value=f"_{item_description}_")
        await interaction.command.koduck.send_message(interaction, embed=embed)

    return
