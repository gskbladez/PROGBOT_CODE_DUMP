import discord
import requests
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
import json
import datetime

load_dotenv()
bot_token = os.getenv('DISCORD_TOKEN')

MAX_POWER_QUERY = 5
MAX_NCP_QUERY = 5
MAX_CHIP_QUERY = 5
MAX_VIRUS_QUERY = 5
MAX_ELEMENT_ROLL = 12
MAX_MOD_QUERY = 5
MAX_BOND_QUERY = 4
MAX_NPU_QUERY = MAX_NCP_QUERY
MAX_ELEMENT_QUERY = 12
ROLL_COMMENT_CHAR = '#'
MAX_CHEER_JEER_ROLL = 5
MAX_CHEER_JEER_VALUE = 100
MAX_AUDIENCES = 100
AUDIENCE_TIMEOUT = datetime.timedelta(days=0, hours=1, seconds=0)
MAX_SPOTLIGHTS = 100
MAX_CHECKLIST_SIZE = 10
SPOTLIGHT_TIMEOUT = datetime.timedelta(days=0, hours=3, seconds=10)
PROBABLY_INFINITE = 99
MAX_RANDOM_VIRUSES = 6
MAX_WEATHER_QUERY = 5
REROLL_DICE_SIZE_THRESHOLD = 10000000000
MAX_REROLL_QUERY = 20
MAX_REROLL_QUERY_LARGE = 5
FORMAT_LIMIT = 175 # technically actually 198 or so, buuuuut

# Runtime database; expires on shutdown
audience_data = {}
spotlight_db = {}

commands_df = pd.read_csv(settings.commandstablename, sep="\t").fillna('')

# Background task is run every set interval while bot is running (by default every 10 seconds)
async def backgroundtask():
    await clean()
    return

async def clean():
    clean_audience() # cleans up audience_data if it hasn't been used in AUDIENCE_TIMEOUT
    clean_spotlight() # cleans up spotlight_db if it hasn't been used in SPOTLIGHT_TIMEOUT
    return

def clean_audience():
    #with open(settings.audiencefile, "r") as afp:
    #    audience_data = json.load(afp)
    del_keys = [key for key in audience_data if
                (datetime.datetime.now() - datetime.datetime.strptime(audience_data[key]["last_modified"], '%Y-%m-%d %H:%M:%S')) > AUDIENCE_TIMEOUT]
    for key in del_keys: del audience_data[key]
    #with open(settings.audiencefile, 'w') as afp:
    #    json.dump(audience_data, afp, sort_keys=True, indent=4, default=str)
    return

def clean_spotlight():
    del_keys = [key for key in spotlight_db if
                (datetime.datetime.now() - datetime.datetime.strptime(spotlight_db[key]["Last Modified"], '%Y-%m-%d %H:%M:%S')) > SPOTLIGHT_TIMEOUT]
    for key in del_keys: del spotlight_db[key]
    #with open(settings.audiencefile, 'w') as afp:
    #    json.dump(audience_data, afp, sort_keys=True, indent=4, default=str)
    return


skill_list = ['Sense', 'Info', 'Coding',
              'Strength', 'Speed', 'Stamina',
              'Charm', 'Bravery', 'Affinity']
skill_color_dictionary = {"Mind": 0x81A7C6,
                          "Body": 0xDF8F8D,
                          "Soul": 0xF8E580}
weather_color_dictionary = {"Blue": 0x8ae2ff,
                            "Yellow": 0xffff5e,
                            "Red": 0xff524d}
achievement_color_dictionary = {"Gold": 0xffe852}
cc_dict = {"ChitChat": "Chit Chat", "Radical Spin": "RadicalSpin", "Skateboard Dog": "SkateboardDog",
           "Night Drifters": "NightDrifters", "Underground Broadcast": "UndergroundBroadcast",
           "Mystic Lilies": "MysticLilies", "Genso Network": "GensoNetwork, Genso", "Leximancy": "",
           "New Connections": "NewConnections", "Silicon Skin": "SiliconSkin",
           "The Walls Will Swallow You": "TWWSY, TheWallsWillSwallowYou, The Walls, TheWalls, Walls",
           "MUDSLURP": "Discord, MUD",
           "Tarot": "", "Nyx": ""}

help_categories = {"Lookups": ':mag: **Lookups**',
                  "Rollers": ':game_die: **Rollers**',
                  "Helpers": ':thumbsup: **Helpers**',
                  "Reminders (Base)": ':information_source: **Reminders (Base)**',
                  "Reminders (Advanced Content)": ':trophy: **Reminders (Advanced Content)**',
                  "Reminders (Liberation)": ':map: **Reminders (Liberation)**',
                  "Reminders (DarkChips)": ':smiling_imp: **Reminders (DarkChips)**',
                  "Safety Tools": ':shield: **Safety Tools**'}

cc_list = list(cc_dict.keys())
cc_df = pd.DataFrame.from_dict({"Source": cc_list, "Alias": list(cc_dict.values())})
playermade_list = ["Genso Network"]

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
                       "Genso Network": 0xff605d,
                       "Dark": 0xB088D0,
                       "Item": 0xffffff,
                       "Chip": 0xbfbfbf,
                       "Mystery": 0x000000}
virus_colors = {"Virus": 0x7c00ff,
                "MegaVirus": 0xA8E8E8,
                "OmegaVirus": 0xA8E8E8}
cj_colors = {"cheer": 0xffe657, "jeer": 0xff605d}

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
                             "image": settings.sapphire_md_image}}

roll_difficulty_dict = {'E': 3, 'N': 4, 'H': 5}

settings.backgroundtask = backgroundtask

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

daemon_df = pd.read_csv(settings.daemonfile, sep="\t").fillna('').dropna(subset=['Name'])
bond_df = pd.read_csv(settings.bondfile, sep="\t").fillna('').dropna(subset=['BondPower'])
tag_df = pd.read_csv(settings.tagfile, sep="\t").fillna('')
mysterydata_df = pd.read_csv(settings.mysterydatafile, sep="\t").fillna('')
networkmod_df = pd.read_csv(settings.networkmodfile, sep="\t").fillna('')
crimsonnoise_df = pd.read_csv(settings.crimsonnoisefile, sep="\t").fillna('')
audience_df = pd.read_csv(settings.audienceparticipationfile, sep="\t").fillna('')

element_df = pd.read_csv(settings.elementfile, sep="\t").fillna('')
element_category_list = pd.unique(element_df["category"].dropna())

help_df = pd.read_csv(settings.helpfile, sep="\t").fillna('')
help_df["Response"] = help_df["Response"].str.replace('\\\\n', '\n', regex=True)
help_cmd_list = [i for i in help_df["Command"] if i]
help_df["Type"] = help_df["Type"].astype("category")
help_df["Type"].cat.rename_categories(help_categories, inplace=True)
help_df["Type"].cat.reorder_categories(list(help_categories.values())+[""], inplace=True)

pmc_chip_df = pd.read_csv(settings.pmc_chipfile, sep="\t").fillna('')
pmc_power_df = pd.read_csv(settings.pmc_powerfile, sep="\t").fillna('')
pmc_virus_df = pd.read_csv(settings.pmc_virusfile, sep="\t").fillna('')
pmc_daemon_df = pd.read_csv(settings.pmc_daemonfile, sep="\t").fillna('')

nyx_chip_df = pd.read_csv(settings.nyx_chipfile, sep="\t").fillna('')
nyx_power_df = pd.read_csv(settings.nyx_ncpfile, sep="\t").fillna('')

rulebook_df = pd.read_csv(settings.rulebookfile, sep="\t",  converters = {'Version': str}).fillna('')
pmc_link = rulebook_df[rulebook_df["Name"] == "Player-Made Repository"]["Link"].iloc[0]
nyx_link = rulebook_df[rulebook_df["Name"] == "Nyx"]["Link"].iloc[0]
grid_link = rulebook_df[rulebook_df["Name"] == "Grid-Based Combat"]["Link"].iloc[0]
rulebook_df = rulebook_df[(rulebook_df["Name"] == "NetBattlers") | (rulebook_df["Name"] == "NetBattlers Advance")]
# these might start complaining; double check that the labels in the rulebook are exact: captilization and whitespace matter!
rulebook_df["Type"] = rulebook_df["Type"].astype('category').cat.reorder_categories(["Mobile", "Full Res", "Bonus BattleChips"])
rulebook_df["Release"] = rulebook_df["Release"].astype('category').cat.reorder_categories(["Beta", "Alpha", "Pre-Alpha", "Version"])
rulebook_df = rulebook_df.sort_values(["Name", "Release", "Version", "Type"])

adventure_df = pd.read_csv(settings.adventurefile, sep="\t").fillna('')
fight_df = pd.read_csv(settings.fightfile, sep="\t").fillna('')
weather_df = pd.read_csv(settings.weatherfile, sep="\t").fillna('')
achievement_df = pd.read_csv(settings.achievementfile, sep="\t").fillna('')
glossary_df = pd.read_csv(settings.glossaryfile, sep="\t").fillna('')

parser = dice_algebra.parser
lexer = dice_algebra.lexer

if not os.path.isfile(settings.logfile):
    with open(settings.prefixfile, 'w') as lfp:
        pass

if not os.path.isfile(settings.logfile):
    with open(settings.prefixfile, 'w') as lfp:
        pass

if not os.path.isfile(settings.customresponsestablename):
    with open(settings.customresponsestablename, 'w') as ffp:
        pass

required_files = [settings.commandstablename, settings.settingstablename, settings.userlevelstablename]

bad_files = [f for f in required_files if not os.path.isfile(f)]
if bad_files:
    raise FileNotFoundError("Required files missing: %s " % ", ".join(bad_files))

##################
# BASIC COMMANDS #
##################
# Be careful not to leave out this command or else a restart might be needed for any updates to commands
async def updatecommands(context, *args, **kwargs):

    #tableitems = yadon.ReadTable(settings.commandstablename).items()

    def cmd_func(row):
        koduck.addcommand(row['Command'],globals()[row['Function']], row['Type'], int(row['Permission']))
        return

    if commands_df.shape[0] > 0:
        koduck.clearcommands()
        try:
            commands_df.apply(cmd_func, axis=1)
        except (KeyError, IndexError, ValueError) as e:
            print(e)
            pass


async def goodnight(context, *args, **kwargs):
    return await koduck.client.logout()


async def sendmessage(context, *args, **kwargs):
    if len(args) < 2:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_sendmessage_noparam)
    channelid = args[0]
    THEchannel = koduck.client.get_channel(int(channelid))
    THEmessagecontent = context["paramline"][context["paramline"].index(settings.paramdelim) + 1:].strip()
    return await koduck.sendmessage(context["message"], sendchannel=THEchannel, sendcontent=THEmessagecontent,
                                    ignorecd=True)


async def bugreport(context, *args, **kwargs):
    if not context['params']:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Sends a bug report to the ProgBot Devs! " + \
                                                    "Please describe the error in full. " + \
                                                    "(i.e. `{cp}bugreport Sword is listed as 3 damage when it is 2 damage.`)".replace(
                                                        "{cp}", koduck.get_prefix(context["message"])))

    channelid = int(settings.bugreport_channel_id)

    progbot_bugreport_channel = koduck.client.get_channel(channelid)
    message_content = context["paramline"]
    message_author = context["message"].author
    if context["message"].channel.type is discord.ChannelType.private:
        message_guild = "Direct message"
    else:
        message_guild = context["message"].guild.name
    # originchannel = "<#{}>".format(context["message"].channel.id) if isinstance(context["message"].channel,
    #                                                                            discord.TextChannel) else ""
    embed = discord.Embed(title="**__New Bug Report!__**", description="_{}_".format(message_content),
                          color=0x5058a8)
    embed.set_footer(
        text="Submitted by: {}#{} ({})".format(message_author.name, message_author.discriminator, message_guild))
    embed.set_thumbnail(url="https://raw.githubusercontent.com/gskbladez/meddyexe/master/virusart/bug.png")
    await koduck.sendmessage(context["message"], sendchannel=progbot_bugreport_channel, sendembed=embed, ignorecd=True)
    return await koduck.sendmessage(context["message"], sendcontent="**_Bug Report Submitted!_**\nThanks for the help!")


async def changestatus(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.client.change_presence(activity=discord.Game(name=""))
    else:
        return await koduck.client.change_presence(activity=discord.Game(name=context["paramline"]))


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
    async for message in context["message"].channel.history(limit=settings.purgesearchlimit):
        if counter >= limit:
            break
        if message.author.id == koduck.client.user.id:
            await message.delete()
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

def export_tsv(df, filename):
    df.to_csv(filename, sep='\t', index=False)
    return

async def addresponse(context, *args, **kwargs):
    if len(args) < 2:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_addresponse_noparam)
    trigger = args[0]
    response = args[1]
    result = yadon.AppendRowToTable(settings.customresponsestablename, trigger, [response])
    if result == -1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_addresponse_failed)
    else:
        temp_command = {'Command': trigger, "Type": "match", 'Function': 'customresponse', 'Category': 'Custom', 'Permission': '1'}
        global commands_df
        commands_df = commands_df.append(temp_command, ignore_index=True)
        export_tsv(commands_df, settings.commandstablename)
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
        global commands_df
        commands_df = commands_df[commands_df["Command"] != trigger]
        export_tsv(commands_df, settings.commandstablename)
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
    availablecommands = commands_df[commands_df["Permission"] <= currentlevel].sort_values(["Function", "Command", "Permission"])
    if (context["message"].author.id == context["message"].guild.owner_id):
        availablecommands = availablecommands.append(commands_df[commands_df["Permission"] == 4])
    cmd_groups = availablecommands.groupby(["Category"])
    return_msgs = ["**%s**\n*%s*" % (name, ", ".join(help_group["Command"].values)) for name, help_group in cmd_groups if
                   name]
    return await koduck.sendmessage(context["message"], sendcontent="\n\n".join(return_msgs))


