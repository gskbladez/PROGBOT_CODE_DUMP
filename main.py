import discord
import asyncio
import sys, os, random
import koduck, yadon
import settings
import pandas as pd
import numpy as np
import re
import dice_algebra
import rply
from dotenv import load_dotenv

load_dotenv()
bot_token = os.getenv('DISCORD_TOKEN')

# Background task is run every set interval while bot is running (by default every 10 seconds)
async def backgroundtask():
    pass

MAX_POWER_QUERY = 5
MAX_NCP_QUERY = 5
MAX_CHIP_QUERY = 5
MAX_VIRUS_QUERY = 5
MAX_ELEMENT_ROLL = 12
MAX_MOD_QUERY = 5
ROLL_COMMENT_CHAR = '#'

skill_list = ['Sense', 'Info', 'Coding',
              'Strength', 'Speed', 'Stamina',
              'Charm', 'Bravery', 'Affinity']
cc_list = ["ChitChat", "Radical Spin", "Skateboard Dog", "Night Drifters", "Underground Broadcast",
           "Mystic Lilies", "Genso Network", "Leximancy", "Underground Broadcast", "New Connections", "Nyx"]
playermade_list = ["Genso Network"]

cc_color_dictionary = {"Mega": 0xA8E8E8,
                       "ChitChat": 0xff8000,
                       "Radical Spin": 0x3f5cff,
                       "Skateboard Dog": 0xff0000,
                       "Night Drifters": 0xff0055,
                       "Mystic Lilies": 0x99004c,
                       "Leximancy": 0x481f65,
                       "Underground Broadcast": 0x73ab50,
                       "New Connections": 0xededed,
                       "Tarot": 0xfcf4dc,
                       "Nyx": 0x878787,
                       "Genso Network": 0xff605d,
                       "Dark": 0xB088D0,
                       "Item": 0xffffff}

BUGREPORT_CHANNEL_ID = 704684798584815636

# TODO: add Nyx CC
mysterydata_dict = {"common": {"color": 0x48C800,
                               "image": "https://raw.githubusercontent.com/gskbladez/meddyexe/master/virusart/commonmysterydata.png"},
                    "uncommon": {"color": 0x00E1DF,
                                 "image": "https://raw.githubusercontent.com/gskbladez/meddyexe/master/virusart/uncommonmysterydata.png"},
                    "rare": {"color": 0xD8E100,
                             "image": "https://raw.githubusercontent.com/gskbladez/meddyexe/master/virusart/raremysterydata.png"}}

roll_difficulty_dict = {'E': 3, 'N': 4, 'H': 5}

settings.backgroundtask = backgroundtask


# Riject is a godsend: https://docs.google.com/spreadsheets/d/1aB6bOOo4E1zGhQmw2muOVdzNpu5ZBk58XZYforc8Eqw/edit?usp=sharing
# Other lists: https://docs.google.com/spreadsheets/d/1bnpvmU4KwmXzHUTuN3Al_W5ZKBuHAmy3Z-dEmCS6SqY/edit?usp=sharing
def prep_chip_df(df):
    df = df.fillna('')
    df["chip_lowercase"] = df["Chip"].str.lower()
    df["from_lowercase"] = df["From?"].str.lower()
    df["license_lowercase"] = df["License"].str.lower()
    df["category_lowercase"] = df["Category"].str.lower()

    return df


def prep_power_df(df):
    df = df.fillna('')
    df["power_lowercase"] = df["Power/NCP"].str.lower()
    df["from_lowercase"] = df["From?"].str.lower()
    return df


def prep_virus_df(df):
    df = df.fillna('')
    df["from_lowercase"] = df["From?"].str.lower()
    df["name_lowercase"] = df["Name"].str.lower()
    df["category_lowercase"] = df["Category"].str.lower()
    return df

def prep_daemon_df(df):
    df = df.fillna('')
    df["name_lowercase"] = df["Name"].str.lower()
    return df


chip_df = prep_chip_df(pd.read_csv(r"chipdata.tsv", sep="\t"))
power_df = prep_power_df(pd.read_csv(r"powerncpdata.tsv", sep="\t"))
virus_df = prep_virus_df(pd.read_csv(r"virusdata.tsv", sep="\t"))
daemon_df = prep_daemon_df(pd.read_csv(r"daemondata.tsv", sep="\t"))

bond_df = pd.read_csv(r"bonddata.tsv", sep="\t").fillna('')
bond_df["bondpower_lowercase"] = bond_df["BondPower"].str.lower()

tag_df = pd.read_csv(r"tagdata.tsv", sep="\t").fillna('')
tag_df["tag_lowercase"] = tag_df["Tag"].str.lower()

mysterydata_df = pd.read_csv(r"mysterydata.tsv", sep="\t").fillna('')
mysterydata_df["mysterydata_lowercase"] = mysterydata_df["MysteryData"].str.lower()

networkmod_df = pd.read_csv(r"networkmoddata.tsv", sep="\t").fillna('')
networkmod_df["name_lowercase"] = networkmod_df["Name"].str.lower()

crimsonnoise_df = pd.read_csv(r"crimsonnoisedata.tsv", sep="\t").fillna('')
crimsonnoise_df["mysterydata_lowercase"] = crimsonnoise_df["MysteryData"].str.lower()

element_df = pd.read_csv(r"elementdata.tsv", sep="\t").fillna('')
element_df["category_lowercase"] = element_df["category"].str.lower()
current_element_categories = ", ".join(pd.unique(element_df["category"]))


help_df = pd.read_csv(r"helpresponses.tsv", sep="\t").fillna('')
help_df["command_lowercase"] = help_df["Command"].str.lower()
help_df["Response"] = help_df["Response"].str.replace('\\\\n', '\n',regex=True)

chip_known_aliases = chip_df[chip_df["Alias"] != ""].copy()
chip_tag_list = chip_df["Tags"].str.split(",", expand=True) \
                               .stack() \
                               .str.strip() \
                               .str.lower() \
                               .unique()
virus_tag_list = virus_df["Tags"].str.split(";|,", expand=True) \
                                 .stack() \
                                 .str.strip() \
                                 .str.lower() \
                                 .unique()

pmc_chip_df = prep_chip_df(pd.read_csv(r"playermade_chipdata.tsv", sep="\t"))
pmc_power_df = prep_power_df(pd.read_csv(r"playermade_powerdata.tsv", sep="\t"))
pmc_virus_df = prep_virus_df(pd.read_csv(r"playermade_virusdata.tsv", sep="\t"))
pmc_daemon_df = prep_daemon_df(pd.read_csv(r"playermade_daemondata.tsv", sep="\t"))

