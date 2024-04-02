# -*- coding: utf_8 -*-
#Koduck connects to Discord as a bot and sets up a system in which functions are triggered by messages it can see that meet a set of conditions
#Yadon helps by using text files to keep track of data, like command details, settings, and user levels!
#- Yadon will provide fresh data whenever it's used. However, Koduck needs to keep its own track of two things and won't know if the text files were manually updated:
#-- Command details include function objects, which can't be passed in simply through text (from Yadon), since Koduck should not have access to these functions
#--- Which means command details can only be passed in from outside (main) either before client startup or through a function triggered by a command
#--- To make it easier to initialize commands from Yadon, Koduck will try to run the "refresh_commands" command after startup if it was passed in
#-- Settings are stored as attributes in a module where a bunch of required settings are initialized
#--- Settings read from the settings table will replace any initialized settings
#--- If a setting is removed from the settings table and refresh_settings() is called, the setting will still be active (to be fixed)

import discord
import asyncio
import settings, yadon
import sys, re
import datetime, functools, traceback
from typing import Optional, Union
from discord.ext import tasks

intents = discord.Intents.default()
client = discord.Client(
    activity=discord.Game(name=settings.default_status),
    intents=intents
    )
koduck_instance = None

class Koduck:
    #singleton
    def __new__(cls):
        if koduck_instance:
            return koduck_instance
        else:
            return super(Koduck, cls).__new__(cls)
    
    def __init__(self):
        self.client = client
        global koduck_instance
        koduck_instance = self
        self.command_tree = discord.app_commands.CommandTree(self.client)
        
        #command -> (function, type, tier)
        #command is a string which represents the command name
        #function is the function object to run when the command is triggered
        #type is a string that determines the trigger type of the command, should be one of (prefix, match, contain, slash)
        #tier is an integer which represents the user authority level required to run the command
        self.commands = {}
        self.prefix_commands = []
        self.match_commands = []
        self.contain_commands = []
        self.slash_commands = []
        
        self.output_history = {} #userid -> list of Discord Messages sent by bot in response to the user, oldest first (only keeps track since bot startup)
        self.last_message_DT = {} #channelid -> datetime of most recent Discord Message sent
        self.interactions = {} #interactionid -> boolean indicating whether the interaction received a response

        self.refresh_settings()
    
    #Records bot activity in the log text file, each log on one line, formatted by settings.log_format. Check log_fields below to see which fields can be formatted.
    #- type: type of activity
    #- message: the Discord Message that triggered the activity
    #- extra: an extra string that helps describes the activity (if, for example, a message is not involved)
    def log(self, type: str = "", message: Optional[discord.Message] = None, interaction: Optional[discord.Interaction] = None, extra: str = ""):
        log_fields = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f"),
            "type": type,
            "server_id": "",
            "server_name": "",
            "channel_id": "",
            "channel_name": "",
            "user_id": "",
            "discord_tag": "",
            "nickname": "",
            "message_content": "",
            "data": "",
            "extra": extra,
        }
        
        if message:
            log_fields["user_id"] = message.author.id
            username = message.author.name
            discr = message.author.discriminator
            log_fields["discord_tag"] = "{}#{}".format(username, discr)
            if message.guild is not None:
                log_fields["server_id"] = message.guild.id
                log_fields["channel_id"] = message.channel.id
                log_fields["server_name"] = message.guild.name
                log_fields["nickname"] = message.author.nick or ""
            if hasattr(message.channel, "name"):
                log_fields["channel_name"] = "#" + message.channel.name
            log_fields["message_content"] = message.content
            
            for property_name in ["embeds", "attachments", "stickers"]:
                if hasattr(message, property_name) and isinstance(getattr(message, property_name), list) and len(getattr(message, property_name)) > 0:
                    if not log_fields["data"]:
                        log_fields["data"] = {}
                    log_fields["data"][property_name] = []
                    for thing in getattr(message, property_name):
                        dump = {slot: getattr(thing, slot) for slot in thing.__slots__ if hasattr(thing, slot)}
                        log_fields["data"][property_name].append(dump)
        
        elif interaction:
            log_fields["user_id"] = interaction.user.id
            username = interaction.user.name
            discr = interaction.user.discriminator
            log_fields["discord_tag"] = "{}#{}".format(username, discr)
            if interaction.guild is not None:
                log_fields["server_id"] = interaction.guild.id
                log_fields["channel_id"] = interaction.channel.id
                log_fields["server_name"] = interaction.guild.name
                log_fields["nickname"] = interaction.user.nick or ""
            if hasattr(interaction.channel, "name"):
                log_fields["channel_name"] = "#" + interaction.channel.name
            if not log_fields["data"]:
                log_fields["data"] = {}
            log_fields["data"]["interaction"] = interaction.data
        
        log_string = settings.log_format.format(**log_fields)
        log_string = log_string.replace("\n", "\\n") + "\n"
        with open(settings.log_file, "a", encoding="utf8") as file:
            file.write(log_string)
    
    #Sends a Discord Message to a Discord Channel, possibly including a Discord Embed. Returns the Message object or a string if sending failed (i.e. cooldown is active)
    #- receive_message: the Discord Message or Interaction that triggered the activity (can be None)
    #- channel: the Discord Channel to send the message to; by default it's the channel where the triggering message was sent
    #- content: the String to include in the outgoing Discord Message
    #- embed: the Discord Embed to attach to the outgoing Discord Message
    #- file: a Discord File to include in the outgoing Discord Message
    #- view: a Discord View to include in the outgoing Discord Message
    #- ignore_cd: set this to True to ignore cooldown checks
    async def send_message(self, receive_message: Optional[Union[discord.Message, discord.Interaction]] = None,
                           channel: Optional[discord.abc.Messageable] = None,
                           ignore_cd: bool = False,
                           ephemeral: bool = False,
                           **kwargs):
        content = kwargs["content"] if "content" in kwargs else ""
        embed = kwargs["embed"] if "embed" in kwargs else None
        send_channel = channel

        user_id = receive_message.user.id if isinstance(receive_message, discord.Interaction) else receive_message.author.id

        # not sure what this does
        if send_channel is None and isinstance(receive_message, discord.Interaction):
            send_channel = receive_message.channel

        # If send_message was triggered by a user message, check cooldowns
        if receive_message is not None:
            if send_channel is None:
                send_channel = receive_message.channel
            
            #Check cooldowns
            cooldown_active = False
            # oops breaks on interactions
            user_level = self.get_user_level(user_id)
            if user_level < settings.ignore_cd_level:
                cooldown_active = self.check_channel_cooldown(send_channel.id)
                cooldown_active = cooldown_active or self.check_user_cooldown(user_id)
            
            #ignore message if bot is on channel cooldown or user cooldown
            if cooldown_active and not ignore_cd:
                self.log(type="cooldown", extra=settings.log_cooldown_active)
                return

        #send message to a "/run" interaction
        if isinstance(receive_message, SlashMessage) and channel is None:
            if not receive_message.interaction.response.is_done():
                the_message = await receive_message.interaction.response.send_message(**kwargs)
            else:
                the_message = await receive_message.interaction.followup.send(**kwargs)
        #send message to an interaction
        elif isinstance(receive_message, discord.Interaction) and channel is None:
            #This is not returning the sent message for some reason, so here's a workaround to fetch it after it's sent
            if not receive_message.response.is_done():
                await receive_message.response.send_message(**kwargs)
                the_message = await receive_message.original_response() # you seem get stuck on other errors, esp. spotlight...
            else:
                the_message = await receive_message.followup.send(**kwargs)
        #send message normally
        else:
            the_message = await send_channel.send(**kwargs)
        
        #track user outputs
        if receive_message is not None and the_message is not None:
            user_last_outputs = self.get_user_last_outputs(user_id)
            user_last_outputs.append(the_message)
            self.output_history[user_id] = user_last_outputs[max(0,len(user_last_outputs)-settings.output_history_size):]
        self.last_message_DT[send_channel.id] = datetime.datetime.now()
        
        return the_message
    
    #Assciates a String to a Function.
    #- command_name: a string which represents the command name (will be converted to lowercase)
    #- function: the function object that the command should call
    #- type: a string that determines the trigger type of the command, should be one of (prefix, match, contain, slash)
    #- tier: an integer which represents the level of authority needed to run this command
    #- description: description to display for slash commands
    def add_command(self, command_name, function, type, tier, description=""):
        if type == "prefix":
            self.prefix_commands.append(command_name.lower())
        elif type == "match":
            self.match_commands.append(command_name.lower())
        elif type == "contain":
            self.contain_commands.append(command_name.lower())
        elif type == "slash":
            self.slash_commands.append(command_name.lower())
            
            #wrap the function to log the interaction
            async def wrapper_function(interaction, **kwargs):
                interaction.command.koduck.log(type="interaction_user", interaction=interaction)
                if interaction.command.koduck.get_user_level(interaction.user.id) < interaction.command.command_tier:
                    return await interaction.response.send_message(content=settings.message_restricted_access, ephemeral=True)
                try:
                    return await function(interaction, **kwargs)
                except Exception as e:
                    exc_type, exc_value, _ = sys.exc_info()
                    error_message = "{}: {}".format(exc_type.__name__, exc_value)
                    traceback.print_exc()
                    if interaction.response.is_done():
                        await interaction.followup.send(content=settings.message_something_broke + "\n``{}``".format(error_message))
                    else:
                        await interaction.response.send_message(content=settings.message_something_broke + "\n``{}``".format(error_message), ephemeral=True)
                    koduck_instance.log(type="command_error", extra=settings.log_unhandled_error.format(error_message))
                    
            functools.update_wrapper(wrapper_function, function)
            
            app_command = discord.app_commands.Command(name=command_name, description=description, callback=wrapper_function)
            app_command.koduck = self
            app_command.command_tier = tier
            
            self.command_tree.add_command(app_command)
        else:
            return
        self.commands[command_name.lower()] = (function, type, tier)
    
    #Remove a command, returns 0 if successful, -1 if command not recognized
    def remove_command(self, command):
        if command not in self.commands.keys():
            return -1
        command_details = self.commands[command]
        {"prefix": self.prefix_commands, "match": self.match_commands, "contain": self.contain_commands, "slash": self.slash_commands}[command_details[1]].remove(command)
        del self.commands[command]
    
    def clear_commands(self):
        self.prefix_commands = []
        self.match_commands = []
        self.contain_commands = []
        self.slash_commands = []
        self.commands = {}
        self.command_tree.clear_commands(guild=None)
    
    #Registers a "run" slash command which simulates running a prefix command
    #This is helpful if the bot doesn't have the message_content intent (for unverified bots that are in over 100 servers) and you prefer to use prefix commands
    def add_run_slash_command(self):
        async def run_command(interaction, command: str):
            message_content = settings.command_prefix + command
            message = SlashMessage(interaction, message_content)
            await on_message(message)
            #If the command didn't respond with anything, send a default response
            if not interaction.response.is_done():
                await interaction.response.send_message(content=settings.run_command_default_response)
        
        app_command = discord.app_commands.Command(name=settings.run_command_name, description=settings.run_command_description, callback=run_command)
        app_command.koduck = self
        self.command_tree.add_command(app_command)
    
    async def refresh_app_commands(self):
        await self.command_tree.sync()
    
    #Use this function if settings table was manually updated (it will always be run on startup)
    #token can only be updated by restarting the bot
    #Note: settings is a module with attributes, so removing a setting manually from the table doesn't actually remove the attribute
    #Note: number values will be converted to int/float, and string values will convert "\n"s and "\t"s (since Yadon uses these to organize data)
    def refresh_settings(self):
        table = yadon.ReadTable(settings.settings_table_name, named_columns=True)
        if not table:
            return
        for key, setting in table.items():
            try:
                value = setting["Value"]
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
    #returns None if setting name doesn't exist or auth level is lower than setting's level (defaults to max user level if not specified or setting is in settings.py), returns old value if it does and updating its value succeeded
    def update_setting(self, variable, value, auth_level=settings.default_user_level):
        try:
            oldvalue = getattr(settings, variable)
        except AttributeError:
            return
        
        try:
            setting_level = int(yadon.ReadRowFromTable(settings.settings_table_name, variable, named_columns=True)["Tier"])
        except (IndexError, ValueError, TypeError):
            setting_level = settings.max_user_level
        if setting_level > auth_level:
            return
        
        value = value.replace("\n", "\\n").replace("\t", "\\t")
        yadon.WriteRowToTable(settings.settings_table_name, variable, {"Value": value, "Tier": setting_level}, named_columns=True)
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
    def add_setting(self, variable, value, auth_level=settings.default_user_level):
        try:
            getattr(settings, variable)
            return
        except AttributeError:
            pass
        
        value = value.replace("\n", "\\n").replace("\t", "\\t")
        yadon.WriteRowToTable(settings.settings_table_name, variable, {"Value": value, "Tier": auth_level}, named_columns=True)
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
    #returns None if setting doesn't exist or level is lower than setting's level (defaults to max user level if not specified or setting is in settings.py), returns the old value if it did
    def remove_setting(self, variable, auth_level=settings.default_user_level):
        try:
            value = getattr(settings, variable)
        except AttributeError:
            return
        
        try:
            setting_level = int(yadon.ReadRowFromTable(settings.settings_table_name, variable, named_columns=True)["Tier"])
        except (IndexError, ValueError):
            setting_level = settings.max_user_level
        if setting_level > auth_level:
            return
        
        yadon.RemoveRowFromTable(settings.settings_table_name, variable, named_columns=True)
        delattr(settings, variable)
        return value
    
    #Updates a user's authority level. Returns 0 if successful, -1 if not (i.e. level wasn't an integer)
    def update_user_level(self, user_id, level):
        #level should be an integer
        try:
            int(level)
        except ValueError:
            return -1
        
        yadon.WriteRowToTable(settings.user_levels_table_name, user_id, [str(level)])
        return 0
    
    def get_user_level(self, user_id):
        try:
            return int(yadon.ReadRowFromTable(settings.user_levels_table_name, str(user_id))[0])
        except (TypeError, IndexError, ValueError):
            return settings.default_user_level
    
    #Run a command as if it was triggered by a Discord message
    async def run_command(self, command, context=None, *args, **kwargs):
        if context is None:
            context = KoduckContext()
            context.koduck = koduck_instance
        try:
            function = self.commands[command][0]
            return await function(context, *args, **kwargs)
        except (KeyError, IndexError):
            return
    
    def check_channel_cooldown(self, channel_id):
        #calculate time since the last bot output on the given channel
        try:
            TD = datetime.datetime.now() - self.last_message_DT[channel_id]
            return ((TD.microseconds / 1000) + (TD.seconds * 1000) < settings.channel_cooldown)
        except KeyError:
            return False
    
    def check_user_cooldown(self, user_id):
        user_level = self.get_user_level(user_id)
        user_last_outputs = self.get_user_last_outputs(user_id)
        if len(user_last_outputs) > 0:
            #calculate time since the last bot output from the user
            TD = datetime.datetime.now(datetime.timezone.utc) - user_last_outputs[-1].created_at
            user_cooldown = 0
            while user_cooldown == 0 and user_level >= 0:
                try:
                    user_cooldown = getattr(settings, "user_cooldown_{}".format(user_level))
                except AttributeError:
                    user_level -= 1
            return ((TD.microseconds / 1000) + (TD.seconds * 1000) < user_cooldown)
        else:
            return False

    def get_user_last_outputs(self, user_id):
        try:
            user_last_outputs = self.output_history[user_id]
        except KeyError:
            self.output_history[user_id] = []
            user_last_outputs = self.output_history[user_id]
        return user_last_outputs

