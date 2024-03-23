import typing
import discord
import requests
import random
import settings
import pandas as pd
import re
import datetime
from maincommon import clean_args, roll_row_from_table, send_query_msg, find_value_in_table
from maincommon import help_df, cc_color_dictionary, pmc_link

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
MAX_WEATHER_ROLL = 14

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
weather_category_list = pd.unique(weather_df["Category"].dropna())

glossary_df = pd.read_csv(settings.glossaryfile, sep="\t").fillna('')

pmc_daemon_df = pd.read_csv(settings.pmc_daemonfile, sep="\t").fillna('')

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

async def crimsonnoise(interaction: discord.Interaction, md_type: typing.Literal["Common", "Uncommon", "Rare"]):
    arg = md_type.lower().strip()
    crimsonnoise_type = crimsonnoise_df[crimsonnoise_df["MysteryData"].str.contains("^%s$" % re.escape(arg), flags=re.IGNORECASE)]

    if crimsonnoise_type.shape[0] == 0:
        return await interaction.command.koduck.send_message(interaction, 
                                                             content=f"You typed {md_type}! Please specify either Common, Uncommon, or Rare CrimsonNoise.", 
                                                             ephemeral=True)
    firstroll = random.randint(1, 6)
    if firstroll != 6:
        reward_type = "Chip"
        result_text = " BattleChip!"
    else:
        reward_type = "NCP"
        result_text = " NCP!"

    result_chip = roll_row_from_table(crimsonnoise_type, df_filters={"Type": reward_type})["Value"]

    result_text = result_chip + result_text 
    cn_color = cc_color_dictionary["Genso Network"]
    cn_type = arg.capitalize()

    embed = discord.Embed(title=f"__{cn_type} CrimsonNoise__",
                          description=f"_{interaction.user.mention} accessed the {cn_type} CrimsonNoise..._\n\nGot: **{result_text}**",
                          color=cn_color)

    return await interaction.command.koduck.send_message(interaction, embed=embed)

def query_daemon():
    result_title = "Listing all Daemons (excluding Player Made Content)..."
    result_msg = ", ".join(daemon_df["Name"])
    return True, result_title, result_msg

async def daemon(context, *args, **kwargs):
    cleaned_args = clean_args(args)
    arg_combined = " ".join(cleaned_args)
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await context.koduck.send_message(receive_message=context["message"],
                                        content="Lists the complete information of a **Daemon** for DarkChip rules. "
                                                    + "Use `daemon all` to pull up the names of all Official Daemons!")
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
            return await context.koduck.send_message(receive_message=context["message"],
                                            content="Couldn't find the rules for this command! (You should probably let the devs know...)")
        return await context.koduck.send_message(receive_message=context["message"],
                                        content=ruling_msg["Response"])

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
    return await context.koduck.send_message(receive_message=context["message"], embed=embed)

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
        return await context.koduck.send_message(receive_message=context["message"],
                                        content="Pulls up info for 1-%d **Network Modifiers**! I can also list all Network Modifiers if you tell me `list` or `all`!" % MAX_MOD_QUERY)

    if len(cleaned_args) > MAX_MOD_QUERY:
        return await context.koduck.send_message(receive_message=context["message"],
                                        content="Can't pull up more than %d Network Mods!" % MAX_MOD_QUERY)

    if cleaned_args[0] in ["list", "all"]:
        _, result_title, result_msg = query_network()
        return await send_query_msg(context, result_title, result_msg)
    elif cleaned_args[0] in ['rule', 'ruling', 'rules']:
        ruling_msg = await find_value_in_table(context, help_df, "Command", "networkmodruling", suppress_notfound=True)
        if ruling_msg is None:
            return await context.koduck.send_message(receive_message=context["message"],
                                            content="Couldn't find the rules for this command! (You should probably let the devs know...)")
        return await context.koduck.send_message(receive_message=context["message"],
                                        content=ruling_msg["Response"])

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
        await context.koduck.send_message(receive_message=context["message"], embed=embed)

    return