parser = dice_algebra.parser
lexer = dice_algebra.lexer


##################
# BASIC COMMANDS #
##################
# Be careful not to leave out this command or else a restart might be needed for any updates to commands
async def updatecommands(context, *args, **kwargs):
    tableitems = yadon.ReadTable(settings.commandstablename).items()
    if tableitems is not None:
        koduck.clearcommands()
        for name, details in tableitems:
            try:
                koduck.addcommand(name, globals()[details[0]], details[1], int(details[2]))
            except (KeyError, IndexError, ValueError):
                pass


async def goodnight(context, *args, **kwargs):
    return await koduck.client.logout()


async def sendmessage(context, *args, **kwargs):
    if len(args) < 2:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_sendmessage_noparam)
    channelid = args[0]
    THEchannel = koduck.client.get_channel(channelid)
    THEmessagecontent = context["paramline"][context["paramline"].index(settings.paramdelim) + 1:].strip()
    return await koduck.sendmessage(context["message"], sendchannel=THEchannel, sendcontent=THEmessagecontent,
                                    ignorecd=True)


async def bugreport(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_bugreport_noparam)

    channelid = BUGREPORT_CHANNEL_ID

    progbot_bugreport_channel = koduck.client.get_channel(channelid)
    THEmessagecontent = context["paramline"]
    THEmessageauthor = context["message"].author
    #originchannel = "<#{}>".format(context["message"].channel.id) if isinstance(context["message"].channel,
    #                                                                            discord.TextChannel) else ""
    embed = discord.Embed(title="**__New Bug Report!__**", description="_{}_".format(THEmessagecontent),
                          color=0x5058a8)
    embed.set_footer(
        text="Submitted by: {}#{}".format(THEmessageauthor.name, THEmessageauthor.discriminator))
    embed.set_thumbnail(url="https://raw.githubusercontent.com/gskbladez/meddyexe/master/virusart/bug.png")
    await koduck.sendmessage(context["message"], sendchannel=progbot_bugreport_channel, sendembed=embed, ignorecd=True)
    return await koduck.sendmessage(context["message"], sendcontent="**_Bug Report Submitted!_**\nThanks for the help!")


async def changestatus(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.client.change_presence(game=discord.Game(name=""))
    else:
        return await koduck.client.change_presence(game=discord.Game(name=context["paramline"]))


async def updatesettings(context, *args, **kwargs):
    koduck.updatesettings()
    return


# note: discord server prevents any user, including bots, from changing usernames more than twice per hour
# bot name is updated in the background task, so it won't update immediately
async def updatesetting(context, *args, **kwargs):
    if len(args) < 2:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_updatesetting_noparam)
    variable = args[0]
    value = context["paramline"][context["paramline"].index(settings.paramdelim) + 1:].strip()
    result = koduck.updatesetting(variable, value, koduck.getuserlevel(context["message"].author.id))
    if result is not None:
        return await koduck.sendmessage(context["message"],
                                        sendcontent=settings.message_updatesetting_success.format(variable, result,
                                                                                                  value))
    else:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_updatesetting_failed)


async def addsetting(context, *args, **kwargs):
    if len(args) < 2:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_updatesetting_noparam)
    variable = args[0]
    value = context["paramline"][context["paramline"].index(settings.paramdelim) + 1:].strip()
    result = koduck.addsetting(variable, value, koduck.getuserlevel(context["message"].author.id))
    if result is not None:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_addsetting_success)
    else:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_addsetting_failed)


async def removesetting(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_removesetting_noparam)
    result = koduck.removesetting(args[0], koduck.getuserlevel(context["message"].author.id))
    if result is not None:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_removesetting_success)
    else:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_removesetting_failed)


async def admin(context, *args, **kwargs):
    # need exactly one mentioned user (the order in the mentioned list is unreliable)
    if len(context["message"].mentions) != 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_nomentioneduser)

    userid = context["message"].mentions[0].id
    userlevel = koduck.getuserlevel(userid)

    # already an admin
    if userlevel == 2:
        return await koduck.sendmessage(context["message"],
                                        sendcontent=settings.message_addadmin_failed.format(settings.botname))
    else:
        koduck.updateuserlevel(userid, 2)
        return await koduck.sendmessage(context["message"],
                                        sendcontent=settings.message_addadmin_success.format(userid, settings.botname))


async def unadmin(context, *args, **kwargs):
    # need exactly one mentioned user (the order in the mentioned list is unreliable)
    if len(context["message"].mentions) != 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_nomentioneduser)

    userid = context["message"].mentions[0].id
    userlevel = koduck.getuserlevel(userid)

    # not an admin
    if userlevel < 2:
        return await koduck.sendmessage(context["message"],
                                        sendcontent=settings.message_removeadmin_failed.format(settings.botname))
    else:
        koduck.updateuserlevel(userid, 1)
        return await koduck.sendmessage(context["message"],
                                        sendcontent=settings.message_removeadmin_success.format(userid,
                                                                                                settings.botname))


# Searches through the past settings.purgesearchlimit number of messages in this channel and deletes given number of bot messages
async def purge(context, *args, **kwargs):
    try:
        limit = int(args[0])
    except (IndexError, ValueError):
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_purge_invalidparam)

    counter = 0
    async for message in koduck.client.logs_from(context["message"].channel, limit=settings.purgesearchlimit):
        if counter >= limit:
            break
        if message.author.id == koduck.client.user.id:
            await koduck.client.delete_message(message)
            counter += 1


async def restrictuser(context, *args, **kwargs):
    # need exactly one mentioned user (the order in the mentioned list is unreliable)
    if len(context["message"].mentions) != 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_nomentioneduser)

    userid = context["message"].mentions[0].id
    userlevel = koduck.getuserlevel(userid)

    # already restricted
    if userlevel == 0:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_restrict_failed)
    # don't restrict high level users
    elif userlevel >= 2:
        return await koduck.sendmessage(context["message"],
                                        sendcontent=settings.message_restrict_failed2.format(settings.botname))
    else:
        koduck.updateuserlevel(userid, 0)
        return await koduck.sendmessage(context["message"],
                                        sendcontent=settings.message_restrict_success.format(userid, settings.botname))


