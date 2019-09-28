import discord
import asyncio
import sys, os, random
import koduck, yadon
import settings

#Background task is run every set interval while bot is running (by default every 10 seconds)
async def backgroundtask():
    pass
settings.backgroundtask = backgroundtask

##################
# BASIC COMMANDS #
##################
#Be careful not to leave out this command or else a restart might be needed for any updates to commands
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
    THEmessagecontent = context["paramline"][context["paramline"].index(settings.paramdelim)+1:].strip()
    return await koduck.sendmessage(context["message"], sendchannel=THEchannel, sendcontent=THEmessagecontent, ignorecd=True)

async def changestatus(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.client.change_presence(game=discord.Game(name=""))
    else:
        return await koduck.client.change_presence(game=discord.Game(name=context["paramline"]))

async def updatesettings(context, *args, **kwargs):
    koduck.updatesettings()
    return

#note: discord server prevents any user, including bots, from changing usernames more than twice per hour
#bot name is updated in the background task, so it won't update immediately
async def updatesetting(context, *args, **kwargs):
    if len(args) < 2:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_updatesetting_noparam)
    variable = args[0]
    value = context["paramline"][context["paramline"].index(settings.paramdelim)+1:].strip()
    result = koduck.updatesetting(variable, value, koduck.getuserlevel(context["message"].author.id))
    if result is not None:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_updatesetting_success.format(variable, result, value))
    else:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_updatesetting_failed)

async def addsetting(context, *args, **kwargs):
    if len(args) < 2:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_updatesetting_noparam)
    variable = args[0]
    value = context["paramline"][context["paramline"].index(settings.paramdelim)+1:].strip()
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
    #need exactly one mentioned user (the order in the mentioned list is unreliable)
    if len(context["message"].mentions) != 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_nomentioneduser)
    
    userid = context["message"].mentions[0].id
    userlevel = koduck.getuserlevel(userid)
    
    #already an admin
    if userlevel == 2:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_addadmin_failed.format(settings.botname))
    else:
        koduck.updateuserlevel(userid, 2)
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_addadmin_success.format(userid, settings.botname))

async def unadmin(context, *args, **kwargs):
    #need exactly one mentioned user (the order in the mentioned list is unreliable)
    if len(context["message"].mentions) != 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_nomentioneduser)
    
    userid = context["message"].mentions[0].id
    userlevel = koduck.getuserlevel(userid)
    
    #not an admin
    if userlevel < 2:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_removeadmin_failed.format(settings.botname))
    else:
        koduck.updateuserlevel(userid, 1)
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_removeadmin_success.format(userid, settings.botname))

#Searches through the past settings.purgesearchlimit number of messages in this channel and deletes given number of bot messages
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
    #need exactly one mentioned user (the order in the mentioned list is unreliable)
    if len(context["message"].mentions) != 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_nomentioneduser)
    
    userid = context["message"].mentions[0].id
    userlevel = koduck.getuserlevel(userid)
    
    #already restricted
    if userlevel == 0:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_restrict_failed)
    #don't restrict high level users
    elif userlevel >= 2:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_restrict_failed2.format(settings.botname))
    else:
        koduck.updateuserlevel(userid, 0)
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_restrict_success.format(userid, settings.botname))

async def unrestrictuser(context, *args, **kwargs):
    #need exactly one mentioned user (the order in the mentioned list is unreliable)
    if len(context["message"].mentions) != 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_nomentioneduser)
    
    userid = context["message"].mentions[0].id
    userlevel = koduck.getuserlevel(userid)
    
    if userlevel != 0:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_unrestrict_failed)
    else:
        koduck.updateuserlevel(userid, 1)
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_unrestrict_success.format(userid, settings.botname))

#When someone says a trigger message, respond with a custom response!
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
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_addresponse_success.format(trigger, response))

async def removeresponse(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_removeresponse_noparam)
    trigger = args[0]
    result = yadon.RemoveRowFromTable(settings.customresponsestablename, trigger)
    if result == -1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_removeresponse_failed.format(trigger))
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
    #filter out the commands that the user doesn't have permission to run
    currentlevel = koduck.getuserlevel(context["message"].author.id)
    availablecommands = []
    for commandname in koduck.commands.keys():
        command = koduck.commands[commandname]
        if command[2] <= currentlevel and command[1] == "prefix":
            availablecommands.append(commandname)
    return await koduck.sendmessage(context["message"], sendcontent=", ".join(availablecommands))