async def help_cmd(context, *args, **kwargs):
    # Default message if no parameter is given
    if len(args) == 0:
        message_help = "Hi, I'm **ProgBot**, a bot made for *NetBattlers*, the Unofficial MMBN RPG! \n" + \
                       "My prefix for commands here is `{cp}`. You can also DM me using my default prefix `%s`! \n" % settings.commandprefix + \
                       "To see a list of all commands you can use, type `{cp}commands`. " + \
                       "You can type `{cp}help` and any other command for more info on that command!\n" + \
                       "I can also pull up info on some rules and descriptions! Check `{cp}help all` for the list of details I can help with!"
        return await koduck.sendmessage(context["message"],
                                        sendcontent=message_help.replace("{cp}", koduck.get_prefix(context["message"])).replace("{pd}",
                                                                                                                 settings.paramdelim))

    cleaned_args = clean_args(args)
    if cleaned_args[0] in ['list', 'all']:
        sub_df = help_df[help_df["Hidden?"] == False]
        help_groups = sub_df.groupby(["Type"])
        return_msgs = ["%s\n*%s*" % (name, ", ".join(help_group["Command"].values)) for name, help_group in help_groups if name]
        return await koduck.sendmessage(context["message"], sendcontent="\n\n".join(return_msgs))

    funkyarg = ''.join(cleaned_args)
    help_msg = await find_value_in_table(context, help_df, "Command", funkyarg, suppress_notfound=True, allow_duplicate=True)
    if help_msg is None:
        help_response = help_df[help_df["Command"] == "unknowncommand"].iloc[0]["Response"]
    else:
        help_response = help_msg["Response"].replace("{cp}", koduck.get_prefix(context["message"]))
        if help_msg["Ruling?"]:
            ruling_msg = await find_value_in_table(context, help_df, "Command", help_msg["Ruling?"], suppress_notfound=True)
            if ruling_msg is None:
                return await koduck.sendmessage(context["message"],
                                    sendcontent="Couldn't pull up additional ruling information for %s! You should probably let the devs know..." % help_msg["Ruling?"])
            help_response = help_response + "\n\n" + ruling_msg["Response"].replace("{cp}", koduck.get_prefix(context["message"]))

        # determines custom emojis
        unique_emojis = np.unique(np.array(re.findall(r"<:(\S+):>", help_response)))
        for cust_emoji in unique_emojis:
            if (koduck.client.get_guild(id=settings.source_guild_id)) and (cust_emoji in settings.custom_emojis):
                help_response = re.sub(r"<:%s:>" % cust_emoji, settings.custom_emojis[cust_emoji], help_response)
            else:
                help_response = re.sub(r"(^\s*)?<:%s:>(\s*$|\s)?" % cust_emoji, "", help_response)

    return await koduck.sendmessage(context["message"],
                                    sendcontent=help_response)


# this command is currently unused in ProgBot. lbr it's kind of creepy
async def userinfo(context, *args, **kwargs):
    # if there is no mentioned user (apparently they have to be in the server to be considered "mentioned"), use the message sender instead
    if context["message"].guild is None:
        user = context["message"].author
    elif len(context["message"].mentions) == 0:
        user = context["message"].guild.get_member(context["message"].author.id)
    elif len(context["message"].mentions) == 1:
        user = context["message"].guild.get_member(context["message"].mentions[0].id)
    else:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_nomentioneduser2)

    username = user.name
    discr = user.discriminator
    avatar = user.avatar_url
    creationdate = user.created_at

    # these properties only appear in Member object (subclass of User) which is only available from Servers
    if context["message"].guild is not None:
        game = user.activity
        joindate = user.joined_at
        color = user.color
        if game is None:
            status_line = str(user.status).capitalize()
        else:
            act_type_dict = {discord.ActivityType.playing: "Playing",
                             discord.ActivityType.streaming: "Streaming",
                             discord.ActivityType.listening: "Listening to",
                             discord.ActivityType.watching: "Watching"}
            if game.type in act_type_dict:
                status_line = "%s %s" % (act_type_dict[game.type], game.name)
            else:
                status_line = game.name
        embed = discord.Embed(title="{}#{}".format(username, discr), description=status_line, color=color)
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


def get_roll_from_macro(diff, dicenum):
    roll_difficulty = roll_difficulty_dict[diff.upper()]
    roll_dicenum = int(dicenum)
    return "%dd6>%d" % (roll_dicenum, roll_difficulty)


def roll_master(roll_line, format_limit=FORMAT_LIMIT):
    # subs out the macros
    macro_regex = r"\$?(E|N|H)(\d+)"
    roll_line = re.sub(macro_regex, lambda m: get_roll_from_macro(m.group(1), m.group(2)), roll_line,
                       flags=re.IGNORECASE)
    # adds 1 in front of bare d6, d20 references
    roll_line = re.sub(r"(?P<baredice>^|\b)d(?P<dicesize>\d+)", r"\g<baredice>1d\g<dicesize>", roll_line)
    zero_formatted_roll = re.sub(r'{(.*)}', '0', roll_line)
    roll_is_underflow = False
    roll_results = parser.parse(lexer.lex(zero_formatted_roll))

    if hasattr(roll_results, "modifications"):
        if (len(roll_results.modifications) == 2):
            if len(re.findall(r"(\*|\_|~)+", roll_results.modifications[1][1])) > (format_limit * 2):
                raise dice_algebra.OutOfDiceBounds("Too many formatting elements! (Yes this is a weird error.)\n(Basically your roll is too fancy.)\n(Try not using `>`/`<` operators, or lowering the number of dice!)");
        if sum(roll_results.results) == 0:
            results_bare_str = roll_results.modifications[0][1]
            num_ones = len(re.findall(r'(\D*1\D*)', results_bare_str))
            roll_is_underflow = num_ones >= 3

    return roll_results, roll_is_underflow


def format_hits_roll(roll_result):
    str_result = str(roll_result)
    num_hits = roll_result.eval()
    if 'hit' in str_result:
        if num_hits == 1:
            result_str = "{} = **__{} hit!__**".format(str_result, num_hits)
        else:
            result_str = "{} = **__{} hits!__**".format(str_result, num_hits)
    else:
        result_str = "{} = **__{}__**".format(str_result, roll_result.eval())
    return result_str


async def repeatroll(context, *args, **kwargs):
    if "paramline" not in context:
        ruling_msg = await find_value_in_table(context, help_df, "Command", "rollhelp", suppress_notfound=True)
        if ruling_msg is None:
            return await koduck.sendmessage(context["message"],
                                            sendcontent="Couldn't find the rules for this command! (You should probably let the devs know...)")

        return await koduck.sendmessage(context["message"],
                                        sendcontent=("I can repeat a roll command for you! Try `{cp}repeatroll 3, 5d6>4` or `{cp}repeatroll 3, $N5`!\n\n" + ruling_msg["Response"]).replace(
                                            "{cp}", koduck.get_prefix(context["message"])))
    if len(args) < 2:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Must be in the format of `{cp}repeatroll [repeats], [dice roll]` (i.e. `{cp}repeatroll 3, 5d6>4`)".replace(
                                            "{cp}", koduck.get_prefix(context["message"])))
    try:
        repeat_arg = int(args[0])
    except ValueError:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="First argument needs to be the number of times you want to repeat the roll!")
    if repeat_arg <= 0:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Can't repeat a roll a negative or zero number of times!")

    roll_line = args[1]

    if ROLL_COMMENT_CHAR in roll_line:
        roll_line, roll_comment = roll_line.split(ROLL_COMMENT_CHAR, 1)
    else:
        roll_comment = ""

    roll_line = re.sub("\s+", "", roll_line).lower()
    if not roll_line:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="No roll given!")

    dice_size = re.search('d(\d+)', roll_line)
    reroll_size = int(dice_size.group(1))
    if repeat_arg > MAX_REROLL_QUERY:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Too many small rerolls in one query! Maximum of %d for dice sizes under %d!" % (MAX_REROLL_QUERY, REROLL_DICE_SIZE_THRESHOLD))
    if repeat_arg > MAX_REROLL_QUERY_LARGE and reroll_size > REROLL_DICE_SIZE_THRESHOLD:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Too many large rerolls in one query! Maximum of %d for dice sizes over %d!" % (MAX_REROLL_QUERY_LARGE, REROLL_DICE_SIZE_THRESHOLD))

    try:
        roll_heck = [roll_master(roll_line, format_limit=(FORMAT_LIMIT/repeat_arg)) for i in range(0, repeat_arg)]
        roll_results, is_underflow_list = list(zip(*roll_heck))
    except rply.errors.LexingError:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Unexpected characters found! Did you type out the roll correctly?")
    except AttributeError as e:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Sorry, I can't understand the roll. Try writing it out differently!")
    except dice_algebra.DiceError:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="The dice algebra is incorrect! Did you type out the roll correctly?")
    except dice_algebra.OutOfDiceBounds as e:
        return await koduck.sendmessage(context["message"],
                                        sendcontent=str(e))
    except dice_algebra.BadArgument as e:
        return await koduck.sendmessage(context["message"], sendcontent="Bad argument! " + str(e))


    roll_outputs = [format_hits_roll(result) for result in roll_results]
    progroll_output = "{} *rolls...*".format(context["message"].author.mention)
    if roll_comment:
        progroll_output += " #{}".format(roll_comment.rstrip())
    progroll_output = "{}\n>>> {}".format(progroll_output,"\n".join(roll_outputs))

    progmsg = await koduck.sendmessage(context["message"], sendcontent=progroll_output)
    if not any(is_underflow_list):
        return
    try:
        await progmsg.add_reaction(settings.custom_emojis["underflow"])
    except discord.errors.HTTPException:
        return


async def roll(context, *args, **kwargs):
    if "paramline" not in context:
        ruling_msg = await find_value_in_table(context, help_df, "Command", "rollhelp", suppress_notfound=True)
        if ruling_msg is None:
            return await koduck.sendmessage(context["message"],
                                            sendcontent="Couldn't find the rules for this command! (You should probably let the devs know...)")
        return await koduck.sendmessage(context["message"],
                                        sendcontent=("I can roll dice for you! Try `{cp}roll 5d6>4` or `{cp}roll $N5`!\n\n" + ruling_msg["Response"]).replace(
                                            "{cp}", koduck.get_prefix(context["message"])))
    roll_line = context["paramline"]
    if ROLL_COMMENT_CHAR in roll_line:
        roll_line, roll_comment = roll_line.split(ROLL_COMMENT_CHAR, 1)
    else:
        roll_comment = ""

    roll_line = re.sub("\s+", "", roll_line).lower()
    if not roll_line:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="No roll given!")

    try:
        roll_results, is_underflow = roll_master(roll_line)
    except rply.errors.LexingError:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Unexpected characters found! Did you type out the roll correctly?")
    except AttributeError as e:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Sorry, I can't understand the roll. Try writing it out differently!")
    except dice_algebra.DiceError:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="The dice algebra is incorrect! Did you type out the roll correctly?")
    except dice_algebra.OutOfDiceBounds:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Too many dice were rolled! No more than %d!" % dice_algebra.DICE_NUM_LIMIT)
    except dice_algebra.BadArgument as e:
        return await koduck.sendmessage(context["message"], sendcontent="Bad argument! " + str(e))

    progroll_output = "{} *rolls...* {}".format(context["message"].author.mention, format_hits_roll(roll_results))
    if roll_comment:
        progroll_output += " #{}".format(roll_comment.rstrip())

    progmsg = await koduck.sendmessage(context["message"], sendcontent=progroll_output)
    if not is_underflow:
        return
    try:
        await progmsg.add_reaction(settings.custom_emojis["underflow"])
    except discord.errors.HTTPException:
        return


async def tag(context, *args, **kwargs):
    cleaned_args = clean_args(args)
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Give me a BattleChip tag or Virus/Chip category, and I can pull up its info for you!")
    full_arg = "".join(cleaned_args)
    tag_info = await find_value_in_table(context, tag_df, "Tag", full_arg)
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
    return await koduck.sendmessage(context["message"], sendembed=embed)


async def find_value_in_table(context, df, search_col, search_arg, suppress_notfound=False, alias_message=False, allow_duplicate=False):
    if "Alias" in df:
        alias_check = df[
            df["Alias"].str.contains("(?:^|,|;)\s*%s\s*(?:$|,|;)" % re.escape(search_arg), flags=re.IGNORECASE)]
        if (alias_check.shape[0] > 1) and (not allow_duplicate):
            await koduck.sendmessage(context["message"],
                                     sendcontent="Found more than one match for %s! You should probably let the devs know...")
            return None
        if alias_check.shape[0] != 0:
            search_arg = alias_check.iloc[0][search_col]
            if alias_message:
                await koduck.sendmessage(context["message"],
                                         sendcontent="Found as an alternative name for **%s**!" % search_arg)

    search_results = df[df[search_col].str.contains("\s*^%s\s*$" % re.escape(search_arg), flags=re.IGNORECASE)]
    if search_results.shape[0] == 0:
        if not suppress_notfound:
            await koduck.sendmessage(context["message"],
                                     sendcontent="I can't find `%s`!" % search_arg)
        return None
    elif search_results.shape[0] > 1:
        if allow_duplicate:
            return search_results.iloc[random.randrange(0, search_results.shape[0])]
        else:
            await koduck.sendmessage(context["message"],
                                     sendcontent="Found more than one match for %s! You should probably let the devs know..." % search_arg)
        return None
    return search_results.iloc[0]

async def send_query_msg(context, return_title, return_msg):
    return await koduck.sendmessage(context["message"], sendcontent="**%s**\n*%s*" % (return_title, return_msg))


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
        return_title = "Pulling up all BattleChips from the `%s` Crossover Content..." % subdf.iloc[0]["From?"]
        return_msg = ", ".join(subdf["Chip"])
    elif arg_lower not in ["core"] and arg_lower in chip_from_list:
        subdf = chip_df[chip_df["From?"].str.contains(re.escape(arg_lower), flags=re.IGNORECASE)]
        if subdf.shape[0] == 0:
            return False, "", ""
        return_title = "Pulling up all BattleChips from the `%s` Crossover Content..." % subdf.iloc[0]["From?"]
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