async def unrestrictuser(context, *args, **kwargs):
    # need exactly one mentioned user (the order in the mentioned list is unreliable)
    if len(context["message"].mentions) != 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_nomentioneduser)

    userid = context["message"].mentions[0].id
    userlevel = koduck.getuserlevel(userid)

    if userlevel != 0:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_unrestrict_failed)
    else:
        koduck.updateuserlevel(userid, 1)
        return await koduck.sendmessage(context["message"],
                                        sendcontent=settings.message_unrestrict_success.format(userid,
                                                                                               settings.botname))


# When someone says a trigger message, respond with a custom response!
async def customresponse(context, *args, **kwargs):
    response = yadon.ReadRowFromTable(settings.customresponsestablename, context["command"])
    if response:
        return await koduck.sendmessage(context["message"], sendcontent=response[0])


async def addresponse(context, *args, **kwargs):
    if len(args) < 2:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_addresponse_noparam)
    trigger = args[0]
    response = args[1]
    result = yadon.AppendRowToTable(settings.customresponsestablename, trigger, [response])
    if result == -1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_addresponse_failed)
    else:
        yadon.WriteRowToTable(settings.commandstablename, trigger, ["customresponse", "match", "1"])
        koduck.addcommand(trigger, customresponse, "match", 1)
        return await koduck.sendmessage(context["message"],
                                        sendcontent=settings.message_addresponse_success.format(trigger, response))


async def removeresponse(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_removeresponse_noparam)
    trigger = args[0]
    result = yadon.RemoveRowFromTable(settings.customresponsestablename, trigger)
    if result == -1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent=settings.message_removeresponse_failed.format(trigger))
    else:
        yadon.RemoveRowFromTable(settings.commandstablename, trigger)
        koduck.removecommand(trigger)
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_removeresponse_success)


async def oops(context, *args, **kwargs):
    if len(args) == 1:
        if args[0].lower().strip() == "help":
            return await koduck.sendmessage(context["message"],
                                            sendcontent="Deletes the bot message from the user's last valid command.")

    try:
        THEmessage = koduck.outputhistory[context["message"].author.id].pop()
    except (KeyError, IndexError):
        return settings.message_oops_failed
    try:
        await koduck.delete_message(THEmessage)
        return settings.message_oops_success
    except discord.errors.NotFound:
        return await oops(context, *args, **kwargs)


async def commands(context, *args, **kwargs):
    # filter out the commands that the user doesn't have permission to run
    currentlevel = koduck.getuserlevel(context["message"].author.id)
    availablecommands = []
    for commandname in koduck.commands.keys():
        command = koduck.commands[commandname]
        if command[2] <= currentlevel and command[1] == "prefix":
            availablecommands.append(commandname)
    return await koduck.sendmessage(context["message"], sendcontent=", ".join(availablecommands))


async def help_cmd(context, *args, **kwargs):
    # Default message if no parameter is given
    if len(args) == 0:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_help.replace("{cp}",
                                                                                                      settings.commandprefix).replace(
            "{pd}", settings.paramdelim))

    help_msg = await find_value_in_table(context, help_df, "command_lowercase", args[0], override=True)

    if help_msg is None:
        help_response = help_df[help_df["Command"] == "unknowncommand"].iloc[0]["Response"]
    else:
        help_response = help_msg["Response"]

    return await koduck.sendmessage(context["message"],
                                    sendcontent=help_response)


async def userinfo(context, *args, **kwargs):
    # if there is no mentioned user (apparently they have to be in the server to be considered "mentioned"), use the message sender instead
    if context["message"].server is None:
        user = context["message"].author
    elif len(context["message"].mentions) == 0:
        user = context["message"].server.get_member(context["message"].author.id)
    elif len(context["message"].mentions) == 1:
        user = context["message"].server.get_member(context["message"].mentions[0].id)
    else:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_nomentioneduser2)

    username = user.name
    discr = user.discriminator
    avatar = user.avatar_url
    creationdate = user.created_at

    # these properties only appear in Member object (subclass of User) which is only available from Servers
    if context["message"].server is not None:
        game = user.game
        joindate = user.joined_at
        color = user.color
        if game is None:
            embed = discord.Embed(title="{}#{}".format(username, discr), description=str(user.status), color=color)
        else:
            embed = discord.Embed(title="{}#{}".format(username, discr), description="Playing {}".format(game.name),
                                  color=color)
        embed.add_field(name="Account creation date", value=creationdate.strftime("%Y-%m-%d %H:%M:%S UTC"),
                        inline=False)
        embed.add_field(name="Server join date", value=joindate.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)
        embed.set_thumbnail(url=avatar)
        return await koduck.sendmessage(context["message"], sendembed=embed)
    else:
        embed = discord.Embed(title="{}#{}".format(username, discr), description="Account creation date: {}".format(
            creationdate.strftime("%Y-%m-%d %H:%M:%S UTC")))
        embed.set_thumbnail(url=avatar)
        return await koduck.sendmessage(context["message"], sendembed=embed)


async def roll(context, *args, **kwargs):
    parser = dice_algebra.parser
    lexer = dice_algebra.lexer

    roll_difficulty_dict = {'E': 3, 'N': 4, 'H': 5}
    if "paramline" not in context:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="I can roll dice for you! Try `>roll 5d6>4` or `>roll $N5`!")

    roll_line = context["paramline"]
    if ROLL_COMMENT_CHAR in roll_line:
        roll_line, roll_comment = roll_line.split(ROLL_COMMENT_CHAR, 1)
    else:
        roll_comment = ""

    roll_line = re.sub("\s+", "", roll_line).lower()
    if not roll_line:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="No roll given!")

    roll_macro_match = re.match(r"\$?(E|N|H)(\d+)", roll_line, flags=re.IGNORECASE)
    if roll_macro_match:
        roll_difficulty = roll_difficulty_dict[roll_macro_match.group(1).upper()]
        roll_dicenum = int(roll_macro_match.group(2))
        zero_formatted_roll = "%dd6>%d" % (roll_dicenum, roll_difficulty)
    else:
        # adds 1 in front of bare d6, d20 references
        roll_line = re.sub("(?P<baredice>^|\s+)d(?P<dicesize>\d+)", r"\g<baredice>1d\g<dicesize>", roll_line)
        zero_formatted_roll = re.sub('{(.*)}', '0', roll_line)

    try:
        roll_results = parser.parse(lexer.lex(zero_formatted_roll))
        str_result = str(roll_results)
        if 'hit' in str_result:
            num_hits = roll_results.eval()
            progroll_output = "{} *rolls...* {} = **__{} hits!__**".format(context["message"].author.mention,
                                                                             str_result, num_hits)
            if num_hits == 1:
                progroll_output = progroll_output.replace("hits", "hit")
        else:
            progroll_output = "{} *rolls...* {} = **__{}__**".format(context["message"].author.mention,
                                                                     str_result, roll_results.eval())

        if roll_comment:
            progroll_output += "   #{}".format(roll_comment.rstrip())
        return await koduck.sendmessage(context["message"],
                                        sendcontent=progroll_output)
    except rply.errors.LexingError:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Unexpected characters found! Did you type out the roll correctly?")
    except AttributeError:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Sorry, I can't understand the roll. Try writing it out differently!")
    except dice_algebra.DiceError:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="The dice algebra is incorrect! Did you type out the roll correctly?")


