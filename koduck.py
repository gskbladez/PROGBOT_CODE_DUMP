# -*- coding: utf_8 -*-
#Koduck connects to Discord as a bot and sets up a system in which functions are triggered by messages it can see that meet a set of conditions
#Yadon helps by using text files to keep track of data, like command details, settings, and user levels!
#- Yadon will provide fresh data whenever it's used. However, Koduck needs to keep its own track of two things and won't know if the text files were manually updated:
#-- Command details include function objects, which can't be passed in simply through text (from Yadon), since Koduck should not have access to main
#--- Which means command details can only be passed in from outside (main) either before client startup or through a function triggered by a command
#--- To make it easier to initialize commands from Yadon, Koduck will try to run the "updatecommands" command after startup if it was passed in
#-- Settings are stored as attributes in a module where a bunch of required settings are initialized
#--- Settings read from the settings table will replace any initialized settings
#--- If a setting is removed from the settings table and updatesettings() is called, the setting will still be active (to be fixed)

import discord
import asyncio
import sys, os, traceback
import datetime
import settings, yadon

client = discord.Client()

#command -> (function, type, tier)
#command is a string which represents the command name
#function is the function object to run when the command is triggered
#type: a string that determines the trigger type of the command, should be one of (prefix, match, contain)
#tier is an integer which represents the user authority level required to run the command
commands = {}
prefixcommands = []
matchcommands = []
containcommands = []

outputhistory = {} #userid -> list of Discord Messages sent by bot in response to the user, oldest first (only keeps track since bot startup)
lastmessageDT = {} #channelid -> datetime of most recent Discord Message sent

is_python38 = sys.version[0:3] == '3.8'

#######################
#GENERAL BOT FUNCTIONS#
#######################
#Records bot activity in the log text files.
#- message: the Discord Message that triggered the activity (for retrieving stats like date, time, channel, and user)
#- logresult: a String that indicates the result of the activity (can be whatever you like)
def log(message=None, logresult=""):
    logresult = logresult.replace("\n", "\\n")
    
    if message is None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        #normal log file
        logstring = "{}\t\t\t\t\t{}\n".format(timestamp, logresult)
        with open(settings.logfile, "a", encoding="utf8") as file:
            file.write(logstring)
        
        #formatted log file
        logstring = settings.logformat.replace("%t", timestamp).replace("%s", "").replace("%c", "#" + "").replace("%u", "").replace("%U", "").replace("%n", "").replace("%m", "").replace("%r", logresult) + "\n"
        with open(settings.formattedlogfile, "a", encoding="utf8") as file:
            file.write(logstring)
    
    else:
        #determine some values
        logmessage = message.content.replace("\n", "\\n")
        if is_python38:
            timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
        else:
            timestamp = message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        username = message.author.name
        discr = message.author.discriminator
        if is_python38:
            server = message.guild
        else:
            server = message.server
        if server is not None:
            servername = server.name
            nickname = message.author.nick or ""
        else:
            servername = "None"
            nickname = ""
        if message.channel.name is not None:
            channelname = message.channel.name
        else:
            channelname = "None"
        
        #normal log file
        logstring = "{}\t{}\t{}\t{}\t{}\t{}\n".format(timestamp, server.id, message.channel.id if server is not None else "", message.author.id, logmessage, logresult)
        with open(settings.logfile, "a", encoding="utf8") as file:
            file.write(logstring)
        
        #formatted log file
        logstring = settings.logformat.replace("%t", timestamp).replace("%s", servername).replace("%c", "#" + channelname).replace("%u", username).replace("%U", "{}#{}".format(username, discr)).replace("%n", nickname).replace("%m", logmessage).replace("%r", logresult) + "\n"
        with open(settings.formattedlogfile, "a", encoding="utf8") as file:
            file.write(logstring)