async def help(context, *args, **kwargs):
    #Default message if no parameter is given
    if len(args) == 0:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_help.replace("{cp}", settings.commandprefix).replace("{pd}", settings.paramdelim))
    #Try to retrieve the help message for the query
    else:
        querycommand = args[0]
        try:
            #Use {cp} for command prefix and {pd} for parameter delimiter
            return await koduck.sendmessage(context["message"], sendcontent=getattr(settings, "message_help_{}".format(querycommand)).replace("{cp}", settings.commandprefix).replace("{pd}", settings.paramdelim))
        except AttributeError:
            return await koduck.sendmessage(context["message"], sendcontent=settings.message_help_unknowncommand)

async def userinfo(context, *args, **kwargs):
    #if there is no mentioned user (apparently they have to be in the server to be considered "mentioned"), use the message sender instead
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
    
    #these properties only appear in Member object (subclass of User) which is only available from Servers
    if context["message"].server is not None:
        game = user.game
        joindate = user.joined_at
        color = user.color
        if game is None:
            embed = discord.Embed(title="{}#{}".format(username, discr), description=str(user.status), color=color)
        else:
            embed = discord.Embed(title="{}#{}".format(username, discr), description="Playing {}".format(game.name), color=color)
        embed.add_field(name="Account creation date", value=creationdate.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)
        embed.add_field(name="Server join date", value=joindate.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)
        embed.set_thumbnail(url=avatar)
        return await koduck.sendmessage(context["message"], sendembed=embed)
    else:
        embed = discord.Embed(title="{}#{}".format(username, discr), description="Account creation date: {}".format(creationdate.strftime("%Y-%m-%d %H:%M:%S UTC")))
        embed.set_thumbnail(url=avatar)
        return await koduck.sendmessage(context["message"], sendembed=embed)

async def roll(context, *args, **kwargs):
    parameters = [1, settings.rolldefaultmax, 0] #quantity, max, filter
    
    #parse parameters
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
    
    #quantity should not be negative
    parameters[0] = max(parameters[0], 1)
    
    #roll dice!
    results = []
    for i in range(parameters[0]):
        if parameters[1] >= 0:
            results.append(random.randint(1, parameters[1]))
        else:
            results.append(random.randint(parameters[1], 1))
    
    #print output
    if parameters[2] != 0:
        successes = 0
        for i in range(len(results)):
            if results[i] <= parameters[2]:
                results[i] = "~~{}~~".format(results[i])
            else:
                successes += 1
        return await koduck.sendmessage(context["message"], sendcontent="{} _rolls..._ ({}) = **__{} hits!__**".format(context["message"].author.mention, ", ".join([str(x) for x in results]) if len(results) > 1 else results[0], successes))
    else:
        return await koduck.sendmessage(context["message"], sendcontent="{} _rolls a..._ **{}!**".format(context["message"].author.mention, ", ".join([str(x) for x in results]) if len(results) > 1 else results[0]))

async def tag(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent="Give me a Battle Chip tag and I can pull up its info for you!")
    table = yadon.ReadTable("tagdata")
    case_insensitive =  {key.lower():key for key in table.keys()}
    try:
        name = case_insensitive[args[0].lower()]
    except KeyError:
        return await koduck.sendmessage(context["message"], sendcontent="I don't recognize that Battle Chip tag!")
    values = table[name]
    
    
    embed = discord.Embed(title="__{}{}__".format("{}".format(name), " ({})".format(table[name][0]) if values[0] != "-" else""), description=(table[name][1]), color=0x24ff00)
    return await koduck.sendmessage(context["message"], sendembed=embed)