async def chip(context, *args, **kwargss):
    cleaned_args = clean_args(args)
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Give me the name of 1-%d **BattleChips** and I can pull up their info for you!\n\n" % MAX_CHIP_QUERY+
                                                    "I can also query chips by **Category**, **Tag**, **License**, and **Crossover Content**! \n" +
                                                    "I can also list all current chip categories with `{cp}chip category`, and all current chip tags with `{cp}chip tag`. To pull up details on a specific Category or Tag, use `{cp}tag` instead. (i.e. `{cp}tag blade`)"\
                                        .replace("{cp}", koduck.get_prefix(context["message"])))
    if cleaned_args[0] in ['rule', 'ruling', 'rules']:
        ruling_msg = await find_value_in_table(context, help_df, "Command", "chipruling", suppress_notfound=True)
        if ruling_msg is None:
            return await koduck.sendmessage(context["message"],
                                        sendcontent="Couldn't find the rules for this command! (You should probably let the devs know...)")
        return await koduck.sendmessage(context["message"],
                                    sendcontent=ruling_msg["Response"].replace("{cp}", koduck.get_prefix(context["message"])))
    if cleaned_args[0] in ['folder', 'folders']:
        ruling_msg = await find_value_in_table(context, help_df, "Command", "folder", suppress_notfound=True)
        if ruling_msg is None:
            return await koduck.sendmessage(context["message"],
                                        sendcontent="Couldn't find the rules for this command! (You should probably let the devs know...)")
        return await koduck.sendmessage(context["message"],
                                    sendcontent=ruling_msg["Response"].replace("{cp}", koduck.get_prefix(context["message"])))
    if 'blank' in cleaned_args[0]:
        embed = discord.Embed(
            title="__Blank BattleChip__",
            description="*Slot into your PET to download the attack data of defeated Viruses or other entities mid-battle." +
                        "\nBlank chips do not need to be in a Folder to use." +
                        "\nUnless the GM says otherwise, NetOps always have plenty of blank chips available.*",
            color=cc_color_dictionary["Item"])
        return await koduck.sendmessage(context["message"], sendembed=embed)

    if '??' in cleaned_args[0]:
        embed = discord.Embed(
            title="__?????__",
            color=cc_color_dictionary["Mystery"])

        embed.add_field(name="[???/???/???]",
            value="*An unknown chip was slotted in!*")
        return await koduck.sendmessage(context["message"], sendembed=embed)

    if cleaned_args[0] in ['category', 'categories']:
        result_title = "Displaying all known BattleChip Categories..."
        result_text = ", ".join(chip_category_list)
        return await send_query_msg(context, result_title, result_text)
    elif cleaned_args[0] in ['tag', 'tags']:
        result_title = "Displaying all known BattleChip Tags..."
        result_text = ", ".join([i.capitalize() for i in chip_tag_list])
        return await send_query_msg(context, result_title, result_text)
    elif cleaned_args[0] in ['navi', 'navichip']:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="NaviChips are **MegaChips** that store attack data from defeated Navis! Each NaviChip is unique, based off the Navi it was downloaded from. NaviChips are determined by the GM.".replace(
                                                        "{cp}", koduck.get_prefix(context["message"])))
    arg_combined = ' '.join(cleaned_args)
    is_query, return_title, return_msg = query_chip(cleaned_args)
    if is_query:
        return await send_query_msg(context, return_title, return_msg)

    would_be_valid = pity_cc_check(arg_combined)
    if would_be_valid:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="`%s` has no Crossover Content BattleChips!" % would_be_valid)

    if len(cleaned_args) > MAX_CHIP_QUERY:
        return await koduck.sendmessage(context["message"], sendcontent="Too many chips, no more than 5!")

    for arg in cleaned_args:
        if not arg:
            continue
        chip_title, subtitle_trimmed, chip_description, color, _ = await chipfinder(context, arg)
        if chip_title is None:
            continue
        embed = discord.Embed(
            title="__%s__" % chip_title,
            color=color)
        embed.add_field(name="[%s]" % subtitle_trimmed,
                        value="_%s_" % chip_description)
        await koduck.sendmessage(context["message"], sendembed=embed)


async def chipfinder(context, arg, suppress_err_msg=False):
    chip_info = await find_value_in_table(context, chip_df, "Chip", arg, suppress_notfound=True, alias_message=True)
    if chip_info is None:
        chip_info = await find_value_in_table(context, pmc_chip_df, "Chip", arg, suppress_notfound=True,
                                              alias_message=True)
        if chip_info is None:
            chip_info = await find_value_in_table(context, nyx_chip_df, "Chip", arg, suppress_notfound=suppress_err_msg,
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
        msg_time = context["message"].created_at
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
    else:
        color = -1  # error code
    return color


async def power_ncp(context, arg, force_power=False, ncp_only=False, suppress_err_msg=False):
    if ncp_only:
        local_power_df = power_df[power_df["Sort"] != "Virus Power"]
        local_pmc_df = pmc_power_df[pmc_power_df["Sort"] != "Virus Power"]
    else:
        local_power_df = power_df
        local_pmc_df = pmc_power_df

    power_info = await find_value_in_table(context, local_power_df, "Power/NCP", arg, suppress_notfound=True,
                                           alias_message=True)

    if power_info is None:
        power_info = await find_value_in_table(context, local_pmc_df, "Power/NCP", arg, suppress_notfound=True,
                                               alias_message=True)
        if power_info is None:
            power_info = await find_value_in_table(context, nyx_power_df, "Power/NCP", arg, suppress_notfound=suppress_err_msg,
                                                   alias_message=True)
            if power_info is None:
                return None, None, None, None, None

    power_name = power_info["Power/NCP"]

    if ncp_only and any(power_df["Power/NCP"].str.contains("%sncp" % power_name, flags=re.IGNORECASE)):
        power_info = await find_value_in_table(context, local_power_df, "Power/NCP", power_name+"ncp",
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
            power_true_info = await find_value_in_table(context, local_power_df, "Power/NCP", power_skill)
            power_color = find_skill_color(power_true_info["Skill"])
        else:
            power_color = 0xffffff
    field_footer = ""

    # determines custom emojis
    if koduck.client.get_guild(id=settings.source_guild_id):
        emojis_available = True
        if power_tag in ['Instant']:
            emoji_tag = settings.custom_emojis["instant"]
        if power_type in ['Cost']:
            emoji_type = settings.custom_emojis["cost"]
        elif power_type in ['Roll']:
            emoji_type = settings.custom_emojis["roll"]
    else:
        emojis_available = False

    if power_eb == '-' or force_power:  # display as power, rather than ncp
        if power_type == 'Passive' or power_type == '-' or power_type == 'Upgrade':
            field_title = 'Passive Power'
        elif emojis_available:
            field_title = "%s Power/%s%s" % (power_skill, emoji_type, power_type)
            if power_tag:
                field_title += "/%s%s" % (emoji_tag, power_tag)
        else:
            field_title = "%s Power/%s" % (power_skill, power_type)
            if power_tag:
                field_title += "/%s" % power_tag

        field_description = power_description

        # Unused Source description line
        if False:
            if power_source in playermade_list:
                field_footer = "Source: %s (Unofficial)" % power_source
            elif power_source in cc_list:
                field_footer = "Source: %s (Crossover Content)" % power_source

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
            msg_time = context["message"].created_at
            if msg_time.month == 4 and msg_time.day == 1:
                power_name += (" (%s Legal!! Crossover NCP) " % power_source)
            else:
                power_name += (" (%s Illegal Crossover NCP) " % power_source)
        elif power_source != "Core":
            power_name += " (%s Crossover NCP)" % power_source

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


# lowercases all args and strips trailing/leading whitespaces
# splits args with no commas into separate arguments
def clean_args(args, lowercase=True):
    if len(args) == 1:
        args = re.split(r"(?:,|;|\s+)", args[0])

    if lowercase:
        args = [i.lower().strip() for i in args if i and not i.isspace()]
    else:
        args = [i.strip() for i in args if i and not i.isspace()]
    return args



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


async def power(context, *args, **kwargs):
    cleaned_args = clean_args(args)
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Give me the name of 1-%d **Powers** and I can pull up their info for you!\n\n" % MAX_POWER_QUERY +
                                                    "I can also query Powers by **Skill**, **Type**, and whether or not it is **Virus**-exclusive! " +
                                                    "Try giving me multiple queries at once, i.e. `{cp}power sense cost` or `{cp}power virus passive`!".replace(
                                                        "{cp}", koduck.get_prefix(context["message"])))
    if cleaned_args[0] in ['rule', 'ruling', 'rules']:
        ruling_msg = await find_value_in_table(context, help_df, "Command", "powerruling", suppress_notfound=True)
        if ruling_msg is None:
            return await koduck.sendmessage(context["message"],
                                        sendcontent="Couldn't find the rules for this command! (You should probably let the devs know...)")
        return await koduck.sendmessage(context["message"],
                                    sendcontent=ruling_msg["Response"].replace("{cp}", koduck.get_prefix(context["message"])))

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
        power_name, field_title, field_description, power_color, field_footer = await power_ncp(context, arg,
                                                                                                force_power=True)
        if power_name is None:
            continue

        embed = discord.Embed(title="__{}__".format(power_name),
                              color=power_color)
        embed.add_field(name="**[{}]**".format(field_title),
                        value="_{}_".format(field_description))
        if field_footer:
            embed.set_footer(text=field_footer)
        await koduck.sendmessage(context["message"], sendembed=embed)
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
        results_title = "Pulling up all NCPs from the `%s` Crossover Content..." % subdf.iloc[0]["From?"]
        results_msg = ", ".join(subdf["Power/NCP"])
    elif arg_lower in valid_cc_list:
        subdf = ncp_df[ncp_df["From?"].str.contains(re.escape(arg_lower), flags=re.IGNORECASE)]
        results_title = "Pulling up all NCPs from the `%s` Crossover Content..." % subdf.iloc[0]["From?"]
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


async def ncp(context, *args, **kwargs):
    cleaned_args = clean_args(args)
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Give me the names of 1-%d **NaviCust Parts** (NCPs) and I can pull up their info for you!\n\n" % MAX_POWER_QUERY +
                                                    "I can also query NCPs by **EB** and **Crossover Content!**")

    if cleaned_args[0] in ['rule', 'ruling', 'rules']:
        ruling_msg = await find_value_in_table(context, help_df, "Command", "ncpruling", suppress_notfound=True)
        if ruling_msg is None:
            return await koduck.sendmessage(context["message"],
                                        sendcontent="Couldn't find the rules for this command! (You should probably let the devs know...)")
        return await koduck.sendmessage(context["message"],
                                    sendcontent=ruling_msg["Response"].replace("{cp}", koduck.get_prefix(context["message"])))

    arg_combined = " ".join(cleaned_args)
    is_query, results_title, results_msg = query_ncp(arg_combined)
    if is_query:
        return await send_query_msg(context, results_title, results_msg)
    would_be_valid = pity_cc_check(arg_combined)
    if would_be_valid:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="`%s` has no Crossover Content NCPs!" % would_be_valid)

    if len(cleaned_args) > MAX_NCP_QUERY:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Too many NCPs, no more than 5!")

    for arg in cleaned_args:
        if not arg:
            continue

        power_name, field_title, field_description, power_color, _ = await power_ncp(context, arg, force_power=False,
                                                                                     ncp_only=True)
        if power_name is None:
            continue

        embed = discord.Embed(title="__{}__".format(power_name),
                              color=power_color)
        embed.add_field(name="**[{}]**".format(field_title),
                        value="_{}_".format(field_description))
        await koduck.sendmessage(context["message"], sendembed=embed)
    return


def query_npu(arg):
    if arg.capitalize() in skill_list:
        return False, "", ""

    eb_match = re.match(r"^(\d+)(?:\s*EB)?$", arg, flags=re.IGNORECASE)
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


async def upgrade(context, *args, **kwargs):
    cleaned_args = clean_args(args)
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Give me the name of 1-%d default Navi Powers and I can find its **upgrades** for you!" % MAX_NPU_QUERY)
    if len(cleaned_args) > MAX_NPU_QUERY:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="I can't pull up more than %d Navi Power Upgrades at a time!" % MAX_NPU_QUERY)

    if cleaned_args[0] in ['rule', 'ruling', 'rules']:
        ruling_msg = await find_value_in_table(context, help_df, "Command", "npuruling", suppress_notfound=True)
        if ruling_msg is None:
            return await koduck.sendmessage(context["message"],
                                        sendcontent="Couldn't find the rules for this command! (You should probably let the devs know...)")
        return await koduck.sendmessage(context["message"],
                                    sendcontent=ruling_msg["Response"].replace("{cp}", koduck.get_prefix(context["message"])))

    for arg in cleaned_args:
        arg = arg.lower()

        is_upgrade, result_title, result_msg = query_npu(arg)
        if is_upgrade:
            await send_query_msg(context, result_title, result_msg)
            continue
        if any((power_df["Type"] == "Upgrade") & power_df["Power/NCP"].str.contains("^%s$" % re.escape(arg), flags=re.IGNORECASE)):
            await ncp(context, arg, [])
            continue
        await koduck.sendmessage(context["message"],
                                 sendcontent="Couldn't find any Navi Power Upgrades for `%s`!" % arg)
    return


async def virus_master(context, arg, simplified=True):
    virus_info = await find_value_in_table(context, virus_df, "Name", arg, suppress_notfound=True, alias_message=True)

    if virus_info is None:
        virus_info = await find_value_in_table(context, pmc_virus_df, "Name", arg)
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
        virus_footer += " (%s Crossover %s)" % (virus_source, virus_footer_bit)
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
        result_title = "Viruses from the `%s` Crossover Content..." % sub_df.iloc[0]["From?"]
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


async def virus(context, *args, **kwargs):
    cleaned_args = clean_args(args)
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Give me the name of 1-%d **Viruses** and I can pull up their info for you!\n\n" % MAX_VIRUS_QUERY +
                                                    "I can query Viruses by **Category**, **Tag**, or **Crossover Content**, and pull up the list of Virus categories with `{cp}virus category`!\n".replace(
                                                        "{cp}", koduck.get_prefix(context["message"])) +
                                                    "For a list of all Virus categories, use `{cp}virus category`, and all current Virus tags with `{cp}virus tag`. To pull up details on a specific Category or Tag, use `{cp}tag` instead. (i.e. `{cp}tag artillery`)".replace(
                                                        "{cp}", koduck.get_prefix(context["message"])))
    elif cleaned_args[0] in ['category', 'categories']:
        result_title = "Displaying all known Virus Categories..."
        result_text = ", ".join(virus_category_list)
        return await send_query_msg(context, result_title, result_text)
    elif cleaned_args[0] in ['tag', 'tags']:
        result_title = "Displaying all known Virus Tags..."
        result_text = ", ".join([i.capitalize() for i in virus_tag_list])
        return await send_query_msg(context, result_title, result_text)
    elif cleaned_args[0] in ['rule', 'ruling', 'rules']:
        ruling_msg = await find_value_in_table(context, help_df, "Command", "virusruling", suppress_notfound=True)
        if ruling_msg is None:
            return await koduck.sendmessage(context["message"],
                                        sendcontent="Couldn't find the rules for this command! (You should probably let the devs know...)")
        return await koduck.sendmessage(context["message"],
                                    sendcontent=ruling_msg["Response"].replace("{cp}", koduck.get_prefix(context["message"])))
    elif len(cleaned_args) > MAX_VIRUS_QUERY:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Too many viruses, no more than %d!" % MAX_VIRUS_QUERY)

    arg_combined = " ".join(cleaned_args)
    is_query, result_title, result_msg = query_virus(arg_combined)
    if is_query:
        return await send_query_msg(context, result_title, result_msg)

    for arg in cleaned_args:
        if not arg:
            continue
        virus_name, _, virus_description, virus_footer, virus_image, virus_color = await virus_master(context, arg,
                                                                                                      simplified=True)
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
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Give me the name of a **Virus** and I can pull up its full info for you!")
    elif len(cleaned_args) > 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="I can only output one virusx block at a time!")

    if cleaned_args[0] in ['category', 'categories']:
        result_title = "Displaying all known Virus Categories..."
        result_text = ", ".join(virus_category_list)
        return await send_query_msg(context, result_title, result_text)

    virus_name, virus_title, virus_descript_block, virus_footer, virus_image, virus_color = await virus_master(context,
                                                                                                               args[0],
                                                                                                               simplified=False)
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
                                        sendcontent="This command can sort battlechips, NCPs, and powers by Category, and single out Crossover Content chips! " +
                                                    "Please type `{cp}help query` for more information.".replace("{cp}",
                                                                                                                 koduck.get_prefix(context["message"])))
    arg = cleaned_args[0]
    arg_combined = " ".join(cleaned_args)

    is_chip_query, chip_title, chip_msg = query_chip(cleaned_args)
    is_ncp_query, ncp_title, ncp_msg = query_ncp(arg_combined)
    if is_chip_query and is_ncp_query:
        result_title = "Pulling up all BattleChips and NCPs from %s..." % re.match(r".*(`.+`).*", chip_title).group(1)
        ncp_addon = ["%s(NCP)" % i for i in ncp_msg.split(", ")]
        result_msg = chip_msg + ", " + ", ".join(ncp_addon)
        return await send_query_msg(context, result_title, result_msg)
    elif is_chip_query:
        return await send_query_msg(context, chip_title, chip_msg)
    elif is_ncp_query:
        return await send_query_msg(context, ncp_title, ncp_msg)

    is_virus_query, result_title, result_msg = query_virus(arg_combined)
    if is_virus_query:
        return await send_query_msg(context, result_title, result_msg)

    is_npu_query, result_title, result_msg = query_npu(arg_combined)
    if is_npu_query:
        return await send_query_msg(context, result_title, result_msg)

    is_power_query, result_title, result_msg = query_power(cleaned_args)
    if is_power_query:
        return await send_query_msg(context, result_title, result_msg)

    if arg in ['daemon', 'daemons']:
        _, result_title, result_msg = query_daemon()
        return await send_query_msg(context, result_title, result_msg)

    if arg_combined in ['networkmod', 'mod', 'new connections', 'newconnections']:
        _, result_title, result_msg = query_network()
        return await send_query_msg(context, result_title, result_msg)

    if arg_combined in ['weather', 'cyberweather']:
        _, result_title, result_msg = query_weather()
        return await send_query_msg(context, result_title, result_msg)

    would_be_valid = pity_cc_check(arg_combined)
    if would_be_valid:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="`%s` has no queryable Crossover Content!" % would_be_valid)

    return await koduck.sendmessage(context["message"],
                                    sendcontent="`%s` is not a valid query!" % args[0])