#Sends a Discord Message to a Discord Channel, possibly including a Discord Embed. Returns the Message object or a string if sending failed (i.e. cooldown is active)
#- receivemessage: the Discord Message that triggered the activity (can be None)
#- sendchannel: the Discord Channel to send the message to; by default it's the channel where the triggering message was sent
#- sendcontent: the String to include in the outgoing Discord Message
#- sendembed: the Discord Embed to attach to the outgoing Discord Message
async def sendmessage(receivemessage, sendchannel=None, sendcontent="", sendembed=None, ignorecd=False):
    #If sendmessage was triggered by a user message, check cooldowns
    if receivemessage is not None:
        if sendchannel is None:
            sendchannel = receivemessage.channel
        
        #Check channel cooldown
        cooldownactive = False
        userlevel = getuserlevel(receivemessage.author.id)
        if userlevel < settings.ignorecdlevel:
            #calculate time since the last bot output on this channel
            global lastmessageDT
            try:
                TD = datetime.datetime.now() - lastmessageDT[sendchannel.id]
                cooldownactive = ((TD.microseconds / 1000) + (TD.seconds * 1000) < settings.channelcooldown)
            except KeyError:
                pass
        
        try:
            userlastoutputs = outputhistory[receivemessage.author.id]
        except KeyError:
            outputhistory[receivemessage.author.id] = []
            userlastoutputs = outputhistory[receivemessage.author.id]
        if len(userlastoutputs) > 0:
            #calculate time since the last bot output from the user
            if is_python38:
                TD = datetime.datetime.now() - userlastoutputs[-1].created_at
            else:
                TD = datetime.datetime.now() - userlastoutputs[-1].timestamp
            usercooldown = 0
            while usercooldown == 0 and userlevel >= 0:
                try:
                    usercooldown = getattr(settings, "usercooldown_{}".format(userlevel))
                except AttributeError:
                    userlevel -= 1
            cooldownactive = ((TD.microseconds / 1000) + (TD.seconds * 1000) < usercooldown) or cooldownactive
        
        #ignore message if bot is on channel cooldown or user cooldown
        if cooldownactive and not ignorecd:
            log(receivemessage, logresult=settings.message_cooldownactive)
            return
    
    #Discord messages cap at 2000 characters
    if len(sendcontent) > 2000:
        sendcontent = settings.message_resulttoolong.format(len(sendcontent))
    
    #send the message and track some data
    #THEmessage = await client.send_message(sendchannel, sendcontent, embed=sendembed)
    THEmessage = await receivemessage.channel.send(sendcontent, embed=sendembed)
    log(THEmessage)
    if receivemessage is not None:
        userlastoutputs.append(THEmessage)
        outputhistory[receivemessage.author.id] = userlastoutputs[max(0,len(userlastoutputs)-settings.outputhistorysize):]
    lastmessageDT[sendchannel.id] = datetime.datetime.now()
    
    return THEmessage

#Assciates a String to a Function.
#- command: a string which represents the command name (will be converted to lowercase)
#- function: the function object that the command should call
#- type: a string that determines the trigger type of the command, should be one of (prefix, match, contain)
#- tier: an integer which represents the level of authority needed to run this command
def addcommand(command, function, type, tier):
    if type == "prefix":
        prefixcommands.append(command.lower())
    elif type == "match":
        matchcommands.append(command.lower())
    elif type == "contain":
        containcommands.append(command.lower())
    else:
        return
    commands[command.lower()] = (function, type, tier)

#Remove a command, returns 0 if successful, -1 if command not recognized
def removecommand(command):
    if command not in commands.keys():
        return -1
    commanddetails = commands[command]
    {"prefix": prefixcommands, "match": matchcommands, "contain": containcommands}[commanddetails[1]].remove(command)
    del commands[command]

def clearcommands():
    prefixcommands = []
    matchcommands = []
    containcommands = []
    commands = {}

#Use this function if settings table was manually updated (it will always be run on startup)
#token can only be updated by restarting the bot
#botname is updated in the background task, so it won't update immediately
#Note: settings is a module with attributes, so removing a setting manually from the table doesn't actually remove the attribute
def updatesettings():
    table = yadon.ReadTable(settings.settingstablename)
    for key, values in table.items():
        try:
            value = values[0]
            #try to convert into float or int, otherwise treat as string
            try:
                if float(value) % 1 == 0:
                    value = int(value)
                else:
                    value = float(value)
            except ValueError:
                value = value.replace("\\n", "\n").replace("\\t", "\t")
        except IndexError:
            value = None
        setattr(settings, key, value)

#update a setting and updates the settings file accordingly
#returns None if setting name doesn't exist or auth level is lower than setting's level (defaults to 1), returns old value if it does and updating its value succeeded
def updatesetting(variable, value, authlevel=1):
    try:
        oldvalue = getattr(settings, variable)
    except AttributeError:
        return
    
    try:
        settinglevel = int(yadon.ReadRowFromTable(settings.settingstablename, variable)[1])
    except (IndexError, ValueError):
        settinglevel = 1
    if settinglevel > authlevel:
        return
    
    value = value.replace("\n", "\\n").replace("\t", "\\t")
    yadon.WriteRowToTable(settings.settingstablename, variable, [value, settinglevel])
    try:
        if float(value) % 1 == 0:
            value = int(value)
        else:
            value = float(value)
    except ValueError:
        value = value.replace("\\n", "\n").replace("\\t", "\t")
    setattr(settings, variable, value)
    return oldvalue

#add a setting and updates the settings file accordingly
#returns None if setting already exists, returns value if it doesn't
def addsetting(variable, value, authlevel=1):
    try:
        getattr(settings, variable)
        return
    except AttributeError:
        pass
    
    value = value.replace("\n", "\\n").replace("\t", "\\t")
    yadon.WriteRowToTable(settings.settingstablename, variable, [value, str(authlevel)])
    try:
        if float(value) % 1 == 0:
            value = int(value)
        else:
            value = float(value)
    except ValueError:
        value = value.replace("\\n", "\n").replace("\\t", "\t")
    setattr(settings, variable, value)
    return value

