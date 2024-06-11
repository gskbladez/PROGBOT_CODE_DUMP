import datetime
import subprocess
import discord
import settings
import re
import dice_algebra
import rply
from maincommon import bot, commands_dict

REROLL_DICE_SIZE_THRESHOLD = 1000000000
MAX_REROLL_QUERY = 20
MAX_REROLL_QUERY_LARGE = 5
ROLL_COMMENT_CHAR = '#'
FORMAT_LIMIT = 175 # technically actually 198 or so, buuuuut
IS_UNDERFLOW = 1
IS_DEVILISH = 2

roll_difficulty_dict = {'E': 3, 'N': 4, 'H': 5}

parser = dice_algebra.parser
lexer = dice_algebra.lexer
last_entropy = None

def get_roll_from_macro(diff, dicenum):
    roll_difficulty = roll_difficulty_dict[diff.upper()]
    roll_dicenum = int(dicenum)
    return "%dd6>%d" % (roll_dicenum, roll_difficulty)


def roll_master(roll_line, format_limit=FORMAT_LIMIT):
    retcode = 0
    # subs out the macros
    macro_regex = r"\$?(E|N|H)(\d+)"
    roll_line = re.sub(macro_regex, lambda m: get_roll_from_macro(m.group(1), m.group(2)), roll_line,
                       flags=re.IGNORECASE)
    # adds 1 in front of bare d6, d20 references
    roll_line = re.sub(r"(?P<baredice>^|\b)d(?P<dicesize>\d+)", r"\g<baredice>1d\g<dicesize>", roll_line)
    zero_formatted_roll = re.sub(r'{(.*)}', '0', roll_line)
    roll_is_underflow = False
    roll_results = parser.parse(lexer.lex(zero_formatted_roll))

    if hasattr(roll_results, "modifications"):
        if (len(roll_results.modifications) == 2):
            if len(re.findall(r"(\*|\_|~)+", roll_results.modifications[1][1])) > (format_limit * 2):
                raise dice_algebra.OutOfDiceBounds("Too many formatting elements! (Yes this is a weird error.)\n(Basically your roll is too fancy.)\n(Try not using `>`/`<` operators, or lowering the number of dice!)");
        if sum(roll_results.results) == 0:
            results_bare_str = roll_results.modifications[0][1]
            num_ones = len(re.findall(r'(\D*1\D*)', results_bare_str))
            retcode = IS_UNDERFLOW if num_ones >= 3 else 0
        else:
            results_bare_str = roll_results.modifications[0][1]
            num_six = len(re.findall(r'(\D*6\D*)', results_bare_str))
            retcode = IS_DEVILISH if num_six == 3 else 0

    return roll_results, retcode


def format_hits_roll(roll_result):
    str_result = str(roll_result)
    num_hits = roll_result.eval()
    if 'hit' in str_result:
        if num_hits == 1:
            result_str = "{} = **__{} hit!__**".format(str_result, num_hits)
        else:
            result_str = "{} = **__{} hits!__**".format(str_result, num_hits)
    else:
        result_str = "{} = **__{}__**".format(str_result, roll_result.eval())
    return result_str

@bot.tree.command(name='roll', description=commands_dict["roll"])
async def roll(interaction: discord.Interaction, cmd: str, repeat: int = 1):
    if repeat <= 0:
        await interaction.response.send_message(interaction, content="Can't repeat a roll a negative or zero number of times!", ephemeral=True)

    roll_line = cmd

    if ROLL_COMMENT_CHAR in roll_line:
        roll_line, roll_comment = roll_line.split(ROLL_COMMENT_CHAR, 1)
    else:
        roll_comment = ""
    orig_roll_line = roll_line
    roll_line = re.sub("\s+", "", roll_line).lower()
    if not roll_line:
        await interaction.response.send_message(interaction, content="No roll command given!", ephemeral=True)

    dice_size = re.search('d(\d+)', roll_line)
    if not dice_size:
        dice_size = re.search('(?:E|N|H)(\d+)', roll_line, re.IGNORECASE)

    if dice_size:
        reroll_size = int(dice_size.group(1))

        if repeat > MAX_REROLL_QUERY:
            return await interaction.response.send_message(interaction,
                                                                 content=f"Too many small rerolls in one query! Maximum of {MAX_REROLL_QUERY} for dice sizes under {REROLL_DICE_SIZE_THRESHOLD}!",
                                                                 ephemeral=True)

        if repeat > MAX_REROLL_QUERY_LARGE and reroll_size > REROLL_DICE_SIZE_THRESHOLD:
            return await interaction.response.send_message(interaction,
                                                                 content=f"Too many small rerolls in one query! Maximum of {MAX_REROLL_QUERY_LARGE} for dice sizes under {REROLL_DICE_SIZE_THRESHOLD}!",
                                                                 ephemeral=True)
    try:
        roll_heck = [roll_master(roll_line, format_limit=int(FORMAT_LIMIT/repeat)) for i in range(0, repeat)]
        err_msg = ""
        roll_results, retcodes = list(zip(*roll_heck))
    except rply.errors.LexingError:
        err_msg = "Unexpected characters found! Did you type out the roll correctly?"
    except AttributeError:
        err_msg = "Sorry, I can't understand the roll. Try writing it out differently!"
    except dice_algebra.DiceError:
        err_msg = "The dice algebra is incorrect! Did you type out the roll correctly?"
    except dice_algebra.OutOfDiceBounds as e:
        err_msg = str(e)
    except dice_algebra.BadArgument as e:
        err_msg = "Bad argument! " + str(e)

    if err_msg:
        return await interaction.response.send_message(content=err_msg, ephemeral=True)

    roll_outputs = [format_hits_roll(result) for result in roll_results]

    if repeat == 1:
        progroll_output = f"{interaction.user.mention} *rolls `{orig_roll_line}` for...* {roll_outputs[0]}"
        if roll_comment:
            progroll_output += f" #{roll_comment.rstrip()}"
    else:
        progroll_output = f"{interaction.user.mention} *rolls `{orig_roll_line}` {repeat} times...*"
        if roll_comment:
            progroll_output += f" #{roll_comment.rstrip()}"
        progroll_output = "{}\n>>> {}".format(progroll_output, "\n".join(roll_outputs))

    progmsg = await interaction.response.send_message(content=progroll_output)
    
    try:
        if IS_UNDERFLOW in retcodes:
            await progmsg.add_reaction(settings.custom_emojis["underflow"])
        if IS_DEVILISH in retcodes:
            await progmsg.add_reaction(settings.custom_emojis["devilish"])
    except discord.errors.HTTPException as e:
        print(e)
        return

@bot.tree.command(name='entropy', description=commands_dict["entropy"])
async def entropy(interaction: discord.Interaction):
    try:
        completedproc = subprocess.run(['cat','/proc/sys/kernel/random/entropy_avail'], stdout = subprocess.PIPE, timeout=1, encoding='ascii')
        return await interaction.response.send_message(f"Randomization quantum: **{completedproc.stdout.strip()}**!")
    except subprocess.TimeoutExpired:
        return await interaction.response.send_message(content="Orb did not respond... ask again later!", ephemeral=True)
    except Exception as e:
        return await interaction.response.send_message(content="Orb was cracked... You should let the devs know!", ephemeral=True)
    