# TODO: Support virus category and Support chip tag conflict with each other
async def tag(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Give me a BattleChip tag or Virus/Chip category, and I can pull up its info for you!")

    tag_info = await find_value_in_table(context, tag_df, "tag_lowercase", args[0])
    if tag_info is None:
        return

    tag_title = tag_info["Tag"]
    tag_description = tag_info["Description"]
    tag_alt = tag_info["AltName"]

    if tag_alt:
        tag_title += " (%s)" % tag_alt

    embed = discord.Embed(
        title="__%s__" % tag_title,
        description=tag_description,
        color=0x24ff00)
    return await koduck.sendmessage(context["message"], sendembed=embed)


async def find_value_in_table(context, df, search_col, search_arg, override=False):
    search_results = df[df[search_col] == search_arg.lower()]
    if search_results.shape[0] == 0:
        if not override:
            await koduck.sendmessage(context["message"],
                                     sendcontent="I can't find `%s`!" % search_arg)
        return None
    elif search_results.shape[0] > 1:
        await koduck.sendmessage(context["message"],
                                 sendcontent="Found more than one match for %s! You should probably let the devs know..." % search_arg)
        return None
    return search_results.iloc[0]


async def send_query_msg(context, return_title, return_msg):
    return await koduck.sendmessage(context["message"], sendcontent="**%s**\n*%s*" % (return_title, return_msg))


def query_chip(arg_lower):
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
        subdf = chip_df[chip_df["Tags"].str.contains("Incident|incident")]
        return_msg = ", ".join(subdf["Chip"])
    elif arg_lower in arg_lower in chip_tag_list:
        subdf = chip_df[chip_df["Tags"].str.contains(re.escape(arg_lower), flags=re.IGNORECASE) &
                        ~chip_df["Tags"].str.contains("dark|incident|mega", flags=re.IGNORECASE)]
        return_title = "Pulling up all BattleChips with the `%s` tag (excluding MegaChips)..." % re.escape(arg_lower).capitalize()
        return_msg = ", ".join(subdf["Chip"])
    elif arg_lower in pd.unique(chip_df["category_lowercase"]):
        subdf = chip_df[(chip_df["category_lowercase"] == arg_lower) &
                        ~chip_df["Tags"].str.contains("dark|incident|mega", flags=re.IGNORECASE)]
        return_title = "Pulling up all chips in the `%s` category (excluding MegaChips)..." % subdf.iloc[0]["Category"]
        return_msg = ", ".join(subdf["Chip"])
    elif arg_lower in pd.unique(chip_df["license_lowercase"]):
        subdf = chip_df[chip_df["license_lowercase"] == arg_lower]
        return_title = "Pulling up all `%s` BattleChips..." % subdf.iloc[0]["License"]
        return_msg = ", ".join(subdf["Chip"])
    elif arg_lower not in ["core"] and arg_lower in pd.unique(chip_df["from_lowercase"]):
        subdf = chip_df[chip_df["from_lowercase"] == arg_lower]
        return_title = "Pulling up all BattleChips from the `%s` Crossover Content..." % subdf.iloc[0]["From?"]
        return_msg = ", ".join(subdf["Chip"])
    elif arg_lower in [i.lower() for i in playermade_list]:
        subdf = pmc_chip_df[pmc_chip_df["from_lowercase"] == arg_lower]
        return_title = "Pulling up all BattleChips from the unofficial `%s` Player-Made Content..." % subdf.iloc[0]["From?"]
        return_msg = ", ".join(subdf["Chip"])
    else:
        return False, "", ""

    return True, return_title, return_msg


def pity_cc_check(arg):
    try:
        would_be_valid = next(i for i in cc_list if re.match(r"^%s$" % re.escape(arg), i, flags=re.IGNORECASE))
        return would_be_valid
    except StopIteration:
        return None


async def chip(context, *args, **kwargss):
    cleaned_args = clean_args(args)
    if len(cleaned_args) < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Give me the name of a Battle Chip and I can pull up its info for you!\n"+
                                                    "I can also query chips by Category, Tag, License, and Crossover Content!")
    arg_lower = cleaned_args[0]
    is_query, return_title, return_msg = query_chip(arg_lower)
    if is_query:
        return await send_query_msg(context, return_title, return_msg)

    would_be_valid = pity_cc_check(arg_lower)
    if would_be_valid:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="`%s` has no Crossover Content BattleChips!" % would_be_valid)

    if len(cleaned_args) > MAX_CHIP_QUERY:
        return await koduck.sendmessage(context["message"], sendcontent="Too many chips, no more than 5!")

    for arg in cleaned_args:
        if not arg:
            continue

        try:
            alias_check = chip_known_aliases[chip_known_aliases["Alias"].str.contains( "(?:^|,|;)\s*%s\s*(?:$|,|;)" %
                                                                                       re.escape(arg),
                                                                                       flags=re.IGNORECASE)]
            if alias_check.shape[0] > 1:
                return await koduck.sendmessage(context["message"],
                                                sendcontent="Too many chips found! You should probably let the devs know...")
            elif alias_check.shape[0] != 0:
                arg = alias_check.iloc[0]["Chip"]
                await koduck.sendmessage(context["message"],
                                         sendcontent="Found as an alternative name for **%s**!" % arg)

        except re.error:
            pass

        chip_info = await find_value_in_table(context, chip_df, "chip_lowercase", arg, override=True)
        if chip_info is None:
            chip_info = await find_value_in_table(context, pmc_chip_df, "chip_lowercase", arg)
            if chip_info is None:
                continue

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

        # this determines embed colors
        color = 0xbfbfbf
        if chip_tags_list:
            if 'Dark' in chip_tags:
                color = cc_color_dictionary['Dark']
                chip_tags_list.remove("Dark")
                chip_title_sub += "Dark"
            elif 'Mega' in chip_tags:
                color = cc_color_dictionary['Mega']
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

        embed = discord.Embed(
            title="__%s__" % chip_title,
            color=color)
        embed.add_field(name="[%s]" % "/".join(subtitle_trimmed),
                        value="_%s_" % chip_description)
        await koduck.sendmessage(context["message"], sendembed=embed)