#Context that is attached to callbacks
class KoduckContext:
    def __init__(self):
        self.koduck = None
        self.message = None
        self.command = ""
        self.command_line = ""
        self.param_line = ""
        self.params = []
        self.args = []
        self.kwargs = {}
    
    #Allows subscriptable (i.e. context["message"] and context.message both work)
    def __getitem__(self, item):
        return getattr(self, item)

#Message-like object used in the "run" slash command
class SlashMessage():
    def __init__(self, interaction, message_content):
        self.interaction = interaction
        self.author = interaction.user
        self.channel = interaction.channel
        self.guild = interaction.guild
        self.content = message_content
        self.created_at = interaction.created_at
        self.raw_mentions = [int(x) for x in re.findall(r'<@!?([0-9]+)>', self.content)]
        self.raw_channel_mentions = [int(x) for x in re.findall(r'<#([0-9]+)>', self.content)]
        self.raw_role_mentions = [int(x) for x in re.findall(r'<@&([0-9]+)>', self.content)]
        self.mentions = []
        self.channel_mentions = []
        self.role_mentions = []
        if "resolved" in interaction.data:
            if "users" in interaction.data["resolved"]:
                self.mentions = list(interaction.data["resolved"]["users"].values())
            if "channels" in interaction.data["resolved"]:
                self.channel_mentions = list(interaction.data["resolved"]["channels"].values())
            if "roles" in interaction.data["resolved"]:
                self.role_mentions = list(interaction.data["resolved"]["roles"].values())

