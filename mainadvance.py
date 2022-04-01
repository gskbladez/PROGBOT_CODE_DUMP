import discord
import requests
import random
import koduck
import settings
import pandas as pd
import re
import datetime
from maincommon import clean_args
from maincommon import send_query_msg
from maincommon import find_value_in_table
from maincommon import help_df
from maincommon import cc_color_dictionary
from maincommon import pmc_link
from random import randint

MAX_MOD_QUERY = 5
ROLL_COMMENT_CHAR = '#'
MAX_CHEER_JEER_ROLL = 5
MAX_CHEER_JEER_VALUE = 100
MAX_AUDIENCES = 100
AUDIENCE_TIMEOUT = datetime.timedelta(days=0, hours=1, seconds=0)
MAX_SPOTLIGHTS = 100
MAX_CHECKLIST_SIZE = 10
SPOTLIGHT_TIMEOUT = datetime.timedelta(days=0, hours=3, seconds=10)
MAX_WEATHER_QUERY = 6


pmc_daemon_df = pd.read_csv(settings.pmc_daemonfile, sep="\t").fillna('')

cj_colors = {"cheer": 0xffe657, "jeer": 0xff605d}
achievement_color_dictionary = {"Gold": 0xffe852}
weather_color_dictionary = {"Blue": 0x8ae2ff,
                            "Yellow": 0xffff5e,
                            "Red": 0xff524d}

daemon_df = pd.read_csv(settings.daemonfile, sep="\t").fillna('').dropna(subset=['Name'])
networkmod_df = pd.read_csv(settings.networkmodfile, sep="\t").fillna('')
crimsonnoise_df = pd.read_csv(settings.crimsonnoisefile, sep="\t").fillna('')
audience_df = pd.read_csv(settings.audienceparticipationfile, sep="\t").fillna('')

achievement_df = pd.read_csv(settings.achievementfile, sep="\t").fillna('')
achievement_df["Category"] = achievement_df["Category"].astype('category').cat.reorder_categories(["First Steps", "Admin Privileges", "Tricky Bits", "Smooth Operation", "Milestones"])
achievement_df = achievement_df.sort_values(["Category", "Name"])
adventure_df = pd.read_csv(settings.adventurefile, sep="\t").fillna('')
fight_df = pd.read_csv(settings.fightfile, sep="\t").fillna('')
weather_df = pd.read_csv(settings.weatherfile, sep="\t").fillna('')
glossary_df = pd.read_csv(settings.glossaryfile, sep="\t").fillna('')

pmc_daemon_df = pd.read_csv(settings.pmc_daemonfile, sep="\t").fillna('')
autoloot_df = pd.read_csv(settings.autolootfile, sep="\t").fillna('')

audience_data = {}
spotlight_db = {}

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

async def crimsonnoise(context, *args, **kwargs):
    cleaned_args = clean_args(args)
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await koduck.sendmessage(context["message"],
                                        sendcontent="I can roll **CrimsonNoise** for you! Specify `{cp}crimsonnoise common`, `{cp}crimsonnoise`, or `{cp}crimsonnoise rare`!".replace(
                                            "{cp}", koduck.get_prefix(context["message"])))

    arg = cleaned_args[0]
    crimsonnoise_type = crimsonnoise_df[crimsonnoise_df["MysteryData"].str.contains("^%s$" % re.escape(arg), flags=re.IGNORECASE)]

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

    match_candidates = achievement_df[achievement_df["Name"].str.contains(re.escape(cleaned_args), flags=re.IGNORECASE)]
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
                if any(name_list.str.contains(re.escape(arg), flags=re.IGNORECASE)):
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

    if cleaned_args[0].lower() in ['close', 'shutdown', 'end', 'stop', 'finish']:
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
            if any(name_list.str.contains(re.escape(arg), flags=re.IGNORECASE)):
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
    match_candidates = participant_list[participant_list.str.contains(re.escape(arg), flags=re.IGNORECASE)]
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
        #print(r.status_code, r.reason)
        #print("Response:", r.content)
        return await koduck.sendmessage(context["message"],
                                 sendcontent="Sorry, I got an unexpected response from Notion! Please try again later! (If this persists, let the devs know!)")

    # just leaving this here for the next time i need to work on this again..
    #parse = json.loads(r.content)
    #print(json.dumps(parse, indent=4, sort_keys=True))

    # iza helped me rewrite the overwhelming bulk of this.
    # she's amazing, she's wonderful, and if you're not thankful for her presence in mmg i'll bite your kneecaps off.
    repo_results_dict = {}
    blockmap = r.json()["recordMap"]
    if "block" not in blockmap:
        return await koduck.sendmessage(context["message"],
                                 sendcontent="I can't find anything with that query, sorry!")
    else:
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

# There are 7 major categories that need to be procedurally filled out.
# Cost, Guard, Category, Damage, Range, Tags, Effect
# Each condition has several sub conditions and tables that are met based on rolling the dice.
async def autoloot(context, *args, **kwargs):
    cleaned_args = clean_args(args)

    skill_sub = autoloot_df[autoloot_df["Type"] == "StatSkill"]
    category_sub = autoloot_df[autoloot_df["Type"] == "Category"]

    verb_sub = autoloot_df[autoloot_df["Type"] == "VerbTable"]
    noun_sub = autoloot_df[autoloot_df["Type"] == "NounTable"]
    adj_sub = autoloot_df[autoloot_df["Type"] == "AdjectiveTable"]

    guarddmg_sub = autoloot_df[autoloot_df["Type"] == "GuardTriggerDamage"]
    guardelement_sub = autoloot_df[autoloot_df["Type"] == "GuardTriggerElement"]
    guardhp_sub = autoloot_df[autoloot_df["Type"] == "GuardTriggerHP"]
    guardroll_sub = autoloot_df[autoloot_df["Type"] == "GuardTriggerRoll"]

    xdmg_chipdf_sub = autoloot_df[autoloot_df["Type"] == "XDamageChip"]
    xdmg_mathdf_sub = autoloot_df[autoloot_df["Type"] == "XDamageMath"]

    tagdf_sub = autoloot_df[autoloot_df["Type"] == "TagTable"]

    cndown_sub = autoloot_df[autoloot_df["Type"] == "ConditionalOwnership"]
    cndloc_sub = autoloot_df[autoloot_df["Type"] == "ConditionalLocation"]

    miscbday_sub = autoloot_df[autoloot_df["Type"] == "MiscBirthday"]
    miscdays_sub = autoloot_df[autoloot_df["Type"] == "MiscDays"]