def find_skill_color(skill_key):
    if skill_key in ["Sense", "Info", "Coding"]:
        color = 0x81A7C6
    elif skill_key in ["Strength", "Speed", "Stamina"]:
        color = 0xDF8F8D
    elif skill_key in ["Charm", "Bravery", "Affinity"]:
        color = 0xF8E580
    else:
        color = -1  # error code
    return color

async def power_ncp(context, arg, force_power = False, ncp_only = False):
    if ncp_only:
        local_power_df = power_df[power_df["Sort"] != "Virus Power"]
    else:
        local_power_df = power_df
    power_info = await find_value_in_table(context, local_power_df, "power_lowercase", arg, override=True)

    if power_info is None:
        power_info = await find_value_in_table(context, pmc_power_df, "power_lowercase", arg)
        if power_info is None:
            return None, None, None, None

    power_name = power_info["Power/NCP"]
    power_skill = power_info["Skill"]
    power_type = power_info["Type"]
    power_description = power_info["Effect"]
    power_eb = power_info["EB"]
    power_source = power_info["From?"]

    # this determines embed colors
    power_color = find_skill_color(power_skill)
    if power_color < 0:
        if power_source in cc_color_dictionary:
            power_color = cc_color_dictionary[power_source]
        elif (power_color < 0) and power_skill.lower() in local_power_df["power_lowercase"].values:
            power_true_info = await find_value_in_table(context, local_power_df, "power_lowercase", power_skill)
            power_color = find_skill_color(power_true_info["Skill"])
        else:
            power_color = 0xffffff

    if power_eb == '-' or force_power:  # display as power, rather than ncp
        if power_type == 'Passive' or power_type == '-' or power_type == 'Upgrade':
            field_title = 'Passive Power'
        else:
            field_title = "%s Power/%s" % (power_skill, power_type)

        field_description = power_description
    else:
        field_title = '%s EB' % power_eb

        if power_source == "Power Upgrades":
            field_title += "/%s Power Upgrade NCP" % power_skill
        elif power_type == "Minus":
            power_name += " (%s Unofficial MinusCust Program)" % power_source
            field_title = "+" + field_title
        elif power_source in playermade_list:
            power_name += " (%s Unofficial NCP)" % power_source
        elif power_source != "Core":
            power_name += " (%s Crossover NCP)" % power_source

        if power_type in ['Passive', '-', 'Upgrade', 'Minus']:
            field_description = power_description
        else:
            field_description = "(%s/%s) %s" % (power_skill, power_type, power_description)

    return power_name, field_title, field_description, power_color


def clean_args(args):
    if len(args) == 1:
        args = re.split(r"(?:,|;)", args[0])
    args = [i.lower().strip() for i in args if i]
    return args


def query_power(args):
    sub_df = power_df
    is_default = True
    search_tag_list = []

    if len(args) > 1:
        args = " ".join(args)
    else:
        args = args[0]
    args = args.split()
    for arg in args:
        arg_capital = arg.capitalize()
        if arg in [i.lower() for i in skill_list]:
            sub_df = sub_df[(power_df["Skill"] == arg_capital)]
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
        sub_df = sub_df[sub_df["Sort"] == "Virus Power"]
        search_tag_list.append('Virus')
    results_title = "Searching for `%s` Powers..." % " ".join(search_tag_list)
    results_msg = ", ".join(sub_df["Power/NCP"])

    return True, results_title, results_msg


async def power(context, *args, **kwargs):
    cleaned_args = clean_args(args)
    if len(cleaned_args) < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Give me the name of a Navi Power and I can pull up its info for you!\n"+
                                                    "I can also query Powers by Skill, Type, and whether or not it is Virus-exclusive! Try giving me multiple queries at once, i.e. `>power sense cost` or `power virus passive`!")

    if len(cleaned_args) > MAX_POWER_QUERY:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Too many powers, no more than 5!")

    is_query, results_title, results_msg = query_power(cleaned_args)
    if is_query:
        if not results_msg:
            return await koduck.sendmessage(context["message"], sendcontent="No powers found with that query!")
        return await send_query_msg(context, results_title, results_msg)


    for arg in cleaned_args:
        if not arg:
            continue
        is_power_ncp = re.match(r"^(\S+)\s*ncp$", arg, flags=re.IGNORECASE)
        if is_power_ncp:
            arg = is_power_ncp.group(1)
        power_name, field_title, field_description, power_color = await power_ncp(context, arg, force_power=True)
        if power_name is None:
            continue

        embed = discord.Embed(title="__{}__".format(power_name),
                              color=power_color)
        embed.add_field(name="**[{}]**".format(field_title),
                        value="_{}_".format(field_description))
        await koduck.sendmessage(context["message"], sendembed=embed)
    return


def query_ncp(arg_lower):
    ncp_df = power_df[power_df["Sort"] != "Virus Power"]
    valid_cc_list = list(pd.unique(ncp_df["From?"].str.lower().str.strip()))
    [valid_cc_list.remove(i) for i in ["core", "power upgrades"]]
    eb_match = re.match(r"^(\d+)(?:\s*EB)$", arg_lower, flags=re.IGNORECASE)

    if eb_match:
        eb_search = eb_match.group(1)
        subdf = ncp_df[ncp_df["EB"] == eb_search]
        results_title = "Finding all `%s EB` NCPs..." % eb_search
        results_msg = ", ".join(subdf["Power/NCP"])
        return True, results_title, results_msg
    elif arg_lower in valid_cc_list:
        subdf = ncp_df[ncp_df["from_lowercase"] == arg_lower]
        results_title = "Pulling up all NCPs from the `%s` Crossover Content..." % subdf.iloc[0]["From?"]
        results_msg = ", ".join(subdf["Power/NCP"])
    elif arg_lower in [i.lower() for i in playermade_list]:
        subdf = pmc_power_df[(pmc_power_df["from_lowercase"] == arg_lower) &
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

async def ncp(context, *args, **kwargs):
    cleaned_args = clean_args(args)
    if len(cleaned_args) < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Give me the name of a NaviCust Part and I can pull up its info for you!\n"+
                                                    "I can also query NCPs by EB and Crossover Content!")
    arg_lower = cleaned_args[0]
    is_query, results_title, results_msg = query_ncp(arg_lower)
    if is_query:
        return await send_query_msg(context, results_title, results_msg)
    would_be_valid = pity_cc_check(arg_lower)
    if would_be_valid:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="`%s` has no Crossover Content NCPs!" % would_be_valid)

    if len(cleaned_args) > MAX_NCP_QUERY:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Too many NCPs, no more than 5!")

    for arg in cleaned_args:
        if not arg:
            continue
        if any(power_df["power_lowercase"] == "%sncp" % arg):
            arg += "ncp"
        power_name, field_title, field_description, power_color = await power_ncp(context, arg, force_power=False, ncp_only=True)
        if power_name is None:
            continue

        embed = discord.Embed(title="__{}__".format(power_name),
                              color=power_color)
        embed.add_field(name="**[{}]**".format(field_title),
                        value="_{}_".format(field_description))
        await koduck.sendmessage(context["message"], sendembed=embed)
    return