async def chip(context, *args, **kwargss):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent="Give me the name of a Battle Chip and I can pull up its info for you!")
    elif len(args) > 5:
        return await koduck.sendmessage(context["message"], sendcontent="Too many chips, no spamming!")
    table = yadon.ReadTable("chipdata")
    case_insensitive =  {key.lower():key for key in table.keys()}
    for arg in args:
        try:
            name = case_insensitive[arg.lower()]
        except KeyError:
            return await koduck.sendmessage(context["message"], sendcontent="I don't recognize that Battle Chip!")
            continue
        values = table[name]
    
        damage = values[0]
        type = values[1]
        description = values[2]
        categroy = values[3]
        tags = values[4]
        crossover = values[5]
        
        if "Mega" in values[5]:
          color = 0xA8E8E8
        elif "ChitChat" in values[5]:
          color = 0xff8000
        elif "Radical Spin" in values[5]:
          color = 0x3f5cff
        elif "Underground Broadcast" in values[5]:
          color = 0x73ab50
        elif "Mystic Lilies" in values[5]:
          color = 0x99004c
        elif "Dark" in values[5]:
          color = 0xB088D0
        elif "Item" in values[3]:
          color = 0xffffff
        else:
          color = 0xbfbfbf
        embed = discord.Embed(title="__{}{}__".format("{}".format(name), " ({} Chip)".format(values[5]) if values[5] != "-" else""), color=color)
        embed.add_field(name="**[{}{}{}{}]**".format("{} Damage/".format(values[0]) if values[0] != "-" else "", "{}/".format(values[1]) if values[1] != "-" else "", values[3], "/{}".format(values[4]) if values[4] != "-" else ""), value="_{}_".format(values[2]))
        await koduck.sendmessage(context["message"], sendembed=embed)

async def power(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent="Give me the name of a Navi Power and I can pull up its info for you!")
    table = yadon.ReadTable("powerdata")
    case_insensitive =  {key.lower():key for key in table.keys()}
    try:
        name = case_insensitive[args[0].lower()]
    except KeyError:
         return await koduck.sendmessage(context["message"], sendcontent="I don't recognize that NaviPower!")
    values = table[name]
    
    category = values[0]
    type = values[1]
    description = values[2]
    
    if category in ["Sense", "Info", "Coding"]:
        color = 0x81A7C6
    elif category in ["Strength", "Speed", "Stamina"]:
        color = 0xDF8F8D
    elif category in ["Charm", "Bravery", "Affinity"]:
        color = 0xF8E580
    else:
        color = 0xffffff
    embed = discord.Embed(title="__{}__".format(name), color=color)
    embed.add_field(name="**[{}{}]**".format("{} Power".format(values[0]),"/{}".format(values[1]) if values[1] != "-" else ""), value="_{}_".format(values[2]))
    return await koduck.sendmessage(context["message"], sendembed=embed)

async def NCP(context, *args, **kwargs):
    if len(args) <1:
        return await koduck.sendmessage(context["message"], sendcontent="Give me the name of an NCP and I can pull up its info for you!")
    table = yadon.ReadTable("ncpdata")
    case_insensitive =  {key.lower():key for key in table.keys()}
    try:
        name = case_insensitive[args[0].lower()]
    except KeyError:
         return await koduck.sendmessage(context["message"], sendcontent="I don't recognize that NCP!")
    values = table[name]
    
    exabytes = values[0]
    power = values[1]
    description = values[2]
    crossover = values[3]
    
    if power in ["LockOn", "Volley", "BlindMode", "Splash", "Tracker", "Refresh", "Reconfig", "Analyze", "Foresight", "Extend", "MapEdit", "HotSwap", "Disruption", "Firewall", "NoClip"]:
        color = 0x81A7C6
    elif power in ["Breakcharge", "Followthrough", "Gutsy", "Shockwave", "Shatter", "Warp", "Afterimages", "JumpJets", "Sneakrun", "ArtfulDodger", "Regenerate", "Clear", "KineticArmor", "Reflect", "HyperArmor"]:
        color = 0xDF8F8D
    elif power in ["Overwrite", "ModelEdit", "Playback", "Harmless", "Hypnotize", "Rally", "Bodyguard", "Vengeance", "Glare", "Duel", "Save", "CodeInjection", "Shift", "Control", "Alt"]:
        color = 0xF8E580
    elif crossover in ["ChitChat"]:
        color = 0xff8000
    elif crossover in ["Skateboard Dog"]:
        color = 0xff0000
    elif crossover in ["Mystic Lilies"]:
        color = 0x99004c
    else:
        color = 0xffffff
    embed = discord.Embed(title="__{}{}__".format((name)," ({} Crossover NCP)".format(values[3]) if values[3] != "-" else ""), color=color)
    embed.add_field(name="**[{}{}]**".format("{} EB".format(values[0]), "/{} Power Upgrade NCP".format(values[1]) if values[1] != "-" else ""), value="_{}_".format(values[2]))
    return await koduck.sendmessage(context["message"], sendembed=embed)

