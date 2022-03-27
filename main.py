import discord
import os
import koduck
import yadon
import settings
import pandas as pd
from dotenv import load_dotenv
import mainadvance
import mainroll
import mainsafety
import mainnb


load_dotenv()
bot_token = os.getenv('DISCORD_TOKEN')

commands_df = pd.read_csv(settings.commandstablename, sep="\t").fillna('')


# Background task is run every set interval while bot is running (by default every 10 seconds)
async def backgroundtask():
    await clean()
    return


async def clean():
    mainadvance.clean_audience() # cleans up audience_data if it hasn't been used in AUDIENCE_TIMEOUT
    mainadvance.clean_spotlight() # cleans up spotlight_db if it hasn't been used in SPOTLIGHT_TIMEOUT
    return


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

    def cmd_func(row):
        if "advance" in row["Module"]:
            koduck.addcommand(row['Command'], getattr(mainadvance, row['Function']), row['Type'], int(row['Permission']))
        elif "safety" in row["Module"]:
            koduck.addcommand(row['Command'], getattr(mainsafety, row['Function']), row['Type'], int(row['Permission']))
        elif "roll" in row["Module"]:
            koduck.addcommand(row['Command'], getattr(mainroll, row['Function']), row['Type'], int(row['Permission']))
        elif "base" in row["Module"]:
            koduck.addcommand(row['Command'], getattr(mainnb, row['Function']), row['Type'], int(row['Permission']))
        else:
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
    if context["message"].channel.type is discord.ChannelType.private:
        pass
    elif (context["message"].author.id == context["message"].guild.owner_id):
        availablecommands = availablecommands.append(commands_df[commands_df["Permission"] == 4])
    availablecommands = availablecommands[~availablecommands["Hidden"]]
    cmd_groups = availablecommands.groupby(["Category"])
    return_msgs = ["**%s**\n*%s*" % (name, ", ".join(help_group["Command"].values)) for name, help_group in cmd_groups if
                   name]
    return await koduck.sendmessage(context["message"], sendcontent="\n\n".join(return_msgs))


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

async def invite(context, *args, **kwargs):
    invite_link = settings.invite_link
    color = 0x71c142
    embed = discord.Embed(title="Just click here to invite me to one of your servers!",
                          color=color,
                          url=invite_link)
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


def setup():
    koduck.addcommand("updatecommands", updatecommands, "prefix", 3)

settings.backgroundtask = backgroundtask
setup()
koduck.client.run(bot_token)  # to run locally, ask a dev for the .env file