def query_npu(arg):
    result_npu = power_df[power_df["Skill"].str.contains("^%s$" % re.escape(arg), flags=re.IGNORECASE)]
    if result_npu.shape[0] == 0:
        return False, "", ""
    result_title = "Finding all Navi Power Upgrades for `%s`..." % result_npu.iloc[0]["Skill"]
    result_string = ", ".join(result_npu["Power/NCP"])
    return True, result_title, result_string


async def upgrade(context, *args, **kwargs):
    cleaned_args = clean_args(args)
    if len(cleaned_args) < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Give me the name of a default NaviPower and I can find its upgrades for you!")

    for arg in cleaned_args:
        arg = arg.lower()
        is_upgrade, result_title, result_msg = query_npu(arg)
        if not is_upgrade:
            await koduck.sendmessage(context["message"],
                                            sendcontent="Couldn't find any Navi Power Upgrades for `%s`!" % arg)
            continue
        await send_query_msg(context, result_title, result_msg)
    return


#TODO: add BlackBossom art
async def virus_master(context, arg, simplified=True):
    virus_info = await find_value_in_table(context, virus_df, "name_lowercase", arg, override=True)

    if virus_info is None:
        virus_info = await find_value_in_table(context, pmc_virus_df, "name_lowercase", arg)
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

    if virus_artist:
        virus_footer += "\n(Artwork by %s)" % virus_artist
    if virus_source in playermade_list:
        virus_footer += " (%s Unofficial Virus)" % virus_source
    elif virus_source in cc_list:
        virus_footer += " (%s Crossover Virus)" % virus_source

    if virus_source in cc_color_dictionary:
        virus_color = cc_color_dictionary[virus_source]
    else:
        virus_color = 0x7c00ff

    virus_descript_block = ""
    virus_title = ""

    virus_skills = [(key, int(val)) for key, val in virus_skills.items() if val and int(val) != 0]

    if not simplified:
        virus_title = "HP %d" % int(virus_hp)
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
    valid_cc_list = list(pd.unique(virus_df["From?"].str.lower().str.strip()))
    [valid_cc_list.remove(i) for i in ["core"]]
    if arg_lower in valid_cc_list:
        sub_df = virus_df[virus_df["from_lowercase"] == arg_lower]
        result_title = "Viruses from the `%s` Crossover Content..." % sub_df.iloc[0]["From?"]
        result_msg = ", ".join(sub_df["Name"])
    elif arg_lower in list(pd.unique(virus_df["category_lowercase"])):
        sub_df = virus_df[virus_df["Category"] == arg_lower.capitalize()]
        result_title = "Viruses in the `%s` category..." % sub_df.iloc[0]["Category"]
        result_msg = ", ".join(sub_df["Name"])
    elif arg_lower in virus_tag_list:
        sub_df = virus_df[virus_df["Tags"].str.contains(re.escape(arg_lower), flags=re.IGNORECASE)]
        result_title = "Viruses with the `%s` tag..." % arg_lower.capitalize()
        result_msg = ", ".join(sub_df["Name"])
    else:
        return False, "", ""
    return True, result_title, result_msg


#TODO: Add virus aliases (MettaurOmega for Omega character)
async def virus(context, *args, **kwargs):
    cleaned_args = clean_args(args)
    if len(cleaned_args) < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Give me the name of 1-%d viruses and I can pull up their info for you!\n" % MAX_VIRUS_QUERY +
                                                    "I can also query Viruses by Category, Tag, and Crossover Content!")
    elif len(cleaned_args) > MAX_VIRUS_QUERY:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Too many viruses, no more than %d!" % MAX_VIRUS_QUERY)
    arg_lower = args[0].lower()
    is_query, result_title, result_msg = query_virus(arg_lower)
    if is_query:
        return await send_query_msg(context, result_title, result_msg)

    for arg in cleaned_args:
        if not arg:
            continue
        virus_name, _, virus_description, virus_footer, virus_image, virus_color = await virus_master(context, arg, simplified=True)
        if virus_name is None:
            continue

        embed = discord.Embed(title=virus_name,
                              description=virus_description,
                              color=virus_color)
        embed.set_thumbnail(url=virus_image)
        embed.set_footer(text=virus_footer)
        await koduck.sendmessage(context["message"], sendembed=embed)


async def virusx(context, *args, **kwargs):
    cleaned_args = clean_args(args)
    if len(cleaned_args) < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Give me the name of a virus and I can pull up its full info for you!")
    elif len(cleaned_args) > 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="I can only output one virusx block at a time!")

    virus_name, virus_title, virus_descript_block, virus_footer, virus_image, virus_color = await virus_master(context, args[0], simplified=False)
    if virus_name is None:
        return

    embed = discord.Embed(title=virus_name, color=virus_color)

    embed.set_thumbnail(url=virus_image)
    embed.add_field(name=virus_title,
                    value=virus_descript_block, inline=True)
    embed.set_footer(text=virus_footer)
    return await koduck.sendmessage(context["message"], sendembed=embed)


