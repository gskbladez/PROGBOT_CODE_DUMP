import json
import os
import typing
import discord
import requests
import random
import settings
from pandas import DataFrame, Series, unique, read_csv
import re
import datetime
from maincommon import clean_args, roll_row_from_table, send_query_msg, send_msg, find_value_in_table, send_multiple_embeds
from maincommon import help_df, cc_color_dictionary, pmc_link
#import shelve
from maincommon import bot, commands_dict, filter_table

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
MAX_WEATHER_ROLL = 6

pmc_daemon_df = read_csv(settings.pmc_daemonfile, sep="\t").fillna('')

cj_colors = {"cheer": 0xffe657, "jeer": 0xff605d}
achievement_color_dictionary = {"Gold": 0xffe852}
weather_color_dictionary = {"Blue": 0x8ae2ff,
                            "Yellow": 0xffff5e,
                            "Red": 0xff524d}

daemon_df = read_csv(settings.daemonfile, sep="\t").fillna('').dropna(subset=['Name'])
networkmod_df = read_csv(settings.networkmodfile, sep="\t").fillna('')
crimsonnoise_df = read_csv(settings.crimsonnoisefile, sep="\t").fillna('')
audience_df = read_csv(settings.audienceparticipationfile, sep="\t").fillna('')

achievement_df = read_csv(settings.achievementfile, sep="\t").fillna('')
achievement_df["Category"] = achievement_df["Category"].astype('category').cat.reorder_categories(["First Steps", "Admin Privileges", "Tricky Bits", "Smooth Operation", "Milestones"])
achievement_df = achievement_df.sort_values(["Category", "Name"])
weather_df = read_csv(settings.weatherfile, sep="\t").fillna('')
weather_category_list = unique(weather_df["Category"].dropna())

glossary_df = read_csv(settings.glossaryfile, sep="\t").fillna('')
pmc_daemon_df = read_csv(settings.pmc_daemonfile, sep="\t").fillna('')

# I should honestly make this a configuration but meh

def clean_audience():
    try:
        with open(settings.audiencesave, 'r') as afp:
            audience_data = json.load(afp)
            del_keys = [key for key in audience_data if
                        (datetime.datetime.now() - datetime.datetime.strptime(audience_data[key]["last_modified"], '%Y-%m-%d %H:%M:%S')) > AUDIENCE_TIMEOUT]
            for key in del_keys: del audience_data[key]
    except json.JSONDecodeError:
        audience_data = {}
    with open(settings.audiencesave, 'w') as afp:
        json.dump(audience_data, afp, indent=4, default=str)
    return


def clean_spotlight():
    try:
        with open(settings.spotlightsave, 'r') as afp:
            spotlight_db = json.load(afp)
            del_keys = [key for key in spotlight_db if
                        (datetime.datetime.now() - datetime.datetime.strptime(spotlight_db[key]["Last Modified"], '%Y-%m-%d %H:%M:%S')) > SPOTLIGHT_TIMEOUT]
            for key in del_keys: del spotlight_db[key]
    except json.JSONDecodeError as e:
        spotlight_db = {}
    with open(settings.spotlightsave, 'w') as afp:
        json.dump(spotlight_db, afp, indent=4, default=str)
    return