async def virus(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent="Give me the name of a virus and I can pull up its info for you!")
    elif len(args) > 5:
        return await koduck.sendmessage(context["message"], sendcontent="Too many viruses, no spamming!")
    table = yadon.ReadTable("virusdata")
    case_insensitive =  {key.lower():key for key in table.keys()}
    for arg in args:
        try:
            name = case_insensitive[args[0].lower()]
        except KeyError:
            return await koduck.sendmessage(context["message"], sendcontent="I don't recognize that virus!")
            continue
        values = table[name]
    
        embed = discord.Embed(title="__{}__".format(name), description="_{}_".format(table[name][17]), color=0x7c00ff)
        embed.set_thumbnail(url=values[19])
        await koduck.sendmessage(context["message"], sendembed=embed)

async def virusx(context, *args, **kwargs):
    if len(args) <1:
        return await koduck.sendmessage(context["message"], sendcontent="Give me the name of a virus and I can pull up its full info for you!")
    table = yadon.ReadTable("virusdata")
    case_insensitive =  {key.lower():key for key in table.keys()}
    try:
        name = case_insensitive[args[0].lower()]
    except KeyError:
         return await koduck.sendmessage(context["message"], sendcontent="I don't recognize that virus!")
    values = table[name]
    
    HP = values[0]
    Element = values[1]
    Mind = values[2]
    Body = values[3]
    Soul = values[4]
    Sense = values[5]
    Info = values[6]
    Coding = values[7]
    Strength = values[8]
    Speed = values[9]
    Stamina = values[10]
    Charm = values[11]
    Bravery = values[12]
    Affinity = values[13]
    Powers = values[14]
    Drops = values[15]
    Tags = values[16]
    Description = values[17]
    Category = values[18]
    
    embed = discord.Embed(title="__{}__".format(name), color=0x7c00ff)
    stats = ["HP", "Element", "Mind", "Body", "Soul", "Sense", "Info", "Coding", "Strength", "Speed", "Stamina", "Charm", "Bravery", "Affinity"]
    stats_string = ""
    for i in range(5, len(stats)):
        if values[i] != "-":
            stats_string += "{} {}/".format(values[i], stats[i])
    stats_string = stats_string[:-1]
    
    embed.set_thumbnail(url=values[19])
    embed.add_field(name="**{} HP**".format(HP), value="**_Element: {}_**\n{} Mind/{} Body/{} Soul\n{}\nPowers: {}\nDrops: {}\n**__Tags: {}__**\n_''{}''_".format(Element, Mind, Body, Soul, stats_string, Powers, Drops, Tags, Description), inline=True)
    embed.set_footer(text="Category: {}.".format(Category))
    return await koduck.sendmessage(context["message"], sendembed=embed)

async def query(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent="This command can sort battlechips, NCPs, and powers by Category, and single out Crossover Content chips!")
    table = yadon.ReadTable("querydata")
    results = []
    for chipname, values in table.items():
        if args[0].lower() == values[0].lower():
            results.append(chipname)
        elif values[1].startswith("[") and args[0].lower() == values[1][1:values[1].index("]")].lower():
            results.append(chipname)
    if not results:
        return await koduck.sendmessage(context["message"], sendcontent="I can't find any chips, NCPs, or Powers in that Category, or from that Crossover title.")
    else:
        return await koduck.sendmessage(context["message"], sendcontent="*Battlechips/NCPs/Powers in the ''``{}``'' category, or from that specific Crossover...*\n**{}**".format(args[0],", ".join(results)))

