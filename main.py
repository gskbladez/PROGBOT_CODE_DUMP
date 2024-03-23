import asyncio
import os

import discord
import typing
from dotenv import load_dotenv

from koduck import Koduck
import sys, logging
import yadon
import settings
import pandas as pd

import mainadvance
import mainroll
import mainsafety
import mainnb
import mainaprilfools

commands_df = pd.read_csv(settings.commands_table_name, sep="\t").fillna('')

#Required method to setup Koduck. Can also be run as a comamnd after startup to update any manual changes to the commands table.
async def refresh_commands(context, *args, **kwargs):
    errors = []

    def cmd_func(row):
        if "advance" in row["Module"]:
            context.koduck.add_command(row['Command'], getattr(mainadvance, row['Function']), row['Type'],
                                       int(row['Permission']), row["Description"])
        elif "safety" in row["Module"]:
            context.koduck.add_command(row['Command'], getattr(mainsafety, row['Function']), row['Type'],
                                       int(row['Permission']), row["Description"])
        elif "roll" in row["Module"]:
            context.koduck.add_command(row['Command'], getattr(mainroll, row['Function']), row['Type'],
                                       int(row['Permission']), row["Description"])
        elif "base" in row["Module"]:
            context.koduck.add_command(row['Command'], getattr(mainnb, row['Function']), row['Type'],
                                       int(row['Permission']), row["Description"])
        elif "fools" in row["Module"]:
            context.koduck.add_command(row['Command'], getattr(mainaprilfools, row['Function']), row['Type'],
                                       int(row['Permission']), row["Description"])
        else:
            context.koduck.add_command(row['Command'], globals()[row['Function']], row['Type'], int(row['Permission']), row["Description"])
        return

    if commands_df.shape[0] == 0:
        return
    if commands_df.shape[0] > 0:
        context.koduck.clear_commands()
        try:
            commands_df.apply(cmd_func, axis=1)
        except Exception as e:
            errors.append(f"Failed to import commands, starting with: `{str(e)}`")

    if settings.enable_run_command:
        context.koduck.add_run_slash_command()

    errors = "\n".join(errors)
    if context.message is not None:
        if errors:
            await context.koduck.send_message(context.message, content="There were some errors while refreshing commands:" + "\n" + errors)
        else:
            await context.koduck.send_message(context.message, content="Commands refreshed successfully")
    elif errors:
        print(errors)


#Background task is run every set interval while bot is running (by default every 10 seconds)
async def background_task(koduck_instance):
    pass
settings.background_task = background_task


# PROGBOTBOTTER
async def invite(context, *args, **kwargs):
    invite_link = settings.invite_link
    color = 0x71c142
    embed = discord.Embed(title="Just click here to invite me to one of your servers!",
                          color=color,
                          url=invite_link)

    return await context.koduck.send_message(receive_message=context["message"], embed=embed)

async def commands(context, *args, **kwargs):
    # filter out the commands that the user doesn't have permission to run
    currentlevel = context.koduck.get_user_level(context["message"].author.id)
    availablecommands = commands_df[commands_df["Permission"] <= currentlevel].sort_values(["Function", "Command", "Permission"])
    if context["message"].channel.type is discord.ChannelType.private:
        pass
    elif (context["message"].author.id == context["message"].guild.owner_id):
        availablecommands = availablecommands.append(commands_df[commands_df["Permission"] == 4])
    availablecommands = availablecommands[~availablecommands["Hidden"]]
    cmd_groups = availablecommands.groupby(["Category"])
    return_msgs = ["**%s**\n*%s*" % (name, ", ".join(help_group["Command"].values)) for name, help_group in cmd_groups if
                   name]
    return await context.koduck.send_message(receive_message=context["message"], content="\n\n".join(return_msgs))


async def bugreport(interaction: discord.Interaction, message: str):
    channelid = interaction.channel
    progbot_bugreport_channel = koduck.client.get_channel(settings.bugreport_channel_id)
    message_author = interaction.user
    if channelid.type is discord.ChannelType.private:
        message_guild = "Direct message"
    else:
        message_guild = interaction.guild.name
    embed = discord.Embed(title="**__New Bug Report!__**", description="_{}_".format(message),
                          color=0x5058a8)
    embed.set_footer(
        text="Submitted by: {}#{} ({})".format(message_author.name, message_author.discriminator, message_guild))
    embed.set_thumbnail(url="https://raw.githubusercontent.com/gskbladez/meddyexe/master/virusart/bug.png")
    await interaction.command.koduck.send_message(interaction, channel=progbot_bugreport_channel,
                                      embed=embed)
    await interaction.command.koduck.send_message(interaction, content="**_Bug Report Submitted!_**\nThanks for the help!")


async def ping(interaction: discord.Interaction, delay: int, option:str=""):
    await interaction.response.defer(thinking=True)
    await asyncio.sleep(delay)
    if option:
        return await interaction.command.koduck.send_message(interaction, content="pong!")
    await interaction.command.koduck.send_message(interaction, content="pong")


async def break_test(context, *args, **kwargs):
    return await context.koduck.send_message(receive_message=context["message"], content=str(0 / 0))


#Syncs the slash commands to Discord. This is not done automatically and should be done by running this command if changes were made to the slash commands.
async def refresh_app_commands(context, *args, **kwargs):
    await context.koduck.send_message(receive_message=context.message, content=settings.message_refresh_app_commands_progress)
    # takes more than 3 seconds to refresh app commands, now...
    await context.koduck.refresh_app_commands()


async def change_status(context, *args, **kwargs):
    if not context.param_line:
        return await context.koduck.client.change_presence(activity=discord.Game(name=""))
    else:
        return await context.koduck.client.change_presence(activity=discord.Game(name=context.param_line))


async def goodnight(interaction: discord.Interaction):
    interaction.command.koduck.send_message(interaction, content="Goodnight!")
    return await koduck.client.close()

load_dotenv()
bot_token = os.getenv('DISCORD_TOKEN')

required_files = [settings.commands_table_name, settings.user_levels_table_name]

bad_files = [f for f in required_files if not os.path.isfile(f)]
if bad_files:
    raise FileNotFoundError("Required files missing: %s " % ", ".join(bad_files))

koduck = Koduck()
koduck.add_command("refreshcommands", refresh_commands, "prefix", 3)
if settings.enable_debug_logger:
    log_handler = logging.FileHandler(filename=settings.debug_log_file_name, encoding='utf-8', mode='w')
    koduck.client.run(bot_token, log_handler=log_handler, log_level=logging.DEBUG)
else:
    koduck.client.run(bot_token, log_handler=None)