#remove a setting and updates the settings file accordingly
#returns None if setting doesn't exist or level is lower than setting's level (defaults to 1), returns the old value if it did
def removesetting(variable, authlevel=1):
    try:
        value = getattr(settings, variable)
    except AttributeError:
        return
    
    try:
        settinglevel = int(yadon.ReadRowFromTable(settings.settingstablename, variable)[1])
    except (IndexError, ValueError):
        settinglevel = 1
    if settinglevel > authlevel:
        return
    
    yadon.RemoveRowFromTable(settings.settingstablename, variable)
    delattr(settings, variable)
    return value

#Updates a user's authority level. Returns 0 if successful, -1 if not (i.e. level wasn't an integer)
def updateuserlevel(userid, level):
    #level should be an integer
    try:
        int(level)
    except ValueError:
        return -1
    
    yadon.WriteRowToTable(settings.userlevelstablename, userid, [str(level)])
    return 0

def getuserlevel(userid):
    try:
        return int(yadon.ReadRowFromTable(settings.userlevelstablename, userid)[0])
    except (TypeError, IndexError, ValueError):
        return 1

#Run a command as if it was triggered by a Discord message
async def runcommand(command, message=None, params=[]):
    try:
        function = commands[command][0]
        return await function(message, params)
    except (KeyError, IndexError):
        return

#######
#SETUP#
#######
updatesettings()

#background task is run every set interval while bot is running
async def backgroundtask():
    await client.wait_until_ready()
    while not client.is_closed:
        if client.user.bot and client.user.name != settings.botname:
            await client.edit_profile(username=settings.botname)
        if callable(settings.backgroundtask):
            client.loop.create_task(settings.backgroundtask())
        await asyncio.sleep(settings.backgroundtaskinterval)
client.loop.create_task(backgroundtask())

@client.event
async def on_ready():
    print("Jacking In!")
    print("Name: {}".format(client.user.name))
    print("ID: {}".format(client.user.id))
    await runcommand("updatecommands")
    if is_python38:
        await client.change_presence(status=discord.Status.online, activity=discord.Game(name='NetBattlers RPG'))
    else:
        await client.change_presence(status=discord.Status.Online, activity=discord.Game(name='NetBattlers RPG'))

##############
#INPUT OUTPUT#
##############
@client.event
async def on_message(message):
    #ignore bot messages
    if message.author.bot:
        return
    
    try:
        #PARSE COMMAND AND PARAMS
        context, args, kwargs = {"message": message, "command": ""}, [], {}
        
        #PREFIX COMMANDS
        if message.content.startswith(settings.commandprefix):
            context["commandline"] = message.content[len(settings.commandprefix):]
            try:
                context["command"] = context["commandline"][0:context["commandline"].index(" ")].lower()
                context["paramline"] = context["commandline"][context["commandline"].index(" ")+1:]
                context["params"] = context["paramline"].split(settings.paramdelim)
            except ValueError:
                context["command"] = context["commandline"].lower()
                context["params"] = []
            for param in context["params"]:
                if "=" in param:
                    keyword = param[:param.index("=")].strip()
                    value = param[param.index("=")+1:].strip()
                    kwargs[keyword] = value
                else:
                    args.append(param.strip())
            #Reset context if not a valid command
            if context["command"] not in prefixcommands:
                log(message, logresult=settings.message_unknowncommand)
                context, args, kwargs = {"message": message, "command": ""}, [], {}
        
        #MATCH COMMANDS
        if not context["command"]:
            for commandname in matchcommands:
                if commandname == message.content.lower():
                    context["command"] = commandname
                    break
        
        #CONTAIN COMMANDS
        if not context["command"]:
            for commandname in containcommands:
                if commandname in message.content.lower():
                    context["command"] = commandname
                    break
        
        if not context["command"]:
            return
        
        #CHECK PERMISSIONS OF USER
        userlevel = getuserlevel(message.author.id)
        if userlevel < commands[context["command"]][2]:
            #notify user of restricted access only if it's a prefix command
            if context["command"] in prefixcommands:
                await sendmessage(message, sendcontent=settings.message_restrictedaccess)
            log(None, settings.message_restrictedaccess)
            return
        
        log(message)
        #RUN THE COMMAND
        function = commands[context["command"]][0]
        result = await function(context, *args, **kwargs)
        if isinstance(result, str):
            log(None, result)
    
    except Exception as e:
        traceback.print_exc()
        await sendmessage(message, sendcontent=settings.message_somethingbroke)
        log(message, logresult=settings.message_unhandlederror)