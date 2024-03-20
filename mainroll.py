import discord
import koduck
import settings
import re
import dice_algebra
import rply
from maincommon import find_value_in_table
from maincommon import help_df

REROLL_DICE_SIZE_THRESHOLD = 1000000000
MAX_REROLL_QUERY = 20
MAX_REROLL_QUERY_LARGE = 5
ROLL_COMMENT_CHAR = '#'
FORMAT_LIMIT = 175 # technically actually 198 or so, buuuuut

roll_difficulty_dict = {'E': 3, 'N': 4, 'H': 5}

parser = dice_algebra.parser
lexer = dice_algebra.lexer


def get_roll_from_macro(diff, dicenum):
    roll_difficulty = roll_difficulty_dict[diff.upper()]
    roll_dicenum = int(dicenum)
    return "%dd6>%d" % (roll_dicenum, roll_difficulty)


def roll_master(roll_line, format_limit=FORMAT_LIMIT):
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
            roll_is_underflow = num_ones >= 3

    return roll_results, roll_is_underflow


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


async def repeatroll(context, *args, **kwargs):
    if not args:
        ruling_msg = await find_value_in_table(context, help_df, "Command", "rollhelp", suppress_notfound=True)
        if ruling_msg is None:
            return await context.koduck.send_message(receive_message=context["message"],
                                            content="Couldn't find the rules for this command! (You should probably let the devs know...)")

        return await context.koduck.send_message(receive_message=context["message"],
                                        content=("I can repeat a roll command for you! Try `{cp}repeatroll 3, 5d6>4` or `{cp}repeatroll 3, $N5`!\n\n" + ruling_msg["Response"]).replace(
                                            "{cp}", koduck.get_prefix(context["message"])))
    if len(args) < 2:
        return await context.koduck.send_message(receive_message=context["message"],
                                        content="Must be in the format of `{cp}repeatroll [repeats], [dice roll]` (i.e. `{cp}repeatroll 3, 5d6>4`)".replace(
                                            "{cp}", koduck.get_prefix(context["message"])))
    try:
        repeat_arg = int(args[0])
    except ValueError:
        return await context.koduck.send_message(receive_message=context["message"],
                                        content="First argument needs to be the number of times you want to repeat the roll!")
    if repeat_arg <= 0:
        return await context.koduck.send_message(receive_message=context["message"],
                                        content="Can't repeat a roll a negative or zero number of times!")

    roll_line = context.param_line.split(",", 1)[1]

    if ROLL_COMMENT_CHAR in roll_line:
        roll_line, roll_comment = roll_line.split(ROLL_COMMENT_CHAR, 1)
    else:
        roll_comment = ""

    roll_line = re.sub("\s+", "", roll_line).lower()
    if not roll_line:
        return await context.koduck.send_message(receive_message=context["message"],
                                        content="No roll given!")

    dice_size = re.search('d(\d+)', roll_line)
    if not dice_size:
        dice_size = re.search('(?:E|N|H)(\d+)', roll_line, re.IGNORECASE)

    if dice_size:
        reroll_size = int(dice_size.group(1))

        if repeat_arg > MAX_REROLL_QUERY:
            return await context.koduck.send_message(receive_message=context["message"],
                                            content="Too many small rerolls in one query! Maximum of %d for dice sizes under %d!" % (MAX_REROLL_QUERY, REROLL_DICE_SIZE_THRESHOLD))
        if repeat_arg > MAX_REROLL_QUERY_LARGE and reroll_size > REROLL_DICE_SIZE_THRESHOLD:
            return await context.koduck.send_message(receive_message=context["message"],
                                            content="Too many large rerolls in one query! Maximum of %d for dice sizes over %d!" % (MAX_REROLL_QUERY_LARGE, REROLL_DICE_SIZE_THRESHOLD))

    try:
        roll_heck = [roll_master(roll_line, format_limit=(FORMAT_LIMIT/repeat_arg)) for i in range(0, repeat_arg)]
        roll_results, is_underflow_list = list(zip(*roll_heck))
    except rply.errors.LexingError:
        return await context.koduck.send_message(receive_message=context["message"],
                                        content="Unexpected characters found! Did you type out the roll correctly?")
    except AttributeError:
        return await context.koduck.send_message(receive_message=context["message"],
                                        content="Sorry, I can't understand the roll. Try writing it out differently!")
    except dice_algebra.DiceError:
        return await context.koduck.send_message(receive_message=context["message"],
                                        content="The dice algebra is incorrect! Did you type out the roll correctly?")
    except dice_algebra.OutOfDiceBounds as e:
        return await context.koduck.send_message(receive_message=context["message"],
                                        content=str(e))
    except dice_algebra.BadArgument as e:
        return await context.koduck.send_message(receive_message=context["message"], content="Bad argument! " + str(e))


    roll_outputs = [format_hits_roll(result) for result in roll_results]
    progroll_output = "{} *rolls...*".format(context["message"].author.mention)
    if roll_comment:
        progroll_output += " #{}".format(roll_comment.rstrip())
    progroll_output = "{}\n>>> {}".format(progroll_output,"\n".join(roll_outputs))

    progmsg = await context.koduck.send_message(receive_message=context["message"], content=progroll_output)
    if not any(is_underflow_list):
        return
    try:
        await progmsg.add_reaction(settings.custom_emojis["underflow"])
    except discord.errors.HTTPException:
        return