@bot.tree.command(name='crimsonnoise', description=commands_dict["crimsonnoise"])
async def crimsonnoise(interaction: discord.Interaction, md_type: typing.Literal["Common", "Uncommon", "Rare"]):
    arg = md_type.lower().strip()
    
    crimsonnoise_type = filter_table(crimsonnoise_df, {"MysteryData": f"^{re.escape(arg)}$"})

    if crimsonnoise_type.shape[0] == 0:
        return send_msg(interaction,
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

    return await interaction.response.send_message(embed=embed)

def query_daemon():
    result_title = "Listing all Daemons (excluding Player Made Content)..."
    off_df = filter_table(daemon_df, {"Name": "Neko Virus"}, not_filt=True)
    result_msg = ", ".join(off_df["Name"])
    return True, result_title, result_msg


@bot.tree.command(name='daemon', description=commands_dict["daemon"])
async def daemon(interaction: discord.Interaction, name: str):
    cleaned_args = clean_args([name])
    arg_combined = " ".join(cleaned_args)
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await send_msg(interaction, "Lists the complete information of a **Daemon** for DarkChip rules. Use `daemon all` to pull up the names of all Official Daemons!")
    is_ruling = False
    ruling_msg = None
    if arg_combined in ["all", "list"]:
        _, result_title, result_msg = query_daemon()
        return await send_query_msg(interaction, result_title, result_msg)
    elif cleaned_args[0] in ['rule', 'ruling', 'rules', 'advice']:
        is_ruling = True
        ruling_msg, _ = await find_value_in_table(help_df, "Command", "daemonruling", suppress_notfound=True)
    elif cleaned_args[0] in ['darkchip', 'dark', 'darkchips', 'chip', 'chips']:
        is_ruling = True
        ruling_msg, _ = await find_value_in_table(help_df, "Command", "darkchip", suppress_notfound=True)
    elif cleaned_args[0] in ['tribute', 'tributes']:
        is_ruling = True
        ruling_msg, _ = await find_value_in_table(help_df, "Command", "tribute", suppress_notfound=True)
    elif cleaned_args[0] in ['chaosunison', 'chaos', 'chaosunion']:
        is_ruling = True
        ruling_msg, _ = await find_value_in_table(help_df, "Command", "domain", suppress_notfound=True)
    elif cleaned_args[0] in ['daemonbond', 'bond']:
        is_ruling = True
        ruling_msg, _ = await find_value_in_table(help_df, "Command", "daemonbond", suppress_notfound=True)

    if is_ruling:
        if ruling_msg is None:
            return await send_msg(interaction,
                                  "Couldn't find the rules for this command! (You should probably let the devs know...)", ephemeral=True)
        return await send_msg(interaction,ruling_msg["Response"])

    daemon_info, _ = await find_value_in_table(daemon_df, "Name", arg_combined, suppress_notfound=True)
    if daemon_info is None:
        daemon_info, add_msg = await find_value_in_table(pmc_daemon_df, "Name", arg_combined)
        if daemon_info is None:
            return await send_msg(interaction, add_msg)

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
    return await interaction.response.send_message(embed=embed)


def query_network():
    result_title = "Listing all Network Modifiers from the `New Connections` crossover content..."
    result_msg = ", ".join(networkmod_df["Name"])
    return True, result_title, result_msg


def query_weather():
    result_title = "Listing all types of CyberWeather from NetBattlers Advance..."
    result_msg = ", ".join(weather_df["Name"])
    return True, result_title, result_msg


@bot.tree.command(name='networkmod', description=commands_dict["networkmod"])
async def networkmod(interaction: discord.Interaction, query: str):
    cleaned_args = clean_args([query])
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await send_msg(interaction,"Pulls up info for 1-%d **Network Modifiers**! I can also list all Network Modifiers if you tell me `list` or `all`!" % MAX_MOD_QUERY)

    if len(cleaned_args) > MAX_MOD_QUERY:
        return await send_msg(interaction,"Can't pull up more than %d Network Mods!" % MAX_MOD_QUERY, ephemeral=True)

    if cleaned_args[0] in ["list", "all"]:
        _, result_title, result_msg = query_network()
        return await send_query_msg(interaction, result_title, result_msg)
    elif cleaned_args[0] in ['rule', 'ruling', 'rules']:
        ruling_msg, _ = await find_value_in_table(help_df, "Command", "networkmodruling", suppress_notfound=True)
        if ruling_msg is None:
            return await send_msg(interaction,
                                  "Couldn't find the rules for this command! (You should probably let the devs know...)", ephemeral=True)
        return await send_msg(interaction, ruling_msg["Response"])

    msg_warn = []
    msg_embeds = []
    for arg in cleaned_args:
        networkmod_info, add_msg = await find_value_in_table(networkmod_df, "Name", arg, suppress_notfound=False)
        msg_warn.append(add_msg)
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
        msg_embeds.append(embed)

    return await send_multiple_embeds(interaction, msg_embeds, msg_warn)
    


def change_audience(channel_id, cj_type, amount):
    id = str(channel_id)
    try:
        with open(settings.audiencesave, "r") as afp:
            audience_data = json.load(afp)
    except json.JSONDecodeError:
        audience_data = {}

    with open(settings.audiencesave, "w") as afp:
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

        json.dump(audience_data, afp, indent=4, default=str)

        return (0, word_term, "Cheer Points: %d, Jeer Points: %d" % (c_val, j_val))


def get_audience(channel_id):
    try:
        with open(settings.audiencesave, "r") as afp:
            audience_data = json.load(afp)
    except json.JSONDecodeError:
        audience_data = {}

    id = str(channel_id)
    if id not in audience_data:
        return (-1, "Audience Participation hasn't been started in this channel!")
    c_val = audience_data[id]["cheer"]
    j_val = audience_data[id]["jeer"]
    return (0, (c_val, j_val))


def start_audience(channel_id):
    try:
        with open(settings.audiencesave, "r") as afp:
            audience_data = json.load(afp)
    except json.JSONDecodeError:
        audience_data = {}

    with open(settings.audiencesave, "w") as afp:
        id = str(channel_id)
        if len(audience_data) > MAX_AUDIENCES:
            return (-2, "ProgBot's hosting too many audiences right now! Try again later!", "")
        if id in audience_data:
            c_val = audience_data[id]["cheer"]
            j_val = audience_data[id]["jeer"]
            return (-1,
                    "Audience Participation was already started in this channel!",
                    "Cheer Points: %d, Jeer Points: %d" % (c_val, j_val))
        audience_data[id] = {"cheer": 0, "jeer": 0, "last_modified": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        json.dump(audience_data, afp, indent=4, default=str)

        return (0, "", "")


def end_audience(channel_id):
    try:
        with open(settings.audiencesave, "r") as afp:
            audience_data = json.load(afp)
    except json.JSONDecodeError:
        audience_data = {}

    with open(settings.audiencesave, "w") as afp:
        id = str(channel_id)
        
        try:
            del audience_data[id]
            json.dump(audience_data, afp, indent=4, default=str)
            return 0
        except KeyError:
            return -1


@bot.tree.command(name='audiencecheer', description=commands_dict["audiencecheer"])
async def cheer(interaction: discord.Interaction, command:typing.Literal['spend', 'add', 'list'], num:int=1):
    arg = command.lower().strip()
    return await cheer_jeer_master(interaction, "cheer", arg, num)


@bot.tree.command(name='audiencejeer', description=commands_dict["audiencejeer"])
async def jeer(interaction: discord.Interaction, command:typing.Literal['spend', 'add', 'list'], num:int=1):
    arg = command.lower().strip()
    return await cheer_jeer_master(interaction, "jeer", arg, num)
    

async def cheer_jeer_master(interaction: discord.Interaction, cj_type: str, arg:str, num:int):
    channel_id = interaction.channel.id

    if arg == 'list':
        embed_msg = f"**Listing {cj_type.capitalize()}s from the Audience Participation rules...**\n"
        sub_df = filter_table(audience_df, {"Type": re.escape(cj_type)})
        embed_bits = []
        for cj_type in sub_df["Type"].unique():
            subsub_df = sub_df[sub_df["Type"] == cj_type]
            subsub_index = range(1, subsub_df.shape[0] + 1)
            line_items = ["> %d. *%s*"%(i, val) for i, val in zip(subsub_index, subsub_df["Option"].values)]
            embed_submsg = "**%s:**\n" % cj_type.capitalize() + "\n".join([l.strip() for l in line_items])
            embed_bits.append(embed_submsg)
        embed_msg += "\n\n".join(embed_bits)
        return await interaction.response.send_message(content=embed_msg)
    
    embed_descript = ""
    if num > MAX_CHEER_JEER_ROLL:
        return await interaction.response.send_message(content=f"Rolling too many {cj_type.capitalize()}s! Up to {MAX_CHEER_JEER_ROLL}!", ephemeral=True)
    if num <= 0:
        embed_descript = f"{interaction.user.mention} rolled ... {num} {cj_type.capitalize()}s! Huh?!\n\n"
    elif arg == 'add':
        num = -1 * num
    elif arg=='spend' and num == 1:
        sub_df = filter_table(audience_df, {"Type": re.escape(cj_type)})
        random_roll = random.randrange(sub_df.shape[0])
        cj_roll = "*%s*" % sub_df["Option"].iloc[random_roll]

        embed_descript = f"{interaction.user.mention} rolled a {cj_type.capitalize()}!\n\n{cj_roll}\n\n"
    
    embed_footer = ""
    retval = get_audience(channel_id)
    if retval[0] == 0: # success code
        c_val = retval[1][0]
        j_val = retval[1][1]
        # error: number would go into negatives
        if ('c' in cj_type and (num > c_val)) or ('j' in cj_type and (num > j_val)):
            embed_descript = f"Not enough {cj_type.capitalize()}!"
            embed_footer = "Cheer Points: %d, Jeer Points: %d" % retval[1]
        else:
            _, aud_term, embed_footer = change_audience(channel_id, cj_type, -1 * num)
            embed_descript += f"({aud_term})" 
    elif not embed_descript:
        return await interaction.response.send_message(content="An audience hasn't been started for this channel yet!", ephemeral=True)

    embed = discord.Embed(title="__Audience Participation__",
                            description=embed_descript,
                            color=cj_colors[cj_type])
    if embed_footer:
        embed.set_footer(text=embed_footer)

    return await  interaction.response.send_message(embed=embed)


@bot.tree.command(name='audience', description=commands_dict["audience"])
async def audience(interaction: discord.Interaction, command:typing.Literal['start', 'view', 'end', 'help']):
    if interaction.channel.type is discord.ChannelType.private:
        channel_id = interaction.channel.id
        channel_name = interaction.user.name
        msg_location = f"{channel_name}! (Direct messages)" 
    else:
        channel_id = interaction.channel.id
        channel_name = interaction.channel.name
        channel_server = interaction.channel.guild
        msg_location = f"#{channel_name}! ({channel_server})"
    arg = command.lower().strip()
    if arg == 'help':
        ruling_msg, _ = await find_value_in_table(help_df, "Command", "audienceruling", suppress_notfound=True)
        if ruling_msg is None:
            return await interaction.response.send_message(content="Couldn't find the rules for this command! (You should probably let the devs know...)")
        return await interaction.response.send_message(ruling_msg["Response"])
    if arg == 'start':
        retvalue = start_audience(channel_id)
        if retvalue[0] == -1:
            embed_descript = retvalue[1]
            embed_foot = retvalue[2]
        elif retvalue[0] == -2:
            return await interaction.response.send_message(retvalue[1])
        else:
            embed_descript = "Starting up the audience for %s" % msg_location
            embed_foot = "Cheer Points: 0, Jeer Points: 0"
        embed = discord.Embed(title="__Audience Participation__",
                              description=embed_descript,
                              color=cj_colors["cheer"])
        embed.set_footer(text=embed_foot)
        return await interaction.response.send_message( embed=embed)
    elif arg == 'end':
        ret_val = end_audience(channel_id)
        if ret_val == -1:
            return await interaction.response.send_message(content="An audience hasn't been started for this channel yet!", ephemeral=True)
        embed = discord.Embed(title="__Audience Participation__",
                              description="Ending the audience session for %s\nGoodnight!" % msg_location,
                              color=cj_colors["jeer"])
        return await interaction.response.send_message(embed=embed)
    elif arg == 'view':
        retval = get_audience(channel_id)
        if retval[0] == -1:
            return await interaction.response.send_message(
                content="Audience Participation hasn't been started in this channel!", ephemeral=True)
        c_val = retval[1][0]
        j_val = retval[1][1]
        if c_val >= j_val:
            embed_color = cj_colors["cheer"]
        else:
            embed_color = cj_colors["jeer"]
        embed = discord.Embed(title="__Audience Participation__",
                              description=f"Pulling up the audience for {msg_location}",
                              color=embed_color)
        embed.set_footer(text=f"Cheer Points: {c_val}, Jeer Points: {j_val}")
        return await interaction.response.send_message( embed=embed)

    else:
        return await interaction.response.send_message(content="Sorry, don't recognize the audience command!", ephemeral=True)


@bot.tree.command(name='weather', description=commands_dict["weather"])
async def weather(interaction: discord.Interaction, query:str):
    cleaned_args = clean_args([query])
    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await interaction.response.send_message(
            "Pulls up info for 1-%d types of **CyberWeather**! I can also list all types of CyberWeather if you tell me `list` or `all`!" % MAX_WEATHER_QUERY)

    if len(cleaned_args) > MAX_WEATHER_QUERY:
        return await interaction.response.send_message( 
            content="Can't pull up more than %d types of CyberWeather!" % MAX_WEATHER_QUERY)

    if cleaned_args[0] in ["list", "all"]:
        _, result_title, result_msg = query_weather()
        return await send_query_msg(interaction, result_title, result_msg)
    elif cleaned_args[0] in ['rule', 'ruling', 'rules']:
        ruling_msg, _ = await find_value_in_table(help_df, "Command", "weather",
                                               suppress_notfound=True)
        if ruling_msg is None:
            return await interaction.response.send_message(
                content="Couldn't find the rules for this command! (You should probably let the devs know...)")
        return await interaction.response.send_message(ruling_msg["Response"])

    msg_warn = []
    msg_embeds = []
    for arg in cleaned_args:
        weather_info, add_msg = await find_value_in_table(weather_df, "Name", arg, suppress_notfound=False)
        msg_warn.append(add_msg)
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
        msg_embeds.append(embed)
            
    return await send_multiple_embeds(interaction, msg_embeds, msg_warn)


@bot.tree.command(name='weatherforecast', description=commands_dict["weatherforecast"])
async def weatherforecast(interaction: discord.Interaction, num:int=1, category:typing.Literal['All', 'Basic', 'Glitched', 'Error']='All'):
    # most of this was borrowed from the element code god bless you whoever worked on it
    weather_return_number = num  # number of weather to return, 1 by default
    weather_category = None if category=='All' else category.strip()
    sub_weather_df = weather_df

    if not weather_category:
        sub_weather_df = weather_df
    else:
        sub_weather_df = weather_df[weather_df["Category"].str.fullmatch(re.escape(weather_category), flags=re.IGNORECASE)]
        if sub_weather_df.shape[0] == 0:
            return await interaction.response.send_message(
                content="Not a valid category!\n" +
                        "Categories: **%s**" % ", ".join(weather_category_list), ephemeral=True)

    category_range_max = sub_weather_df.shape[0]
    if weather_return_number < 1:
        return await interaction.response.send_message( 
                content="The number of weather can't be 0 or negative!", ephemeral=True)
    if weather_return_number > MAX_WEATHER_ROLL:
        return await interaction.response.send_message( 
                content=f"That's too many weathers! Are you sure you need more than {MAX_WEATHER_ROLL}?", ephemeral=True)
    if weather_category and weather_return_number > category_range_max:
        return await interaction.response.send_message( 
                content=f"That's too many weathers for this category! Are you sure you need more than {category_range_max}?", ephemeral=True)
    
    weather_selected = random.sample(range(sub_weather_df.shape[0]), weather_return_number)
    weather_name = [sub_weather_df.iloc[i]["Name"] for i in weather_selected]
    
    if weather_category is None:
        weather_flavor_title = f"Picked {weather_return_number} random weather(s):"
    else:
        weather_flavor_title = f"Picked {weather_return_number} random weather(s) from the {weather_category} category:"

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
    return await interaction.response.send_message( embed=embed)


@bot.tree.command(name='achievement', description=commands_dict["achievement"])
async def achievement(interaction: discord.Interaction, query:str):
    cleaned_args = query.lower()

    if cleaned_args in ["list", "all"]:
        achieve_groups = achievement_df.groupby(["Category"])
        return_msgs = ["**%s:**\n*%s*" % (name, ", ".join(achieve_group["Name"].values)) for name, achieve_group in achieve_groups
                       if name]
        return await interaction.response.send_message("\n\n".join(return_msgs))

    match_candidates = filter_table(achievement_df, {"Name": re.escape(cleaned_args)})
    if match_candidates.shape[0] < 1:
        return await interaction.response.send_message("Didn't find any matches for `%s`!" % query, ephemeral=True)
    if match_candidates.shape[0] > 1:
        return await interaction.response.send_message(content="Found multiple matches for `%s`:\n*%s*" %
                                                       (query, ", ".join(match_candidates["Name"].to_list())))
    achievement_info = match_candidates.iloc[0]
    achievement_name = achievement_info["Name"]
    achievement_description = achievement_info["Description"]
    achievement_type = achievement_info["Category"]
    achievement_color = achievement_color_dictionary["Gold"]

    embed = discord.Embed(title="__{}__".format(achievement_name),
                          color=achievement_color)
    embed.add_field(name="**[{} Achievement]**".format(achievement_type),
                    value="_{}_".format(achievement_description))

    return await interaction.response.send_message(embed=embed)


@bot.tree.command(name='spotlight', description=commands_dict["spotlight"])
async def spotlight(interaction:discord.Interaction, names:str="", command:typing.Literal['start', 'mark', 'add', 'remove', 'view', 'edit', 'reset', 'end', 'help']='mark'):
    try:
        with open(settings.spotlightsave, 'r') as afp:
            spotlight_db = json.load(afp)
    except json.JSONDecodeError:
        spotlight_db = {}

    with open(settings.spotlightsave, 'w') as afp:
        if interaction.channel.type is discord.ChannelType.private:
            channel_id = str(interaction.channel.id)
            channel_name = interaction.user.name
            msg_location = f"{channel_name} (Direct messages)"
        else:
            channel_id = str(interaction.channel.id)
            channel_name = interaction.channel.name
            channel_server = interaction.channel.guild
            msg_location = f"#{channel_name} ({channel_server})"
        
        arg = command.strip().lower()
        name_list = [n.strip() for n in names.split(",") if n]

        if arg == 'help':
            ruling_msg, _ = await find_value_in_table(help_df, "Command", "flow", suppress_notfound=True)
            if ruling_msg is None:
                return await interaction.response.send_message( 
                    content="Couldn't find the rules for this command! (You should probably let the devs know...)", ephemeral=True)
            return await interaction.response.send_message(ruling_msg["Response"])

        notification_msg = ""
        err_msg = ""

        is_start = arg == 'start'
        if channel_id not in spotlight_db:
            if len(name_list) == 0:
                return await interaction.response.send_message( 
                    embed=embed_spotlight_message("Spotlight Tracker not yet started in this channel!",
                                                    msg_location, error=True),
                                                    ephemeral=True)
            is_start = True

        if is_start:
            if channel_id in spotlight_db:
                spotlight_db[channel_id]["Last Modified"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return await interaction.response.send_message( embed=embed_spotlight_message("Spotlight Tracker already started in this channel!",
                                                                                msg_location, error=True), ephemeral=True)
            if (len(spotlight_db)+1) > MAX_SPOTLIGHTS:
                return await interaction.response.send_message(content="Too many Spotlight Checklists are active in ProgBot right now! Please try again later.", ephemeral=True)
            if len(name_list) > (MAX_CHECKLIST_SIZE + 1):
                return await interaction.response.send_message( 
                                                embed=embed_spotlight_message(f"Max of {MAX_CHECKLIST_SIZE} participants in a checklist!", msg_location, error=True), ephemeral=True)
            participants={}
            nl = Series("", index=range(len(name_list)))
            i=0
            dups = []
            for n in name_list:
                if any(nl.str.contains(re.escape(n), flags=re.IGNORECASE)):
                    dups.append(n)
                else:
                    nl.iloc[i] = n
                    participants[n] = False
                    i += 1
            if dups:
                err_msg = "(Note: %s are duplicates!)" % ", ".join(dups)
            
            spotlight_db[channel_id] = participants
            spotlight_db[channel_id]["Last Modified"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            embed = embed_spotlight_tracker(spotlight_db[channel_id], msg_location, notification=err_msg)
            json.dump(spotlight_db, afp, indent=4, default=str)
            return await interaction.response.send_message( embed=embed)

        spotlight_db[channel_id]["Last Modified"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if arg == 'end':
            del spotlight_db[channel_id]
            json.dump(spotlight_db, afp, indent=4, default=str)
            return await interaction.response.send_message( 
                                            embed=embed_spotlight_message("Shutting down this Spotlight Tracker! Goodnight!",
                                                                            msg_location))
        elif arg == 'add':
            if not name_list:
                return await interaction.response.send_message( 
                                                embed=embed_spotlight_message("Please list who you want to add!",
                                                                                msg_location, error=True), ephemeral=True)
            if (len(spotlight_db[channel_id]) + len(name_list) - 1) > MAX_CHECKLIST_SIZE:
                return await interaction.response.send_message( 
                                                embed=embed_spotlight_message("Max of %d participants in a checklist!" %
                                                                                MAX_CHECKLIST_SIZE,
                                                                                msg_location, error=True), ephemeral=True)
            dups = []
            n = len(name_list) # max number of new entries
            nl = Series(list(spotlight_db[channel_id].keys()) + ([""]*n))
            i = len(spotlight_db[channel_id]) # end of the array
            for n in name_list:
                if any(nl.str.contains(re.escape(n), flags=re.IGNORECASE)):
                    dups.append(n)
                else:
                    nl.iloc[i] = n
                    spotlight_db[channel_id][n] = False
                    i += 1
                if dups:
                    err_msg = "(%s already in the checklist!)" % ", ".join(dups)
        elif arg == 'reset':
            if not name_list:
                spotlight_db[channel_id] = {k:(False if k != "Last Modified" else v) for k, v in spotlight_db[channel_id].items()}
            for n in name_list:
                match_name = await find_spotlight_participant(interaction, n, spotlight_db[channel_id], msg_location)
                if match_name is None:
                    return
                spotlight_db[channel_id][match_name] = False
                continue
        elif arg == 'remove':
            if not name_list:
                return await interaction.response.send_message( 
                                                embed=embed_spotlight_message("Please specify who you want to remove!",
                                                                                msg_location, error=True), ephemeral=True)
            for n in name_list:
                match_name = await find_spotlight_participant(interaction, n, spotlight_db[channel_id], msg_location)
                if match_name is None:
                    continue
                del spotlight_db[channel_id][match_name]
                continue
        elif arg =='edit':
            if len(name_list) != 2:
                return await interaction.response.send_message(
                    embed=embed_spotlight_message("Need the original name and the new name to change it to!",
                    msg_location, error=True), ephemeral=True)

            match_name = await find_spotlight_participant(interaction, name_list[0], spotlight_db[channel_id], msg_location)
            if match_name is not None:
                spotlight_db[channel_id][name_list[1]] = spotlight_db[channel_id].pop(match_name)
        elif arg=='mark' and name_list:
            already_went_list = []
            for n in name_list:
                match_name = await find_spotlight_participant(interaction, n, spotlight_db[channel_id], msg_location)
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
        elif arg=='view':
            pass

        json.dump(spotlight_db, afp, indent=4, default=str)
        notify_str = "\n".join([i for i in (notification_msg, err_msg) if i])
        embed = embed_spotlight_tracker(spotlight_db[channel_id], msg_location, notification=notify_str)
        if not interaction.response.is_done():
            return await interaction.response.send_message(embed=embed)
        return await interaction.followup.send(embed=embed)


async def find_spotlight_participant(interaction, arg, participant_dict, message_location):
    participant_list = Series(participant_dict.keys())
    participant_list = participant_list[participant_list != "Last Modified"]
    exact_match = participant_list[participant_list.str.contains(f"^{re.escape(arg)}$", flags=re.IGNORECASE)]
    if exact_match.shape[0] == 1:
        return exact_match.iloc[0]
    match_candidates = participant_list[participant_list.str.contains(re.escape(arg), flags=re.IGNORECASE)]
    if match_candidates.shape[0] == 0:
        await interaction.response.send_message(
                                 embed=embed_spotlight_message("Unable to find `%s` as a participant!" % arg,
                                                                   message_location, error=True))
        return None
    if match_candidates.shape[0] > 1:
        await interaction.response.send_message(
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
    if "Last Modified" in participants:
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


@bot.tree.command(name='playermaderepo', description=commands_dict["playermaderepo"])
async def repo(interaction: discord.Interaction, query:str):
    if query.lower().strip()=="link":
        message_help =  f"You can access the full Player-Made Repository here! \n__<{pmc_link}>__\n\nWant to submit something? Ask russelcs in the Merry Mancer Games server!"
        return await interaction.response.send_message(message_help)
    
    user_query = query

    # api change @ 5/28/24 iza
    # now it uses integrations with secret tokens to manage access to pages
    # at least filters make more sense now
    headers = {
        "Authorization": "Bearer " + settings.notion_pmc_token,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    notion_url = f"https://api.notion.com/v1/databases/{settings.notion_pmc_id}/query"
    search_params = {
        "filter": {
            "or": [
                {
                    "property": "Name", 
                    "title": {"contains": query}
                },{
                    "property": "Author", 
                    "rich_text": {"contains": query}
                },
            ]
        }
    }
    r = requests.post(notion_url, json=search_params, headers=headers)

    # R:200 - all good
    # R:3xx - what the fuck notion?
    # R:4xx - bad request, wrong api endpoint, notion changed the api again, scrape the new fields (i.e.: our problem)
    # R:5xx - notion's down (i.e.: not our problem)
    if r.status_code != 200:
        print(r.status_code, r.reason)
        print("Response:", r.content)
        interaction.response.send_message("Sorry, I got an unexpected response from Notion! Please try again later! (If this persists, let the devs know!)")
        return

    # just leaving this here for the next time i need to work on this again..
    #parse = json.loads(r.content)
    #print(json.dumps(parse, indent=4, sort_keys=True))

    # based off of amon's previous work! 
    repo_results_html = r.json()["results"]
    if not repo_results_html:
        return await interaction.response.send_message("I can't find anything with that query, sorry!")
    repo_results = []
    for repo_result in repo_results_html:
        rr = repo_result["properties"]
        a = rr["Author"]["rich_text"][0]["plain_text"]
        t = rr["Name"]["title"][0]["plain_text"]
        l = rr["Link"]["url"]
        repo_results.append({"name": t, "author": a, "link": l})
    
    num_results = len(repo_results) 
    if len(repo_results) == 1:
        repo_result_row = repo_results[0]
        generated_msg = "**Found {} entry for _'{}'_..** \n" + \
                        "**_`{}`_** by __*{}*__:\n __<{}>__"
        return await interaction.response.send_message(
            generated_msg.format(num_results, user_query, repo_result_row["name"], repo_result_row["author"], repo_result_row["link"]))
    if len(repo_results) > 1:
        repo_results_names = [i["name"] for i in repo_results]
        generated_msg = "**Found {} entries for _'{}'_..** \n" + \
                        "*'%s'*" % "', '".join(repo_results_names)
        return await interaction.response.send_message(
            generated_msg.format(num_results, user_query))