async def query(context, *args, **kwargs):
    cleaned_args = clean_args(args)
    if len(cleaned_args) < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="This command can sort battlechips, NCPs, and powers by Category, and single out Crossover Content chips! Please type `>help query` for more information.")

    arg = cleaned_args[0]

    is_chip_query, chip_title, chip_msg = query_chip(arg)
    is_ncp_query, ncp_title, ncp_msg = query_ncp(arg)
    if is_chip_query and is_ncp_query:
        result_title = "Pulling up all BattleChips and NCPs from %s..." % re.match(r".*(`.+`).*", chip_title).group(1)
        ncp_addon = ["%s(NCP)" % i for i in ncp_msg.split(", ")]
        result_msg = chip_msg + ", ".join(ncp_addon)
        return await send_query_msg(context, result_title, result_msg)
    elif is_chip_query:
        return await send_query_msg(context, chip_title, chip_msg)
    elif is_ncp_query:
        return await send_query_msg(context, ncp_title, ncp_msg)

    is_virus_query, result_title, result_msg = query_virus(arg)
    if is_virus_query:
        return await send_query_msg(context, result_title, result_msg)

    is_npu_query, result_title, result_msg = query_npu(arg)
    if is_npu_query:
        return await send_query_msg(context, result_title, result_msg)

    is_power_query, result_title, result_msg = query_power(cleaned_args)
    if is_power_query:
        return await send_query_msg(context, result_title, result_msg)

    if arg == 'daemon':
        _, result_title, result_msg = query_daemon()
        return await send_query_msg(context, result_title, result_msg)

    if arg in ['networkmod', 'mod']:
        _, result_title, result_msg = query_network()
        return await send_query_msg(context, result_title, result_msg)

    would_be_valid = pity_cc_check(arg)
    if would_be_valid:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="`%s` has no queryable Crossover Content!" % would_be_valid)

    return await koduck.sendmessage(context["message"],
                                    sendcontent="`%s` is not a valid query!" % args[0])


async def mysterydata_master(context, args, force_reward = False):
    arg = args[0]
    mysterydata_type = mysterydata_df[mysterydata_df["mysterydata_lowercase"] == arg]

    if mysterydata_type.shape[0] == 0:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Please specify either Common, Uncommon, or Rare MysteryData.")
    if force_reward:
        firstroll = random.randint(3,5)
    else:
        firstroll = random.randint(1, 6)
    if firstroll <= 2:
        zenny_val = mysterydata_type[mysterydata_type["Type"] == "Zenny"].iloc[0]["Value"]
        result_chip = "%d" % (int(zenny_val) * (random.randint(1, 6) + random.randint(1, 6)))
        result_text = " Zenny!"
    else:
        if firstroll <= 4:
            reward_type = "Chip"
            result_text = " BattleChip!"
        elif firstroll == 5:
            reward_type = "NCP"
            result_text = " NCP!"
        else:
            reward_type = "Misc Table"
            result_text = ""
        df_sub = mysterydata_type[mysterydata_type["Type"] == reward_type]
        row_num = random.randint(1, df_sub.shape[0]) - 1
        result_chip = df_sub.iloc[row_num]["Value"]
    result_text = "%s%s" % (re.sub(r"\.$", '!', result_chip), result_text)  # replaces any periods with exclamation marks!

    if arg in mysterydata_dict:
        md_color = mysterydata_dict[arg]["color"]
        md_image_url = mysterydata_dict[arg]["image"]
    else:
        md_color = 0xffffff
        md_image_url = ""

    md_type = arg.capitalize()

    embed = discord.Embed(title="__{} MysteryData__".format(md_type),
                          description="_%s accessed the MysteryData..._\n" % context["message"].author.mention +
                                      "\nGot: **%s**" % result_text,
                          color=md_color)
    embed.set_thumbnail(url=md_image_url)

    return await koduck.sendmessage(context["message"], sendembed=embed)


async def mysterydata(context, *args, **kwargs):
    cleaned_args = clean_args(args)
    if len(cleaned_args) < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="I can roll Mystery Data for you! Specify `>mysterydata common`, `>mysterydata uncommon`, or `>mysterydata rare`!")

    await mysterydata_master(context, cleaned_args, force_reward=False)


async def crimsonnoise(context, *args, **kwargs):
    cleaned_args = clean_args(args)
    if len(cleaned_args) < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="I can roll CrimsonNoise for you! Specify `>crimsonnoise common`, `>crimsonnoise`, or `>crimsonnoise rare`!")

    arg = cleaned_args[0]
    crimsonnoise_type = crimsonnoise_df[crimsonnoise_df["mysterydata_lowercase"] == arg]

    if crimsonnoise_type.shape[0] == 0:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Please specify either Common, Uncommon, or Rare CrimsonNoise.")
    firstroll = random.randint(1, 6)
    if firstroll != 6:
        reward_type = "Chip"
        result_text = " BattleChip!"
    else:
        reward_type = "NCP"
        result_text = " NCP!"

    df_sub = crimsonnoise_type[crimsonnoise_type["Type"] == reward_type]
    row_num = random.randint(1, df_sub.shape[0]) - 1
    result_chip = df_sub.iloc[row_num]["Value"]

    result_text = "%s%s" % (result_chip, result_text)  # replaces any periods with exclamation marks!
    cn_color = cc_color_dictionary["Genso Network"]
    cn_type = arg.capitalize()

    embed = discord.Embed(title="__{} CrimsonNoise__".format(cn_type),
                          description="_%s accessed the CrimsonNoise..._\n" % context["message"].author.mention +
                                      "\nGot: **%s**" % result_text,
                          color=cn_color)

    return await koduck.sendmessage(context["message"], sendembed=embed)


async def mysteryreward(context, *args, **kwargs):
    cleaned_args = clean_args(args)
    if len(cleaned_args) < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="I can roll Mystery Data for you, keeping it to the BattleChips and NCPs! Specify `>mysterydata common`, `>mysterydata uncommon`, or `>mysterydata rare`!")

    await mysterydata_master(context, cleaned_args, force_reward=True)
    return


async def bond(context, *args, **kwargs):
    cleaned_args = clean_args(args)
    if len(cleaned_args) < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Give me a Bond Power and I can pull up its info for you!")

    bond_info = await find_value_in_table(context, bond_df, "bondpower_lowercase", cleaned_args[0])
    if bond_info is None:
        return

    bond_title = bond_info["BondPower"]
    bond_cost = bond_info["Cost"]
    bond_description = bond_info["Description"]

    embed = discord.Embed(
        title="__%s__" % bond_title,
        color=0x24ff00)
    embed.add_field(name="**({} Bond Point(s))**".format(bond_cost),
                    value="_{}_".format(bond_description))

    return await koduck.sendmessage(context["message"], sendembed=embed)


def query_daemon():
    result_title = "Listing all Daemons (excluding Player Made Content)..."
    result_msg = ", ".join(daemon_df["Name"])
    return True, result_title, result_msg