# COST:
    cost_r = random.randint(1, 6)
    if cost_r == 1:
        cost_txt = ("Spend 1 BP: ")
    elif cost_r == 2:
        row_num = random.randint(1, skill_sub.shape[0]) - 1
        skill = [skill_sub.iloc[row_num]["Result"]]
        cost_txt = ("Spend 1 {}: ".format(*skill))
    elif cost_r == 3:
        cost_txt = ("Spend {} HP: ".format(random.randint(1, 6)))
    else:
        cost_txt = ("")
    cost_result = cost_txt
    # check length of cost_r on function fill

# GUARD:
    guard_r = random.randint(1, 6)
    guard_result = ""
    if guard_r not in range(1, 3):
        guard_result = ""
    else:
        triggertype_r = random.randint(1, 6)
        if triggertype_r in range(1, 4): # "Next Time You" condition range

            recursion_value = 1
            recursion_firsttime = True
            prefix_text = "Next time you "

            while recursion_value < 10:
                nty_r = random.randint(1, 6)
                if nty_r == 1:  # condition: damage
                    row_num = random.randint(1, guarddmg_sub.shape[0]) - 1
                    guarddmg = [guarddmg_sub.iloc[row_num]["Result"]]
                    guard_txt = ("{} damage,".format(*guarddmg))
                    break
                if nty_r == 2:  #condition: element
                    row_num = random.randint(1, guardelement_sub.shape[0]) - 1
                    guardelement = [guardelement_sub.iloc[row_num]["Result"]]
                    guard_txt = ("{} element,".format(*guardelement))
                    break
                if nty_r == 3:  # condition: health
                    row_num = random.randint(1, guardhp_sub.shape[0]) - 1
                    guardhp = [guardhp_sub.iloc[row_num]["Result"]]
                    guard_txt = ("{} HP,".format(*guardhp))
                    break
                if nty_r == 4:  # condition: rolls
                    row_num = random.randint(1, guardroll_sub.shape[0]) - 1
                    guardroll = [guardroll_sub.iloc[row_num]["Result"]]
                    guard_txt = "roll {} {} hits,".format(*guardroll, random.randint(1,6))
                    break
                if nty_r == 5:  # condition: verbs
                    row_num = random.randint(1, verb_sub.shape[0]) - 1
                    verb = [verb_sub.iloc[row_num]["Result"]]
                    guard_txt = ("{},".format(*verb))
                    break
                if nty_r == 6:
                    if recursion_firsttime:
                        recursion_value = 3
                        recursion_firsttime = False
                    else:
                        prefix_text = ("Next {} times you ".format(recursion_value))
                        recursion_value += 1
            guard_result = prefix_text + guard_txt
        if triggertype_r in range(4, 7): # "After" condition range
            after_r = random.randint(1, 6)
            if after_r in range(1, 3):
                guard_result = ("After {} minutes, ".format(random.randint(1,6)))
            elif after_r in range(3, 5):
                guard_result = ("After {} rolls, ".format(random.randint(1,6)))
            elif after_r == 5:
                guard_result = ("After you say {} words, ".format(random.randint(1,6)))
            elif after_r == 6:
                row_num = random.randint(1, verb_sub.shape[0]) - 1
                verb = [verb_sub.iloc[row_num]["Result"]]
                row_num = random.randint(1, noun_sub.shape[0]) - 1
                noun = [noun_sub.iloc[row_num]["Result"]]
                guard_result = ("After you {} {} {}s, ".format(*verb, random.randint(1,6), *noun))


# CATEGORY:
    row_num = random.randint(1, category_sub.shape[0]) - 1
    category = [category_sub.iloc[row_num]["Result"]]

    category_result = category[0]

    row_num = random.randint(1, adj_sub.shape[0]) - 1
    adj = [adj_sub.iloc[row_num]["Result"]]
    row_num = random.randint(1, noun_sub.shape[0]) - 1
    noun = [noun_sub.iloc[row_num]["Result"]]
    row_num = random.randint(1, verb_sub.shape[0]) - 1
    verb = [verb_sub.iloc[row_num]["Result"]]

    # category conditionals
    if category_result == 'Hazard':
        hazard_r = random.randint(1, 5)
        if hazard_r == 1:
            hazard_txt = ("Surfaces and objects Close to the target turn {}. ".format(*adj))
        elif hazard_r == 2:
            hazard_txt = ("Turns an object into {}. ".format(*noun))
        elif hazard_r == 3:
            hazard_txt = ("An {} {} pops out of a surface. ".format(*adj, *noun))
        elif hazard_r == 4:
            hazard_txt = ("Makes all {}s {}.".format(*noun, *verb))
        elif hazard_r == 5:
            hazard_txt = ("Disguise the target as a {}. ".format(*noun))
        elif hazard_r == 6:
            hazard_txt = ("All {} objects explode.".format(*adj))
        category_description = hazard_txt
    elif category_result == 'Summon':
        summon_r = random.randint(1, 6)
        if summon_r in range(1, 4):
            summon_txt = ("a {}".format(*noun))
        elif summon_r in range(4, 6):
            summon_txt = ("a {} {}".format(*adj, *noun))
        elif summon_r == 6:
            roll = random.randint(1, 6)
            summon_txt = ("{} {} {}".format(roll, *adj, *noun))
        category_description = ("Summons {}.".format(summon_txt))
    elif category_result == 'Rush':
        rush_r = random.randint(1, 6)

        if rush_r in range(1, 3):
            rush_txt = "Dash Close to the target!"
        elif rush_r in range(3, 5):
            rush_txt = "Fly through the air Close to the target!"
        elif rush_r == 5:
            rush_txt = "Dash a range band away from the target!"
        elif rush_r == 6:
            rush_txt = "Fly through the air a range band away from the target!"
        category_description = (rush_txt)
    else:
        category_description = ""

