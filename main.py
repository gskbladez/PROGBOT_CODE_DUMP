import discord
import asyncio
import sys, os, random
import koduck, yadon
import settings
import pandas as pd

# Background task is run every set interval while bot is running (by default every 10 seconds)
async def backgroundtask():
    pass

settings.backgroundtask = backgroundtask

chip_df = pd.read_csv(r"chipdata.tsv", sep="\t").fillna('')
chip_df["chip_lowercase"] = chip_df["Chip"].str.lower()

ncp_df = pd.read_csv(r"ncpdata.tsv", sep="\t").fillna('')
ncp_df["ncp_lowercase"] = ncp_df["Power/NCP"].str.lower()

power_df = pd.read_csv(r"powerncpdata.tsv", sep="\t").fillna('')
power_df["power_lowercase"] = power_df["Power/NCP"].str.lower()

virus_df = pd.read_csv(r"virusdata.tsv", sep="\t").fillna('')
virus_df["name_lowercase"] = virus_df["Name"].str.lower()

daemon_df = pd.read_csv(r"daemondata.tsv", sep="\t").fillna('')
daemon_df["name_lowercase"] = daemon_df["Name"].str.lower()

bond_df = pd.read_csv(r"bonddata.tsv", sep="\t").fillna('')
bond_df["bondpower_lowercase"] = bond_df["BondPower"].str.lower()

tag_df = pd.read_csv(r"tagdata.tsv", sep="\t").fillna('')
tag_df["tag_lowercase"] = tag_df["Tag"].str.lower()

mysterydata_df = pd.read_csv(r"mysterydata.tsv", sep="\t").fillna('')
mysterydata_df["mysterydata_lowercase"] = mysterydata_df["MysteryData"].str.lower()

element_df = pd.read_csv(r"elementdata.tsv", sep="\t").fillna('')
element_df["category_lowercase"] = element_df["category"].str.lower()

help_df = pd.read_csv(r"helpresponses.tsv", sep="\t").fillna('')
help_df["command_lowercase"] = help_df["Command"].str.lower()
help_df["Response"] = help_df["Response"].str.replace('\\\\n', '\n',regex=True)

cc_color_dictionary = {"Mega": 0xA8E8E8,
                         "ChitChat": 0xff8000,
                         "Radical Spin": 0x3f5cff,
                         "Underground Broadcast": 0x73ab50,
                         "Mystic Lilies": 0x99004c,
                         "Genso Network": 0xff605d,
                         "Leximancy": 0x481f65,
                         "Dark": 0xB088D0,
                         "Item": 0xffffff}

mysterydata_dict = {"common": {"color": 0x48C800,
                               "image": "https://raw.githubusercontent.com/gskbladez/meddyexe/master/virusart/commonmysterydata.png"},
                    "uncommon": {"color": 0x00E1DF,
                                 "image": "https://raw.githubusercontent.com/gskbladez/meddyexe/master/virusart/uncommonmysterydata.png"},
                    "rare": {"color": 0xD8E100,
                             "image": "https://raw.githubusercontent.com/gskbladez/meddyexe/master/virusart/raremysterydata.png"}}

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
    channelid = "704684798584815636"
    THEchannel = koduck.client.get_channel(channelid)
    THEmessagecontent = context["paramline"]
    originchannel = "<#{}>".format(context["message"].channel.id) if isinstance(context["message"].channel,
                                                                                discord.Channel) else ""
    embed = discord.Embed(title="**__New Bug Report!__**", description="_{}_".format(context["paramline"]),
                          color=0x5058a8)
    embed.set_footer(
        text="Submitted by: {}#{}".format(context["message"].author.name, context["message"].author.discriminator))
    embed.set_thumbnail(url="https://raw.githubusercontent.com/gskbladez/meddyexe/master/virusart/bug.png")
    await koduck.sendmessage(context["message"], sendchannel=THEchannel, sendembed=embed, ignorecd=True)
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
    try:
        THEmessage = koduck.outputhistory[context["message"].author.id].pop()
    except (KeyError, IndexError):
        return settings.message_oops_failed
    try:
        await koduck.client.delete_message(THEmessage)
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


async def help(context, *args, **kwargs):
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

    # Try to retrieve the help message for the query
    #querycommand = args[0]
    #try:
        # Use {cp} for command prefix and {pd} for parameter delimiter
    #    return await koduck.sendmessage(context["message"], sendcontent=getattr(settings, "message_help_{}".format(
    #        querycommand)).replace("{cp}", settings.commandprefix).replace("{pd}", settings.paramdelim))
    #except AttributeError:
    #    return await koduck.sendmessage(context["message"], sendcontent=settings.message_help_unknowncommand)


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


