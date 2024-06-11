import re

import discord
from discord.ext import commands
import pandas as pd
import settings
import random

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

element_df = pd.read_csv(settings.elementfile, sep="\t").fillna('')
element_category_list = pd.unique(element_df["category"].dropna())

help_df = pd.read_csv(settings.helpfile, sep="\t").fillna('')
help_df["Response"] = help_df["Response"].str.replace('\\\\n', '\n', regex=True)
help_cmd_list = [i for i in help_df["Command"] if i]
help_df["Type"] = help_df["Type"].astype("category")
help_df["Type"] = help_df["Type"].cat.rename_categories(help_categories).cat.reorder_categories(list(help_categories.values())+[""])

rulebook_df = pd.read_csv(settings.rulebookfile, sep="\t",  converters = {'Version': str}).fillna('')
pmc_link = rulebook_df[rulebook_df["Name"] == "Player-Made Repository"]["Link"].iloc[0]
nyx_link = rulebook_df[rulebook_df["Name"] == "Nyx"]["Link"].iloc[0]
grid_link = rulebook_df[rulebook_df["Name"] == "Grid-Based Combat"]["Link"].iloc[0]
rulebook_df = rulebook_df[(rulebook_df["Name"] == "NetBattlers") | (rulebook_df["Name"] == "NetBattlers Advance")]
# these might start complaining; double check that the labels in the rulebook are exact: captilization and whitespace matter!
rulebook_df["Type"] = rulebook_df["Type"].astype('category').cat.reorder_categories(["Mobile", "Full Res", "Bonus BattleChips"])
rulebook_df["Release"] = rulebook_df["Release"].astype('category').cat.reorder_categories(["Beta", "Alpha", "Pre-Alpha", "Version"])
rulebook_df = rulebook_df.sort_values(["Name", "Release", "Version", "Type"])

playermade_list = ["Genso Network"]

commands_df = pd.read_csv(settings.commands_table_name, sep="\t").fillna('')
commands_dict = dict(zip(commands_df["Command"], commands_df["Description"]))

bot = commands.Bot(command_prefix=">", 
                   activity=discord.Activity(type=discord.ActivityType.playing, name="with Slash Commands"), 
                   status=discord.Status.online,
                   intents=discord.Intents.default())

def clean_args(args, lowercase=True):
    if len(args) == 1:
        args = re.split(r"(?:,|;|\s+)", args[0])

    if lowercase:
        args = [i.lower().strip() for i in args if i and not i.isspace()]
    else:
        args = [i.strip() for i in args if i and not i.isspace()]
    return args


async def send_query_msg(interaction, return_title, return_msg):
    return await interaction.response.send_message("**%s**\n*%s*" % (return_title, return_msg))


async def find_value_in_table(interaction: discord.Interaction, df, search_col, search_arg, suppress_notfound=False, alias_message=False, allow_duplicate=False):
    if not search_arg:
        return None
    if "Alias" in df:
        alias_check = df[
            df["Alias"].str.contains("(?:^|,|;)\s*%s\s*(?:$|,|;)" % re.escape(search_arg), flags=re.IGNORECASE)]
        if (alias_check.shape[0] > 1) and (not allow_duplicate):
            await interaction.response.send_message(f"Found more than one match for {search_arg}! You should probably let the devs know...", ephemeral=True)
            return None
        if alias_check.shape[0] != 0:
            search_arg = alias_check.iloc[0][search_col]
            if alias_message:
                await interaction.response.send_message(f"Found as an alternative name for **{search_arg}**!")

    search_results = df[df[search_col].str.contains("\s*^%s\s*$" % re.escape(search_arg), flags=re.IGNORECASE)]
    if search_results.shape[0] == 0:
        if not suppress_notfound:
            await interaction.response.send_message(content="I can't find `%s`!" % search_arg, ephemeral=True)
        return None
    elif search_results.shape[0] > 1:
        if allow_duplicate:
            return search_results.iloc[random.randrange(0, search_results.shape[0])]
        else:
            await interaction.response.send_message(content=f"Found more than one match for {search_arg}! You should probably let the devs know...", ephemeral=True)
        return None
    return search_results.iloc[0]


def roll_row_from_table(roll_df, df_filters={}):
    bool_filt = None
    if df_filters:
        for k, v in df_filters.items():
            if bool_filt is None:
                bool_filt = (roll_df[k] == v)
            else:
                bool_filt = bool_filt & (roll_df[k] == v)
        sub_df = roll_df[bool_filt]
    else:
        sub_df = roll_df
    row_num = random.randint(1, sub_df.shape[0]) - 1
    return sub_df.iloc[row_num]