async def mysterydata_master(context, args, force_reward=False):
    arg = args[0]
    mysterydata_type = mysterydata_df[mysterydata_df["MysteryData"].str.contains("^%s$" % arg, flags=re.IGNORECASE)]

    if mysterydata_type.shape[0] == 0:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Please specify either Common, Uncommon, or Rare MysteryData. Also accepts Gold, Violet, or Sapphire.")

    roll_probabilities = mysterydata_type[mysterydata_type["Type"] == "Info"]
    if force_reward:
        roll_probabilities = roll_probabilities[roll_probabilities["Value"].str.contains("^BattleChip|NCP|NPU$", flags=re.IGNORECASE)]
    firstroll = random.randint(1, roll_probabilities.shape[0])-1
    roll_category = roll_probabilities.iloc[firstroll]["Value"]

    df_sub = mysterydata_type[mysterydata_type["Type"] == roll_category]
    row_num = random.randint(1, df_sub.shape[0]) - 1
    result_chip = df_sub.iloc[row_num]["Value"]
    if not re.match(r"\w+\s\w+", result_chip): # is not a sentence
        result_text = " %s!" % roll_category
    else:
        result_chip = re.sub(r"\.$", '!', result_chip)  # replaces any periods with exclamation marks!
        result_text = ""

    if roll_category == "Zenny":
        result_chip = "%d" % (int(result_chip) * (random.randint(1, 6) + random.randint(1, 6)))

    result_text = result_chip + result_text

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
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await koduck.sendmessage(context["message"],
                                        sendcontent="I can roll **Mystery Data** for you! Specify Common, Uncommon, or Rare! You can also roll for Gold, Violet, or Sapphire from NetBattlers Advance.\n" + \
                                                    "You can also ask for advice using `{cp}mysterydata advice`!".replace(
                                            "{cp}", koduck.get_prefix(context["message"])))

    if cleaned_args[0] in ['advice', 'rule', 'ruling', 'rules']:
        ruling_msg = await find_value_in_table(context, help_df, "Command", "mysterydataruling", suppress_notfound=True)
        if ruling_msg is None:
            return await koduck.sendmessage(context["message"],
                                            sendcontent="Couldn't find the rules for this command! (You should probably let the devs know...)")
        return await koduck.sendmessage(context["message"],
                                        sendcontent=ruling_msg["Response"].replace("{cp}", koduck.get_prefix(context["message"])))
    await mysterydata_master(context, cleaned_args, force_reward=False)


async def crimsonnoise(context, *args, **kwargs):
    cleaned_args = clean_args(args)
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await koduck.sendmessage(context["message"],
                                        sendcontent="I can roll **CrimsonNoise** for you! Specify `{cp}crimsonnoise common`, `{cp}crimsonnoise`, or `{cp}crimsonnoise rare`!".replace(
                                            "{cp}", koduck.get_prefix(context["message"])))

    arg = cleaned_args[0]
    crimsonnoise_type = crimsonnoise_df[crimsonnoise_df["MysteryData"].str.contains("^%s$" % arg, flags=re.IGNORECASE)]

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
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await koduck.sendmessage(context["message"],
                                        sendcontent="I can roll **Mystery Data** for you, keeping it to the BattleChips and NCPs! " +
                                                    "Specify Common, Uncommon, or Rare! You can also roll for Gold, Violet, or Sapphire from NetBattlers Advance!".replace(
                                                        "{cp}", koduck.get_prefix(context["message"])))

    await mysterydata_master(context, cleaned_args, force_reward=True)
    return


async def bond(context, *args, **kwargs):
    cleaned_args = [arg.lower() for arg in args]
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Give me a **Bond Power** and I can pull up its info for you!\nFor a list of all Bond Powers, use `{cp}bond all`!".replace(
                                                        "{cp}", koduck.get_prefix(context["message"])))
    elif cleaned_args[0] in ['rule', 'ruling', 'rules']:
        ruling_msg = await find_value_in_table(context, help_df, "Command", "bondruling", suppress_notfound=True)
        if ruling_msg is None:
            return await koduck.sendmessage(context["message"],
                                        sendcontent="Couldn't find the rules for this command! (You should probably let the devs know...)")
        return await koduck.sendmessage(context["message"],
                                    sendcontent=ruling_msg["Response"].replace("{cp}", koduck.get_prefix(context["message"])))
    elif (len(cleaned_args) > MAX_BOND_QUERY):
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Too many Bond Powers; no more than %d!\nBesides, there's only four Bond Powers in the game!" % MAX_BOND_QUERY)
    if cleaned_args[0] in ['all', 'list']:
        result_title = "Pulling up all Bond Powers..."
        result_msg = ', '.join(bond_df["BondPower"])
        return await send_query_msg(context, result_title, result_msg)

    for arg in cleaned_args:
        bond_info = await find_value_in_table(context, bond_df, "BondPower", arg)
        if bond_info is None:
            return

        bond_title = bond_info["BondPower"]
        bond_cost = bond_info["Cost"]
        bond_description = bond_info["Description"]

        embed = discord.Embed(
            title="__%s__" % bond_title,
            color=0x24ff00)
        embed.add_field(name="**({})**".format(bond_cost),
                        value="_{}_".format(bond_description))

        await koduck.sendmessage(context["message"], sendembed=embed)
    return


def query_daemon():
    result_title = "Listing all Daemons (excluding Player Made Content)..."
    result_msg = ", ".join(daemon_df["Name"])
    return True, result_title, result_msg


async def daemon(context, *args, **kwargs):
    cleaned_args = clean_args(args)
    arg_combined = " ".join(cleaned_args)
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Lists the complete information of a **Daemon** for DarkChip rules. "
                                                    + "Use `{cp}daemon all` to pull up the names of all Official Daemons!".replace("{cp}", koduck.get_prefix(context["message"])))
    is_ruling = False
    ruling_msg = None
    if arg_combined in ["all", "list"]:
        _, result_title, result_msg = query_daemon()
        return await send_query_msg(context, result_title, result_msg)
    elif cleaned_args[0] in ['rule', 'ruling', 'rules', 'advice']:
        is_ruling = True
        ruling_msg = await find_value_in_table(context, help_df, "Command", "daemonruling", suppress_notfound=True)
    elif cleaned_args[0] in ['darkchip', 'dark', 'darkchips', 'chip', 'chips']:
        is_ruling = True
        ruling_msg = await find_value_in_table(context, help_df, "Command", "darkchip", suppress_notfound=True)
    elif cleaned_args[0] in ['tribute', 'tributes']:
        is_ruling = True
        ruling_msg = await find_value_in_table(context, help_df, "Command", "tribute", suppress_notfound=True)
    elif cleaned_args[0] in ['chaosunison', 'chaos', 'chaosunion']:
        is_ruling = True
        ruling_msg = await find_value_in_table(context, help_df, "Command", "domain", suppress_notfound=True)
    elif cleaned_args[0] in ['daemonbond', 'bond']:
        is_ruling = True
        ruling_msg = await find_value_in_table(context, help_df, "Command", "daemonbond", suppress_notfound=True)

    if is_ruling:
        if ruling_msg is None:
            return await koduck.sendmessage(context["message"],
                                            sendcontent="Couldn't find the rules for this command! (You should probably let the devs know...)")
        return await koduck.sendmessage(context["message"],
                                        sendcontent=ruling_msg["Response"].replace("{cp}", koduck.get_prefix(context["message"])))

    daemon_info = await find_value_in_table(context, daemon_df, "Name", arg_combined, suppress_notfound=True)
    if daemon_info is None:
        daemon_info = await find_value_in_table(context, pmc_daemon_df, "Name", arg_combined)
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
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Give you up to %d random **elements** from the Element Generation table. " % MAX_ELEMENT_QUERY +
                                                    "To use, enter `{cp}element [#]` or `{cp}element [category] [#]`!\n"\
                                        .replace("{cp}", koduck.get_prefix(context["message"])) +
                                                    "Categories: **%s**" % ", ".join(element_category_list))

    if cleaned_args[0] in ['rule', 'ruling', 'rules', 'advice']:
        ruling_msg = await find_value_in_table(context, help_df, "Command", "elementruling", suppress_notfound=True)
        if ruling_msg is None:
            return await koduck.sendmessage(context["message"],
                                            sendcontent="Couldn't find the rules for this command! (You should probably let the devs know...)")
        return await koduck.sendmessage(context["message"],
                                        sendcontent=ruling_msg["Response"].replace("{cp}", koduck.get_prefix(context["message"])))
    if len(cleaned_args) > 2:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Command is too long! Just give me `{cp}element [#]` or `{cp}element [category] [#]`!".replace(
                                            "{cp}", koduck.get_prefix(context["message"])))

    element_return_number = 1  # number of elements to return, 1 by default
    element_category = None
    sub_element_df = element_df
    for arg in cleaned_args:
        try:
            element_return_number = int(arg)
            break
        except ValueError:
            element_category = arg.lower().capitalize()

            sub_element_df = element_df[element_df["category"].str.contains(re.escape(arg), flags=re.IGNORECASE)]
            if sub_element_df.shape[0] == 0:
                return await koduck.sendmessage(context["message"],
                                                sendcontent="Not a valid category!\n" +
                                                            "Categories: **%s**" % ", ".join(element_category_list))

    if element_return_number < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="The number of elements can't be 0 or negative!")
    if element_return_number > MAX_ELEMENT_QUERY:
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
    split_args = [re.sub(r"([a-z])(\d)",r"\1 \2", arg, re.IGNORECASE) for arg in args]
    cleaned_args = clean_args([" ".join(split_args)])

    errmsg = []
    if args:
        is_get_latest = cleaned_args[0] in ["all", "latest", "new"]
    else:
        is_get_latest = True

    if is_get_latest:
        rulebook_df["BiggNumber"] = pd.to_numeric(rulebook_df["Version"])
        ret_books = rulebook_df.loc[rulebook_df.groupby(["Name"])["BiggNumber"].idxmax()]
        book_names = ["**%s %s %s**: <%s>" % (book["Name"], book["Release"], book["Version"], book["Link"]) for _, book in
                      ret_books.iterrows()]
    elif cleaned_args[0] == "help":
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Links the **rulebooks** for NetBattlers! " +
                                                    "You can also look for a specific rulebook version! (i.e. `{cp}rulebook beta 7 adv 6`) \n"
                                                    .replace("{cp}", koduck.get_prefix(context["message"])))
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
                    await koduck.sendmessage(context["message"], sendcontent="Going with Version `%s`!" % version_str)
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
                if book_query["Version"] is None:
                    await koduck.sendmessage(context["message"],
                                             sendcontent="Going with all versions!")
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
                await koduck.sendmessage(context["message"],
                                         sendcontent="Don't know which book you want! Please specify either 'Beta', 'Advance', or 'Alpha'!'")
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
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Couldn't find any rulebooks for `%s`!" % " ".join(args))
    return await koduck.sendmessage(context["message"],  sendcontent="\n".join(book_names))


def query_network():
    result_title = "Listing all Network Modifiers from the `New Connections` crossover content..."
    result_msg = ", ".join(networkmod_df["Name"])
    return True, result_title, result_msg


def query_weather():
    result_title = "Listing all types of CyberWeather from NetBattlers Advance..."
    result_msg = ", ".join(weather_df["Name"])
    return True, result_title, result_msg

async def networkmod(context, *args, **kwargs):
    cleaned_args = clean_args(args)
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Pulls up info for 1-%d **Network Modifiers**! I can also list all Network Modifiers if you tell me `list` or `all`!" % MAX_MOD_QUERY)

    if len(cleaned_args) > MAX_MOD_QUERY:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Can't pull up more than %d Network Mods!" % MAX_MOD_QUERY)

    if cleaned_args[0] in ["list", "all"]:
        _, result_title, result_msg = query_network()
        return await send_query_msg(context, result_title, result_msg)
    elif cleaned_args[0] in ['rule', 'ruling', 'rules']:
        ruling_msg = await find_value_in_table(context, help_df, "Command", "networkmodruling", suppress_notfound=True)
        if ruling_msg is None:
            return await koduck.sendmessage(context["message"],
                                            sendcontent="Couldn't find the rules for this command! (You should probably let the devs know...)")
        return await koduck.sendmessage(context["message"],
                                        sendcontent=ruling_msg["Response"].replace("{cp}", koduck.get_prefix(context["message"])))

    for arg in cleaned_args:
        networkmod_info = await find_value_in_table(context, networkmod_df, "Name", arg, suppress_notfound=False)
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
    invite_link = settings.invite_link
    color = 0x71c142
    embed = discord.Embed(title="Just click here to invite me to one of your servers!",
                          color=color,
                          url=invite_link)
    return await koduck.sendmessage(context["message"], sendembed=embed)