async def mysterydata(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent="Please specify either Common, Uncommon, or Rare MysteryData.")
    table = yadon.ReadTable("mysterydata")
    
    if args[0].lower() == "common":
        firstroll = random.randint(1, 6)
        if firstroll in [1, 2]:
            return await koduck.sendmessage(context["message"], sendcontent="You get: [2d6] * 100 Zenny")
        elif firstroll in [3, 4]:
            secondroll = random.randint(1, 36)
        elif firstroll == 5:
            secondroll = random.randint(37, 72)
        elif firstroll == 6:
            secondroll = random.randint(73, 78)
    
    elif args[0].lower() == "uncommon":
        firstroll = random.randint(1, 6)
        if firstroll in [1, 2]:
            return await koduck.sendmessage(context["message"], sendcontent="You get: [2d6] * 250 Zenny")
        elif firstroll in [3, 4]:
            secondroll = random.randint(79, 114)
        elif firstroll == 5:
            secondroll = random.randint(115, 150)
        elif firstroll == 6:
            secondroll = random.randint(151, 156)
    
    elif args[0].lower() == "rare":
        firstroll = random.randint(1, 6)
        if firstroll in [1, 2]:
            return await koduck.sendmessage(context["message"], sendcontent="You get: [2d6] * 500 Zenny")
        elif firstroll in [3, 4]:
            secondroll = random.randint(157, 192)
        elif firstroll == 5:
            secondroll = random.randint(193, 228)
        elif firstroll == 6:
            secondroll = random.randint(229, 234)
    
    else:
      return await koduck.sendmessage(context["message"], sendcontent="Please specify either Common, Uncommon, or Rare MysteryData.")
    values = table[str(secondroll)]
    
    #Color changes based on MysteryData Selection
    if (values[1]) in["Common"]:
        color = 0x48C800
    elif (values[1]) in["Uncommon"]:
        color = 0x00E1DF
    elif (values[1]) in["Rare"]:
        color = 0xD8E100
    else :
        color = 0xffffff
    
    embed = discord.Embed(title="__{} MysteryData__".format(values[1]), description="_{} accessed the MysteryData..._\n \nGot: **{}{}! **".format(context["message"].author.mention, values[0], " " + values[2] if values[2] != "-" else ""), color=color)
    if values[1] in["Common"]:
        embed.set_thumbnail(url = "https://raw.githubusercontent.com/gskbladez/meddyexe/master/virusart/commonmysterydata.png")
    elif values[1] in["Uncommon"]:
        embed.set_thumbnail(url = "https://raw.githubusercontent.com/gskbladez/meddyexe/master/virusart/uncommonmysterydata.png")
    elif values[1] in["Rare"]:
        embed.set_thumbnail(url = "https://raw.githubusercontent.com/gskbladez/meddyexe/master/virusart/raremysterydata.png")
    
    return await koduck.sendmessage(context["message"], sendembed=embed)

async def mysteryreward(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent="Please specify either Common, Uncommon, or Rare MysteryData.")
    table = yadon.ReadTable("mysterydata")
    
    if args[0].lower() == "common":
        firstroll = random.randint(1, 3)
        if firstroll in [1, 2]:
            secondroll = random.randint(1, 36)
        elif firstroll == 3:
            secondroll = random.randint(37, 72)
    
    elif args[0].lower() == "uncommon":
        firstroll = random.randint(1, 3)
        if firstroll in [1, 2]:
            secondroll = random.randint(79, 114)
        elif firstroll == 3:
            secondroll = random.randint(115, 150)
    
    elif args[0].lower() == "rare":
        firstroll = random.randint(1, 3)
        if firstroll in [1, 2]:
            secondroll = random.randint(157, 192)
        elif firstroll == 3:
            secondroll = random.randint(193, 228)
    
    else:
      return await koduck.sendmessage(context["message"], sendcontent="Please specify either Common, Uncommon, or Rare MysteryData.")
    values = table[str(secondroll)]
    
    #Color changes based on MysteryData Selection
    if (values[1]) in["Common"]:
        color = 0x48C800
    elif (values[1]) in["Uncommon"]:
        color = 0x00E1DF
    elif (values[1]) in["Rare"]:
        color = 0xD8E100
    else :
        color = 0xffffff
    
    embed = discord.Embed(title="__{} MysteryData__".format(values[1]), description="_{} accessed the MysteryData..._\n \nGot: **{}{}! **".format(context["message"].author.mention, values[0], " " + values[2] if values[2] != "-" else ""), color=color)
    if values[1] in["Common"]:
        embed.set_thumbnail(url = "https://raw.githubusercontent.com/gskbladez/meddyexe/master/virusart/commonmysterydata.png")
    elif values[1] in["Uncommon"]:
        embed.set_thumbnail(url = "https://raw.githubusercontent.com/gskbladez/meddyexe/master/virusart/uncommonmysterydata.png")
    elif values[1] in["Rare"]:
        embed.set_thumbnail(url = "https://raw.githubusercontent.com/gskbladez/meddyexe/master/virusart/raremysterydata.png")
    
    return await koduck.sendmessage(context["message"], sendembed=embed)