async def roll(context, *args, **kwargs): #TODO: fix, add comments (parsing)
    parameters = [1, settings.rolldefaultmax, 0]  # quantity, max, filter

    # parse parameters
    if len(args) > 0:
        try:
            parameters[1] = int(args[0])
        except ValueError:
            temp = args[0].split("d")
            if len(temp) > 1:
                temp = temp[0:1] + temp[1].split(">")

            for i in range(len(parameters)):
                try:
                    parameters[i] = int(temp[i])
                except (IndexError, ValueError):
                    pass

    # quantity should not be negative
    parameters[0] = max(parameters[0], 1)

    # roll dice!
    results = []
    for i in range(parameters[0]):
        if parameters[1] >= 0:
            results.append(random.randint(1, parameters[1]))
        else:
            results.append(random.randint(parameters[1], 1))

    # print output
    if parameters[2] != 0:
        successes = 0
        for i in range(len(results)):
            if results[i] <= parameters[2]:
                results[i] = "~~{}~~".format(results[i])
            else:
                successes += 1
        return await koduck.sendmessage(context["message"], sendcontent="{} _rolls..._ ({}) = **__{} hits!__**".format(
            context["message"].author.mention, ", ".join([str(x) for x in results]) if len(results) > 1 else results[0],
            successes))
    else:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="{} _rolls a..._ **{}!**".format(context["message"].author.mention,
                                                                                     ", ".join([str(x) for x in
                                                                                                results]) if len(
                                                                                         results) > 1 else results[0]))


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
                                     sendcontent="I can't find %s!" % search_arg)
        return None
    elif search_results.shape[0] > 1:
        await koduck.sendmessage(context["message"],
                                 sendcontent="Found more than one match for %s! You should probably let the devs know..." % search_arg)
        return None
    return search_results.iloc[0]