async def invite(context, *args, **kwargs):
    invite_link = settings.invite_link
    color = 0x71c142
    embed = discord.Embed(title="Just click here to invite me to one of your servers!",
                          color=color,
                          url=invite_link)
    return await context.koduck.send_message(receive_message=context["message"], embed=embed)


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
            audience_help_msg = "Roll a random Cheer with `cheer!` (Up to %d at once!)\n " % MAX_CHEER_JEER_ROLL + \
                            "I can also list all Cheers with `cheer all`.\n\n " + \
                            "You can add Cheer Points with `cheer add 2`, remove them with `cheer spend 2`, " + \
                            "and pull up the current Cheer points with `cheer now`.\n\n" + \
                            "For more details on Audience Participation rules, try `help cheer` or `help audience`."
            return await context.koduck.send_message(receive_message=context["message"], content=audience_help_msg)

        if cleaned_args[0] in ['rule', 'ruling', 'rules']:
            ruling_msg = await find_value_in_table(context, help_df, "Command", "cheerruling", suppress_notfound=True)
            if ruling_msg is None:
                return await context.koduck.send_message(receive_message=context["message"],
                                                content="Couldn't find the rules for this command! (You should probably let the devs know...)")
            return await context.koduck.send_message(receive_message=context["message"],
                                            content=ruling_msg["Response"])
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
            audience_help_msg = "Roll a random Jeer with `jeer!` (Up to %d at once!)\n" % MAX_CHEER_JEER_ROLL + \
                            "I can also list all Jeers and MegaJeers with `jeer all`.\n\n " + \
                            "You can add Jeer Points with `jeer add 2`, remove them with `jeer spend 2`, " + \
                            "and pull up the current Jeer Points with `jeer now`.\n\n" + \
                            "For more details on Audience Participation rules, try `help jeer` or `help audience`."
            return await context.koduck.send_message(receive_message=context["message"], content=audience_help_msg)

        if cleaned_args[0] in ['rule', 'ruling', 'rules']:
            ruling_msg = await find_value_in_table(context, help_df, "Command", "jeerruling", suppress_notfound=True)
            if ruling_msg is None:
                return await context.koduck.send_message(receive_message=context["message"],
                                                content="Couldn't find the rules for this command! (You should probably let the devs know...)")
            return await context.koduck.send_message(receive_message=context["message"],
                                            content=ruling_msg["Response"])

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
        audience_help_msg = "Roll a random Cheer or Jeer with `audience cheer` or `audience jeer`! (Up to %d at once!)\n" % MAX_CHEER_JEER_ROLL + \
                            "I can also list all Cheers or Jeers with `audience cheer all` or `audience jeer all`.\n\n" + \
                            "Start up an audience tracker for this text channel with `audience start`!\n" + \
                            "You can then add Cheers and Jeers with `audience cheer add 2`, remove them with `audience cheer spend 2`, " + \
                            "and pull up the current Cheer/Jeer points with `audience now`.\n\n" + \
                            "Once you're done, make sure to dismiss the audience with `audience end`."
        return await context.koduck.send_message(receive_message=context["message"], content=audience_help_msg)

    if cleaned_args[0] in ['rule', 'ruling', 'rules']:
        ruling_msg = await find_value_in_table(context, help_df, "Command", "audienceruling", suppress_notfound=True)
        if ruling_msg is None:
            return await context.koduck.send_message(receive_message=context["message"],
                                            content="Couldn't find the rules for this command! (You should probably let the devs know...)")
        return await context.koduck.send_message(receive_message=context["message"],
                                        content=ruling_msg["Response"])

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
            return await context.koduck.send_message(receive_message=context["message"], content=retvalue[1])
        else:
            embed_descript = "Starting up the audience for %s" % msg_location
            embed_foot = "Cheer Points: 0, Jeer Points: 0"
        embed = discord.Embed(title="__Audience Participation__",
                              description=embed_descript,
                              color=cj_colors["cheer"])
        embed.set_footer(text=embed_foot)
        return await context.koduck.send_message(receive_message=context["message"], embed=embed)
    elif cleaned_args[0] == 'end':
        ret_val = end_audience(channel_id)
        if ret_val == -1:
            return await context.koduck.send_message(receive_message=context["message"], content="An audience hasn't been started for this channel yet")
        embed = discord.Embed(title="__Audience Participation__",
                              description="Ending the audience session for %s\nGoodnight!" % msg_location,
                              color=cj_colors["jeer"])
        return await context.koduck.send_message(receive_message=context["message"], embed=embed)

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
                return await context.koduck.send_message(receive_message=context["message"], content="Sorry, you can't ask for both Cheers and Jeers!")
            if "c" in arg:
                query_details[0] = "cheer"
            else:
                query_details[0] = "jeer"
        elif arg.isnumeric():
            query_details[1] = int(arg)
        elif arg in ["now", "current", "show"]:
            is_pullup = True
        else:
            return await context.koduck.send_message(receive_message=context["message"],
                                            content="Sorry, I'm not sure what `%s` means here!" % arg)
    if is_pullup:
        retval = get_audience(channel_id)
        if retval[0] == -1:
            return await context.koduck.send_message(receive_message=context["message"],
                                            content="Audience Participation hasn't been started in this channel!")
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
        return await context.koduck.send_message(receive_message=context["message"], embed=embed)

    if is_spend:
        if not query_details[0]:
            return await context.koduck.send_message(receive_message=context["message"],
                                            content="Did not specify Cheer or Jeer!")
        if query_details[2] == '-':
            change_amount = -1 * query_details[1]
        else:
            change_amount = query_details[1]
        retval = change_audience(channel_id, query_details[0], change_amount)
        if retval[0] == -1:
            return await context.koduck.send_message(receive_message=context["message"], content=retval[1])
        embed = discord.Embed(title="__Audience Participation__",
                              description=retval[1],
                              color=cj_colors[query_details[0]])
        embed.set_footer(text=retval[2])
        return await context.koduck.send_message(receive_message=context["message"], embed=embed)

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
        return await context.koduck.send_message(receive_message=context["message"], content=embed_msg)
    else:
        if query_details[1] > MAX_CHEER_JEER_ROLL:
            return await context.koduck.send_message(receive_message=context["message"], content="Rolling too many Cheers or Jeers! Up to %d!" % MAX_CHEER_JEER_ROLL)
        if not query_details[0]:
            return await context.koduck.send_message(receive_message=context["message"], content="Please specify either Cheer or Jeer!")
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

        return await context.koduck.send_message(receive_message=context["message"], embed=embed)


