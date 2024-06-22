import re

import discord
from pandas import DataFrame, Series, unique, read_csv
from discord.ext import commands
import settings
import random
import logging
import logging.handlers

CONTENT_CHAR_LIMIT = 2000
EMBED_CHAR_LIMIT = 200

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

element_df = read_csv(settings.elementfile, sep="\t").fillna('')
element_category_list = unique(element_df["category"].dropna())

help_df = read_csv(settings.helpfile, sep="\t").fillna('')
help_df["Response"] = help_df["Response"].str.replace('\\\\n', '\n', regex=True)
help_cmd_list = [i for i in help_df["Command"] if i]
help_df["Type"] = help_df["Type"].astype("category")
help_df["Type"] = help_df["Type"].cat.rename_categories(help_categories).cat.reorder_categories(list(help_categories.values())+[""])

rulebook_df = read_csv(settings.rulebookfile, sep="\t",  converters = {'Version': str}).fillna('')
pmc_link = rulebook_df[rulebook_df["Name"] == "Player-Made Repository"]["Link"].iloc[0]
nyx_link = rulebook_df[rulebook_df["Name"] == "Nyx"]["Link"].iloc[0]
grid_link = rulebook_df[rulebook_df["Name"] == "Grid-Based Combat"]["Link"].iloc[0]
random_chip_link = rulebook_df[rulebook_df["Name"] == "Randomized Chips"]["Link"].iloc[0]
rulebook_df = rulebook_df[(rulebook_df["Name"] == "NetBattlers") | (rulebook_df["Name"] == "NetBattlers Advance")]
# these might start complaining; double check that the labels in the rulebook are exact: captilization and whitespace matter!
rulebook_df["Type"] = rulebook_df["Type"].astype('category').cat.reorder_categories(["Mobile", "Full Res", "Bonus BattleChips"])
rulebook_df["Release"] = rulebook_df["Release"].astype('category').cat.reorder_categories(["Beta", "Alpha", "Pre-Alpha", "Version"])
rulebook_df = rulebook_df.sort_values(["Name", "Release", "Version", "Type"])

playermade_list = ["Genso Network"]

commands_df = read_csv(settings.commands_table_name, sep="\t").fillna('')
commands_dict = dict(zip(commands_df["Command"], commands_df["Description"]))

# set up the loggers
errlog = logging.getLogger('err')
err_handler = logging.handlers.RotatingFileHandler(filename=settings.error_file, maxBytes=50 * 1024 * 1024, encoding='utf-8', mode='w')
errlog.addHandler(err_handler)

bot = commands.Bot(command_prefix=">", 
                   activity=discord.Activity(type=discord.ActivityType.playing, name=settings.default_status), 
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
    if len(return_msg) > CONTENT_CHAR_LIMIT:
        if not interaction.response.is_done():
            return await interaction.response.send_message("Too many results! (You should probably let the devs know...)", ephemeral=True)
        return await interaction.channel.send("**%s**\n*%s*" % (return_title, return_msg))
    
    if not interaction.response.is_done():
        return await interaction.response.send_message("**%s**\n*%s*" % (return_title, return_msg)) 
    return await interaction.channel.send("**%s**\n*%s*" % (return_title, return_msg))


async def find_value_in_table(df, search_col, search_arg, suppress_notfound=False, alias_message=False, allow_duplicate=False):
    if not search_arg:
        return None, None
    add_msg = None
    if "Alias" in df:
        alias_check = filter_table(df, {"Alias": f"(?:^|,|;)\s*{re.escape(search_arg)}\s*(?:$|,|;)"})
        if (alias_check.shape[0] > 1) and (not allow_duplicate):
            return None, f"Found more than one match for {search_arg}! You should probably let the devs know..."
        if alias_check.shape[0] != 0:
            search_arg = alias_check.iloc[0][search_col]
            if alias_message:
                add_msg = f"Found as an alternative name for **{search_arg}**!"
    search_results = filter_table(df, {search_col: f"\s*^{re.escape(search_arg)}\s*$"})
    if search_results.shape[0] == 0:
        if not suppress_notfound:
            add_msg = "I can't find `%s`!" % search_arg
        return None, add_msg
    elif search_results.shape[0] > 1:
        if allow_duplicate:
            return search_results.iloc[random.randrange(0, search_results.shape[0])], add_msg
        else:
            return None, f"Found more than one match for {search_arg}! You should probably let the devs know..."
    return search_results.iloc[0], add_msg


async def send_multiple_embeds(i: discord.Interaction, list_embed, list_warn, error_no_embeds=True):
    msg_warns = [m for m in list_warn if m is not None and m]
    if not list_embed and not list_warn:
        return await i.response.send_message(content="No message to send! (You should probably let the dev team know...)", ephemeral=True)
    if msg_warns:
        await i.response.send_message(content="\n".join(msg_warns), ephemeral=error_no_embeds)
    for e in list_embed:
        if not i.response.is_done():
            await i.response.send_message(embed=e)
        else:
            await i.channel.send(embed=e)


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


# separate function on the off chance we can use the SQL DB
# filt_dict uses regex strings; assumes and
def filter_table(df: DataFrame, filt_dict: dict, not_filt = False):
    sub_df = df

    for k, v in filt_dict.items():
        if isinstance(v, bool):
            f = sub_df[k]==v
        else:
            f = sub_df[k].str.contains(v, flags=re.IGNORECASE)
        if not_filt:
            f = ~f
        sub_df = sub_df[f]

    return sub_df

# TODO for dataframe removal: any, unique, iloc[0], get by column, shape, groupby
# Also used: numpy contains