async def roll(context, *args, **kwargs):
    if not args:
        ruling_msg = await find_value_in_table(context, help_df, "Command", "rollhelp", suppress_notfound=True)
        if ruling_msg is None:
            return await context.koduck.send_message(receive_message=context["message"],
                                            content="Couldn't find the rules for this command! (You should probably let the devs know...)")
        return await context.koduck.send_message(receive_message=context["message"],
                                        content=("I can roll dice for you! Try `{cp}roll 5d6>4` or `{cp}roll $N5`!\n\n" + ruling_msg["Response"]).replace(
                                            "{cp}", koduck.get_prefix(context["message"])))
    roll_line = context.param_line
    if ROLL_COMMENT_CHAR in roll_line:
        roll_line, roll_comment = roll_line.split(ROLL_COMMENT_CHAR, 1)
    else:
        roll_comment = ""

    roll_line = re.sub("\s+", "", roll_line).lower()
    if not roll_line:
        return await context.koduck.send_message(receive_message=context["message"],
                                        content="No roll given!")

    try:
        roll_results, is_underflow = roll_master(roll_line)
    except rply.errors.LexingError:
        return await context.koduck.send_message(receive_message=context["message"],
                                        content="Unexpected characters found! Did you type out the roll correctly?")
    except AttributeError:
        return await context.koduck.send_message(receive_message=context["message"],
                                        content="Sorry, I can't understand the roll. Try writing it out differently!")
    except dice_algebra.DiceError:
        return await context.koduck.send_message(receive_message=context["message"],
                                        content="The dice algebra is incorrect! Did you type out the roll correctly?")
    except dice_algebra.OutOfDiceBounds:
        return await context.koduck.send_message(receive_message=context["message"],
                                        content="Too many dice were rolled! No more than %d!" % dice_algebra.DICE_NUM_LIMIT)
    except dice_algebra.BadArgument as e:
        return await context.koduck.send_message(receive_message=context["message"], content="Bad argument! " + str(e))

    progroll_output = "{} *rolls...* {}".format(context["message"].author.mention, format_hits_roll(roll_results))
    if roll_comment:
        progroll_output += " #{}".format(roll_comment.rstrip())

    progmsg = await context.koduck.send_message(receive_message=context["message"], content=progroll_output)
    if not is_underflow:
        return
    try:
        await progmsg.add_reaction(settings.custom_emojis["underflow"])
    except discord.errors.HTTPException:
        return