async def daemon(context, *args, **kwargs):
    cleaned_args = clean_args(args)
    if len(cleaned_args) < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Lists the complete information of a Daemon for DarkChip rules.")
    elif len(cleaned_args) > 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="I can only pull up one Daemon's information at a time!")

    if cleaned_args[0] in ["all", "list"]:
        _, result_title, result_msg = query_daemon()
        return await send_query_msg(context, result_title, result_msg)

    daemon_info = await find_value_in_table(context, daemon_df, "name_lowercase", cleaned_args[0], override=True)
    if daemon_info is None:
        daemon_info = await find_value_in_table(context, pmc_daemon_df, "name_lowercase", cleaned_args[0])
        if daemon_info is None:
            return

    daemon_name = daemon_info["Name"]
    daemon_quote = daemon_info["Quote"]
    daemon_domain = daemon_info["Domain"]
    daemon_tribute = daemon_info["Tribute"]
    daemon_tribute_description = daemon_info["TributeDescription"]
    daemon_source = daemon_info["From?"]
    daemon_chaosUnison = daemon_info["ChaosUnison"]
    daemon_chaosUnison_description = daemon_info["ChaosUnisonDescription"]
    daemon_signatureChip = daemon_info["SignatureDarkChip"]
    daemon_image = daemon_info["Image URL"]

    daemon_description = "**__Domain:__** *%s*\n\n" % (daemon_domain) + \
                         "**__Tribute:__** *%s*\n*%s*\n\n" % (daemon_tribute, daemon_tribute_description) + \
                         "**__ChaosUnison:__** *%s*\n*%s*\n\n" % (daemon_chaosUnison, daemon_chaosUnison_description) + \
                         "**__Signature DarkChip:__** *%s*" % daemon_signatureChip

    if daemon_source in cc_color_dictionary:
        daemon_color = cc_color_dictionary[daemon_source]
    else:
        daemon_color = 0x000000
    embed = discord.Embed(title="**__{}__**".format(daemon_name),
                          color=daemon_color)
    embed.set_thumbnail(url=daemon_image)
    embed.add_field(name="***''{}''***".format(daemon_quote),
                    value=daemon_description)
    return await koduck.sendmessage(context["message"], sendembed=embed)


async def element(context, *args, **kwargs):
    cleaned_args = clean_args(args)
    if len(cleaned_args) < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Give you random elements from the Element Generation table. To use, enter `>element [#]` or `>element [category] [#]`!\n" +
                                                    "Categories: **%s**" % current_element_categories)

    args = cleaned_args[0].split()
    if len(args) > 2:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Command is too long! Just give me `>element [#]` or `>element [category] [#]`!")

    element_return_number = 1  # number of elements to return, 1 by default
    element_category = None
    sub_element_df = element_df
    for arg in args:
        try:
            element_return_number = int(arg)
            break
        except ValueError:
            element_category = arg.lower().capitalize()

            sub_element_df = element_df[element_df["category_lowercase"] == arg.lower()]
            if sub_element_df.shape[0] == 0:
                return await koduck.sendmessage(context["message"],
                                                sendcontent="Not a valid category!\n" +
                                                            "Categories: **%s**" % current_element_categories)

    if element_return_number < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="The number of elements can't be 0 or negative!")
    if element_return_number > 12:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="That's too many elements! Are you sure you need more than %d?" % MAX_ELEMENT_ROLL)

    elements_selected = random.sample(range(sub_element_df.shape[0]), element_return_number)
    elements_name = [sub_element_df.iloc[i]["element"] for i in elements_selected]

    if element_category is None:
        element_flavor_title = "Picked {} random element(s)...".format(str(element_return_number))
    else:
        element_flavor_title = "Picked {} random element(s) from the {} category...".format(str(element_return_number),
                                                                                            element_category)
    element_color = 0x48C800
    elements_list = ", ".join(elements_name)

    embed = discord.Embed(title=element_flavor_title,
                          color=element_color,
                          description=elements_list)
    return await koduck.sendmessage(context["message"], sendembed=embed)


async def rulebook(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="NetBattlers Beta 6 Official Rulebook (high-res): <https://www.merrymancergames.com/wp-content/uploads/2020/04/NetBattlers-Beta-6-Full-Res.pdf>\n" +
                                                    "NetBattlers Beta 6 Official Rulebook (mobile-friendly): <https://www.merrymancergames.com/wp-content/uploads/2020/04/NetBattlers-Beta-6-Mobile.pdf>\n" +
                                                    "NetBattlers Advance, The Supplementary Rulebook: <https://www.merrymancergames.com/wp-content/uploads/2020/04/NetBattlers-Advance-5.pdf>\n\n" +
                                                    "**_For player made content, check the Player-Made Repository!:_**\n<https://docs.google.com/document/d/19-5o7flAimvN7Xk8V1x5BGUuPh_l7JWmpJ9-Boam-nE/edit>")


def query_network():
    result_title = "Listing all Network Modifiers from the New Connections crossover content..."
    result_msg = ", ".join(networkmod_df["Name"])
    return True, result_title, result_msg


async def networkmod(context, *args, **kwargs):
    cleaned_args = clean_args(args)
    if len(cleaned_args) < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Pulls up info for 1-%d Network Modifiers! I can also list all Network Modifiers if you tell me `list` or `all`!" % MAX_MOD_QUERY )

    if len(cleaned_args) > MAX_MOD_QUERY:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Can't pull up more than %d Network Mods!" % MAX_MOD_QUERY)

    if cleaned_args[0] in ["list", "all"]:
        _, result_title, result_msg = query_network()
        return await send_query_msg(context, result_title, result_msg)

    for arg in cleaned_args:
        networkmod_info = await find_value_in_table(context, networkmod_df, "name_lowercase", arg, override=True)
        if networkmod_info is None:
            continue

        networkmod_name = networkmod_info["Name"]
        networkmod_description = networkmod_info["Description"]
        networkmod_color = cc_color_dictionary["New Connections"]

        networkmod_field = 'New Connections Crossover Network Modifier'

        embed = discord.Embed(title="__{}__".format(networkmod_name),
                              color=networkmod_color)
        embed.add_field(name="**[{}]**".format(networkmod_field),
                        value="_{}_".format(networkmod_description))
        await koduck.sendmessage(context["message"], sendembed=embed)

    return


async def invite(context, *args, **kwargs):
    invite_link = "https://discordapp.com/oauth2/authorize?client_id=572878200397627412&scope=bot&permissions=0"
    color = 0x71c142
    embed = discord.Embed(title="Just click here to invite me!",
                          color=color,
                          url=invite_link)
    return await koduck.sendmessage(context["message"], sendembed=embed)


def setup():
    koduck.addcommand("updatecommands", updatecommands, "prefix", 3)


setup()
koduck.client.run(bot_token)  # to run locally, ask a dev for the .env file