# DAMAGE:
    if category_result == 'Support':
        damage_result = ""
        xdamage_description = ""
    else:
        damagetype_r = random.randint(1, 6)
        isXdamage = False
        damagetype = None
        if damagetype_r in range(1, 5):
            damagetype = "single"
        if damagetype_r in range(5, 7):
            damagetype = "multi"

        if not damagetype:
            damage_result = ""
        elif damagetype == "single":
            damagesingle_r = random.randint(1, 6)
            if damagesingle_r == 1:
                damagesingle_txt = "0 Damage"
            elif damagesingle_r == 2:
                damagesingle_txt = "1 Damage"
            elif damagesingle_r == 3:
                damagesingle_txt = "2 Damage"
            elif damagesingle_r == 4:
                damagesingle_txt = "3 Damage"
            elif damagesingle_r == 5:  # big damage conditional
                damagebig_r = random.randint(1, 6)
                if damagebig_r in range(1, 4):
                    damagesingle_txt = "4 Damage"
                elif damagebig_r in range(4, 6):
                    damagesingle_txt = "5 Damage"
                elif damagebig_r == 6:
                    damagesingle_txt = "6 Damage"
            elif damagesingle_r == 6:
                damagesingle_txt = "X Damage"
                isXdamage = True
            damage_result = (damagesingle_txt)

        elif damagetype == "multi":
            damagemulti_base_r = random.randint(1, 6)
            damagemulti_count_r = random.randint(1, 6)
            base_damage = ""
            hit_count = ""

            if damagemulti_base_r == 1:
                base_damage = "0"
            elif damagemulti_base_r in range(2, 4):
                base_damage = "1"
            elif damagemulti_base_r in range(4, 6):
                base_damage = "2"
            elif damagemulti_base_r == 6:
                damagebig_r = random.randint(1, 6)
                if damagebig_r in range(1, 5):
                    base_damage = "3"
                if damagebig_r == 5:
                    base_damage = "4"
                if damagebig_r == 6:
                    base_damage = "X"
                    isXdamage = True

            if damagemulti_count_r in range(1, 4):
                hit_count = "x2"
            elif damagemulti_count_r == 4:
                hit_count = "x3"
            elif damagemulti_count_r == 5:
                hit_count = "x4"
            elif damagemulti_count_r == 6:
                hit_count = "x5"
            damage_result = ("{}{} Damage".format(*base_damage, hit_count))

        if not isXdamage:
            xdamage_txt = ""
        else:
            xdamage_r = random.randint(1, 6)
            if xdamage_r == 1:
                row_num = random.randint(1, skill_sub.shape[0]) - 1
                skill = [skill_sub.iloc[row_num]["Result"]]
                ownership_r = random.randint(1, 2)
                ownership = ""
                if ownership_r == 1:
                    ownership = "Your"
                if ownership_r == 2:
                    ownership = "The target's"
                xdamage_txt = ("X = {} {}.".format(ownership, *skill))
            if xdamage_r == 2:
                row_num = random.randint(1, xdmg_chipdf_sub.shape[0]) - 1
                xdamagechip = [xdmg_chipdf_sub.iloc[row_num]["Result"]]
                xdamage_txt = ("X = {} chips in your Folder.".format(*xdamagechip))
            if xdamage_r == 3:  # whyyyyyy
                hardcode_bullshit_r = randint(1, 5)
                bullshit = ""
                if hardcode_bullshit_r == 1:
                    bullshit = "are Close"
                if hardcode_bullshit_r == 2:
                    bullshit = "are Near"
                if hardcode_bullshit_r == 3:
                    bullshit = ("have {}ed you since jack-in".format(*verb))
                if hardcode_bullshit_r == 4:
                    bullshit = ("you {}ed since jack-in".format(*verb))
                if hardcode_bullshit_r == 5:
                    bullshit = ("are {}ing".format(*verb))

                xdamage_txt = ("X = Number of {} that {}, max {}.".format(*noun, bullshit, random.randint(1, 6)))
            if xdamage_r == 4:
                hardcode_bullshit_r = randint(1, 5)
                bullshit = ""
                if hardcode_bullshit_r == 1:
                    bullshit = "HP"
                if hardcode_bullshit_r == 2:
                    row_num = random.randint(1, skill_sub.shape[0]) - 1
                    skill = [skill_sub.iloc[row_num]["Result"]]
                    bullshit = "{}".format(*skill)
                if hardcode_bullshit_r == 3:
                    bullshit = "unused chips"
                if hardcode_bullshit_r == 4:
                    bullshit = "BP"
                if hardcode_bullshit_r == 5:
                    bullshit = "Max HP"

                xdamage_txt = ("Sacrifice up to {} {} to add to X.".format(random.randint(1, 6), bullshit))
            if xdamage_r == 5:
                hardcode_bullshit_r = randint(1, 3)
                bullshit = ""
                if hardcode_bullshit_r == 1:
                    row_num = random.randint(1, skill_sub.shape[0]) - 1
                    skill = [skill_sub.iloc[row_num]["Result"]]
                    bullshit = "{}".format(*skill)
                if hardcode_bullshit_r == 2:
                    bullshit = "HP"
                if hardcode_bullshit_r == 3:
                    bullshit = "BP"
                xdamage_txt = ("Add 1 to X for each {} reduction.".format(bullshit))
            if xdamage_r == 6:
                row_num = random.randint(1, xdmg_mathdf_sub.shape[0]) - 1
                xmath = [xdmg_mathdf_sub.iloc[row_num]["Result"]]
                xdamage_txt = ("Roll {}d{}, take the {}.".format(random.randint(1, 6), random.randint(1, 6), *xmath))

        xdamage_description = xdamage_txt

# RANGE:
    range_r = random.randint(1, 6)
    if range_r in range(1, 4):
        range_description = "Close"
    if range_r in range(4, 6):
        range_description = "Near"
    if range_r == 6:
        range_description = "Far"