def change_audience(channel_id, cj_type, amount):
    id = str(channel_id)
    #with open(settings.audiencefile, "r") as afp:
    #audience_data = json.load(afp)
    if id not in audience_data:
        return (-1, "Audience Participation hasn't been started in this channel!")
    currentval = audience_data[id][cj_type]
    tempval = currentval + amount
    if tempval < 0:
        return (-1, "There's not enough %ss for that! (Current %ss: %d)" % (*[cj_type.capitalize()]*2, currentval), "")
    if tempval > MAX_CHEER_JEER_VALUE:
        return (-1, "That adds too many %ss! (Current %ss: %d, Max: %d)" % (*[cj_type.capitalize()]*2, currentval, MAX_CHEER_JEER_VALUE), "")

    audience_data[id][cj_type] = tempval
    audience_data[id]["last_modified"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if amount > 0:
        word_term = "Added %d %s!" % (amount, cj_type.capitalize())
    elif amount < 0:
        word_term = "Spent %d %s!" % (-1*amount, cj_type.capitalize())
    else:
        word_term = "Added... 0 %s! Huh?" % (cj_type.capitalize())
    c_val = audience_data[id]["cheer"]
    j_val = audience_data[id]["jeer"]

    #with open(settings.audiencefile, 'w') as afp:
    #    json.dump(audience_data, afp, sort_keys=True, indent=4, default=str)

    return (0, word_term, "Cheer Points: %d, Jeer Points: %d" % (c_val, j_val))


def get_audience(channel_id):
    id = str(channel_id)
    #with open(settings.audiencefile, "r") as afp:
        #audience_data = json.load(afp)
    if id not in audience_data:
        return (-1, "Audience Participation hasn't been started in this channel!")
    c_val = audience_data[id]["cheer"]
    j_val = audience_data[id]["jeer"]
    return (0, (c_val, j_val))


def start_audience(channel_id):
    id = str(channel_id)
    #with open(settings.audiencefile, "r") as afp:
        #audience_data = json.load(afp)
    if len(audience_data) > MAX_AUDIENCES:
        return (-2, "ProgBot's hosting too many audiences right now! Try again later!", "")
    if id in audience_data:
        c_val = audience_data[id]["cheer"]
        j_val = audience_data[id]["jeer"]
        return (-1,
                "Audience Participation was already started in this channel!",
                "Cheer Points: %d, Jeer Points: %d" % (c_val, j_val))
    audience_data[id] = {"cheer": 0, "jeer": 0, "last_modified": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    #with open(settings.audiencefile, 'w') as afp:
    #    json.dump(audience_data, afp, sort_keys=True, indent=4, default=str)

    return (0, "", "")


def end_audience(channel_id):
    id = str(channel_id)
    #with open(settings.audiencefile, "r") as afp:
    #    audience_data = json.load(afp)
    try:
        del audience_data[id]
        #with open(settings.audiencefile, 'w') as afp:
        #    json.dump(audience_data, afp, sort_keys=True, indent=4, default=str)
        return 0
    except KeyError:
        return -1


async def cheer(context, *args, **kwargs):
    cleaned_args = clean_args(args)

    if len(cleaned_args) >= 1:
        if cleaned_args[0] == 'help':
            audience_help_msg = "Roll a random Cheer with `{cp}cheer!` (Up to %d at once!)\n " % MAX_CHEER_JEER_ROLL + \
                            "I can also list all Cheers with `{cp}cheer all`.\n\n " + \
                            "You can add Cheer Points with `{cp}cheer add 2`, remove them with `{cp}cheer spend 2`, " + \
                            "and pull up the current Cheer points with `{cp}cheer now`.\n\n" + \
                            "For more details on Audience Participation rules, try `{cp}help cheer` or `{cp}help audience`."
            return await koduck.sendmessage(context["message"], sendcontent=audience_help_msg.replace("{cp}", koduck.get_prefix(context["message"])))

        if cleaned_args[0] in ['rule', 'ruling', 'rules']:
            ruling_msg = await find_value_in_table(context, help_df, "Command", "cheerruling", suppress_notfound=True)
            if ruling_msg is None:
                return await koduck.sendmessage(context["message"],
                                                sendcontent="Couldn't find the rules for this command! (You should probably let the devs know...)")
            return await koduck.sendmessage(context["message"],
                                            sendcontent=ruling_msg["Response"].replace("{cp}", koduck.get_prefix(context["message"])))
    modded_arg = list(args)
    if modded_arg:
        modded_arg[0] = modded_arg[0] + " cheer"
    else:
        modded_arg = ["cheer"]
    await audience(context, *modded_arg, **kwargs)
    return


async def jeer(context, *args, **kwargs):
    cleaned_args = clean_args(args)
    if len(cleaned_args) >= 1:
        if cleaned_args[0] == 'help':
            audience_help_msg = "Roll a random Jeer with `{cp}jeer!` (Up to %d at once!)\n" % MAX_CHEER_JEER_ROLL + \
                            "I can also list all Jeers and MegaJeers with `{cp}jeer all`.\n\n " + \
                            "You can add Jeer Points with `{cp}jeer add 2`, remove them with `{cp}jeer spend 2`, " + \
                            "and pull up the current Jeer Points with `{cp}jeer now`.\n\n" + \
                            "For more details on Audience Participation rules, try `{cp}help jeer` or `{cp}help audience`."
            return await koduck.sendmessage(context["message"], sendcontent=audience_help_msg.replace("{cp}", koduck.get_prefix(context["message"])))

        if cleaned_args[0] in ['rule', 'ruling', 'rules']:
            ruling_msg = await find_value_in_table(context, help_df, "Command", "jeerruling", suppress_notfound=True)
            if ruling_msg is None:
                return await koduck.sendmessage(context["message"],
                                                sendcontent="Couldn't find the rules for this command! (You should probably let the devs know...)")
            return await koduck.sendmessage(context["message"],
                                            sendcontent=ruling_msg["Response"].replace("{cp}", koduck.get_prefix(context["message"])))

    modded_arg = list(args)
    if modded_arg:
        modded_arg[0] = modded_arg[0] + " jeer"
    else:
        modded_arg = ["jeer"]
    await audience(context, *modded_arg, **kwargs)
    return


async def audience(context, *args, **kwargs):
    if context["message"].channel.type is discord.ChannelType.private:
        channel_id = context["message"].channel.id
        channel_name = context["message"].author.name
        msg_location = "%s! (Direct messages)" % channel_name
    else:
        channel_id = context["message"].channel.id
        channel_name = context["message"].channel.name
        channel_server = context["message"].channel.guild
        msg_location = "#%s! (%s)" % (channel_name, channel_server)
    cleaned_args = clean_args(args)
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        audience_help_msg = "Roll a random Cheer or Jeer with `{cp}audience cheer` or `{cp}audience jeer`! (Up to %d at once!)\n" % MAX_CHEER_JEER_ROLL + \
                            "I can also list all Cheers or Jeers with `{cp}audience cheer all` or `{cp}audience jeer all`.\n\n" + \
                            "Start up an audience tracker for this text channel with `{cp}audience start`!\n" + \
                            "You can then add Cheers and Jeers with `{cp}audience cheer add 2`, remove them with `{cp}audience cheer spend 2`, " + \
                            "and pull up the current Cheer/Jeer points with `{cp}audience now`.\n\n" + \
                            "Once you're done, make sure to dismiss the audience with `{cp}audience end`."
        return await koduck.sendmessage(context["message"], sendcontent=audience_help_msg.replace("{cp}", koduck.get_prefix(context["message"])))

    if cleaned_args[0] in ['rule', 'ruling', 'rules']:
        ruling_msg = await find_value_in_table(context, help_df, "Command", "audienceruling", suppress_notfound=True)
        if ruling_msg is None:
            return await koduck.sendmessage(context["message"],
                                            sendcontent="Couldn't find the rules for this command! (You should probably let the devs know...)")
        return await koduck.sendmessage(context["message"],
                                        sendcontent=ruling_msg["Response"].replace("{cp}", koduck.get_prefix(context["message"])))

    is_query = False
    is_spend = False
    is_pullup = False
    query_details = ["", 1, ""]

    if cleaned_args[0] == 'start':
        retvalue = start_audience(channel_id)
        if retvalue[0] == -1:
            embed_descript = retvalue[1]
            embed_foot = retvalue[2]
        elif retvalue[0] == -2:
            return await koduck.sendmessage(context["message"], sendcontent=retvalue[1])
        else:
            embed_descript = "Starting up the audience for %s" % msg_location
            embed_foot = "Cheer Points: 0, Jeer Points: 0"
        embed = discord.Embed(title="__Audience Participation__",
                              description=embed_descript,
                              color=cj_colors["cheer"])
        embed.set_footer(text=embed_foot)
        return await koduck.sendmessage(context["message"], sendembed=embed)
    elif cleaned_args[0] == 'end':
        ret_val = end_audience(channel_id)
        if ret_val == -1:
            return await koduck.sendmessage(context["message"], sendcontent="An audience hasn't been started for this channel yet")
        embed = discord.Embed(title="__Audience Participation__",
                              description="Ending the audience session for %s\nGoodnight!" % msg_location,
                              color=cj_colors["jeer"])
        return await koduck.sendmessage(context["message"], sendembed=embed)

    for arg in cleaned_args:
        if arg in ["mega", "megacheer", "megajeer"]:
            is_query = True
            query_details[0] = arg
            break
        elif arg in ["add", "subtract", "spend", "gain", "remove"]:
            is_spend = True
            if arg in ["add", "gain"]:
                query_details[2] = "+"
            else:
                query_details[2] = "-"
        elif arg in ["all", "list", "option", "options"]:
            is_query = True
        elif arg in ["cheer", "jeer", "cheers", "jeers", "c", "j"]:
            if query_details[0]:
                return await koduck.sendmessage(context["message"], sendcontent="Sorry, you can't ask for both Cheers and Jeers!")
            if "c" in arg:
                query_details[0] = "cheer"
            else:
                query_details[0] = "jeer"
        elif arg.isnumeric():
            query_details[1] = int(arg)
        elif arg in ["now", "current", "show"]:
            is_pullup = True
        else:
            return await koduck.sendmessage(context["message"],
                                            sendcontent="Sorry, I'm not sure what `%s` means here!" % arg)
    if is_pullup:
        retval = get_audience(channel_id)
        if retval[0] == -1:
            return await koduck.sendmessage(context["message"],
                                            sendcontent="Audience Participation hasn't been started in this channel!")
        c_val = retval[1][0]
        j_val = retval[1][1]
        if c_val >= j_val:
            embed_color = cj_colors["cheer"]
        else:
            embed_color = cj_colors["jeer"]
        embed = discord.Embed(title="__Audience Participation__",
                              description="Pulling up the audience for %s" % msg_location,
                              color=embed_color)
        embed.set_footer(text="Cheer Points: %d, Jeer Points: %d" % (c_val, j_val))
        return await koduck.sendmessage(context["message"], sendembed=embed)

    if is_spend:
        if not query_details[0]:
            return await koduck.sendmessage(context["message"],
                                            sendcontent="Did not specify Cheer or Jeer!")
        if query_details[2] == '-':
            change_amount = -1 * query_details[1]
        else:
            change_amount = query_details[1]
        retval = change_audience(channel_id, query_details[0], change_amount)
        if retval[0] == -1:
            return await koduck.sendmessage(context["message"], sendcontent=retval[1])
        embed = discord.Embed(title="__Audience Participation__",
                              description=retval[1],
                              color=cj_colors[query_details[0]])
        embed.set_footer(text=retval[2])
        return await koduck.sendmessage(context["message"], sendembed=embed)

    elif is_query:
        if not query_details[0]:
            query_details[0] = "eer"
            embed_msg = "**Listing all Cheers/Jeers from the Audience Participation rules...**\n"
        else:
            embed_msg = "**Listing `%s`(s) from the Audience Participation rules...**\n" % query_details[0]
        sub_df = audience_df[audience_df["Type"].str.contains(re.escape(query_details[0]), flags=re.IGNORECASE)]
        embed_bits = []
        for cj_type in sub_df["Type"].unique():
            subsub_df = sub_df[sub_df["Type"] == cj_type]
            subsub_index = range(1, subsub_df.shape[0] + 1)
            line_items = ["> *%d. %s*"%(i, val) for i, val in zip(subsub_index, subsub_df["Option"].values)]
            embed_submsg = "> **%s**\n" % cj_type + "\n".join(line_items)
            embed_bits.append(embed_submsg)
        embed_msg += "\n\n".join(embed_bits)
        return await koduck.sendmessage(context["message"], sendcontent=embed_msg)
    else:
        if query_details[1] > MAX_CHEER_JEER_ROLL:
            return await koduck.sendmessage(context["message"], sendcontent="Rolling too many Cheers or Jeers! Up to %d!" % MAX_CHEER_JEER_ROLL)
        if not query_details[0]:
            return await koduck.sendmessage(context["message"], sendcontent="Please specify either Cheer or Jeer!")
        if query_details[1] <= 0:
            embed_descript = "%s rolled ... %d %ss! Huh?!\n\n" % (context["message"].author.mention, query_details[1], query_details[0].capitalize())
        else:
            sub_df = audience_df[audience_df["Type"].str.contains("^%s$" % re.escape(query_details[0]), flags=re.IGNORECASE)]
            random_roll = [random.randrange(sub_df.shape[0]) for i in range(query_details[1])]
            cj_roll = ["*%s*" % sub_df["Option"].iloc[i] for i in random_roll]

            if len(cj_roll) == 1:
                noun_term = "a %s" % query_details[0].capitalize()
            else:
                noun_term = "%d %ss" % (query_details[1], query_details[0].capitalize())
            embed_descript = "%s rolled %s!\n\n" % (context["message"].author.mention, noun_term) + "\n".join(cj_roll)

        retval = get_audience(channel_id)
        if retval[0] == 0:
            c_val = retval[1][0]
            j_val = retval[1][1]
            if ('c' in query_details[0] and (query_details[1] > c_val)) or (
                    'j' in query_details[0] and (query_details[1] > j_val)):
                embed_descript = "Not enough %s!" % query_details[0].capitalize()
                embed_footer = "Cheer Points: %d, Jeer Points: %d" % retval[1]
            else:
                _, _, embed_footer = change_audience(channel_id, query_details[0], -1 * query_details[1])
        else:
            embed_footer = ""

        embed = discord.Embed(title="__Audience Participation__",
                              description=embed_descript,
                              color=cj_colors[query_details[0]])
        if embed_footer:
            embed.set_footer(text=embed_footer)

        return await koduck.sendmessage(context["message"], sendembed=embed)


async def virusr(context, *args, **kwargs):
    mod_args = []
    for arg in args:
        test_match = re.match(r"^(?P<word1>[^0-9]*)\s*(?P<word2>[^0-9]*)\s*(?P<num>[\d]*)$", arg)
        if test_match is None:
            mod_args = args
            break
        if not test_match.group("num"):
            mod_args.append(arg + " 1")
        else:
            mod_args.append(arg)
    arg_string = " ".join(mod_args)

    cleaned_args = clean_args([arg_string])
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        audience_help_msg = "I can roll 1-%d random **Viruses**!\n" % MAX_RANDOM_VIRUSES + \
                            "You can also give me the **Categories** and **number of Viruses** you want to roll too! (i.e. `{cp}virusr support 1, artillery 2`)\n" + \
                            "You can specify Mega or Omega Viruses too! (Otherwise, they will not be rolled.)\n\n" + \
                            "**Available Virus Categories:** %s" % ", ".join(["Any"] + virus_category_list)
        return await koduck.sendmessage(context["message"],
                                        sendcontent=audience_help_msg.replace("{cp}", koduck.get_prefix(context["message"])))
    virus_roll_list = []
    virus_roll = ["any", 1, "normal"]
    virus_category_lower = [i.lower() for i in virus_category_list] + ["any"]
    total_v = 0
    in_progress = False
    for arg in cleaned_args:
        try:
            virus_roll[1] = int(arg)
            virus_roll_list.append(virus_roll)
            total_v += virus_roll[1]
            virus_roll = ["any", 1, "normal"]
            in_progress = False
            continue
        except ValueError:
            pass
        if arg in ['virus', 'any', 'random']:
            continue
        elif arg in ['mega', 'megavirus']:
            virus_roll[2] = "mega"
            in_progress = True
        elif arg in ['omega', 'omegavirus']:
            virus_roll[2] = "omega"
            in_progress = True
        elif arg in virus_category_lower:
            if virus_roll[0] not in ["any", "random"]:
                virus_roll_list.append(virus_roll)
                total_v += virus_roll[1]
                virus_roll = ["any", 1, "normal"]
                in_progress = False
            virus_roll[0] = arg
            in_progress = True
        else:
            return await koduck.sendmessage(context["message"],
                                            sendcontent="I don't recognize `%s`!" % arg)

    if in_progress:
        virus_roll_list.append(virus_roll)
        total_v += virus_roll[1]

    if total_v > MAX_RANDOM_VIRUSES:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Rolling too many Viruses! (Only up to %d!)" % MAX_RANDOM_VIRUSES)
    elif total_v == 0:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Rolling... no Viruses? Huh?")
    elif total_v == 1:
        virus_keyword = "Virus"
    else:
        virus_keyword = "Viruses"

    virus_roll_titles = []
    viruses_names = []
    for virus_type, virus_num, virus_tier in virus_roll_list:
        if virus_num == 0:
            continue
        if virus_tier == 'mega':
            sub_df = virus_df[virus_df["Tags"].str.contains(r"Mega", flags=re.IGNORECASE) & ~virus_df["Name"].str.contains(r"Ω")]
            virus_cat = "Mega "
        elif virus_tier == 'omega':
            sub_df = virus_df[virus_df["Tags"].str.contains(r"Mega", flags=re.IGNORECASE) & virus_df["Name"].str.contains(r"Ω")]
            virus_cat = "Omega "
        else:
            sub_df = virus_df[~virus_df["Tags"].str.contains(r"Mega", flags=re.IGNORECASE)]
            virus_cat = ""
        if virus_type != "any":
            sub_df = sub_df[sub_df["Category"].str.contains(r"^%s$" % re.escape(virus_type), flags=re.IGNORECASE)]
            virus_cat += sub_df["Category"].iloc[0]
        else:
            virus_cat += "Random"
        if sub_df.shape[0] < virus_num:
            search_query = " ".join([virus_type, virus_tier])
            await koduck.sendmessage(context["message"],
                                     sendcontent="There's only %d `%s` Viruses! Limiting it to %d..." % (sub_df.shape[0], search_query, sub_df.shape[0]))
            virus_num = sub_df.shape[0]

        virus_roll_titles.append("%d %s" % (virus_num, virus_cat))
        viruses_rolled = random.sample(range(sub_df.shape[0]), virus_num)
        viruses_names += [sub_df.iloc[i]["Name"] for i in viruses_rolled]

    virus_title = ", ".join(virus_roll_titles)
    virus_list = ", ".join(viruses_names)
    embed = discord.Embed(title="Rolling %s %s..." % (virus_title, virus_keyword),
                          color=virus_colors["Virus"],
                          description=virus_list)
    return await koduck.sendmessage(context["message"], sendembed=embed)


async def break_test(context, *args, **kwargs):
    return await koduck.sendmessage(context["message"], sendcontent=str(0 / 0))

# UGH permissions
async def change_prefix(context, *args, **kwargs):
    if not args:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Changes the prefix that I use for this server! The default prefix is `%s`" % settings.commandprefix)
    is_changed = koduck.change_prefix(context["message"].guild.id, args[0])
    if is_changed:
        await koduck.sendmessage(context["message"],
                                 sendcontent="Command prefix successfully changed to `%s`" % args[0])
    else:
        await koduck.sendmessage(context["message"],
                                 sendcontent="Error occurred!")
    return

async def repo(context, *args, **kwargs):
    cleaned_args = clean_args(args)
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        message_help =  "Give me the name of custom game content and I can look them up on the official **repository** for you! " + \
                        "Want to submit something? You can access the full Player-Made Repository here! \n__<{}>__"
        return await koduck.sendmessage(context["message"],
                                    sendcontent=message_help.format(pmc_link))
    user_query = context["paramline"]

    # api change @ 10/24/21:
    # major change is that "query" is no longer a thing and "type" no longer accepts table searching in favor of "reducers".
    # table search aggregate is now categorized under the "reducer" parameter.
    # searchQuery is no longer embedded in loader and is now in "sort". "query" is no longer a parameter field.
    # UTZ has been moved to "sort" as well.
    # collectionId and collectionViewId appear to have been deprecated in favor of "collection" and "collectionView" sub-parameters.
    # now requires id and separate "spaceId" values, though what the usecase for the latter is unknown to me.

    data = {
        "collection": {
            "id": settings.notion_collection_id, "spaceId": settings.notion_collection_space_id
        },
        "collectionView": {
            "id": settings.notion_collection_view_id, "spaceId": settings.notion_collection_space_id
        },
        "loader": {
            "type": "reducer",
            "reducers": {
                "collection_group_results": {
                    "type": "results",
                    "limit": 50
                },
                "table:uncategorized:title:count": {
                    "type": "aggregation",
                    "aggregation":
                        {"property":"title",
                         "aggregator":"count"}
                }
            },
        "sort":
            [{"property":"g=]<","direction":"ascending"},
             {"property":"title","direction":"ascending"},
             {"property":"UjPS","direction":"descending"}],
            "searchQuery": user_query,
            "userTimeZone": "America/Chicago"
        }
    }

    r = requests.post(settings.notion_query_link, json=data)

    # R:200 - all good
    # R:3xx - what the fuck notion?
    # R:4xx - bad request, wrong api endpoint, notion changed the api again, scrape the new fields (i.e.: our problem)
    # R:5xx - notion's down (i.e.: not our problem)
    if r.status_code != 200:
        print(r.status_code, r.reason)
        print("Response:", r.content)
        return await koduck.sendmessage(context["message"],
                                 sendcontent="Sorry, I got an unexpected response from Notion! Please try again later! (If this persists, let the devs know!)")

    # just leaving this here for the next time i need to work on this again..
    #parse = json.loads(r.content)
    #print(json.dumps(parse, indent=4, sort_keys=True))

    # iza helped me rewrite the overwhelming bulk of this.
    # she's amazing, she's wonderful, and if you're not thankful for her presence in mmg i'll bite your kneecaps off.
    repo_results_dict = {}
    blockmap = r.json()["recordMap"]["block"]
    for k in blockmap:
        if "properties" in blockmap[k]["value"]:
            repo_results_dict[k] = blockmap[k]["value"]["properties"]
    df_column_names = {}

    header_blk = r.json()["recordMap"]["collection"][data["collection"]["id"]]["value"]["schema"]
    for k in header_blk:
        df_column_names[k] = header_blk[k]["name"]

    repo_results_df = pd.DataFrame.from_dict(repo_results_dict, orient="index").rename(columns=df_column_names).dropna(axis='columns',how='any')
    repo_results_df = repo_results_df.apply(lambda x: x.explode().explode() if x.name in ['Status', 'Name', 'Author', 'Category', 'Game', 'Contents'] else x)

    size = repo_results_df.shape[0]
    if not size:
        await koduck.sendmessage(context["message"],
                                 sendcontent="I can't find anything with that query, sorry!")
    else:
        repo_results_df['Link'] = repo_results_df['Link'].explode().apply(lambda x: x[0])
        repo_result_row = repo_results_df.iloc[0]
    if size == 1:
        generated_msg = "**Found {} entry for _'{}'_..** \n" + \
                        "**_`{}`_** by __*{}*__:\n __<{}>__"
        return await koduck.sendmessage(context["message"],
                                    sendcontent=generated_msg.format(size, user_query, repo_result_row["Name"], repo_result_row["Author"], repo_result_row["Link"]))
    if size > 1:
        repo_results = "', '".join(repo_results_df["Name"])
        generated_msg = "**Found {} entries for _'{}'_..** \n" + \
                        "*'%s'*" % repo_results
        return await koduck.sendmessage(context["message"],
                                        sendcontent=generated_msg.format(size, user_query))

async def adventure(context, *args, **kwargs):
    cleaned_args = clean_args(args)
    if len(cleaned_args) < 1:
        cleaned_args.append("core")
    if cleaned_args[0] == 'help':
        adventure_help_msg = "I can generate an adventure for you! Specify `{cp}adventure` with the type of story you'd like!\n" + \
                             "*Core, Chaos*"
        return await koduck.sendmessage(context["message"], sendcontent=adventure_help_msg.replace("{cp}", settings.commandprefix))
    if len(cleaned_args) > 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="I can only generate one adventure at a time!")
    await adventure_master(context, cleaned_args)

async def adventure_master(context, args):
# -----------------------------------------------------------------------
# ADVENTURE HEADERS
    # The "Sort" column controls how the data is sorted between the option presets.
    # The "Definition" column controls the filtering rules for grammar correction.
    # All of the randomization is done initially for the Chaos preset.

    # The following sorting mechanisms have been removed until more options have been created for them.
    # Atmosphere, NPC last names, vulnerability header, some sort/definition rules that are needed in later iterations
# -----------------------------------------------------------------------
# Classification headers (for the type of adventure the generator sorts from)
# These three work together (Except core rulebook doesn't really care about ClassHeader, for now.)

    classdf_sub = adventure_df[adventure_df["Type"] == "ClassHeader"]
    row_num = random.randint(1, classdf_sub.shape[0]) - 1
    # sort_class = [classdf_sub.iloc[row_num]["Sort"]]
    class_header = [classdf_sub.iloc[row_num]["Result"]]

# Adventure headers
# Corresponds to the header table in the book. Extended for customization.

    advheaddf_sub = adventure_df[adventure_df["Type"] == "AdvHeader"]
    row_num = random.randint(1, advheaddf_sub.shape[0]) - 1
    sort_advheader = [advheaddf_sub.iloc[row_num]["Sort"]]
    define_advheader = [advheaddf_sub.iloc[row_num]["Definition"]]
    adv_header = [advheaddf_sub.iloc[row_num]["Result"]]

# Header results
# Corresponds to the results table in the book.

    headresultdf_sub = adventure_df[adventure_df["Type"] == "HeaderResult"]
    row_num = random.randint(1, headresultdf_sub.shape[0]) - 1
    sort_headresult = [headresultdf_sub.iloc[row_num]["Sort"]]
    define_headresult = [headresultdf_sub.iloc[row_num]["Definition"]]
    header_result = [headresultdf_sub.iloc[row_num]["Result"]]

# -----------------------------------------------------------------------
# Element generation. Just borrowed the element picker code for this.

    navi_element = 1
    navi_element = random.sample(range(element_df.shape[0]), navi_element)
    navi_element = [element_df.iloc[i]["element"] for i in navi_element]

# -----------------------------------------------------------------------
# Conflict generators. Headers for conflicts and vulnerabilities primarily exist for homebrew tables.

    conflictheaddf_sub = adventure_df[adventure_df["Type"] == "ConflictHeader"]
    row_num = random.randint(1, conflictheaddf_sub.shape[0]) - 1
    # sort_conflicthead = [conflictheaddf_sub.iloc[row_num]["Sort"]]
    # define_conflicthead = [conflictheaddf_sub.iloc[row_num]["Definition"]]
    conflict_header = [conflictheaddf_sub.iloc[row_num]["Result"]]

    conflictresultdf_sub = adventure_df[adventure_df["Type"] == "ConflictResult"]
    row_num = random.randint(1, conflictresultdf_sub.shape[0]) - 1
    sort_conflictresult = [conflictresultdf_sub.iloc[row_num]["Sort"]]
    # define_conflictresult = [conflictresultdf_sub.iloc[row_num]["Definition"]]
    conflict_result = [conflictresultdf_sub.iloc[row_num]["Result"]]

    vulnresdf_sub = adventure_df[adventure_df["Type"] == "VulnResult"]
    row_num = random.randint(1, vulnresdf_sub.shape[0]) - 1
    sort_vulnres = [vulnresdf_sub.iloc[row_num]["Sort"]]
    # define_vulnres = [vulnresdf_sub.iloc[row_num]["Definition"]]
    vuln_result = [vulnresdf_sub.iloc[row_num]["Result"]]

# -----------------------------------------------------------------------
# Extended generator tables.

    conflicttypedf_sub = adventure_df[adventure_df["Type"] == "ConflictType"]
    row_num = random.randint(1, conflicttypedf_sub.shape[0]) - 1
    conflict_type = [conflicttypedf_sub.iloc[row_num]["Result"]]

# -----------------------------------------------------------------------
# Generators for human beings.
# Although with the NBC you never know, it might be for ghosts instead.
# First name generator corresponds to the first names in the Core book. Last names are homebrew.
# Maybe to-do navi names too?

    npcfirstdf_sub = adventure_df[adventure_df["Type"] == "NPCFirstName"]
    row_num = random.randint(1, npcfirstdf_sub.shape[0]) - 1
    sort_npcfirst = [npcfirstdf_sub.iloc[row_num]["Sort"]]
    npc_firstname = [npcfirstdf_sub.iloc[row_num]["Result"]]

# -----------------------------------------------------------------------
# these use the same tables, just need individual results
    npcpersonalitydf_sub = adventure_df[adventure_df["Type"] == "Personality"]
    row_num = random.randint(1, npcpersonalitydf_sub.shape[0]) - 1
    sort_npcpersonality = [npcpersonalitydf_sub.iloc[row_num]["Sort"]]
    npc_personality = [npcpersonalitydf_sub.iloc[row_num]["Result"]]

    navipersonalitydf_sub = adventure_df[adventure_df["Type"] == "Personality"]
    row_num = random.randint(1, navipersonalitydf_sub.shape[0]) - 1
    navi_personality = [navipersonalitydf_sub.iloc[row_num]["Result"]]
# -----------------------------------------------------------------------

    npcoccupationdf_sub = adventure_df[adventure_df["Type"] == "Occupation"]
    row_num = random.randint(1, npcoccupationdf_sub.shape[0]) - 1
    sort_npcoccupation = [npcoccupationdf_sub.iloc[row_num]["Sort"]]
    npc_occupation = [npcoccupationdf_sub.iloc[row_num]["Result"]]

    npcfeaturedf_sub = adventure_df[adventure_df["Type"] == "Feature"]
    row_num = random.randint(1, npcfeaturedf_sub.shape[0]) - 1
    sort_npcfeature = [npcfeaturedf_sub.iloc[row_num]["Sort"]]
    npc_feature = [npcfeaturedf_sub.iloc[row_num]["Result"]]

    navihostilitydf_sub = adventure_df[adventure_df["Type"] == "NaviHostility"]
    row_num = random.randint(1, navihostilitydf_sub.shape[0]) - 1
    navi_hostility = [navihostilitydf_sub.iloc[row_num]["Result"]]

    if args[0] == 'core':
        while sort_advheader[0].lower() != 'core':
            row_num = random.randint(1, advheaddf_sub.shape[0]) - 1
            sort_advheader = [advheaddf_sub.iloc[row_num]["Sort"]]
            define_advheader = [advheaddf_sub.iloc[row_num]["Definition"]]
            adv_header = [advheaddf_sub.iloc[row_num]["Result"]]

        while sort_headresult[0].lower() != 'core' or define_headresult[0] != define_advheader[0]:
            row_num = random.randint(1, headresultdf_sub.shape[0]) - 1
            sort_headresult = [headresultdf_sub.iloc[row_num]["Sort"]]
            define_headresult = [headresultdf_sub.iloc[row_num]["Definition"]]
            header_result = [headresultdf_sub.iloc[row_num]["Result"]]

        while sort_conflictresult[0].lower() != 'core':
            row_num = random.randint(1, conflictresultdf_sub.shape[0]) - 1
            sort_conflictresult = [conflictresultdf_sub.iloc[row_num]["Sort"]]
            # define_conflictresult = [conflictresultdf_sub.iloc[row_num]["Definition"]]
            conflict_result = [conflictresultdf_sub.iloc[row_num]["Result"]]

        while sort_npcfirst[0].lower() != 'core':
            row_num = random.randint(1, npcfirstdf_sub.shape[0]) - 1
            sort_npcfirst = [npcfirstdf_sub.iloc[row_num]["Sort"]]
            npc_firstname = [npcfirstdf_sub.iloc[row_num]["Result"]]

        while sort_npcpersonality[0].lower() != 'core':
            row_num = random.randint(1, npcpersonalitydf_sub.shape[0]) - 1
            sort_npcpersonality = [npcpersonalitydf_sub.iloc[row_num]["Sort"]]
            npc_personality = [npcpersonalitydf_sub.iloc[row_num]["Result"]]

        while sort_npcoccupation[0].lower() != 'core':
            row_num = random.randint(1, npcoccupationdf_sub.shape[0]) - 1
            sort_npcoccupation = [npcoccupationdf_sub.iloc[row_num]["Sort"]]
            npc_occupation = [npcoccupationdf_sub.iloc[row_num]["Result"]]

        while sort_npcfeature[0].lower() != 'core':
            row_num = random.randint(1, npcfeaturedf_sub.shape[0]) - 1
            sort_npcfeature = [npcfeaturedf_sub.iloc[row_num]["Sort"]]
            npc_feature = [npcfeaturedf_sub.iloc[row_num]["Result"]]

        while sort_vulnres[0].lower() != 'core':
            row_num = random.randint(1, vulnresdf_sub.shape[0]) - 1
            sort_vulnres = [vulnresdf_sub.iloc[row_num]["Sort"]]
            # define_vulnres = [vulnresdf_sub.iloc[row_num]["Definition"]]
            vuln_result = [vulnresdf_sub.iloc[row_num]["Result"]]

        generated_msg = "The adventure starts with the kids {} {} " + \
                        "But an evildoer is there to {} Their name is **{}**, and they are {} {}, notable for {}. Their vulnerability is {}\n"
        return await koduck.sendmessage(context["message"],
                                        sendcontent=generated_msg.format(*adv_header, *header_result,
                                                                         *conflict_result, *npc_firstname,
                                                                         *npc_personality, *npc_occupation,
                                                                         *npc_feature, *vuln_result))
#   TODO:
#    if (args[0] == 'extended'):
    if args[0] == 'chaos':
        generated_msg = "The adventure starts with {} {} {} " + \
                        "But {} {} Their vulnerability is {}\n" + \
                        "**{}** is {} {}, notable for {}.\n" + \
                        "Next, {} meet {} navi with the element of {} that greets them with {}.\n" + \
                        "The primary conflict is {}"
        return await koduck.sendmessage(context["message"],
                                        sendcontent=generated_msg.format(*class_header, *adv_header, *header_result,
                                                                         *conflict_header, *conflict_result,
                                                                         *vuln_result,
                                                                         *npc_firstname, *npc_personality,
                                                                         *npc_occupation, *npc_feature, *class_header,
                                                                         *navi_personality, *navi_element, *navi_hostility, *conflict_type))
    else:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Please specify either Core or Chaos.")

async def fight(context, *args, **kwargs):
    cleaned_args = clean_args(args)

    skilldf_sub = fight_df[fight_df["Type"] == "Skill"]
    weapondf_sub = fight_df[fight_df["Type"] == "SecretWeapon"]
    weaknessdf_sub = fight_df[fight_df["Type"] == "Weakness"]
    arenadf_sub = fight_df[fight_df["Type"] == "Arena"]
    manifestdf_sub = fight_df[fight_df["Type"] == "ElementManifest"]
    navistartdf_sub = fight_df[fight_df["Type"] == "NaviStart"]
    troubledf_sub = fight_df[fight_df["Type"] == "TroubleType"]
    objectivedf_sub = fight_df[fight_df["Type"] == "FightObjective"]
    realassistdf_sub = fight_df[fight_df["Type"] == "RealWorldAssist"]

    # element
    navi_element = 1
    navi_element = random.sample(range(element_df.shape[0]), navi_element)
    navi_element = [element_df.iloc[i]["element"] for i in navi_element]
    # skills
    row_num = random.randint(1, skilldf_sub.shape[0]) - 1
    bestskill = [skilldf_sub.iloc[row_num]["Result"]]
    row_num = random.randint(1, skilldf_sub.shape[0]) - 1
    trainedskill = [skilldf_sub.iloc[row_num]["Result"]]
    # secret weapon
    row_num = random.randint(1, weapondf_sub.shape[0]) - 1
    secret_weapon = [weapondf_sub.iloc[row_num]["Result"]]
    # weakness
    row_num = random.randint(1, weaknessdf_sub.shape[0]) - 1
    weakness = [weaknessdf_sub.iloc[row_num]["Result"]]
    # arena
    row_num = random.randint(1, arenadf_sub.shape[0]) - 1
    arena = [arenadf_sub.iloc[row_num]["Result"]]
    # element manifest
    row_num = random.randint(1, manifestdf_sub.shape[0]) - 1
    element_manifest = [manifestdf_sub.iloc[row_num]["Result"]]
    # navi start
    row_num = random.randint(1, navistartdf_sub.shape[0]) - 1
    navi_start = [navistartdf_sub.iloc[row_num]["Result"]]
    # trouble type
    row_num = random.randint(1, troubledf_sub.shape[0]) - 1
    trouble_type = [troubledf_sub.iloc[row_num]["Result"]]
    # fight objective
    row_num = random.randint(1, objectivedf_sub.shape[0]) - 1
    fight_objective = [objectivedf_sub.iloc[row_num]["Result"]]
    # real world assist
    row_num = random.randint(1, realassistdf_sub.shape[0]) - 1
    real_world_assist = [realassistdf_sub.iloc[row_num]["Result"]]
    if (len(cleaned_args) < 1):
        generated_msg = "For this fight, this Navi has the element **{}**, and is proficient in **{}**. They are also trained in **{}**. " + \
                        "**{}**, but their weakness is **{}**.\n" + \
                        "The arena is **{}**, and the Navi's element manifests as **{}**. The Navi is **{}**!\n" + \
                        "{}, and the NetOps need to **{}**! However, in the real world, **{}** is there to help!"
        return await koduck.sendmessage(context["message"],
                                        sendcontent=generated_msg.format(*navi_element, *bestskill, *trainedskill,
                                                                         *secret_weapon, *weakness,
                                                                         *arena,
                                                                         *element_manifest, *navi_start,
                                                                         *trouble_type, *fight_objective, *real_world_assist))
    if cleaned_args[0] == 'help':
        fight_help_msg = "I can generate a Navi boss fight for you! Specify `{cp}fight` to generate one!"
        return await koduck.sendmessage(context["message"], sendcontent=fight_help_msg.replace("{cp}", settings.commandprefix))


async def sheet(context, *args, **kwargs):
    msg_txt = ("**Official NetBattlers Character Sheet:** <%s>\nFor player-made character sheets, search for sheets in the Player-Made Repository using `{cp}repo sheets`!" % settings.character_sheet).replace(
                                                        "{cp}", koduck.get_prefix(context["message"]))
    return await koduck.sendmessage(context["message"], sendcontent=msg_txt)


async def spotlight(context, *args, **kwargs):
    if context["message"].channel.type is discord.ChannelType.private:
        channel_id = context["message"].channel.id
        channel_name = context["message"].author.name
        msg_location = "%s (Direct messages)" % channel_name
    else:
        channel_id = context["message"].channel.id
        channel_name = context["message"].channel.name
        channel_server = context["message"].channel.guild
        msg_location = "#%s (%s)" % (channel_name, channel_server)

    cleaned_args = clean_args([" ".join(args)], lowercase=False) # begone, you hecking commas
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        help_msg = "Start up a **Spotlight Checklist** for this text channel with `{cp}spotlight start`! Add people right away with `{cp}spotlight start Lan/MegaMan Mayl/Roll Dex/GutsMan`.\n" + \
                   "Mark off people who've acted with `{cp}spotlight Lan`! The checklist will automatically refresh when everyone has acted!\n\n" + \
                   "**List of Commands:**\n" + \
                   "> `{cp}spotlight start`, `{cp}spotlight start Lan/MegaMan Mayl/Roll`: Start the checklist in this text channel. You can include names too, separated by spaces or commas!\n" + \
                   "> `{cp}spotlight Lan`: Mark off Lan/MegaMan off the checklist. Case insensitive. You don't need to type the full name!\n" + \
                   "> `{cp}spotlight add Yai/Glyde Chaud/ProtoMan`: Add a new person to the checklist. You can add multiple people at once!\n" + \
                   "> `{cp}spotlight remove Chaud`: Remove a person from the checklist. You can remove multiple people at once!\n" + \
                   "> `{cp}spotlight edit Yai Yai/Glide`: Update a person's name in the checklist. One at a time!\n" + \
                   "> `{cp}spotlight show`: Shows the current Spotlight Checklist.\n" + \
                   "> `{cp}spotlight reset`, `{cp}spotlight reset Lan`: Unmark the entire checklist, or unmark a specific player\n" + \
                   "> `{cp}spotlight end`: Ends the checklist. Will also automatically close after %d hours.\n" % (SPOTLIGHT_TIMEOUT.seconds/3600)
        return await koduck.sendmessage(context["message"],
                                        sendcontent=help_msg.replace("{cp}", koduck.get_prefix(context["message"])))
    if cleaned_args[0].lower() in ['rules', 'rule', 'book', 'rulebook']:
        ruling_msg = await find_value_in_table(context, help_df, "Command", "flow", suppress_notfound=True)
        if ruling_msg is None:
            return await koduck.sendmessage(context["message"],
                                            sendcontent="Couldn't find the rules for this command! (You should probably let the devs know...)")
        return await koduck.sendmessage(context["message"],
                                        sendcontent=ruling_msg["Response"].replace("{cp}", koduck.get_prefix(context["message"])))

    notification_msg = ""
    err_msg = ""
    if cleaned_args[0].lower() in ['start', 'begin', 'on']:
        if channel_id in spotlight_db:
            spotlight_db[channel_id]["Last Modified"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return await koduck.sendmessage(context["message"],
                                            sendembed=embed_spotlight_message("Spotlight Tracker already started in this channel!",
                                                                              msg_location, error=True))
        if (len(spotlight_db)+1) > MAX_SPOTLIGHTS:
            return await koduck.sendmessage(context["message"],
                                            sendcontent="Too many Spotlight Checklists are active in ProgBot right now! Please try again later.")
        if len(cleaned_args) > (MAX_CHECKLIST_SIZE + 1):
            return await koduck.sendmessage(context["message"],
                                            sendembed=embed_spotlight_message("Max of %d participants in a checklist!" %
                                                                              MAX_CHECKLIST_SIZE,
                                                                              msg_location, error=True))
        if len(cleaned_args) > 1:
            participants = {}
            dups = []
            i = 0
            name_list = pd.Series("", index=range(len(cleaned_args)-1))
            for arg in cleaned_args[1:]:
                if any(name_list.str.contains(arg, flags=re.IGNORECASE)):
                    dups.append(arg)
                else:
                    name_list.iloc[i] = arg
                    participants[arg] = False
                    i += 1
            if dups:
                err_msg = "(Note: %s are duplicates!)" % ", ".join(dups)
        else:
            participants = {}
        spotlight_db[channel_id] = participants
        spotlight_db[channel_id]["Last Modified"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        embed = embed_spotlight_tracker(spotlight_db[channel_id], msg_location, notification=err_msg)
        return await koduck.sendmessage(context["message"], sendembed=embed)

    if channel_id not in spotlight_db:
            return await koduck.sendmessage(context["message"],
                                            sendembed=embed_spotlight_message("Spotlight Tracker not yet started in this channel!",
                                                                              msg_location, error=True))

    spotlight_db[channel_id]["Last Modified"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if cleaned_args[0].lower() in ['close', 'shutdown', 'end']:
        del spotlight_db[channel_id]
        return await koduck.sendmessage(context["message"],
                                        sendembed=embed_spotlight_message("Shutting down this Spotlight Tracker! Goodnight!",
                                                                          msg_location))
    if cleaned_args[0].lower() == 'add':
        if len(cleaned_args) == 1:
            return await koduck.sendmessage(context["message"],
                                            sendembed=embed_spotlight_message("Please list who you want to add!",
                                                                              msg_location, error=True))
        if (len(spotlight_db[channel_id]) + len(cleaned_args) - 2) > MAX_CHECKLIST_SIZE:
            return await koduck.sendmessage(context["message"],
                                            sendembed=embed_spotlight_message("Max of %d participants in a checklist!" %
                                                                              MAX_CHECKLIST_SIZE,
                                                                              msg_location, error=True))
        dups = []
        n = len(cleaned_args)-1 # max number of new entries
        name_list = pd.Series(list(spotlight_db[channel_id].keys()) + ([""]*n))
        i = len(spotlight_db[channel_id]) # end of the array
        for arg in cleaned_args[1:]:
            if any(name_list.str.contains(arg, flags=re.IGNORECASE)):
                dups.append(arg)
            else:
                name_list.iloc[i] = arg
                spotlight_db[channel_id][arg] = False
                i += 1
            if dups:
                err_msg = "(%s already in the checklist!)" % ", ".join(dups)
    elif cleaned_args[0].lower() in ['reset', 'clear']:
        if len(cleaned_args) == 1 or cleaned_args[1] == "all":
            spotlight_db[channel_id] = {k:(False if k != "Last Modified" else v) for k, v in spotlight_db[channel_id].items()}
        for arg in cleaned_args[1:]:
            match_name = await find_spotlight_participant(arg, spotlight_db[channel_id], context, msg_location)
            if match_name is None:
                return
            spotlight_db[channel_id][match_name] = False
            continue
    elif cleaned_args[0].lower() in ['remove', 'delete', 'kick']:
        if len(cleaned_args) == 1:
            return await koduck.sendmessage(context["message"],
                                            sendembed=embed_spotlight_message("Please specify who you want to remove!",
                                                                              msg_location, error=True))
        for arg in cleaned_args[1:]:
            match_name = await find_spotlight_participant(arg, spotlight_db[channel_id], context, msg_location)
            if match_name is None:
                continue
            del spotlight_db[channel_id][match_name]
            continue
    elif cleaned_args[0].lower() in ['edit', 'change', 'update', 'rename']:
        if len(cleaned_args) != 3:
            return await koduck.sendmessage(context["message"],
                                            sendembed=embed_spotlight_message("Need just the original name and the new name to change it too!",
                                                                              msg_location, error=True))

        match_name = await find_spotlight_participant(cleaned_args[1], spotlight_db[channel_id], context, msg_location)
        if match_name is not None:
            spotlight_db[channel_id][cleaned_args[2]] = spotlight_db[channel_id].pop(match_name)
    elif cleaned_args[0].lower() not in ['show', "now", "display", "what"]:
        already_went_list = []
        for arg in cleaned_args:
            match_name = await find_spotlight_participant(arg, spotlight_db[channel_id], context, msg_location)
            if match_name is None:
                continue
            if spotlight_db[channel_id][match_name]:
                already_went_list.append(match_name)
            else:
                spotlight_db[channel_id][match_name] = True

        if len(spotlight_db[channel_id]) > 1: # not just last modified
            if all(spotlight_db[channel_id].values()):
                notification_msg = "Spotlight Reset!"
                spotlight_db[channel_id] = {k:(False if k != "Last Modified" else v) for k, v in spotlight_db[channel_id].items()}

            if already_went_list:
                err_msg = "(%s already went!)" % ", ".join(already_went_list)

    notify_str = "\n".join([i for i in (notification_msg, err_msg) if i])
    embed = embed_spotlight_tracker(spotlight_db[channel_id], msg_location, notification=notify_str)
    return await koduck.sendmessage(context["message"], sendembed=embed)

async def find_spotlight_participant(arg, participant_dict, msg_cnt, message_location):
    participant_list = pd.Series(participant_dict.keys())
    participant_list = participant_list[participant_list != "Last Modified"]
    match_candidates = participant_list[participant_list.str.contains(arg, flags=re.IGNORECASE)]
    if match_candidates.shape[0] == 0:
        await koduck.sendmessage(msg_cnt["message"],
                                 sendembed=embed_spotlight_message("Unable to find `%s` as a participant!" % arg,
                                                                   message_location, error=True))
        return None
    if match_candidates.shape[0] > 1:
        await koduck.sendmessage(msg_cnt["message"],
                                 sendembed=embed_spotlight_message("For `%s`, did you mean: %s?" % (arg, ", ".join(match_candidates.to_list())),
                                                                   message_location, error=True))
        return None
    return match_candidates.iloc[0]
def embed_spotlight_message(err_msg, location, error=False):
    if error:
        embed = discord.Embed(description=err_msg,
                              color=cj_colors["jeer"])
    else:
        embed = discord.Embed(description=err_msg,
                              color=cj_colors["cheer"])
    embed.set_footer(text=location)
    return embed
def embed_spotlight_tracker(dict_line, location, notification=""):
    participants = dict_line.copy()
    del participants["Last Modified"]
    if not participants:
        embed_descript = "*No participants in this channel yet!*"
    else:
        unused_emoji = ":black_large_square:"
        used_emoji = ":ballot_box_with_check:"
        embed_descript = "\n".join(["%s %s" % (used_emoji, participant) if pstatus else "%s %s" % (unused_emoji, participant) for
                          participant, pstatus in participants.items()])
    if notification:
        embed_descript = notification + "\n\n" + embed_descript
    embed = discord.Embed(title="__Spotlight Checklist__",
                          description=embed_descript,
                          color=cj_colors["cheer"])
    embed.set_footer(text=location)
    return embed


async def weather(context, *args, **kwargs):
    cleaned_args = clean_args(args)
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Pulls up info for 1-%d types of **CyberWeather**! I can also list all types of CyberWeather if you tell me `list` or `all`!" % MAX_WEATHER_QUERY)

    if len(cleaned_args) > MAX_WEATHER_QUERY:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Can't pull up more than %d types of CyberWeather!" % MAX_WEATHER_QUERY)

    if cleaned_args[0] in ["list", "all"]:
        _, result_title, result_msg = query_weather()
        return await send_query_msg(context, result_title, result_msg)
    elif cleaned_args[0] in ['rule', 'ruling', 'rules']:
        ruling_msg = await find_value_in_table(context, help_df, "Command", "weather",
                                               suppress_notfound=True)
        if ruling_msg is None:
            return await koduck.sendmessage(context["message"],
                                            sendcontent="Couldn't find the rules for this command! (You should probably let the devs know...)")
        return await koduck.sendmessage(context["message"],
                                        sendcontent=ruling_msg["Response"].replace("{cp}", koduck.get_prefix(context["message"])))

    for arg in cleaned_args:
        weather_info = await find_value_in_table(context, weather_df, "Name", arg, suppress_notfound=False)
        if weather_info is None:
            continue

        weather_name = weather_info["Name"]
        weather_description = weather_info["Description"]
        weather_type = weather_info["Category"]
        if weather_type == "Basic":
            weather_color = weather_color_dictionary["Blue"]
        elif weather_type == "Glitched":
            weather_color = weather_color_dictionary["Yellow"]
        else:
            weather_color = weather_color_dictionary["Red"]

        embed = discord.Embed(title="__{}__".format(weather_name),
                              color=weather_color)
        embed.add_field(name="**[{} CyberWeather]**".format(weather_type),
                        value="_{}_".format(weather_description))
        await koduck.sendmessage(context["message"], sendembed=embed)

    return


async def achievement(context, *args, **kwargs):
    if context["params"]:
        help_msg = context["paramline"].strip().lower() == "help"
    else:
        help_msg = True
    if help_msg:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Pulls up info for a NetBattlers Advance **Achievement**! I can also list all the Achievements if you tell me `list` or `all`!")

    arg = context["paramline"]
    cleaned_args = arg.lower()

    if cleaned_args in ["list", "all"]:
        achieve_groups = achievement_df.groupby(["Category"])
        return_msgs = ["**%s:**\n*%s*" % (name, ", ".join(achieve_group["Name"].values)) for name, achieve_group in achieve_groups
                       if name]
        return await koduck.sendmessage(context["message"], sendcontent="\n\n".join(return_msgs))

    match_candidates = achievement_df[achievement_df["Name"].str.contains(cleaned_args, flags=re.IGNORECASE)]
    if match_candidates.shape[0] < 1:
        return await koduck.sendmessage(context["message"], sendcontent="Didn't find any matches for `%s`!" % arg)
    if match_candidates.shape[0] > 1:
        return await koduck.sendmessage(context["message"], sendcontent="Found multiple matches for `%s`:\n*%s*" %
                                                                        (arg,
                                                                         ", ".join(match_candidates["Name"].to_list())))
    achievement_info = match_candidates.iloc[0]
    achievement_name = achievement_info["Name"]
    achievement_description = achievement_info["Description"]
    achievement_type = achievement_info["Category"]
    achievement_color = achievement_color_dictionary["Gold"]

    embed = discord.Embed(title="__{}__".format(achievement_name),
                          color=achievement_color)
    embed.add_field(name="**[{} Achievement]**".format(achievement_type),
                    value="_{}_".format(achievement_description))

    return await koduck.sendmessage(context["message"], sendembed=embed)

async def glossary(context, *args, **kwargs):
    if not context["params"]:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Use me to pull up a **Glossary** term in ProgBot! I can also try to search for a term if you know the first few letters!")
    arg = context["paramline"].strip()
    cleaned_arg = arg.lower()

    glossary_info = await find_value_in_table(context, glossary_df, "Name", cleaned_arg, suppress_notfound=True) # exact match

    if glossary_info is None: # fuzzier match
        match_candidates = glossary_df[glossary_df["Name"].str.contains("^" + cleaned_arg, flags=re.IGNORECASE)]

        if match_candidates.shape[0] < 1:
            return await koduck.sendmessage(context["message"], sendcontent="Didn't find any matches for `%s` in the glossary!" % arg)
        if match_candidates.shape[0] > 1:
            progbot_list = ["> **%s**: `{cp}%s`".replace("{cp}", koduck.get_prefix(context["message"])) % (nam, cmd)
                            for nam, cmd in zip(match_candidates['Name'], match_candidates['ProgBot Command'])]
            return await koduck.sendmessage(context["message"], sendcontent="Found multiple matches under `%s` in the glossary!\n%s" %
                                                                            (arg, "\n".join(progbot_list)))
        glossary_info = match_candidates.iloc[0]


    if glossary_info["ProgBot Function"] not in globals():
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Don't recognize the function `%s`! (You should probably let the devs know...)" % glossary_info["ProgBot Function"])

    await koduck.sendmessage(context["message"], sendcontent="Pulling up `%s%s`!" % (koduck.get_prefix(context["message"]), glossary_info['ProgBot Command']))
    progbot_func = globals()[glossary_info["ProgBot Function"]]
    return await progbot_func(context, glossary_info["ProgBot Argument"], "")

async def xcard(context, *args, **kwargs):
    return await koduck.sendmessage(context["message"],
                                    sendcontent=":x: **A participant has used an X-card.** Stop the scene and talk it out.")

async def ncard(context, *args, **kwargs):
    return await koduck.sendmessage(context["message"],
                                    sendcontent=":warning: **A participant has used an N-card.** Consider pausing to talk to your table about the direction of the scene to discuss adjustments.")

async def ocard(context, *args, **kwargs):
    return await koduck.sendmessage(context["message"],
                                    sendcontent=":white_check_mark: A participant has used an O-card. Keep going!")

async def luxton(context, *args, **kwargs):
    return await koduck.sendmessage(context["message"],
                                    sendcontent=":exclamation:**A participant would like to discuss a problem with the current content with the table.** Listen to their needs and wants, and consider giving them control over said content, then continue to play accomodating their requests.")

async def line(context, *args, **kwargs):
    return await koduck.sendmessage(context["message"],
                                    sendcontent=":octagonal_sign: **A participant has discovered a new Line.** You should pause to talk about it, and adjust things as necessary.")

async def veil(context, *args, **kwargs):
    return await koduck.sendmessage(context["message"],
                                    sendcontent=":cloud: **A participant has discovered a new Veil.** Consider toning down the detail in the current scene, and pause to talk to your table about it.")

async def opendoor(context, *args, **kwargs):
    return await koduck.sendmessage(context["message"],
                                    sendcontent=":door: **A participant needs to take a break, stop listening, or leave the game for safety reasons.**")

async def ffwd(context, *args, **kwargs):
    return await koduck.sendmessage(context["message"],
                                    sendcontent=":fast_forward: A participant would like to advance past the current scene.")

async def rewind(context, *args, **kwargs):
    return await koduck.sendmessage(context["message"],
                                    sendcontent=":rewind: A participant would like to rewind certain details of a scene.")

async def pause(context, *args, **kwargs):
    return await koduck.sendmessage(context["message"],
                                    sendcontent=":pause_button: A participant would like to take a break.")

async def resume(context, *args, **kwargs):
    return await koduck.sendmessage(context["message"],
                                    sendcontent=":arrow_forward: A participant is ready to resume play.")

async def fbf(context, *args, **kwargs):
    return await koduck.sendmessage(context["message"],
                                    sendcontent=":warning: A participant would like to take it slow during the oncoming scene. Continue as planned with caution.")

async def find_chip_ncp_power(context, *args, **kwargs):
    cleaned_args = clean_args([" ".join(args)])

    if not context["params"] or (cleaned_args[0] in ["help"]):
        return await koduck.sendmessage(context["message"],
                                        sendcontent="I can search through **Chips**, **Powers**, and **NCPs**! Give me 1-%d terms and I'll try to find them!" % MAX_CHIP_QUERY)

    if len(cleaned_args) > MAX_CHIP_QUERY:
        return await koduck.sendmessage(context["message"], sendcontent="Too many items, no more than 5!")

    for arg in cleaned_args:
        item_title, item_trimmed, item_description, item_color, item_footer = await chipfinder(context, arg, suppress_err_msg=True)

        if item_title is None:
            item_title, item_trimmed, item_description, item_color, item_footer = await power_ncp(context, arg, force_power=False,
                                                                                      ncp_only=False, suppress_err_msg=True)
            if item_title is None:
                item_title, item_trimmed, item_description, item_color, item_footer = await power_ncp(context, arg, force_power=False,
                                                                                         ncp_only=True, suppress_err_msg=True)
                if item_title is None:
                    await koduck.sendmessage(context["message"], sendcontent="Unable to find `%s`!" % arg)
                    continue
        embed = discord.Embed(
            title="__%s__" % item_title,
            color=item_color)
        embed.add_field(name="[%s]" % item_trimmed,
                        value="_%s_" % item_description)
        await koduck.sendmessage(context["message"], sendembed=embed)

    return


def setup():
    koduck.addcommand("updatecommands", updatecommands, "prefix", 3)


setup()
koduck.client.run(bot_token)  # to run locally, ask a dev for the .env file
