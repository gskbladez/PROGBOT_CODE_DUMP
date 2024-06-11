import asyncio
import os

import discord
import typing
from dotenv import load_dotenv

import sys, logging
import settings
from pandas import read_csv, DataFrame, Series
from discord.ext import tasks

from maincommon import commands_dict, commands_df, bot
import mainroll
import mainaprilfools
import mainsafety
#import mainadvance
#import mainnb

user_df = read_csv(settings.user_levels_table_name, sep="\t").fillna('')
user_dict = dict(zip(user_df["ID"], user_df["Level"]))

# bot is defined in maincommon

def _get_user_level(user_id: int):
    return user_dict[user_id]

#Background task is run every set interval while bot is running (by default every 10 seconds)
@tasks.loop(minutes=10)
async def background_task():
    #mainadvance.clean_audience() # cleans up audience_data if it hasn't been used in AUDIENCE_TIMEOUT
    #mainadvance.clean_spotlight() # cleans up spotlight_db if it hasn't been used in SPOTLIGHT_TIMEOUT
    pass


# PROGBOTBOTTER
@bot.tree.command(name='hello', description='Says Hello')
async def say_hello(interaction: discord.Interaction):
    await interaction.response.send_message('Hello!')


@bot.tree.command(name='invite', description=commands_dict["invite"])
async def invite(interaction: discord.Interaction):
    invite_link = settings.invite_link
    color = 0x71c142
    embed = discord.Embed(title="Click here to invite me to one of your servers!",
                          color=color,
                          url=invite_link)

    return await interaction.response.send_message(embed=embed)


@bot.tree.command(name='commands', description=commands_dict["commands"])
async def list_commands(interaction: discord.Interaction):
    # filter out the commands that the user doesn't have permission to run
    currentlevel = _get_user_level(interaction.user.id)
    availablecommands = commands_df[commands_df["Permission"] <= currentlevel].sort_values(["Function", "Command", "Permission"])
    if interaction.channel.type is discord.ChannelType.private:
        pass
    elif (interaction.user.id == interaction.guild.owner_id):
        availablecommands = availablecommands.append(commands_df[commands_df["Permission"] == 4])
        
    availablecommands = availablecommands[~availablecommands["Hidden"]]
    cmd_groups = availablecommands.groupby(["Category"])
    return_msgs = ["**%s**\n*%s*" % (name, ", ".join(help_group["Command"].values)) for name, help_group in cmd_groups if name]
    return await interaction.response.send_message(content="\n\n".join(return_msgs))


@bot.tree.command(name='bugreport', description=commands_dict['bugreport'])
async def bugreport(interaction: discord.Interaction, message: str):
    channelid = interaction.channel
    progbot_bugreport_channel = bot.get_channel(settings.bugreport_channel_id)
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
    await progbot_bugreport_channel.send(embed=embed)
    await interaction.response.send_message(content="**_Bug Report Submitted!_**\nThanks for the help!")


@bot.tree.command(name='run', description='admin commands', guild=discord.Object(id=settings.admin_guild))
async def admin(interaction: discord.Interaction, command: typing.Literal["refresh slash commands", "change status", "goodnight"], param_line:str=""):
    if command=="goodnight":
        await interaction.response.send_message(content="Goodnight!")
        return await bot.close()
    if command=="change status":
        return await bot.change_presence(activity=discord.Game(name=param_line))
    #Syncs the slash commands to Discord. Should not is not be done automatically and should be done by running this command if changes were made to the slash commands.
    if command=="refresh slash commands":
        await interaction.response.send_message(content="Refreshing app commands!")
        return await bot.tree.sync()

@bot.event
async def on_ready():
    ag = discord.Object(id=settings.admin_guild)
    bot.tree.clear_commands(guild=ag)
    bot.tree.copy_global_to(guild=ag)
    await bot.tree.sync(guild=ag)
    print("Jacking In!")
    print("Name: {}".format(bot.user.name))
    print("ID: {}".format(bot.user.id))

load_dotenv()
bot_token = os.getenv('DISCORD_TOKEN')

required_files = [settings.commands_table_name, settings.user_levels_table_name, settings.audiencesave, settings.spotlightsave]

bad_files = [f for f in required_files if not os.path.isfile(f)]
if bad_files:
    raise FileNotFoundError("Required files missing: %s " % ", ".join(bad_files))

handler = logging.FileHandler(filename=settings.log_file, encoding='utf-8', mode='w')
bot.run(bot_token, log_handler=handler, log_level=logging.DEBUG)

sys.exit(0)