#background task is run every set interval while bot is running
#this method is added to the event loop automatically on bot setup
@tasks.loop(minutes=10)
async def background_task():
    if callable(settings.background_task):
        try:
            await settings.background_task()
        except Exception as e:
            exc_type, exc_value, _ = sys.exc_info()
            error_message = "{}: {}".format(exc_type.__name__, exc_value)
            traceback.print_exc()
            koduck_instance.log(type="background_task_error", extra=settings.log_unhandled_error.format(error_message))

@client.event
async def on_ready():
    print("Jacking In!")
    print("Name: {}".format(client.user.name))
    print("ID: {}".format(client.user.id))
    background_task.start()
    await koduck_instance.run_command("refreshcommands")

#Log some events from self
@client.event
async def on_message_edit(before, after):
    if after.author.id == koduck_instance.client.user.id:
        koduck_instance.log(type="message_edit", message=after)
@client.event
async def on_message_delete(message):
    if message.author.id == koduck_instance.client.user.id:
        koduck_instance.log(type="message_delete", message=message)

#interactions include app (slash) commands and components
@client.event
async def on_interaction(interaction):
    if interaction.user.id == koduck_instance.client.user.id:
        koduck_instance.log(type="interaction_self")
    #app command interactions are logged in the callback wraper above
    elif interaction.type != discord.InteractionType.application_command:
        koduck_instance.log(type="interaction_user", interaction=interaction)