async def chip(context, *args, **kwargss):
    if len(args) == 1:
        args = args[0].split()

    if len(args) < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Give me the name of a Battle Chip and I can pull up its info for you!")
    elif len(args) > 5:
        return await koduck.sendmessage(context["message"], sendcontent="Too many chips, no more than 5!")

    for arg in args:
        chip_info = await find_value_in_table(context, chip_df, "chip_lowercase", arg)
        if chip_info is None:
            continue

        chip_name = chip_info["Chip"]

        chip_damage = "%s Damage" % chip_info["Dmg"]
        chip_range = chip_info["Range"]
        chip_description = chip_info["Effect"]
        chip_category = chip_info["Category"]
        chip_tags = chip_info["Tags"]
        chip_crossover = chip_info["From?"]

        # this determines embed colors
        color = 0xbfbfbf
        if chip_crossover in cc_color_dictionary:
            color = cc_color_dictionary[chip_crossover]
        if chip_tags:
            if 'Dark' in chip_tags:
                color = cc_color_dictionary['Dark']
            elif 'Mega' in chip_tags:
                color = cc_color_dictionary['Mega']
            elif chip_category == 'Item':
                color = cc_color_dictionary["Item"]

        if chip_crossover == "Core":
            chip_title = "__%s__" % chip_name
        else:
            chip_title = "__%s (%s Chip)__" % (chip_name, chip_crossover)

        subtitle = [chip_damage, chip_range, chip_category, chip_tags]
        subtitle_trimmed = [i for i in subtitle if i and i[0] != '-']

        embed = discord.Embed(
            title=chip_title,
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
        color = -1 # error code
    return color


async def power_ncp(context, args, force_power = False):
    arg = args[0]
    power_info = await find_value_in_table(context, power_df, "power_lowercase", arg)
    if power_info is None:
        return None, None, None, None

    power_name = power_info["Power/NCP"]
    power_skill = power_info["Skill"]
    power_type = power_info["Type"]
    power_description = power_info["Effect"]
    power_eb = power_info["EB"]
    power_source = power_info["From?"]

    # this determines embed colors
    color = find_skill_color(power_skill)
    if (color < 0) and power_source in cc_color_dictionary:
        color = cc_color_dictionary[power_source]
    elif (color < 0) and power_skill.lower() in power_df["power_lowercase"].values:
        power_true_info = await find_value_in_table(context, power_df, "power_lowercase", power_skill)
        color = find_skill_color(power_true_info["Skill"])
    else:
        color = 0xffffff

    if power_eb == '-' or force_power: # display as power, rather than ncp

        if power_type == 'Passive' or power_type == '-' or power_type == 'Upgrade':
            field_title = 'Passive Power'
        else:
            field_title = "%s Power/%s" % (power_skill, power_type)

        field_description = power_description
    else:
        field_title = '%s EB' % power_eb

        if power_source == "Power Upgrades":
            field_title += "/%s Upgrade NCP" % power_skill
        elif power_source != "Core":
            power_name += " (%s Crossover NCP)" % power_source

        if power_type == 'Passive' or power_type == '-' or power_type == 'Upgrade':
            field_description = power_description
        else:
            field_description = "(%s/%s) %s" % (power_skill, power_type, power_description)

    return power_name, field_title, field_description, color


async def power(context, *args, **kwargs):
    #if ncp command, include EB; if power, don't include

    if len(args) < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Give me the name of a Navi Power and I can pull up its info for you!")

    power_name, field_title, field_description, power_color = await power_ncp(context, args, force_power=True)
    if power_name is None:
        return

    embed = discord.Embed(title="__{}__".format(power_name),
                          color=power_color)
    embed.add_field(name="**[{}]**".format(field_title),
                    value="_{}_".format(field_description))
    return await koduck.sendmessage(context["message"], sendembed=embed)


async def NCP(context, *args, **kwargs):
    #navi power upgrades
    if len(args) < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Give me the name of a NaviCust Part and I can pull up its info for you!")

    power_name, field_title, field_description, power_color = await power_ncp(context, args, force_power=False)
    if power_name is None:
        return

    embed = discord.Embed(title="__{}__".format(power_name),
                          color=power_color)
    embed.add_field(name="**[{}]**".format(field_title),
                    value="_{}_".format(field_description))
    return await koduck.sendmessage(context["message"], sendembed=embed)


async def virus_master(context, arg, simplified=True):
    virus_info = await find_value_in_table(context, virus_df, "name_lowercase", arg)

    if virus_info is None:
        return None, None, None, None, None, None

    virus_name = virus_info["Name"]
    virus_description = virus_info["Description"]
    virus_category = virus_info["Category"]
    virus_image = virus_info["ImageURL"]
    virus_artist = virus_info["ImageArtist"]
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

    if virus_source in cc_color_dictionary:
        virus_color = cc_color_dictionary[virus_source]
        virus_footer += " (%s Crossover Virus)" % virus_source
    else:
        virus_color = 0x7c00ff

    virus_descript_block = ""
    virus_title = ""

    virus_skills = [(key, int(val)) for key, val in virus_skills.items() if int(val) != 0]

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


async def virus(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Give me the name of one or more viruses and I can pull up their info for you!")
    elif len(args) > 5:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Too many viruses, no spamming!")

    for arg in args:
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
    if len(args) < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Give me the name of a virus and I can pull up its full info for you!")

    virus_name, virus_title, virus_descript_block, virus_footer, virus_image, virus_color = await virus_master(context, args[0], simplified=False)

    embed = discord.Embed(title=virus_name, color=virus_color)

    embed.set_thumbnail(url=virus_image)
    embed.add_field(name=virus_title,
                    value=virus_descript_block, inline=True)
    embed.set_footer(text=virus_footer)
    return await koduck.sendmessage(context["message"], sendembed=embed)

# types of locks!!!
async def query(context, *args, **kwargs):
    #move these query commands: >upgrade [power], filter out virus skills for >query sense... (>power sense?)
    if len(args) < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="This command can sort battlechips, NCPs, and powers by Category, and single out Crossover Content chips! Please type `>help query` for more information.")
    table = yadon.ReadTable("querydata")
    results = []
    for chipname, values in table.items():
        if args[0].lower() == values[0].lower():
            results.append(chipname)
        elif values[1].startswith("[") and args[0].lower() == values[1][1:values[1].index("]")].lower():
            results.append(chipname)
    if not results:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="I can't find any chips, NCPs, or Powers in that Category, or from that Crossover title.")
    else:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Please check `>help query` for what chip markings mean!\n**_Battlechips/NCPs/Powers in the_  ``'{}'`` _category, or from that specific Crossover..._**\n_{}_".format(
                                            args[0], ", ".join(results)))


def mysterydata_zenny(base_zen):
    z_amount = random.randint(1, 6) + random.randint(1, 6)
    return "%d Zenny!" % (z_amount * base_zen)