async def weather(context, *args, **kwargs):
    cleaned_args = clean_args(args)
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await context.koduck.send_message(receive_message=context["message"],
                                        content="Pulls up info for 1-%d types of **CyberWeather**! I can also list all types of CyberWeather if you tell me `list` or `all`!" % MAX_WEATHER_QUERY)

    if len(cleaned_args) > MAX_WEATHER_QUERY:
        return await context.koduck.send_message(receive_message=context["message"],
                                        content="Can't pull up more than %d types of CyberWeather!" % MAX_WEATHER_QUERY)

    if cleaned_args[0] in ["list", "all"]:
        _, result_title, result_msg = query_weather()
        return await send_query_msg(context, result_title, result_msg)
    elif cleaned_args[0] in ['rule', 'ruling', 'rules']:
        ruling_msg = await find_value_in_table(context, help_df, "Command", "weather",
                                               suppress_notfound=True)
        if ruling_msg is None:
            return await context.koduck.send_message(receive_message=context["message"],
                                            content="Couldn't find the rules for this command! (You should probably let the devs know...)")
        return await context.koduck.send_message(receive_message=context["message"],
                                        content=ruling_msg["Response"])

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
        await context.koduck.send_message(receive_message=context["message"], embed=embed)

    return


async def weatherforecast(context, *args, **kwargs):
    # most of this was borrowed from the element code god bless you whoever worked on it
    cleaned_args = clean_args(args)
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await context.koduck.send_message(receive_message=context["message"],
                                        content="Pulls up a random set of 1-%d types of **CyberWeather**! " % MAX_WEATHER_ROLL + 
                                        "To use, enter `weatherforecast [#]` or `weatherforecast [category] [#]`! The command `randomweather` or `randomweather [category] [#]` can also be used!\n"\
                                         +
                                                    "Categories: **%s**" % ", ".join(weather_category_list))
    if len(cleaned_args) > 2:
        return await context.koduck.send_message(receive_message=context["message"],
                                        content="Command is too long! Just give me `weatherforecast [#]` or `weatherforecast [category] [#]`! The command `randomweather` or `randomweather [category] [#]` can also be used!")
    
    weather_return_number = 1  # number of weather to return, 1 by default
    weather_category = None
    sub_weather_df = weather_df
    for arg in cleaned_args:
        try:
            weather_return_number = int(arg)
        except ValueError:
            weather_category = arg.lower().capitalize()
            
            sub_weather_df = weather_df[weather_df["Category"].str.fullmatch(re.escape(arg), flags=re.IGNORECASE)]
            if sub_weather_df.shape[0] == 0:
                return await context.koduck.send_message(receive_message=context["message"],
                                                content="Not a valid category!\n" +
                                                        "Categories: **%s**" % ", ".join(weather_category_list))
    
    category_range_max = sub_weather_df.shape[0]
    if weather_return_number < 1:
        return await context.koduck.send_message(receive_message=context["message"],
                                    content="The number of weather can't be 0 or negative!")
    if weather_return_number > MAX_WEATHER_ROLL:
        return await context.koduck.send_message(receive_message=context["message"],
                                    content="That's too many weathers! Are you sure you need more than %d?" % MAX_WEATHER_ROLL)
    if weather_category and weather_return_number > category_range_max:
        return await context.koduck.send_message(receive_message=context["message"],
                                    content="That's too many weathers for this category! Are you sure you need more than %d?" % category_range_max)
    
    weather_selected = random.sample(range(sub_weather_df.shape[0]), weather_return_number)
    weather_name = [sub_weather_df.iloc[i]["Name"] for i in weather_selected]
    
    if weather_category is None:
        weather_flavor_title = "Picked {} random weather(s):".format(str(weather_return_number))
    else:
        weather_flavor_title = "Picked {} random weather(s) from the {} category:".format(str(weather_return_number),
                                                                                            weather_category)
    
    weather_color = 0xd5b5f7
    if weather_category == "Basic":
        weather_color = weather_color_dictionary["Blue"]
    elif weather_category == "Glitched":
        weather_color = weather_color_dictionary["Yellow"]
    elif weather_category == "Error":
        weather_color = weather_color_dictionary["Red"]
    
    weather_list = ", ".join(weather_name)
    embed = discord.Embed(title=weather_flavor_title,
                          color=weather_color,
                          description=weather_list)
    # weather_message = "`{} {}`".format(weather_flavor_title,weather_list) # no embed method
    return await context.koduck.send_message(receive_message=context["message"], embed=embed)