# TAG:
    tagnumber_r = random.randint(1, 6)
    if tagnumber_r == 1:
        tagnumber = 0
        tag_result = ("")
    if tagnumber_r in range(2, 4):
        tagnumber = 1
    if tagnumber_r == 4:
        tagnumber = 2
    if tagnumber_r == 5:
        tagnumber = 3
    if tagnumber_r == 6:
        tagnumber = 4

    if tagnumber > 0:
        decide_bonus = random.randint(1, 6)
        taglist = []
        if decide_bonus == 6:
            bonustable_r = random.randint(1, 6)
            if bonustable_r in range(1, 5):
                tagnumber += 2
            else:
                tagnumber += 1
                taglist += ["Simple"]
        while len(taglist) < tagnumber:
            row_num = random.randint(1, tagdf_sub.shape[0]) - 1
            tag_r = tagdf_sub.iloc[row_num]["Result"]
            taglist += [tag_r]
        if guard_result:
            taglist.append("Guard")
        tag_result = ", ".join(taglist)

# EFFECT: Condition
    condition_r = random.randint(1, 6)
    condition_txt = ""
    if condition_r in range (1, 5):
        condition_combined = ""
    if condition_r in range (5, 7):
        conditiontable_r = random.randint(1, 6)
        if conditiontable_r == 1: # target condition table
            target_r = random.randint(1, 6)
            if target_r == 1:
                row_num = random.randint(1, adj_sub.shape[0]) - 1
                adj = [adj_sub.iloc[row_num]["Result"]]
                r = random.randint(1, 2)
                if r == 1:
                    condition_txt = ("is {},".format(*adj))
                if r == 2:
                    condition_txt = ("is not {},".format(*adj))
            if target_r == 2:
                r = random.randint(1, 2)
                if r == 1:
                    condition_txt = ("is deleted by this attack,")
                if r == 2:
                    condition_txt = ("is not deleted by this attack,")
            if target_r == 3:
                r = random.randint(1, 4)
                if r == 1:
                    row_num = random.randint(1, noun_sub.shape[0]) - 1
                    noun = [noun_sub.iloc[row_num]["Result"]]
                    condition_txt = ("is a {},".format(*noun))
                if r == 2:
                    row_num = random.randint(1, noun_sub.shape[0]) - 1
                    noun = [noun_sub.iloc[row_num]["Result"]]
                    condition_txt = ("is not a {},".format(*noun))
                if r == 3:
                    row_num = random.randint(1, noun_sub.shape[0]) - 1
                    noun = [noun_sub.iloc[row_num]["Result"]]
                    condition_txt = ("has a {},".format(*noun))
                if r == 4:
                    row_num = random.randint(1, noun_sub.shape[0]) - 1
                    noun = [noun_sub.iloc[row_num]["Result"]]
                    condition_txt = ("does not have a {},".format(*noun))
            if target_r == 4:
                r = random.randint(1, 2)
                row_num = random.randint(1, skill_sub.shape[0]) - 1
                skill = [skill_sub.iloc[row_num]["Result"]]
                if r == 1:
                    condition_txt = ("failed a {} roll recently,".format(*skill))
                if r == 2:
                    condition_txt = ("succeeded a {} roll recently,".format(*skill))
            if target_r == 5:
                r = random.randint (1, 6)
                row_num = random.randint(1, verb_sub.shape[0]) - 1
                verb = [verb_sub.iloc[row_num]["Result"]]
                if r == 1:
                    condition_txt = ("has {}ed in the past {} scenes,".format(*verb, random.randint(1, 6)))
                if r == 2:
                    condition_txt = ("has {}ed in the past {} seconds,".format(*verb, random.randint(1, 6)))
                if r == 3:
                    condition_txt = ("has {}ed in the past {} minutes,".format(*verb, random.randint(1, 6)))
                if r == 4:
                    condition_txt = ("has {}ed in the past {} hours,".format(*verb, random.randint(1, 6)))
                if r == 5:
                    condition_txt = ("has {}ed in the past {} days,".format(*verb, random.randint(1, 6)))
                if r == 6:
                    condition_txt = ("has {}ed in the past {} years,".format(*verb, random.randint(1, 6)))
            if target_r == 6:
                row_num = random.randint(1, adj_sub.shape[0]) - 1
                adj = [adj_sub.iloc[row_num]["Result"]]
                condition_txt = ("is more {} than you.".format(*adj))
            condition_combined = ("If the target {} ".format(condition_txt))
        if conditiontable_r == 2: # user condition table
            user_r = random.randint(1, 6)
            if user_r == 1:
                r = random.randint(1, 3)
                if r == 1:
                    condition_txt = ("are at {} HP,".format(random.randint(1, 6)))
                if r == 2:
                    condition_txt = ("are below {} HP,".format(random.randint(1, 6)))
                if r == 3:
                    condition_txt = ("are above {} HP,".format(random.randint(1, 6)))
            if user_r == 2:
                row_num = random.randint(1, noun_sub.shape[0]) - 1
                noun = [noun_sub.iloc[row_num]["Result"]]
                r = random.randint(1, 4)
                if r == 1:
                    condition_txt = ("are a {},".format(*noun))
                if r == 2:
                    condition_txt = ("are not a {},".format(*noun))
                if r == 3:
                    condition_txt = ("have a {},".format(*noun))
                if r == 4:
                    condition_txt = ("do not have a {},".format(*noun))
            if user_r == 3:
                r = random.randint(1, 2)
                row_num = random.randint(1, adj_sub.shape[0]) - 1
                adj = [adj_sub.iloc[row_num]["Result"]]
                if r == 1:
                    condition_txt = ("are {},".format(*adj))
                if r == 2:
                    condition_txt = ("are not {}".format(*adj))
            if user_r == 4:
                r = random.randint(1, 2)
                if r == 1:
                    condition_txt = "are deleted by this attack,"
                if r == 2:
                    condition_txt = "are not deleted by this attack,"
            if user_r == 5:
                r = random.randint (1, 6)
                row_num = random.randint(1, verb_sub.shape[0]) - 1
                verb = [verb_sub.iloc[row_num]["Result"]]
                if r == 1:
                    condition_txt = ("has {}ed in the past {} scenes,".format(*verb, random.randint(1, 6)))
                if r == 2:
                    condition_txt = ("has {}ed in the past {} seconds,".format(*verb, random.randint(1, 6)))
                if r == 3:
                    condition_txt = ("has {}ed in the past {} minutes,".format(*verb, random.randint(1, 6)))
                if r == 4:
                    condition_txt = ("has {}ed in the past {} hours,".format(*verb, random.randint(1, 6)))
                if r == 5:
                    condition_txt = ("has {}ed in the past {} days,".format(*verb, random.randint(1, 6)))
                if r == 6:
                    condition_txt = ("has {}ed in the past {} years,".format(*verb, random.randint(1, 6)))
            if user_r == 6:
                r = random.randint(1, 2)
                if r == 1:
                    condition_txt = ("stand still and don't move,")
                if r == 2:
                    condition_txt = ("are moving,")
            condition_combined = ("If you {} ".format(condition_txt))
        if conditiontable_r == 3 :  # damage condition table
            damage_r = random.randint(1, 6)
            if damage_r == 1:
                condition_txt = ("this deals {} damage,".format(random.randint(1, 6)))
            if damage_r == 2:
                r = random.randint(1, 2)
                if r == 1:
                    condition_txt = "you win a parry with this,"
                if r == 2:
                    condition_txt = "you lose a parry with this,"
            if damage_r == 3:
                row_num = random.randint(1, skill_sub.shape[0]) - 1
                skill = [skill_sub.iloc[row_num]["Result"]]
                condition_txt = ("the target successfully defends with {},".format(*skill))
            if damage_r == 4:
                condition_txt = "this hits the target,"
            if damage_r == 5: # i have basically forgotten that the spreadsheet existed at this point but i don't have time
                r = random.randint(1, 6)
                if r == 1:
                    condition_txt = "this is your first attack on the target,"
                if r == 2:
                    condition_txt = "this is your second attack on the target,"
                if r == 3:
                    condition_txt = "this is your third attack on the target,"
                if r == 4:
                    condition_txt = "this is your fourth attack on the target,"
                if r == 5:
                    condition_txt = "this is your fifth attack on the target,"
                if r == 6:
                    condition_txt = "this is your tenth attack on the target,"
            if damage_r == 6:
                condition_txt = ("this deals less than {} damage,".format(random.randint(1, 6)))

            condition_combined = ("If {} ".format(condition_txt))
        if conditiontable_r == 4: # environment condition table
            env_r = randint(1, 6)
            if env_r == 1:
                r = random.randint(1, 4)
                sub_r = random.randint(1, 2)
                row_num = random.randint(1, noun_sub.shape[0]) - 1
                noun = [noun_sub.iloc[row_num]["Result"]]
                row_num = random.randint(1, adj_sub.shape[0]) - 1
                adj = [adj_sub.iloc[row_num]["Result"]]
                if r == 1:
                    if sub_r == 1:
                        condition_txt = ("you are a range band above a {},".format(*noun))
                    if sub_r == 2:
                        condition_txt = ("you are a range band above something {},".format(*adj))
                if r == 2:
                    if sub_r == 1:
                        condition_txt = ("you are a range band below a {},".format(*noun))
                    if sub_r == 2:
                        condition_txt = ("you are a range band below something {},".format(*adj))
                if r == 3:
                    if sub_r == 1:
                        condition_txt = ("you are a range band away from a {},".format(*noun))
                    if sub_r == 2:
                        condition_txt = ("you are a range band away from something {},".format(*adj))
            if env_r == 2:
                row_num = random.randint(1, noun_sub.shape[0]) - 1
                noun = [noun_sub.iloc[row_num]["Result"]]
                condition_txt = ("this damages a {},".format(*noun))
            if env_r == 3:
                condition_txt = "this destroys an object,"
            if env_r == 4:
                condition_txt = "the target is an object,"
            if env_r == 5:
                condition_txt = "the target just destroyed an object,"
            if env_r == 6:
                condition_txt = "everything around you is really messed up - I mean like, straight-up irrevocably busted, the kind of thing that makes you feel bad for whoever’s gotta foot the bill to get everything put back together (and don’t forget the poor sap that has to clean it all up! jeez),"

            condition_combined = ("If {} ".format(condition_txt))
        if conditiontable_r == 5: # element condition table
            element_r = random.randint(1, 6)

            row_num = random.randint(1, cndown_sub.shape[0]) - 1
            cnd_ownership = [cndown_sub.iloc[row_num]["Result"]]
            row_num = random.randint(1, cndloc_sub.shape[0]) - 1
            cnd_location = [cndloc_sub.iloc[row_num]["Result"]]
            if element_r == 1:
                condition_txt = ("you are {} {} element, ".format(*cnd_location, *cnd_ownership))
            if element_r == 2:
                condition_txt = ("{} element is not present,".format(*cnd_ownership))
            if element_r == 3:
                r = random.randint(1, 2)
                sub_r = random.randint(1, 2)
                row_num = random.randint(1, noun_sub.shape[0]) - 1
                noun = [noun_sub.iloc[row_num]["Result"]]
                row_num = random.randint(1, adj_sub.shape[0]) - 1
                adj = [adj_sub.iloc[row_num]["Result"]]
                if r == 1:
                    if sub_r == 1:
                        condition_txt = ("your element is {},".format(*noun))
                    if sub_r == 2:
                        condition_txt = ("your element is {},".format(*adj))
                if r == 2:
                    if sub_r == 1:
                        condition_txt = ("your element is not {},".format(*noun))
                    if sub_r == 2:
                        condition_txt = ("your element is not {},".format(*adj))
            if element_r == 4:
                condition_txt = ("you have {} elements available,".format(random.randint(1, 6)))
            if element_r == 5:
                r = random.randint(1, 3)
                sum = random.randint(1, 6) + random.randint(1, 6)
                if r == 1:
                    condition_txt = ("your element is over {} letters long,".format(sum))
                if r == 2:
                    condition_txt = ("your element is under {} letters long,".format(sum))
                if r == 3:
                    condition_txt = ("your element is exactly {} letters long,".format(sum))
            if element_r == 6:
                condition_txt = "your element is kind of a pain in the butt for the GM,"
            condition_combined = ("If {} ".format(condition_txt))
        if conditiontable_r == 6: # misc condition table
            misc_r = random.randint(1, 6)
            if misc_r == 1:
                row_num = random.randint(1, miscbday_sub.shape[0]) - 1
                misc_bday = [miscbday_sub.iloc[row_num]["Result"]]
                condition_txt = ("it's {} birthday,".format(*misc_bday))
            if misc_r == 2:
                row_num = random.randint(1, adj_sub.shape[0]) - 1
                adj = [adj_sub.iloc[row_num]["Result"]]
                condition_txt = ("the vibes are {},".format(*adj))
            if misc_r == 3:
                condition_txt = ("you correctly predict how much damage this will deal at least {} in advance,".format(random.randint(1, 6)))
            if misc_r == 4:
                row_num = random.randint(1, noun_sub.shape[0]) - 1
                noun = [noun_sub.iloc[row_num]["Result"]]
                condition_txt = ("you can tell a funny joke about a {},".format(*noun))
            if misc_r == 5:
                row_num = random.randint(1, miscdays_sub.shape[0]) - 1
                misc_days = [miscdays_sub.iloc[row_num]["Result"]]
                condition_txt = ("it is {},".format(*misc_days))
            if misc_r == 6:
                condition_txt = "everyone at the table agrees,"
            condition_combined = ("If {} ".format(condition_txt))