def mysterydata_chip(df):
    df_sub = df[df["Type"] == "Chip"]
    row_num = random.randint(1, df_sub.shape[0]) - 1
    result_chip = df_sub.iloc[row_num]["Value"]
    return "%s Battle Chip!" % result_chip


def mysterydata_ncp(df):
    df_sub = df[df["Type"] == "NCP"]
    row_num = random.randint(1, df_sub.shape[0]) - 1
    result_ncp = df_sub.iloc[row_num]["Value"]
    return "%s Battle Chip!" % result_ncp


def mysterydata_event(df):
    df_sub = df[df["Type"] == "Misc Table"]
    row_num = random.randint(1, df_sub.shape[0]) - 1
    result_event = df_sub.iloc[row_num]["Value"]
    return result_event


async def mysterydata_master(context, args, force_reward = False):
    arg = args[0].lower()
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
        result_text = mysterydata_zenny(int(zenny_val))
    elif firstroll <= 4:
        result_text = mysterydata_chip(mysterydata_type)
    elif firstroll == 5:
        result_text = mysterydata_ncp(mysterydata_type)
    else:
        result_text = mysterydata_event(mysterydata_type)

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
    if len(args) < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="I can roll Mystery Data for you! Specify `>mysterydata common`, `>mysterydata uncommon`, or `>mysterydata rare`!")

    await mysterydata_master(context, args, force_reward=False)


async def mysteryreward(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="I can roll Mystery Data for you, keeping it to the BattleChips and NCPs! Specify `>mysterydata common`, `>mysterydata uncommon`, or `>mysterydata rare`!")

    await mysterydata_master(context, args, force_reward=True)
    return


async def bond(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Give me a Bond Power and I can pull up its info for you!")

    bond_info = await find_value_in_table(context, bond_df, "bondpower_lowercase", args[0])
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


async def daemon(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Lists the complete information of a Daemon for DarkChip rules.")

    daemon_info = await find_value_in_table(context, daemon_df, "name_lowercase", args[0])
    if daemon_info is None:
        return

    daemon_name = daemon_info["Name"]
    daemon_quote = daemon_info["Quote"]
    daemon_domain = daemon_info["Domain"]
    daemon_tribute = daemon_info["Tribute"]
    daemon_tribute_description = daemon_info["TributeDescription"]
    daemon_chaosUnison = daemon_info["ChaosUnison"]
    daemon_chaosUnison_description = daemon_info["ChaosUnisonDescription"]
    daemon_signatureChip = daemon_info["SignatureDarkChip"]
    daemon_description = "**__Domain:__** *%s*\n\n" % (daemon_domain) + \
                         "**__Tribute:__** *%s*\n*%s*\n\n" % (daemon_tribute, daemon_tribute_description) + \
                         "**__ChaosUnison:__** *%s*\n*%s*\n\n" % (daemon_chaosUnison, daemon_chaosUnison_description) + \
                         "**__Signature DarkChip:__** *%s*" % daemon_signatureChip

    embed = discord.Embed(title="**__{}__**".format(daemon_name),
                          color=0x000000)
    embed.set_thumbnail(url=daemon_info["ImageLink"])
    embed.add_field(name="***''{}''***".format(daemon_quote),
                    value=daemon_description)
    return await koduck.sendmessage(context["message"], sendembed=embed)


async def element(context, *args, **kwargs):
    current_element_categories = ", ".join(pd.unique(element_df["category"]))
    if len(args) < 1:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Give you random elements from the Element Generation table. To use, enter `>element [#]` or `>element [category] [#]`!\n" +
                                                    "Categories: **%s**" % current_element_categories)
    args = args[0].split()
    if len(args) > 2:
        return await koduck.sendmessage(context["message"],
                                        sendcontent="Command is too long! Just give me `>element [#]` or `>element [category] [#]`!")

    element_return_number = 1  # number of elements to return
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
                                        sendcontent="That's too many elements! Are you sure you need more than 12?")

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


async def invite(context, *args, **kwargs):
    invite_link = "https://discordapp.com/oauth2/authorize?client_id=572878200397627412&scope=bot&permissions=0"
    color = 0x71c142
    embed = discord.Embed(title="Invite ProgBOT to your server!",
                          color=color,
                          url=invite_link,
                          description=invite_link)
    return await koduck.sendmessage(context["message"], sendembed=embed)


def setup():
    koduck.addcommand("updatecommands", updatecommands, "prefix", 3)


setup()
koduck.client.run(settings.token)