#This is where messages come in, whether a command is triggered or not is checked, and parameters are parsed.
#Note: don't use " \ or = as command prefix or param delim, since they are used in parsing, it'll mess stuff up.
@client.event
async def on_message(message):
    #log messages from self
    if message.author.id == koduck_instance.client.user.id:
        koduck_instance.log(type="message_send", message=message)
    
    #ignore bot messages
    if message.author.bot:
        return
    
    try:
        #PARSE COMMAND AND PARAMS
        context, args, kwargs = KoduckContext(), [], {}
        context.koduck = koduck_instance
        context.message = message
        
        #PREFIX COMMANDS
        if message.content.startswith(settings.command_prefix):
            activity_type = "prefix_command"
            context.command_line = message.content[len(settings.command_prefix):]
            try:
                context.command = context.command_line[0:context.command_line.index(" ")].lower()
                context.param_line = context.command_line[context.command_line.index(" ")+1:]
            except ValueError:
                context.command = context.command_line.lower()
            
            #Check if it's a valid prefix command
            if context.command not in koduck_instance.prefix_commands:
                koduck_instance.log(type=activity_type, message=message, extra=settings.message_unknown_command)
                if isinstance(message, SlashMessage):
                    await koduck_instance.send_message(receive_message=message, content=settings.message_unknown_command, ephemeral=True)
                #Reset context
                context, args, kwargs = KoduckContext(), [], {}
                context.message = message
            
            #Else parse params
            else:
                #Things within quotes should escape parsing
                #Find things within quotes, replace them with a number (which shouldn't have param delim)
                temp = context.param_line
                quotes = []
                quote_matches = list(re.finditer(r'(["])(?:\\.|[^\\])*?\1', temp))
                quote_matches.reverse()
                for quote in quote_matches:
                    start = quote.span()[0]
                    end = quote.span()[1]
                    temp = temp[0:start] + '"{}"'.format(len(quotes)) + temp[end:]
                    quotes.append(quote.group())
                
                parsed_params = temp.split(settings.param_delim)
                #Weird thing
                if len(parsed_params) == 1 and parsed_params[0] == '':
                    parsed_params = []
                
                counter = len(quotes) - 1
                #Put the quotes back in, without the quote marks themselves
                def put_quotes_back(text, quotes, counter):
                    ans = text
                    while text.find('"{}"'.format(counter)) != -1 and counter >= 0:
                        ans = ans.replace('"{}"'.format(counter), quotes[counter][1:-1], 1)
                        counter -= 1
                    return (ans, counter)
                for param in parsed_params:
                    #Find equal signs that aren't preceded by backslash
                    equals = [match.span()[0] for match in filter(lambda match: match.span()[0] == 0 or param[match.span()[0]-1] != "\\", re.finditer(r'=', param))]
                    if len(equals) > 0:
                        keyword, counter = put_quotes_back(param[:param.index("=")].strip(), quotes, counter)
                        value, counter = put_quotes_back(param[param.index("=")+1:].strip(), quotes, counter)
                        kwargs[keyword] = value
                        context.params.append("{}={}".format(keyword, value))
                    else:
                        arg, counter = put_quotes_back(param.strip(), quotes, counter)
                        args.append(arg)
                        context.params.append(arg)
                context.args = args
                context.kwargs = kwargs
        
        #MATCH COMMANDS
        if not context.command:
            for command_name in koduck_instance.match_commands:
                if command_name == message.content.lower():
                    activity_type = "match_command"
                    context.command = command_name
                    break
        
        #CONTAIN COMMANDS
        if not context.command:
            for command_name in koduck_instance.contain_commands:
                if command_name in message.content.lower():
                    activity_type = "contain_command"
                    context.command = command_name
                    break
        
        if not context.command:
            return
        
        #CHECK PERMISSIONS OF USER
        user_level = koduck_instance.get_user_level(message.author.id)
        if user_level < koduck_instance.commands[context.command][2]:
            koduck_instance.log(type=activity_type, extra=settings.message_restricted_access)
            #notify user of restricted access only if it's a prefix or slash command
            if context.command in koduck_instance.prefix_commands:
                await koduck_instance.send_message(receive_message=message, content=settings.message_restricted_access, ephemeral=True)
            return
        
        koduck_instance.log(type=activity_type, message=message)
        #RUN THE COMMAND
        function = koduck_instance.commands[context.command][0]
        try:
            result = await function(context, *args, **kwargs)
        except TypeError as e:
            #only catch missing argument error to print a different message
            match = re.search(r'missing [0-9]+ required \w+ arguments?: (.+)', str(e))
            if not match:
                raise e
            return await koduck_instance.send_message(receive_message=message, content=settings.message_missing_params.format(match.group(1)))
        if isinstance(result, str):
            koduck_instance.log(type="result", extra=result)
    
    except Exception as e:
        exc_type, exc_value, _ = sys.exc_info()
        error_message = "{}: {}".format(exc_type.__name__, exc_value)
        traceback.print_exc()
        await koduck_instance.send_message(message, content=settings.message_something_broke + "\n``{}``".format(error_message), ignore_cd=True, ephemeral=True)
        koduck_instance.log(type="command_error", extra=settings.log_unhandled_error.format(error_message))