# EFFECT: Subject
    subject_r = random.randint(1, 6)
    actionHasSubject = False
    if subject_r in range(1, 4):
        actionHasSubject = False
    if subject_r == 4:
        subject = "The user"
        actionHasSubject = True
    if subject_r == 5:
        subject = "Targets"
        actionHasSubject = True
    if subject_r == 6:
        r = random.randint(1, 6)
        if r == 1:
            row_num = random.randint(1, noun_sub.shape[0]) - 1
            noun = [noun_sub.iloc[row_num]["Result"]]
            subject = ("All {} in range".format(*noun))
        if r == 2:
            sub_r = random.randint(1, 2)
            if sub_r == 1:
                subject = ("The target's PET")
            if sub_r == 2:
                subject = ("The user's PET")
        if r == 3:
            subject = "The user and the targets"
        if r == 4:
            subject = "Everything in range"
        if r == 5:
            sub_r = random.randint(1, 2)
            if sub_r == 1:
                subject = ("{} targets of your choice".format(random.randint(1, 6)))
            if sub_r == 2:
                subject = ("{} targets of GM's choice".format(random.randint(1, 6)))
        if r == 6:
            subject = "The server"

#EFFECT: Modal
    isModal = False
    modal_prefix = ""
    modalCheck = random.randint(1, 6)
    if modalCheck in range(1, 5):
        isModal = False
        modalDegree = 1
    if modalCheck in range(5, 7):
        isModal = True
        modal_r = random.randint(1, 6)
        modalDegree = 0
        if modal_r in range(1, 3):
            modal_prefix = "Pick 1: "
            modalDegree = 2
        if modal_r in range(3, 5):
            modal_prefix = "Pick 1: "
            modalDegree = 3
        if modal_r == 5:
            modal_prefix = "Pick 2: "
            modalDegree = 3
        if modal_r == 6:
            r = random.randint(1, 6)
            if r in range(1, 4):
                modal_prefix = "Pick 1: "
                modalDegree = 1 + random.randint(1, 6)
            if r in range(4, 7):
                modal_prefix = ("Pick {}: ".format(random.randint(1, 6)))
                modalDegree = random.randint(1, 6)

