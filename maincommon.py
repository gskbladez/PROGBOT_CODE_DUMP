import re

import discord
import koduck
import settings
import random
import sqlite3

cc_color_dictionary = {"MegaChip": 0xA8E8E8,
                       "ChitChat": 0xff8000,
                       "Radical Spin": 0x3f5cff,
                       "Skateboard Dog": 0xff0000,
                       "Night Drifters": 0xff0055,
                       "Mystic Lilies": 0x99004c,
                       "Leximancy": 0x481f65,
                       "Underground Broadcast": 0x73ab50,
                       "New Connections": 0xededed,
                       "Silicon Skin": 0xf012be,
                       "The Walls Will Swallow You": 0x734b38,
                       "MUDSLURP": 0x7687c6,
                       "Mudslurp": 0x7687c6,
                       "Tarot": 0xfcf4dc,
                       "Nyx": 0xa29e14,
                       "Cast the Dice": 0x429ef5,
                       "Summber Camp": 0xffad33,
                       "Genso Network": 0xff605d,
                       "Dark": 0xB088D0,
                       "Neko Virus": 0xa29e14,
                       "Item": 0xffffff,
                       "Chip": 0xbfbfbf,
                       "Mystery": 0x000000}

help_categories = {"Lookups": ':mag: **Lookups**',
                  "Rollers": ':game_die: **Rollers**',
                  "Helpers": ':thumbsup: **Helpers**',
                  "Reminders (Base)": ':information_source: **Reminders (Base)**',
                  "Reminders (Advanced Content)": ':trophy: **Reminders (Advanced Content)**',
                  "Reminders (Liberation)": ':map: **Reminders (Liberation)**',
                  "Reminders (DarkChips)": ':smiling_imp: **Reminders (DarkChips)**',
                  "Safety Tools": ':shield: **Safety Tools**'}

data_tables = sqlite3.connect(settings.data_tables)
data_tables.row_factory = sqlite3.Row
element_category_list = data_tables.execute("SELECT DISTINCT category FROM element").fetchall()
element_category_list = [row["category"] for row in element_category_list]

help_cmd_list = data_tables.execute("SELECT DISTINCT command FROM commands").fetchall()
help_cmd_list = [row["command"] for row in help_cmd_list]

pmc_link = data_tables.execute("SELECT link from rulebook WHERE name = 'Player-Made Repository'").fetchone()["link"]
nyx_link = data_tables.execute("SELECT link from rulebook WHERE name = 'Nyx'").fetchone()["link"]
grid_link = data_tables.execute("SELECT link from rulebook WHERE name = 'Grid-Based Combat'").fetchone()["link"]

playermade_list = ["Genso Network"]


def clean_args(args, lowercase=True):
    if len(args) == 1:
        args = re.split(r"(?:,|;|\s+)", args[0])

    if lowercase:
        args = [i.lower().strip() for i in args if i and not i.isspace()]
    else:
        args = [i.strip() for i in args if i and not i.isspace()]
    return args


async def send_query_msg(interaction, return_title, return_msg):
    return await interaction.command.koduck.send_message(interaction, content="**%s**\n*%s*" % (return_title, return_msg))


async def find_value_in_table(interaction: discord.Interaction, df, search_col, search_arg, suppress_notfound=False, alias_message=False, allow_duplicate=False):
    if not search_arg:
        return None
    search_arg = str.strip(search_arg)
    search_results = data_tables.execute(f"select * from {df} where {search_col} LIKE '{search_arg}'").fetchall()
    search_len = len(search_results)

    if search_len == 0:
        has_alias = data_tables.execute(f"select count(1) as count from pragma_table_info('{str.lower(df)}') where name='Alias'").fetchone()["count"] > 0
        alias_count = 0
        if has_alias:
            alias_row = data_tables.execute(f"select {search_col}, count(1) as count from {df} where Alias LIKE '%{search_arg}%'").fetchone()

            alias_count = alias_row["count"]
            # SQLITE's "LIKE" command is case insensitive

            if (alias_count > 1) and (not allow_duplicate):
                if(not allow_duplicate):
                    await interaction.command.koduck.send_message(interaction,
                                                                content=f"Found more than one match for {search_arg}! You should probably let the devs know...", ephemeral=True)
                    return None

            if (alias_count == 1):
                search_arg = alias_row[search_col]
                search_results = data_tables.execute(f"select * from {df} where {search_col} LIKE '{search_arg}'").fetchall()
                search_len = len(search_results)
                if alias_message:
                    await interaction.command.koduck.send_message(interaction,
                                                                    content=f"Found as an alternative name for **{search_arg}**!")
        if alias_count == 0:
            if not suppress_notfound:
                await interaction.command.koduck.send_message(interaction, content="I can't find `%s`!" % search_arg, ephemeral=True)
            return None

    elif search_len > 1:
        if allow_duplicate:
            return random.sample(search_results)
        else:
            await interaction.command.koduck.send_message(interaction, content=f"Found more than one match for {search_arg}! You should probably let the devs know...", ephemeral=True)
        return None
    return search_results[0]


def roll_row_from_table(roll_df, df_filters={}):
    filter_str = ''
    if df_filters:
        filter_str += 'WHERE '
        filter_str += ' AND '.join([f"{key} = '{value}'" for key, value in df_filters.items()])
    search_query = f'SELECT * FROM {roll_df} {filter_str} ORDER BY RANDOM() LIMIT 1'
    search_result = data_tables.execute(search_query).fetchone()
    return search_result