async def bond(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent="Give me a Bond Power and I can pull up its info for you!")
    table = yadon.ReadTable("bonddata")
    case_insensitive =  {key.lower():key for key in table.keys()}
    try:
        name = case_insensitive[args[0].lower()]
    except KeyError:
        return await koduck.sendmessage(context["message"], sendcontent="I don't recognize that Bond Power!")
    values = table[name]
    
    bondpoints = values[0]
    description = values[1]
    
    embed = discord.Embed(title="__{}__".format(name), color=0x24ff00)
    embed.add_field(name="**({})**".format(values[0]), value= "_{}_".format(values[1]))
    return await koduck.sendmessage(context["message"], sendembed=embed)

async def daemon(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent="Lists the complete information of a Daemon for DarkChip rules.")
    table = yadon.ReadTable("daemondata")
    case_insensitive =  {key.lower():key for key in table.keys()}
    try:
        name = case_insensitive[args[0].lower()]
    except KeyError:
        return await koduck.sendmessage(context["message"], sendcontent="I don't recognize that Daemon!")
    values = table[name]
    
    Name = "_''{}''_".format(values[0])
    Domain = "**__Domain:__** _{}_".format(values[1])
    Tribute = "\n\n**__Tribute:__** _{}_".format(values[2])
    ChaosUnison = "\n\n**__ChaosUnison:__** _{}_".format(values[3])
    SignatureChip = "\n\n**__Signature DarkChip:__** _{}_".format(values[4])
    Description = "{}{}{}{}".format(Domain, Tribute, ChaosUnison, SignatureChip)

    embed = discord.Embed(title="**__{}__**".format("{}".format(name)), color=0x000000)
    embed.set_thumbnail(url=values[5])
    embed.add_field(name=Name, value=Description)
    return await koduck.sendmessage(context["message"], sendembed=embed)

async def element(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent="Categories: **Nature, Fantasy, Science, Actions, Art, ???**")
    table = yadon.ReadTable("elementdata")
    
    if args[0].lower == "nature":
        element = random.randint(1, 36)
    #this is incomplete, don't mind this at all...
    else:
        element = random.randint(1, 216)
    values = table[str(element)]
    
    embed = discord.Embed(title="Picked a random {} Element...".format(values[1]), color=color)
    embed.add_field(name="**{}**".format(values[0]))
    return await koduck.sendmessage(context["message"], sendembed=embed)

async def rulebook(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent="NetBattlers Beta 4 Official Rulebook (high-res): <http://www.merrymancergames.com/wp-content/uploads/2019/06/NetBattlers-Beta-4-Full-Res.pdf>\nNetBattlers Beta 4 Official Rulebook (mobile-friendly): <http://www.merrymancergames.com/wp-content/uploads/2019/06/NetBattlers-Beta-4-Mobile.pdf>\nNetBattlers Advance, The Supplementary Rulebook: <http://www.merrymancergames.com/wp-content/uploads/2019/06/NetBattlers-Advance-v3.1.pdf>")

def setup():
    koduck.addcommand("updatecommands", updatecommands, "prefix", 3)

setup()
koduck.client.run(settings.token)