# ACTION: Duration
    duration_r = random.randint(1, 6)
    if duration_r == 1:
        duration = "for a moment"
    if duration_r == 2:
        type = ["seconds", "rolls", "minutes"]
        duration = ("for 1d6 {}".format(random.choice(type)))
    if duration_r == 3:
        type = ["minutes", "hours", "sessions", "days"]
        duration = ("for 1d6 out-of-game {}".format(random.choice(type)))
    if duration_r == 4:
        duration = "until jack-out"
    if duration_r == 5:
        duration = "as long as you can convince the GM it should last for"
    if duration_r == 6:
        duration = "forever, even after jack-out"
# ACTION: Effect table
    if isModal:
        action_list = [modal_prefix]
    else:
        action_list = []

    numberOfEffects = 0
    while numberOfEffects < modalDegree:
        #action - subject table
        action_text = ""
        if actionHasSubject:
            r = random.randint(1, 36)
            #action_text = ""
            if r == 1:
                action_text = ("Pushes {} back a range band.".format(subject.lower()))
            if r == 2:
                action_text = ("Stuns {} for {}.".format(subject, duration.lower()))
            if r == 3:
                row_num = random.randint(1, skill_sub.shape[0]) - 1
                skill = [skill_sub.iloc[row_num]["Result"]]
                action_text = ("Upshifts {}'s next {} {} rolls.".format(subject.lower(), random.randint(1, 6), *skill))
            if r == 4:
                row_num = random.randint(1, noun_sub.shape[0]) - 1
                noun = [noun_sub.iloc[row_num]["Result"]]
                action_text = ("Covers {} in {}s for {}.".format(subject.lower(), *noun, duration))
            if r == 5:
                action_text = ("Disables {}'s element for {}.".format(subject.lower(), duration))
            if r == 6:
                action_text = ("{} loses {} HP.".format(subject, random.randint(1, 6)))
            if r == 7:
                row_num = random.randint(1, adj_sub.shape[0]) - 1
                adj = [adj_sub.iloc[row_num]["Result"]]
                action_text = ("{} can now freely move through {} objects.".format(subject, *adj))
            if r == 8:
                row_num = random.randint(1, verb_sub.shape[0]) - 1
                verb = [verb_sub.iloc[row_num]["Result"]]
                row_num = random.randint(1, noun_sub.shape[0]) - 1
                noun = [noun_sub.iloc[row_num]["Result"]]
                action_text = ("{} can {} any {} {}.".format(subject, *verb, *noun, duration))
            if r == 9:
                row_num = random.randint(1, noun_sub.shape[0]) - 1
                noun = [noun_sub.iloc[row_num]["Result"]]
                action_text = ("Turns {} into a {} {}.".format(subject.lower(), *noun, duration))
            if r == 10:
                row_num = random.randint(1, adj_sub.shape[0]) - 1
                adj = [adj_sub.iloc[row_num]["Result"]]
                action_text = ("Makes {} {} {}.".format(subject.lower(), *adj, duration))
            if r == 11:
                row_num = random.randint(1, skill_sub.shape[0]) - 1
                skill = [skill_sub.iloc[row_num]["Result"]]
                action_text = ("{} gets a +{} dice to their next {} roll.".format(subject, random.randint(1, 6), *skill))
            if r == 12:
                action_text = ("Heals {} {} HP.".format(subject.lower(), random.randint(1, 6)))
            if r == 13:
                row_num = random.randint(1, noun_sub.shape[0]) - 1
                noun = [noun_sub.iloc[row_num]["Result"]]
                action_text = ("{} gains the element {} {}.".format(subject, *noun, duration))
            if r == 14:
                emotions = ["positive", "negative", "confusing"]
                action_text = ("Overwhelms {} with {} emotions {}.".format(subject.lower(), random.choice(emotions), duration))
            if r == 15:
                action_text = ("{} starts doing an elaborate dance routine.".format(subject))
            if r == 16:
                row_num = random.randint(1, skill_sub.shape[0]) - 1
                skill = [skill_sub.iloc[row_num]["Result"]]
                action_text = ("You can roll {} on {} as if you were Close.".format(*skill, subject.lower()))
            if r == 17:
                action_text = ("Creates a group DM between the user and {}.".format(subject.lower()))
            if r == 18:
                action_text = ("Jam {}'s PET for {}.".format(subject.lower(), duration))
            if r == 19:
                row_num = random.randint(1, adj_sub.shape[0]) - 1
                adj = [adj_sub.iloc[row_num]["Result"]]
                action_text = ("Rates {} 1-10 based on how {} they are.".format(subject.lower(), *adj))
            if r == 20:
                action_text = ("Launches {} a range band skyward.".format(subject.lower()))
            if r == 21:
                action_text = ("Forces {} to jack out.".format(subject.lower()))
            if r == 22:
                row_num = random.randint(1, adj_sub.shape[0]) - 1
                adj = [adj_sub.iloc[row_num]["Result"]]
                row_num = random.randint(1, noun_sub.shape[0]) - 1
                noun = [noun_sub.iloc[row_num]["Result"]]
                action_text = ("If {} is touch a {} surface, they are attacked by {}s.".format(subject.lower(), *adj, *noun))
            if r == 23:
                action_text = ("{} can refresh a chip in their folder.".format(subject))
            if r == 24:
                action_text = ("Reveals an image of {}'s true love.".format(subject.lower()))
            if r == 25:
                action_text = ("This cannot delete {}.".format(subject.lower()))
            if r == 26:
                row_num = random.randint(1, verb_sub.shape[0]) - 1
                verb = [verb_sub.iloc[row_num]["Result"]]
                action_text = ("Makes {} {} you if {} is Inanimate.".format(subject.lower(), *verb, subject))
            if r == 27:
                action_text = ("Does the exact opposite of the last chip {} used.".format(subject))
            if r == 28:
                action_text = ("Takes a photo of {}.".format(subject))
            if r == 29:
                zenny = random.randint(1, 6) + random.randint(1, 6) + random.randint(1, 6) * 100
                action_text = ("{} loses {} Zenny.".format(subject.lower(), zenny))
            if r == 30:
                action_text = ("Anyone can ask {} {} questions and receive an honest answer.".format(subject.lower(), random.randint(1, 6)))
            if r == 31:
                action_text = ("{}'s PET catches on fire.".format(subject))
            if r == 32:
                row_num = random.randint(1, adj_sub.shape[0]) - 1
                adj = [adj_sub.iloc[row_num]["Result"]]
                action_text = ("Sends a message of {}'s choice to the entire server announced by a {} noise.".format(subject.lower(), *adj))
            if r == 33:
                action_text = ("Swap places with {}.".format(subject.lower()))
            if r == 34:
                action_text = ("Next time {} would fail a roll, they can reroll.".format(subject.lower()))
            if r == 35:
                action_text = ("{} gets a fashion makeover.".format(subject))
            if r == 36:
                action_text = ("Sends an invite to {} to support their favorite indie game developer.".format(subject.lower()))

                # action - no subject table
        else:  # not actionHasSubject:
            r = random.randint(1, 36)
            if r == 1:
                action_text = ("Deals +{} damage.".format(random.randint(1, 6)))
            if r == 2:
                action_text = "Deals double damage."
            if r == 3:
                row_num = random.randint(1, noun_sub.shape[0]) - 1
                noun = [noun_sub.iloc[row_num]["Result"]]
                action_text = ("Vaporizes any {}s.".format(*noun))
            if r == 4:
                action_text = "Screams." # same
            if r == 5:
                row_num = random.randint(1, adj_sub.shape[0]) - 1
                adj = [adj_sub.iloc[row_num]["Result"]]
                action_text = ("Opens a wormhole to somewhere {}.".format(*adj))
            if r == 6:
                action_text = "Does its very best." # not this time hun
            if r == 7:
                row_num = random.randint(1, adj_sub.shape[0]) - 1
                adj = [adj_sub.iloc[row_num]["Result"]]
                row_num = random.randint(1, noun_sub.shape[0]) - 1
                noun = [noun_sub.iloc[row_num]["Result"]]
                action_text = ("Spreads a lot of {} {}s.".format(*adj, *noun))
            if r == 8:
                row_num = random.randint(1, adj_sub.shape[0]) - 1
                adj = [adj_sub.iloc[row_num]["Result"]]
                action_text = ("Burns through any {} material.".format(*adj))
            if r == 9:
                action_text = ("This can hit {} targets.".format(random.randint(1, 6)))
            if r == 10:
                action_text = "This repairs any object it hits."
            if r == 11:
                row_num = random.randint(1, adj_sub.shape[0]) - 1
                adj = [adj_sub.iloc[row_num]["Result"]]
                action_text = ("Changes the session music to something {}.".format(*adj))
            if r == 12:
                row_num = random.randint(1, noun_sub.shape[0]) - 1
                noun = [noun_sub.iloc[row_num]["Result"]]
                row_num = random.randint(1, verb_sub.shape[0]) - 1
                verb = [verb_sub.iloc[row_num]["Result"]]
                action_text = ("Awakens the {} {} Program.".format(*noun, *verb))
            if r == 13:
                row_num = random.randint(1, noun_sub.shape[0]) - 1
                noun = [noun_sub.iloc[row_num]["Result"]]
                action_text = ("Leaves a {} behind.".format(*noun))
            if r == 14:
                row_num = random.randint(1, noun_sub.shape[0]) - 1
                noun = [noun_sub.iloc[row_num]["Result"]]
                action_text = ("A NICE, BIG {}.".format(*noun).upper())
            if r == 15:
                action_text = "This passes through surfaces."
            if r == 16:
                action_text = "This cannot be countered."
            if r == 17:
                row_num = random.randint(1, adj_sub.shape[0]) - 1
                adj = [adj_sub.iloc[row_num]["Result"]]
                action_text = "Gets {} with it.".format(*adj)
            if r == 18:
                action_text = "Reroll this chip in its entirety after use."
            if r == 19:
                action_text = "Makes a blinding light."
            if r == 20:
                row_num = random.randint(1, adj_sub.shape[0]) - 1
                adj = [adj_sub.iloc[row_num]["Result"]]
                action_text = ("Makes the vibes a LOT more {}.".format(*adj))
            if r == 21:
                row_num = random.randint(1, verb_sub.shape[0]) - 1
                verb = [verb_sub.iloc[row_num]["Result"]]
                action_text = ("Can also be defended against by {}ing.".format(*verb))
            if r == 22:
                action_text = "Summons a deafening silence."
            if r == 23:
                row_num = random.randint(1, verb_sub.shape[0]) - 1
                verb = [verb_sub.iloc[row_num]["Result"]]
                action_text = ("This can only be used while {}ing.".format(*verb))
            if r == 24:
                dtype = ["Crushing", "Slashing", "Incendiary", "Holy", "Pure", "Special"]
                action_text = ("Deals {} Damage.".format(random.choice(dtype)))
            if r == 25:
                type = ["Guards", "negative tags", "the GM"]
                action_text = ("Ignores {}.".format(random.choice(type)))
            if r == 26:
                action_text = "This chip permanently breaks after use."
            if r == 27:
                zenny = random.randint(1, 6) * 100
                action_text = ("Spend {} Zenny to refresh this chip.".format(zenny))
            if r == 28:
                zenny = random.randint(1, 6) * 100
                action_text = ("Gain {} Zenny for each point of damage this deals.".format(zenny))
            if r == 29:
                action_text = "Creates a Common Mystery Data."
            if r == 30:
                action_text = "Gives treats to all pets in range."
            if r == 31:
                row_num = random.randint(1, adj_sub.shape[0]) - 1
                adj = [adj_sub.iloc[row_num]["Result"]]
                row_num = random.randint(1, noun_sub.shape[0]) - 1
                noun = [noun_sub.iloc[row_num]["Result"]]
                action_text = ("Exposes the truth behind the mystery of the {} {}.".format(*adj, *noun))
            if r == 32:
                action_text = "Deals triple damage if you successfully lie to the rest of your group about how much damage this chip does."
            if r == 33:
                row_num = random.randint(1, noun_sub.shape[0]) - 1
                noun = [noun_sub.iloc[row_num]["Result"]]
                action_text = ("Replaces all summoned element in range with {}s.".format(*noun))
            if r == 34:
                action_text = "Do Navis feel pain? What about Viruses? It all feels like a sport, a game, a dream... Do you care? Are you happier not knowing? "
            if r == 35:
                type = ["Upshifts", "Downshifts", "Adds 1d6 dice to"]
                row_num = random.randint(1, adj_sub.shape[0]) - 1
                adj = [adj_sub.iloc[row_num]["Result"]]
                type2 = ["parries", "counters", "{} rolls".format(*adj)]
                action_text = "{} {}.".format(random.choice(type), random.choice(type2))
            if r == 36:
                action_text = "Alerts God."  # Too late; not even He can save us now

        numberOfEffects += 1
        if isModal and ("NICE, BIG" not in action_text):
            action_text = action_text[0].lower() + action_text[1:] # lowercases modal phrases
        if numberOfEffects < modalDegree:
            action_list.append(action_text[:-1] + ";")
        else:
            action_list.append(action_text)

    action_result = " ".join(action_list)

    chip_description_list = list(filter(None, (cost_result, guard_result, condition_combined, action_result)))
    chip_list_format = [i[0].lower()+i[1:] if 'NICE, BIG' not in i else i for i in chip_description_list[1:]]  # lowercases the first letter of non-first phrases, except for A NICE, BIG {} and Alerts God
    chip_description_list = chip_description_list[0:1] + chip_list_format
    chip_description_list = [category_description] + chip_description_list + [xdamage_description]
    chip_description = " ".join(chip_description_list)
    subtitle_trimmed = "/".join(filter(None, (damage_result, range_description, category_result, tag_result)))

# NAME:
    row_num = random.randint(1, adj_sub.shape[0]) - 1
    adj = [adj_sub.iloc[row_num]["Result"]]
    row_num = random.randint(1, noun_sub.shape[0]) - 1
    noun = [noun_sub.iloc[row_num]["Result"]]
    embed = discord.Embed(
        title="__{}{}__".format(*adj, *noun),
        color=cc_color_dictionary["Nyx"])
    embed.add_field(name="[%s]" % subtitle_trimmed,
                    value="_%s_" % chip_description)
    await koduck.sendmessage(context["message"], sendembed=embed)
    return