async def achievement(context, *args, **kwargs):
    if context["params"]:
        help_msg = context["param_line"].strip().lower() == "help"
    else:
        help_msg = True
    if help_msg:
        return await context.koduck.send_message(receive_message=context["message"],
                                        content="Pulls up info for a NetBattlers Advance **Achievement**! I can also list all the Achievements if you tell me `list` or `all`!")

    arg = context["param_line"]
    cleaned_args = arg.lower()

    if cleaned_args in ["list", "all"]:
        achieve_groups = achievement_df.groupby(["Category"])
        return_msgs = ["**%s:**\n*%s*" % (name, ", ".join(achieve_group["Name"].values)) for name, achieve_group in achieve_groups
                       if name]
        return await context.koduck.send_message(receive_message=context["message"], content="\n\n".join(return_msgs))

    match_candidates = achievement_df[achievement_df["Name"].str.contains(re.escape(cleaned_args), flags=re.IGNORECASE)]
    if match_candidates.shape[0] < 1:
        return await context.koduck.send_message(receive_message=context["message"], content="Didn't find any matches for `%s`!" % arg)
    if match_candidates.shape[0] > 1:
        return await context.koduck.send_message(receive_message=context["message"], content="Found multiple matches for `%s`:\n*%s*" %
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

    return await context.koduck.send_message(receive_message=context["message"], embed=embed)


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
        help_msg = "Start up a **Spotlight Checklist** for this text channel with `spotlight start`! Add people right away with `spotlight start Lan/MegaMan Mayl/Roll Dex/GutsMan`.\n" + \
                   "Mark off people who've acted with `spotlight Lan`! The checklist will automatically refresh when everyone has acted!\n\n" + \
                   "**List of Commands:**\n" + \
                   "> `spotlight start`, `spotlight start Lan/MegaMan Mayl/Roll`: Start the checklist in this text channel. You can include names too, separated by spaces or commas!\n" + \
                   "> `spotlight Lan`: Mark off Lan/MegaMan off the checklist. Case insensitive. You don't need to type the full name!\n" + \
                   "> `spotlight add Yai/Glyde Chaud/ProtoMan`: Add a new person to the checklist. You can add multiple people at once!\n" + \
                   "> `spotlight remove Chaud`: Remove a person from the checklist. You can remove multiple people at once!\n" + \
                   "> `spotlight edit Yai Yai/Glide`: Update a person's name in the checklist. One at a time!\n" + \
                   "> `spotlight show`: Shows the current Spotlight Checklist.\n" + \
                   "> `spotlight reset`, `spotlight reset Lan`: Unmark the entire checklist, or unmark a specific player\n" + \
                   "> `spotlight end`: Ends the checklist. Will also automatically close after %d hours.\n" % (SPOTLIGHT_TIMEOUT.seconds/3600)
        return await context.koduck.send_message(receive_message=context["message"],
                                        content=help_msg)
    if cleaned_args[0].lower() in ['rules', 'rule', 'book', 'rulebook']:
        ruling_msg = await find_value_in_table(context, help_df, "Command", "flow", suppress_notfound=True)
        if ruling_msg is None:
            return await context.koduck.send_message(receive_message=context["message"],
                                            content="Couldn't find the rules for this command! (You should probably let the devs know...)")
        return await context.koduck.send_message(receive_message=context["message"],
                                        content=ruling_msg["Response"])

    notification_msg = ""
    err_msg = ""
    if cleaned_args[0].lower() in ['start', 'begin', 'on']:
        if channel_id in spotlight_db:
            spotlight_db[channel_id]["Last Modified"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return await context.koduck.send_message(receive_message=context["message"],
                                            embed=embed_spotlight_message("Spotlight Tracker already started in this channel!",
                                                                              msg_location, error=True))
        if (len(spotlight_db)+1) > MAX_SPOTLIGHTS:
            return await context.koduck.send_message(receive_message=context["message"],
                                            content="Too many Spotlight Checklists are active in ProgBot right now! Please try again later.")
        if len(cleaned_args) > (MAX_CHECKLIST_SIZE + 1):
            return await context.koduck.send_message(receive_message=context["message"],
                                            embed=embed_spotlight_message("Max of %d participants in a checklist!" %
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
        return await context.koduck.send_message(receive_message=context["message"], embed=embed)

    if channel_id not in spotlight_db:
            return await context.koduck.send_message(receive_message=context["message"],
                                            embed=embed_spotlight_message("Spotlight Tracker not yet started in this channel!",
                                                                              msg_location, error=True))

    spotlight_db[channel_id]["Last Modified"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if cleaned_args[0].lower() in ['close', 'shutdown', 'end', 'stop', 'finish']:
        del spotlight_db[channel_id]
        return await context.koduck.send_message(receive_message=context["message"],
                                        embed=embed_spotlight_message("Shutting down this Spotlight Tracker! Goodnight!",
                                                                          msg_location))
    if cleaned_args[0].lower() == 'add':
        if len(cleaned_args) == 1:
            return await context.koduck.send_message(receive_message=context["message"],
                                            embed=embed_spotlight_message("Please list who you want to add!",
                                                                              msg_location, error=True))
        if (len(spotlight_db[channel_id]) + len(cleaned_args) - 2) > MAX_CHECKLIST_SIZE:
            return await context.koduck.send_message(receive_message=context["message"],
                                            embed=embed_spotlight_message("Max of %d participants in a checklist!" %
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
            match_name = await find_spotlight_participant(context, arg, spotlight_db[channel_id], context, msg_location)
            if match_name is None:
                return
            spotlight_db[channel_id][match_name] = False
            continue
    elif cleaned_args[0].lower() in ['remove', 'delete', 'kick']:
        if len(cleaned_args) == 1:
            return await context.koduck.send_message(receive_message=context["message"],
                                            embed=embed_spotlight_message("Please specify who you want to remove!",
                                                                              msg_location, error=True))
        for arg in cleaned_args[1:]:
            match_name = await find_spotlight_participant(context, arg, spotlight_db[channel_id], context, msg_location)
            if match_name is None:
                continue
            del spotlight_db[channel_id][match_name]
            continue
    elif cleaned_args[0].lower() in ['edit', 'change', 'update', 'rename']:
        if len(cleaned_args) != 3:
            return await context.koduck.send_message(receive_message=context["message"],
                                            embed=embed_spotlight_message("Need just the original name and the new name to change it too!",
                                                                              msg_location, error=True))

        match_name = await find_spotlight_participant(context, cleaned_args[1], spotlight_db[channel_id], context, msg_location)
        if match_name is not None:
            spotlight_db[channel_id][cleaned_args[2]] = spotlight_db[channel_id].pop(match_name)
    elif cleaned_args[0].lower() not in ['show', "now", "display", "what"]:
        already_went_list = []
        for arg in cleaned_args:
            match_name = await find_spotlight_participant(context, arg, spotlight_db[channel_id], context, msg_location)
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
    return await context.koduck.send_message(receive_message=context["message"], embed=embed)


async def find_spotlight_participant(context, arg, participant_dict, msg_cnt, message_location):
    participant_list = pd.Series(participant_dict.keys())
    participant_list = participant_list[participant_list != "Last Modified"]
    match_candidates = participant_list[participant_list.str.contains(re.escape(arg), flags=re.IGNORECASE)]
    if match_candidates.shape[0] == 0:
        await context.koduck.send_message(msg_cnt["message"],
                                 embed=embed_spotlight_message("Unable to find `%s` as a participant!" % arg,
                                                                   message_location, error=True))
        return None
    if match_candidates.shape[0] > 1:
        await context.koduck.send_message(msg_cnt["message"],
                                 embed=embed_spotlight_message("For `%s`, did you mean: %s?" % (arg, ", ".join(match_candidates.to_list())),
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
        return await context.koduck.send_message(receive_message=context["message"],
                                    content=message_help.format(pmc_link))
    user_query = context["param_line"]

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
        return await context.koduck.send_message(receive_message=context["message"],
                                 content="Sorry, I got an unexpected response from Notion! Please try again later! (If this persists, let the devs know!)")

    # just leaving this here for the next time i need to work on this again..
    #parse = json.loads(r.content)
    #print(json.dumps(parse, indent=4, sort_keys=True))

    # iza helped me rewrite the overwhelming bulk of this.
    # she's amazing, she's wonderful, and if you're not thankful for her presence in mmg i'll bite your kneecaps off.
    repo_results_dict = {}
    blockmap = r.json()["recordMap"]
    if "block" not in blockmap:
        return await context.koduck.send_message(receive_message=context["message"],
                                 content="I can't find anything with that query, sorry!")
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
        await context.koduck.send_message(receive_message=context["message"],
                                 content="I can't find anything with that query, sorry!")
    else:
        repo_results_df['Link'] = repo_results_df['Link'].explode().apply(lambda x: x[0])
        repo_result_row = repo_results_df.iloc[0]
    if size == 1:
        generated_msg = "**Found {} entry for _'{}'_..** \n" + \
                        "**_`{}`_** by __*{}*__:\n __<{}>__"
        return await context.koduck.send_message(receive_message=context["message"],
                                    content=generated_msg.format(size, user_query, repo_result_row["Name"], repo_result_row["Author"], repo_result_row["Link"]))
    if size > 1:
        repo_results = "', '".join(repo_results_df["Name"])
        generated_msg = "**Found {} entries for _'{}'_..** \n" + \
                        "*'%s'*" % repo_results
        return await context.koduck.send_message(receive_message=context["message"],
                                        content=generated_msg.format(size, user_query))


