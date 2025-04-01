import discord
import asyncio
import random
import settings
import re
import typing
from pandas import DataFrame, read_csv, unique, isna
from maincommon import clean_args, find_value_in_table, roll_row_from_table, bot, commands_dict
from maincommon import cc_color_dictionary, filter_table, send_query_msg, send_multiple_embeds
from mainnb import cc_df, help_df

autoloot_df = read_csv(settings.autolootfile, sep="\t").fillna('')

fish_df = read_csv(settings.nf_fish, sep="\t").fillna('')
fish_df = fish_df[fish_df["Name"] != ""]

fish_tag_list = fish_df["Tags"].str.split(";|,", expand=True) \
    .stack() \
    .str.strip() \
    .str.lower() \
    .unique()
fish_tag_list = [i for i in fish_tag_list if i]
[fish_tag_list.remove(i) for i in ["none", "None"] if i in fish_tag_list]
fish_habitats_list = fish_df["Habitats"].str.split(",").explode().str.strip().unique()


nf_abstract_df = read_csv(settings.nf_abstract, sep="\t").fillna('')
nf_corporate_df = read_csv(settings.nf_corporate, sep="\t").fillna('')
nf_gamers_df = read_csv(settings.nf_gamers, sep="\t").fillna('')
nf_realsim_df = read_csv(settings.nf_realsim, sep="\t").fillna('')
nf_undernet_df = read_csv(settings.nf_undernet, sep="\t").fillna('')

MAX_FISH_QUERY = 5





# There are 7 major categories that need to be procedurally filled out.
# Cost, Guard, Category, Damage, Range, Tags, Effect
# Each condition has several sub conditions and tables that are met based on rolling the dice.
@bot.tree.command(name='autoloot', description=commands_dict["autoloot"])
async def autoloot(interaction: discord.Interaction):

# COST:
    cost_r = random.randint(1, 6)
    if cost_r == 1:
        cost_txt = ("Spend 1 BP: ")
    elif cost_r == 2:
        skill = roll_row_from_table(autoloot_df, df_filters={"Type": "StatSkill"})["Result"]
        cost_txt = ("Spend 1 {}: ".format(skill))
    elif cost_r == 3:
        cost_txt = ("Spend {} HP: ".format(random.randint(1, 6)))
    else:
        cost_txt = ("")
    cost_result = cost_txt
    # check length of cost_r on function fill

# GUARD:
    guard_r = random.randint(1, 6)
    guard_result = ""
    if guard_r not in range(1, 3):
        guard_result = ""
    else:
        triggertype_r = random.randint(1, 6)
        if triggertype_r in range(1, 4):  # "Next Time You" condition range

            recursion_value = 1
            recursion_firsttime = True
            prefix_text = "Next time you "

            while recursion_value < 10:
                nty_r = random.randint(1, 6)
                if nty_r == 1:  # condition: damage
                    guarddmg = roll_row_from_table(autoloot_df, df_filters={"Type": "GuardTriggerDamage"})["Result"]
                    guard_txt = (f"{guarddmg} damage,")
                    break
                if nty_r == 2:  #condition: element
                    guardelement = roll_row_from_table(autoloot_df, df_filters={"Type": "GuardTriggerHP"})["Result"]
                    guard_txt = (f"{guardelement} element,")
                    break
                if nty_r == 3:  # condition: health
                    guardhp = roll_row_from_table(autoloot_df, df_filters={"Type": "GuardTriggerElement"})["Result"]
                    guard_txt = (f"{guardhp} HP,")
                    break
                if nty_r == 4:  # condition: rolls
                    guardroll = roll_row_from_table(autoloot_df, df_filters={"Type": "GuardTriggerRoll"})["Result"]
                    guard_txt = f"roll {guardroll} {random.randint(1,6)} hits,"
                    break
                if nty_r == 5:  # condition: verbs
                    verb = roll_row_from_table(autoloot_df, df_filters={"Type": "VerbTable"})["Result"]
                    guard_txt = f"{verb},"
                    break
                if nty_r == 6:
                    if recursion_firsttime:
                        recursion_value = 3
                        recursion_firsttime = False
                    else:
                        prefix_text = (f"Next {recursion_value} times you ")
                        recursion_value += 1
            guard_result = prefix_text + guard_txt
        if triggertype_r in range(4, 7): # "After" condition range
            after_r = random.randint(1, 6)
            if after_r in range(1, 3):
                guard_result = ("After {} minutes, ".format(random.randint(1,6)))
            elif after_r in range(3, 5):
                guard_result = ("After {} rolls, ".format(random.randint(1,6)))
            elif after_r == 5:
                guard_result = ("After you say {} words, ".format(random.randint(1,6)))
            elif after_r == 6:
                verb = roll_row_from_table(autoloot_df, df_filters={"Type": "VerbTable"})["Result"]
                noun = roll_row_from_table(autoloot_df, df_filters={"Type": "NounTable"})["Result"]
                guard_result = (f"After you {verb} {random.randint(1,6)} {noun}s, ")


# CATEGORY:
    category_result = roll_row_from_table(autoloot_df, df_filters={"Type": "Category"})["Result"]

    adj = roll_row_from_table(autoloot_df, df_filters={"Type": "AdjectiveTable"})["Result"]
    noun = roll_row_from_table(autoloot_df, df_filters={"Type": "NounTable"})["Result"]
    verb = roll_row_from_table(autoloot_df, df_filters={"Type": "VerbTable"})["Result"]

    # category conditionals
    if category_result == 'Hazard':
        hazard_r = random.randint(1, 5)
        if hazard_r == 1:
            hazard_txt = (f"Surfaces and objects Close to the target turn {adj}. ")
        elif hazard_r == 2:
            hazard_txt = (f"Turns an object into {noun}. ")
        elif hazard_r == 3:
            hazard_txt = (f"An {adj} {noun} pops out of a surface. ")
        elif hazard_r == 4:
            hazard_txt = (f"Makes all {noun}s {verb}.")
        elif hazard_r == 5:
            hazard_txt = (f"Disguise the target as a {noun}. ")
        elif hazard_r == 6:
            hazard_txt = (f"All {adj} objects explode.")
        category_description = hazard_txt
    elif category_result == 'Summon':
        summon_r = random.randint(1, 6)
        if summon_r in range(1, 4):
            summon_txt = (f"a {noun}")
        elif summon_r in range(4, 6):
            summon_txt = (f"a {adj} {noun}")
        elif summon_r == 6:
            roll = random.randint(1, 6)
            summon_txt = (f"{roll} {adj} {noun}")
        category_description = (f"Summons {summon_txt}.")
    elif category_result == 'Rush':
        rush_r = random.randint(1, 6)

        if rush_r in range(1, 3):
            rush_txt = "Dash Close to the target!"
        elif rush_r in range(3, 5):
            rush_txt = "Fly through the air Close to the target!"
        elif rush_r == 5:
            rush_txt = "Dash a range band away from the target!"
        elif rush_r == 6:
            rush_txt = "Fly through the air a range band away from the target!"
        category_description = rush_txt
    else:
        category_description = ""

# DAMAGE:
    if category_result == 'Support':
        damage_result = ""
        xdamage_description = ""
    else:
        damagetype_r = random.randint(1, 6)
        isXdamage = False
        damagetype = None
        if damagetype_r in range(1, 5):
            damagetype = "single"
        if damagetype_r in range(5, 7):
            damagetype = "multi"

        if not damagetype:
            damage_result = ""
        elif damagetype == "single":
            damagesingle_r = random.randint(1, 6)
            if damagesingle_r == 1:
                damagesingle_txt = "0 Damage"
            elif damagesingle_r == 2:
                damagesingle_txt = "1 Damage"
            elif damagesingle_r == 3:
                damagesingle_txt = "2 Damage"
            elif damagesingle_r == 4:
                damagesingle_txt = "3 Damage"
            elif damagesingle_r == 5:  # big damage conditional
                damagebig_r = random.randint(1, 6)
                if damagebig_r in range(1, 4):
                    damagesingle_txt = "4 Damage"
                elif damagebig_r in range(4, 6):
                    damagesingle_txt = "5 Damage"
                elif damagebig_r == 6:
                    damagesingle_txt = "6 Damage"
            elif damagesingle_r == 6:
                damagesingle_txt = "X Damage"
                isXdamage = True
            damage_result = damagesingle_txt

        elif damagetype == "multi":
            damagemulti_base_r = random.randint(1, 6)
            damagemulti_count_r = random.randint(1, 6)
            base_damage = ""
            hit_count = ""

            if damagemulti_base_r == 1:
                base_damage = "0"
            elif damagemulti_base_r in range(2, 4):
                base_damage = "1"
            elif damagemulti_base_r in range(4, 6):
                base_damage = "2"
            elif damagemulti_base_r == 6:
                damagebig_r = random.randint(1, 6)
                if damagebig_r in range(1, 5):
                    base_damage = "3"
                if damagebig_r == 5:
                    base_damage = "4"
                if damagebig_r == 6:
                    base_damage = "X"
                    isXdamage = True

            if damagemulti_count_r in range(1, 4):
                hit_count = "x2"
            elif damagemulti_count_r == 4:
                hit_count = "x3"
            elif damagemulti_count_r == 5:
                hit_count = "x4"
            elif damagemulti_count_r == 6:
                hit_count = "x5"
            damage_result = f"{base_damage}{hit_count} Damage"

        if not isXdamage:
            xdamage_txt = ""
        else:
            xdamage_r = random.randint(1, 6)
            if xdamage_r == 1:
                skill = roll_row_from_table(autoloot_df, df_filters={"Type": "StatSkill"})["Result"]
                ownership_r = random.randint(1, 2)
                if ownership_r == 1:
                    ownership = "Your"
                if ownership_r == 2:
                    ownership = "The target's"
                xdamage_txt = f"X = {ownership} {skill}."
            if xdamage_r == 2:
                xdamagechip = roll_row_from_table(autoloot_df, df_filters={"Type": "XDamageChip"})["Result"]
                if xdamagechip == 'Category':
                    category = roll_row_from_table(autoloot_df, df_filters={"Type": "Category"})["Result"]
                    xdamagechip = category[0]
                xdamage_txt = f"X = {xdamagechip} chips in your Folder."
            if xdamage_r == 3:  # whyyyyyy
                hardcode_bullshit_r = random.randint(1, 5)
                bullshit = ""
                if hardcode_bullshit_r == 1:
                    bullshit = "are Close"
                if hardcode_bullshit_r == 2:
                    bullshit = "are Near"
                if hardcode_bullshit_r == 3:
                    bullshit = f"have {verb}ed you since jack-in"
                if hardcode_bullshit_r == 4:
                    bullshit = f"you {verb}ed since jack-in"
                if hardcode_bullshit_r == 5:
                    bullshit = f"are {verb}ing"

                xdamage_txt = f"X = Number of {noun} that {bullshit}, max {random.randint(1, 6)}."
            if xdamage_r == 4:
                hardcode_bullshit_r = random.randint(1, 5)
                bullshit = ""
                if hardcode_bullshit_r == 1:
                    bullshit = "HP"
                if hardcode_bullshit_r == 2:
                    skill = roll_row_from_table(autoloot_df, df_filters={"Type": "StatSkill"})["Result"]
                    bullshit = "{}".format(skill)
                if hardcode_bullshit_r == 3:
                    bullshit = "unused chips"
                if hardcode_bullshit_r == 4:
                    bullshit = "BP"
                if hardcode_bullshit_r == 5:
                    bullshit = "Max HP"

                xdamage_txt = f"Sacrifice up to {random.randint(1, 6)} {bullshit} to add to X."
            if xdamage_r == 5:
                hardcode_bullshit_r = random.randint(1, 3)
                bullshit = ""
                if hardcode_bullshit_r == 1:
                    skill = roll_row_from_table(autoloot_df, df_filters={"Type": "StatSkill"})["Result"]
                    bullshit = skill
                if hardcode_bullshit_r == 2:
                    bullshit = "HP"
                if hardcode_bullshit_r == 3:
                    bullshit = "BP"
                xdamage_txt = (f"Add 1 to X for each {bullshit} reduction.")
            if xdamage_r == 6:
                xmath = roll_row_from_table(autoloot_df, df_filters={"Type": "XDamageMath"})["Result"]
                xdamage_txt = (f"Roll {random.randint(1, 6)}d{random.randint(1, 6)}, take the {xmath}.")

        xdamage_description = xdamage_txt

# RANGE:
    range_r = random.randint(1, 6)
    if range_r in range(1, 4):
        range_description = "Close"
    if range_r in range(4, 6):
        range_description = "Near"
    if range_r == 6:
        range_description = "Far"
# TAG:
    tagnumber_r = random.randint(1, 6)
    if tagnumber_r == 1:
        tagnumber = 0
        tag_result = ("")
    if tagnumber_r in range(2, 4):
        tagnumber = 1
    if tagnumber_r == 4:
        tagnumber = 2
    if tagnumber_r == 5:
        tagnumber = 3
    if tagnumber_r == 6:
        tagnumber = 4

    if tagnumber > 0:
        decide_bonus = random.randint(1, 6)
        taglist = []
        if decide_bonus == 6:
            bonustable_r = random.randint(1, 6)
            if bonustable_r in range(1, 5):
                tagnumber += 2
            else:
                tagnumber += 1
                taglist += ["Simple"]
        while len(taglist) < tagnumber:
            tag_r = roll_row_from_table(autoloot_df, df_filters={"Type": "TagTable"})["Result"]
            taglist += [tag_r]
        if guard_result:
            taglist.append("Guard")
        tag_result = ", ".join(taglist)

# EFFECT: Condition
    condition_r = random.randint(1, 6)
    condition_txt = ""
    if condition_r in range (1, 5):
        condition_combined = ""
    if condition_r in range (5, 7):
        conditiontable_r = random.randint(1, 6)
        if conditiontable_r == 1: # target condition table
            target_r = random.randint(1, 6)
            if target_r == 1:
                adj = roll_row_from_table(autoloot_df, df_filters={"Type": "AdjectiveTable"})["Result"]
                r = random.randint(1, 2)
                if r == 1:
                    condition_txt = "is {},".format(adj)
                if r == 2:
                    condition_txt = "is not {},".format(adj)
            if target_r == 2:
                r = random.randint(1, 2)
                if r == 1:
                    condition_txt = "is deleted by this attack,"
                if r == 2:
                    condition_txt = "is not deleted by this attack,"
            if target_r == 3:
                r = random.randint(1, 4)
                if r == 1:
                    noun = roll_row_from_table(autoloot_df, df_filters={"Type": "NounTable"})["Result"]
                    condition_txt = ("is a {},".format(noun))
                if r == 2:
                    noun = roll_row_from_table(autoloot_df, df_filters={"Type": "NounTable"})["Result"]
                    condition_txt = ("is not a {},".format(noun))
                if r == 3:
                    noun = roll_row_from_table(autoloot_df, df_filters={"Type": "NounTable"})["Result"]
                    condition_txt = ("has a {},".format(noun))
                if r == 4:
                    noun = roll_row_from_table(autoloot_df, df_filters={"Type": "NounTable"})["Result"]
                    condition_txt = ("does not have a {},".format(noun))
            if target_r == 4:
                r = random.randint(1, 2)
                skill = roll_row_from_table(autoloot_df, df_filters={"Type": "StatSkill"})["Result"]
                if r == 1:
                    condition_txt = ("failed a {} roll recently,".format(skill))
                if r == 2:
                    condition_txt = ("succeeded a {} roll recently,".format(skill))
            if target_r == 5:
                r = random.randint (1, 6)
                verb = roll_row_from_table(autoloot_df, df_filters={"Type": "StatSkill"})["Result"]
                if r == 1:
                    condition_txt = ("has {}ed in the past {} scenes,".format(verb, random.randint(1, 6)))
                if r == 2:
                    condition_txt = ("has {}ed in the past {} seconds,".format(verb, random.randint(1, 6)))
                if r == 3:
                    condition_txt = ("has {}ed in the past {} minutes,".format(verb, random.randint(1, 6)))
                if r == 4:
                    condition_txt = ("has {}ed in the past {} hours,".format(verb, random.randint(1, 6)))
                if r == 5:
                    condition_txt = ("has {}ed in the past {} days,".format(verb, random.randint(1, 6)))
                if r == 6:
                    condition_txt = ("has {}ed in the past {} years,".format(verb, random.randint(1, 6)))
            if target_r == 6:
                adj = roll_row_from_table(autoloot_df, df_filters={"Type": "AdjectiveTable"})["Result"]
                condition_txt = ("is more {} than you.".format(adj))
            condition_combined = ("If the target {} ".format(condition_txt))
        if conditiontable_r == 2: # user condition table
            user_r = random.randint(1, 6)
            if user_r == 1:
                r = random.randint(1, 3)
                if r == 1:
                    condition_txt = ("are at {} HP,".format(random.randint(1, 6)))
                if r == 2:
                    condition_txt = ("are below {} HP,".format(random.randint(1, 6)))
                if r == 3:
                    condition_txt = ("are above {} HP,".format(random.randint(1, 6)))
            if user_r == 2:
                noun = roll_row_from_table(autoloot_df, df_filters={"Type": "NounTable"})["Result"]
                r = random.randint(1, 4)
                if r == 1:
                    condition_txt = ("are a {},".format(noun))
                if r == 2:
                    condition_txt = ("are not a {},".format(noun))
                if r == 3:
                    condition_txt = ("have a {},".format(noun))
                if r == 4:
                    condition_txt = ("do not have a {},".format(noun))
            if user_r == 3:
                r = random.randint(1, 2)
                adj = roll_row_from_table(autoloot_df, df_filters={"Type": "AdjectiveTable"})["Result"]
                if r == 1:
                    condition_txt = ("are {},".format(adj))
                if r == 2:
                    condition_txt = ("are not {}".format(adj))
            if user_r == 4:
                r = random.randint(1, 2)
                if r == 1:
                    condition_txt = "are deleted by this attack,"
                if r == 2:
                    condition_txt = "are not deleted by this attack,"
            if user_r == 5:
                r = random.randint (1, 6)
                verb = roll_row_from_table(autoloot_df, df_filters={"Type": "VerbTable"})["Result"]
                if r == 1:
                    condition_txt = ("has {}ed in the past {} scenes,".format(verb, random.randint(1, 6)))
                if r == 2:
                    condition_txt = ("has {}ed in the past {} seconds,".format(verb, random.randint(1, 6)))
                if r == 3:
                    condition_txt = ("has {}ed in the past {} minutes,".format(verb, random.randint(1, 6)))
                if r == 4:
                    condition_txt = ("has {}ed in the past {} hours,".format(verb, random.randint(1, 6)))
                if r == 5:
                    condition_txt = ("has {}ed in the past {} days,".format(verb, random.randint(1, 6)))
                if r == 6:
                    condition_txt = ("has {}ed in the past {} years,".format(verb, random.randint(1, 6)))
            if user_r == 6:
                r = random.randint(1, 2)
                if r == 1:
                    condition_txt = ("stand still and don't move,")
                if r == 2:
                    condition_txt = ("are moving,")
            condition_combined = ("If you {} ".format(condition_txt))
        if conditiontable_r == 3 :  # damage condition table
            damage_r = random.randint(1, 6)
            if damage_r == 1:
                condition_txt = ("this deals {} damage,".format(random.randint(1, 6)))
            if damage_r == 2:
                r = random.randint(1, 2)
                if r == 1:
                    condition_txt = "you win a parry with this,"
                if r == 2:
                    condition_txt = "you lose a parry with this,"
            if damage_r == 3:
                skill = roll_row_from_table(autoloot_df, df_filters={"Type": "StatSkill"})["Result"]
                condition_txt = ("the target successfully defends with {},".format(skill))
            if damage_r == 4:
                condition_txt = "this hits the target,"
            if damage_r == 5: # i have basically forgotten that the spreadsheet existed at this point but i don't have time
                r = random.randint(1, 6)
                if r == 1:
                    condition_txt = "this is your first attack on the target,"
                if r == 2:
                    condition_txt = "this is your second attack on the target,"
                if r == 3:
                    condition_txt = "this is your third attack on the target,"
                if r == 4:
                    condition_txt = "this is your fourth attack on the target,"
                if r == 5:
                    condition_txt = "this is your fifth attack on the target,"
                if r == 6:
                    condition_txt = "this is your tenth attack on the target,"
            if damage_r == 6:
                condition_txt = ("this deals less than {} damage,".format(random.randint(1, 6)))

            condition_combined = ("If {} ".format(condition_txt))
        if conditiontable_r == 4: # environment condition table
            env_r = random.randint(1, 6)
            if env_r == 1:
                r = random.randint(1, 4)
                sub_r = random.randint(1, 2)
                noun = roll_row_from_table(autoloot_df, df_filters={"Type": "NounTable"})["Result"]
                adj = roll_row_from_table(autoloot_df, df_filters={"Type": "AdjectiveTable"})["Result"]
                if r == 1:
                    if sub_r == 1:
                        condition_txt = ("you are a range band above a {},".format(noun))
                    if sub_r == 2:
                        condition_txt = ("you are a range band above something {},".format(adj))
                if r == 2:
                    if sub_r == 1:
                        condition_txt = ("you are a range band below a {},".format(noun))
                    if sub_r == 2:
                        condition_txt = ("you are a range band below something {},".format(adj))
                if r == 3:
                    if sub_r == 1:
                        condition_txt = ("you are a range band away from a {},".format(noun))
                    if sub_r == 2:
                        condition_txt = ("you are a range band away from something {},".format(adj))
            if env_r == 2:
                noun = roll_row_from_table(autoloot_df, df_filters={"Type": "NounTable"})["Result"]
                condition_txt = ("this damages a {},".format(noun))
            if env_r == 3:
                condition_txt = "this destroys an object,"
            if env_r == 4:
                condition_txt = "the target is an object,"
            if env_r == 5:
                condition_txt = "the target just destroyed an object,"
            if env_r == 6:
                condition_txt = "everything around you is really messed up - I mean like, straight-up irrevocably busted, the kind of thing that makes you feel bad for whoever’s gotta foot the bill to get everything put back together (and don’t forget the poor sap that has to clean it all up! jeez),"

            condition_combined = ("If {} ".format(condition_txt))
        if conditiontable_r == 5: # element condition table
            element_r = random.randint(1, 6)

            cnd_ownership = roll_row_from_table(autoloot_df, df_filters={"Type": "ConditionalOwnership"})["Result"]
            cnd_location = roll_row_from_table(autoloot_df, df_filters={"Type": "ConditionalLocation"})["Result"]
            if element_r == 1:
                condition_txt = ("you are {} {} element, ".format(cnd_location, cnd_ownership))
            if element_r == 2:
                condition_txt = ("{} element is not present,".format(cnd_ownership))
            if element_r == 3:
                r = random.randint(1, 2)
                sub_r = random.randint(1, 2)
                noun = roll_row_from_table(autoloot_df, df_filters={"Type": "NounTable"})["Result"]
                adj = roll_row_from_table(autoloot_df, df_filters={"Type": "AdjectiveTable"})["Result"]
                if r == 1:
                    if sub_r == 1:
                        condition_txt = ("your element is {},".format(noun))
                    if sub_r == 2:
                        condition_txt = ("your element is {},".format(adj))
                if r == 2:
                    if sub_r == 1:
                        condition_txt = ("your element is not {},".format(noun))
                    if sub_r == 2:
                        condition_txt = ("your element is not {},".format(adj))
            if element_r == 4:
                condition_txt = ("you have {} elements available,".format(random.randint(1, 6)))
            if element_r == 5:
                r = random.randint(1, 3)
                sum = random.randint(1, 6) + random.randint(1, 6)
                if r == 1:
                    condition_txt = ("your element is over {} letters long,".format(sum))
                if r == 2:
                    condition_txt = ("your element is under {} letters long,".format(sum))
                if r == 3:
                    condition_txt = ("your element is exactly {} letters long,".format(sum))
            if element_r == 6:
                condition_txt = "your element is kind of a pain in the butt for the GM,"
            condition_combined = ("If {} ".format(condition_txt))
        if conditiontable_r == 6: # misc condition table
            misc_r = random.randint(1, 6)
            if misc_r == 1:
                misc_bday = roll_row_from_table(autoloot_df, df_filters={"Type": "MiscBirthday"})["Result"]
                condition_txt = ("it's {} birthday,".format(misc_bday))
            if misc_r == 2:
                adj = roll_row_from_table(autoloot_df, df_filters={"Type": "AdjectiveTable"})["Result"]
                condition_txt = ("the vibes are {},".format(adj))
            if misc_r == 3:
                condition_txt = ("you correctly predict how much damage this will deal at least {} minutes in advance,".format(random.randint(1, 6)))
            if misc_r == 4:
                noun = roll_row_from_table(autoloot_df, df_filters={"Type": "NounTable"})["Result"]
                condition_txt = ("you can tell a funny joke about a {},".format(noun))
            if misc_r == 5:
                misc_days = roll_row_from_table(autoloot_df, df_filters={"Type": "MiscDays"})["Result"]
                condition_txt = ("it is {},".format(misc_days))
            if misc_r == 6:
                condition_txt = "everyone at the table agrees,"
            condition_combined = ("If {} ".format(condition_txt))

# EFFECT: Subject
    subject_r = random.randint(1, 6)
    actionHasSubject = False
    if subject_r in range(1, 4):
        actionHasSubject = False
    if subject_r == 4:
        subject = "The user"
        actionHasSubject = True
    if subject_r == 5:
        subject = "Targets"
        actionHasSubject = True
    if subject_r == 6:
        r = random.randint(1, 6)
        if r == 1:
            noun = roll_row_from_table(autoloot_df, df_filters={"Type": "NounTable"})["Result"]
            subject = ("All {} in range".format(noun))
        if r == 2:
            sub_r = random.randint(1, 2)
            if sub_r == 1:
                subject = ("The target's PET")
            if sub_r == 2:
                subject = ("The user's PET")
        if r == 3:
            subject = "The user and the targets"
        if r == 4:
            subject = "Everything in range"
        if r == 5:
            sub_r = random.randint(1, 2)
            if sub_r == 1:
                subject = ("{} targets of your choice".format(random.randint(1, 6)))
            if sub_r == 2:
                subject = ("{} targets of GM's choice".format(random.randint(1, 6)))
        if r == 6:
            subject = "The server"

#EFFECT: Modal
    isModal = False
    modal_prefix = ""
    modalCheck = random.randint(1, 6)
    if modalCheck in range(1, 5):
        isModal = False
        modalDegree = 1
    if modalCheck in range(5, 7):
        isModal = True
        modal_r = random.randint(1, 6)
        modalDegree = 0
        if modal_r in range(1, 3):
            modal_prefix = "Pick 1: "
            modalDegree = 2
        if modal_r in range(3, 5):
            modal_prefix = "Pick 1: "
            modalDegree = 3
        if modal_r == 5:
            modal_prefix = "Pick 2: "
            modalDegree = 3
        if modal_r == 6:
            r = random.randint(1, 6)
            if r in range(1, 4):
                modal_prefix = "Pick 1: "
                modalDegree = 1 + random.randint(1, 6)
            if r in range(4, 7):
                modal_prefix = ("Pick {}: ".format(random.randint(1, 6)))
                modalDegree = random.randint(1, 6)

# ACTION: Duration
    duration_r = random.randint(1, 6)
    if duration_r == 1:
        duration = "for a moment"
    if duration_r == 2:
        duration_type = ["seconds", "rolls", "minutes"]
        duration = (f"for {random.randint(1,6)} {random.choice(duration_type)}")
    if duration_r == 3:
        duration_type = ["minutes", "hours", "sessions", "days"]
        duration = (f"for {random.randint(1,6)} out-of-game {random.choice(duration_type)}")
    if duration_r == 4:
        duration = "until jack-out"
    if duration_r == 5:
        duration = "as long as you can convince the GM it should last for"
    if duration_r == 6:
        duration = "forever, even after jack-out"
# ACTION: Effect table
    if isModal:
        action_list = [modal_prefix]
    else:
        action_list = []

    numberOfEffects = 0
    while numberOfEffects < modalDegree:
        #action - subject table
        action_text = ""
        if actionHasSubject:
            r = random.randint(1, 36)
            #action_text = ""
            if r == 1:
                action_text = ("Pushes {} back a range band.".format(subject.lower()))
            if r == 2:
                action_text = ("Stuns {} for {}.".format(subject.lower(), duration.lower()))
            if r == 3:
                skill = roll_row_from_table(autoloot_df, df_filters={"Type": "StatSkill"})["Result"]
                action_text = ("Upshifts {}'s next {} {} rolls.".format(subject.lower(), random.randint(1, 6), skill))
            if r == 4:
                noun = roll_row_from_table(autoloot_df, df_filters={"Type": "NounTable"})["Result"]
                action_text = ("Covers {} in {}s for {}.".format(subject.lower(), noun, duration))
            if r == 5:
                action_text = ("Disables {}'s element for {}.".format(subject.lower(), duration))
            if r == 6:
                action_text = ("{} loses {} HP.".format(subject, random.randint(1, 6)))
            if r == 7:
                adj = roll_row_from_table(autoloot_df, df_filters={"Type": "AdjectiveTable"})["Result"]
                action_text = ("{} can now freely move through {} objects.".format(subject, adj))
            if r == 8:
                verb = roll_row_from_table(autoloot_df, df_filters={"Type": "VerbTable"})["Result"]
                noun = roll_row_from_table(autoloot_df, df_filters={"Type": "NounTable"})["Result"]
                action_text = ("{} can {} any {} {}.".format(subject, verb, noun, duration))
            if r == 9:
                noun = roll_row_from_table(autoloot_df, df_filters={"Type": "NounTable"})["Result"]
                action_text = ("Turns {} into a {} {}.".format(subject.lower(), noun, duration))
            if r == 10:
                adj = roll_row_from_table(autoloot_df, df_filters={"Type": "AdjectiveTable"})["Result"]
                action_text = ("Makes {} {} {}.".format(subject.lower(), adj, duration))
            if r == 11:
                skill = roll_row_from_table(autoloot_df, df_filters={"Type": "StatSkill"})["Result"]
                action_text = ("{} gets a +{} dice to their next {} roll.".format(subject, random.randint(1, 6), skill))
            if r == 12:
                action_text = ("Heals {} {} HP.".format(subject.lower(), random.randint(1, 6)))
            if r == 13:
                noun = roll_row_from_table(autoloot_df, df_filters={"Type": "NounTable"})["Result"]
                action_text = ("{} gains the element {} {}.".format(subject, noun, duration))
            if r == 14:
                emotions = ["positive", "negative", "confusing"]
                action_text = ("Overwhelms {} with {} emotions {}.".format(subject.lower(), random.choice(emotions), duration))
            if r == 15:
                action_text = ("{} starts doing an elaborate dance routine.".format(subject))
            if r == 16:
                skill = roll_row_from_table(autoloot_df, df_filters={"Type": "StatSkill"})["Result"]
                action_text = ("You can roll {} on {} as if you were Close.".format(skill, subject.lower()))
            if r == 17:
                action_text = ("Creates a group DM between the user and {}.".format(subject.lower()))
            if r == 18:
                action_text = ("Jam {}'s PET for {}.".format(subject.lower(), duration))
            if r == 19:
                adj = roll_row_from_table(autoloot_df, df_filters={"Type": "AdjectiveTable"})["Result"]
                action_text = ("Rates {} 1-10 based on how {} they are.".format(subject.lower(), adj))
            if r == 20:
                action_text = ("Launches {} a range band skyward.".format(subject.lower()))
            if r == 21:
                action_text = ("Forces {} to jack out.".format(subject.lower()))
            if r == 22:
                adj = roll_row_from_table(autoloot_df, df_filters={"Type": "AdjectiveTable"})["Result"]
                noun = roll_row_from_table(autoloot_df, df_filters={"Type": "NounTable"})["Result"]
                action_text = ("If {} is touch a {} surface, they are attacked by {}s.".format(subject.lower(), adj, noun))
            if r == 23:
                action_text = ("{} can refresh a chip in their folder.".format(subject))
            if r == 24:
                action_text = ("Reveals an image of {}'s true love.".format(subject.lower()))
            if r == 25:
                action_text = ("This cannot delete {}.".format(subject.lower()))
            if r == 26:
                verb = roll_row_from_table(autoloot_df, df_filters={"Type": "VerbTable"})["Result"]
                action_text = ("Makes {} {} you if {} is Inanimate.".format(subject.lower(), verb, subject))
            if r == 27:
                action_text = ("Does the exact opposite of the last chip {} used.".format(subject))
            if r == 28:
                action_text = ("Takes a photo of {}.".format(subject))
            if r == 29:
                zenny = random.randint(1, 6) + random.randint(1, 6) + random.randint(1, 6) * 100
                action_text = ("{} loses {} Zenny.".format(subject.lower(), zenny))
            if r == 30:
                action_text = ("Anyone can ask {} {} questions and receive an honest answer.".format(subject.lower(), random.randint(1, 6)))
            if r == 31:
                action_text = ("{}'s PET catches on fire.".format(subject))
            if r == 32:
                adj = roll_row_from_table(autoloot_df, df_filters={"Type": "AdjectiveTable"})["Result"]
                action_text = ("Sends a message of {}'s choice to the entire server announced by a {} noise.".format(subject.lower(), adj))
            if r == 33:
                action_text = ("Swap places with {}.".format(subject.lower()))
            if r == 34:
                action_text = ("Next time {} would fail a roll, they can reroll.".format(subject.lower()))
            if r == 35:
                action_text = ("{} gets a fashion makeover.".format(subject))
            if r == 36:
                action_text = ("Sends an invite to {} to support their favorite indie game developer.".format(subject.lower()))

                # action - no subject table
        else:  # not actionHasSubject:
            r = random.randint(1, 36)
            if r == 1:
                action_text = ("Deals +{} damage.".format(random.randint(1, 6)))
            if r == 2:
                action_text = "Deals double damage."
            if r == 3:
                noun = roll_row_from_table(autoloot_df, df_filters={"Type": "NounTable"})["Result"]
                action_text = ("Vaporizes any {}s.".format(noun))
            if r == 4:
                action_text = "Screams." # same
            if r == 5:
                adj = roll_row_from_table(autoloot_df, df_filters={"Type": "AdjectiveTable"})["Result"]
                action_text = ("Opens a wormhole to somewhere {}.".format(adj))
            if r == 6:
                action_text = "Does its very best." # not this time hun
            if r == 7:
                adj = roll_row_from_table(autoloot_df, df_filters={"Type": "AdjectiveTable"})["Result"]
                noun = roll_row_from_table(autoloot_df, df_filters={"Type": "NounTable"})["Result"]
                action_text = ("Spreads a lot of {} {}s.".format(adj, noun))
            if r == 8:
                adj = roll_row_from_table(autoloot_df, df_filters={"Type": "AdjectiveTable"})["Result"]
                action_text = ("Burns through any {} material.".format(adj))
            if r == 9:
                action_text = ("This can hit {} targets.".format(random.randint(1, 6)))
            if r == 10:
                action_text = "This repairs any object it hits."
            if r == 11:
                adj = roll_row_from_table(autoloot_df, df_filters={"Type": "AdjectiveTable"})["Result"]
                action_text = ("Changes the session music to something {}.".format(adj))
            if r == 12:
                noun = roll_row_from_table(autoloot_df, df_filters={"Type": "NounTable"})["Result"]
                verb = roll_row_from_table(autoloot_df, df_filters={"Type": "VerbTable"})["Result"]
                action_text = ("Awakens the {} {} Program.".format(noun, verb))
            if r == 13:
                noun = roll_row_from_table(autoloot_df, df_filters={"Type": "NounTable"})["Result"]
                action_text = ("Leaves a {} behind.".format(noun))
            if r == 14:
                noun = roll_row_from_table(autoloot_df, df_filters={"Type": "NounTable"})["Result"]
                action_text = ("A NICE, BIG {}.".format(noun).upper())
            if r == 15:
                action_text = "This passes through surfaces."
            if r == 16:
                action_text = "This cannot be countered."
            if r == 17:
                adj = roll_row_from_table(autoloot_df, df_filters={"Type": "AdjectiveTable"})["Result"]
                action_text = "Gets {} with it.".format(adj)
            if r == 18:
                action_text = "Reroll this chip in its entirety after use."
            if r == 19:
                action_text = "Makes a blinding light."
            if r == 20:
                adj = roll_row_from_table(autoloot_df, df_filters={"Type": "AdjectiveTable"})["Result"]
                action_text = ("Makes the vibes a LOT more {}.".format(adj))
            if r == 21:
                verb = roll_row_from_table(autoloot_df, df_filters={"Type": "VerbTable"})["Result"]
                action_text = ("Can also be defended against by {}ing.".format(verb))
            if r == 22:
                action_text = "Summons a deafening silence."
            if r == 23:
                verb = roll_row_from_table(autoloot_df, df_filters={"Type": "VerbTable"})["Result"]
                action_text = ("This can only be used while {}ing.".format(verb))
            if r == 24:
                dtype = ["Crushing", "Slashing", "Incendiary", "Holy", "Pure", "Special"]
                action_text = ("Deals {} Damage.".format(random.choice(dtype)))
            if r == 25:
                type = ["Guards", "negative tags", "the GM"]
                action_text = ("Ignores {}.".format(random.choice(type)))
            if r == 26:
                action_text = "This chip permanently breaks after use."
            if r == 27:
                zenny = random.randint(1, 6) * 100
                action_text = ("Spend {} Zenny to refresh this chip.".format(zenny))
            if r == 28:
                zenny = random.randint(1, 6) * 100
                action_text = ("Gain {} Zenny for each point of damage this deals.".format(zenny))
            if r == 29:
                action_text = "Creates a Common Mystery Data."
            if r == 30:
                action_text = "Gives treats to all pets in range."
            if r == 31:
                adj = roll_row_from_table(autoloot_df, df_filters={"Type": "AdjectiveTable"})["Result"]
                noun = roll_row_from_table(autoloot_df, df_filters={"Type": "NounTable"})["Result"]
                action_text = ("Exposes the truth behind the mystery of the {} {}.".format(adj, noun))
            if r == 32:
                action_text = "Deals triple damage if you successfully lie to the rest of your group about how much damage this chip does."
            if r == 33:
                noun = roll_row_from_table(autoloot_df, df_filters={"Type": "NounTable"})["Result"]
                action_text = ("Replaces all summoned element in range with {}s.".format(noun))
            if r == 34:
                action_text = "Do Navis feel pain? What about Viruses? It all feels like a sport, a game, a dream... Do you care? Are you happier not knowing? "
            if r == 35:
                type = ["Upshifts", "Downshifts", "Adds {} dice to".format(random.randint(1,6))]
                adj = roll_row_from_table(autoloot_df, df_filters={"Type": "AdjectiveTable"})["Result"]
                type2 = ["parries", "counters", "{} rolls".format(adj)]
                action_text = "{} {}.".format(random.choice(type), random.choice(type2))
            if r == 36:
                action_text = "Alerts God."  # Too late; not even He can save us now

        numberOfEffects += 1
        if isModal and ("NICE, BIG" not in action_text):
            action_text = action_text[0].lower() + action_text[1:] # lowercases modal phrases
        if numberOfEffects < modalDegree:
            action_list.append(action_text[:-1] + ";")
        else:
            action_list.append(action_text)

    action_result = " ".join(action_list)

    chip_description_list = list(filter(None, (cost_result, guard_result, condition_combined, action_result)))
    chip_list_format = [i[0].lower()+i[1:] if 'NICE, BIG' not in i else i for i in chip_description_list[1:]]  # lowercases the first letter of non-first phrases, except for A NICE, BIG {} and Alerts God
    chip_description_list = chip_description_list[0:1] + chip_list_format
    chip_description_list = [category_description] + chip_description_list + [xdamage_description]
    chip_description = " ".join(chip_description_list)
    subtitle_trimmed = "/".join(filter(None, (damage_result, range_description, category_result, tag_result)))

# NAME:
    adj = roll_row_from_table(autoloot_df, df_filters={"Type": "AdjectiveTable"})["Result"]
    noun = roll_row_from_table(autoloot_df, df_filters={"Type": "NounTable"})["Result"]
    embed = discord.Embed(
        title="__{}{}__".format(adj, noun),
        color=cc_color_dictionary["Nyx"])
    embed.add_field(name="[%s]" % subtitle_trimmed,
                    value="_%s_" % chip_description)
    return await interaction.response.send_message(embed=embed)

# the vatican is not going to approve what i'm about to do
def clean_args_multi(args, lowercase=True):
    if len(args) == 1:
        args = re.split(r"(?:,|;)\s+", args[0])

    if lowercase:
        args = [i.lower().strip() for i in args if i and not i.isspace()]
    else:
        args = [i.strip() for i in args if i and not i.isspace()]

    return args

async def fish_master(arg, simplified=True):
    fish_info, content_msg = await find_value_in_table(fish_df, "Name", arg, suppress_notfound=True, alias_message=True)

    if fish_info is None:
        fish_info, content_msg = await find_value_in_table(fish_df, "Name", arg)
        if fish_info is None:
            return None, None, None, None, None, None, content_msg

    fish_name = fish_info["Name"] # simple
    fish_description = fish_info["Description"] # simple
    fish_habitats = fish_info["Habitats"]
    fish_diet = fish_info["Diet"]
    fish_hp = fish_info["HP"]
    fish_weight = fish_info["Weight"]
    fish_tags = fish_info["Tags"]
    fish_footer = "Weight: %s" % fish_weight # simple

    fish_color = cc_color_dictionary["NetFishing"]

    fish_descript_block = ""
    fish_title = ""

    if simplified:
        fish_descript_block += "*%s*\n" % fish_description
    else:
        try:
            hp_int = int(fish_hp)
            fish_hp = "%d" % hp_int
        except ValueError:
            pass
        fish_title = "HP %s" % fish_hp
        fish_descript_block = "**Diet:** %s" % fish_diet
        fish_descript_block += "\n"
        fish_descript_block += "**Habitats:** ||%s||" % fish_habitats
        fish_descript_block += "\n"
        fish_descript_block += "**Tags:** %s" % (fish_tags if fish_tags else "None")
        fish_descript_block += "\n"
        fish_descript_block += "*%s*" % fish_description

    return fish_name, fish_title, fish_descript_block, fish_footer, None, fish_color, content_msg

def query_fish(arg_lower):
    # alias_check = filter_table(cc_df, {"Alias": "(?:^|,|;)\s*%s\s*(?:$|,|;)" % re.escape(arg_lower)})

#    fish_habitats_list = fish_df["Habitats"].str.split(",").explode().str.strip().unique()

    habitat_modifiers = {
        "corporate-approved": "-Friendly/+Sterile, -New/+Old",
        "abstract space": "-Silly/+Serious, -Blocky/+Round",
        "g4merz 0nly": "-Casual/Hardcore, -Sci-fi/+Fantasy",
        "realsim": "-Lo-fi/+Hi-fi, -Rainy/+Sunny",
        "the undernet": "-Ravelike/+Gravelike, -Vast/+Narrow"
    }


    if arg_lower in [i.lower() for i in fish_habitats_list]:
        subdf = filter_table(fish_df, {"Habitats": re.escape(arg_lower)})

        # forgive me. i know this is stupid
        # but i tried a multitude of different things to get the data set to play nice.
        habitat_styled = {
            "the undernet": "The Undernet",
            "corporate-approved": "Corporate-Approved",
            "g4merz 0nly": "G4MERZ 0NLY",
            "realsim": "RealSim",
            "abstract space": "Abstract Space"
        }

        styled_habitat = habitat_styled.get(arg_lower, arg_lower.title())

        for habitat, modifiers in habitat_modifiers.items():
            if arg_lower in habitat:
                result_title = f"Fish in the `{styled_habitat}` habitat...\n**Modifiers:** {modifiers}"
                break
        else:
            result_title = f"Fish in the `{subdf.iloc[0]['Habitats']}` habitat..."

        result_msg = ", ".join(subdf["Name"])
    elif arg_lower in fish_tag_list:
        subdf = filter_table(fish_df, {"Tags": re.escape(arg_lower)})
        result_title = "Fish with the `%s` tag..." % arg_lower.capitalize()
        result_msg = ", ".join(subdf["Name"])
    else:
        return False, "", ""
    return True, result_title, result_msg

def query_fish_names():
    result_title = "Displaying all known Fish..."
    off_df = filter_table(fish_df, {"Name": ""})
    result_text = ", ".join(off_df["Name"])
    return True, result_title, result_text

@bot.tree.command(name='fish', description=commands_dict["fish"])
async def fish(interaction: discord.Interaction, query: str, detailed: bool = False):

    cleaned_args = clean_args_multi([query])

    if (len(cleaned_args) < 1) or (cleaned_args[0] == 'help'):
        return await interaction.response.send_message(
            f"Give me the name of 1-{MAX_FISH_QUERY} **Fish** and I can pull up their info for you! Please separate them with commas! (,)\n\n" +
            "I can list all of the Fish with **all**! I can also query Fish by **Tag** or **Habitat**!\n" +
            "To pull up details on a specific Tag, use `tag` instead.")
    elif cleaned_args[0] in ['all', 'list']:
        _, result_title, result_text = query_fish_names()
        return await send_query_msg(interaction, result_title, result_text)
    elif cleaned_args[0] in ['habitat', 'habitats']:
        result_title = "Displaying all known Fish Habitats..."
        result_text = ", ".join(fish_habitats_list)
        return await send_query_msg(interaction, result_title, result_text)


    elif cleaned_args[0] in ['tag', 'tags']:
        result_title = "Displaying all known Fish Tags..."
        result_text = ", ".join([i.capitalize() for i in fish_tag_list])
        return await send_query_msg(interaction, result_title, result_text)
    elif cleaned_args[0] in ['rule', 'ruling', 'rules']:
        ruling_msg, _ = await find_value_in_table(help_df, "Command", "fishruling", suppress_notfound=True)
        if ruling_msg is None:
            return await interaction.response.send_message(
                content="Couldn't find the rules for this command! (You should probably let the devs know...)",
                ephemeral=True)
        return await interaction.response.send_message(ruling_msg["Response"])
    elif len(cleaned_args) > MAX_FISH_QUERY:
        return await interaction.response.send_message(
            content=f"Too many fish, no more than {MAX_FISH_QUERY}!", ephemeral=True)

    arg_combined = " ".join(cleaned_args)

    is_query, result_title, result_msg = query_fish(arg_combined)
    if is_query:
        return await send_query_msg(interaction, result_title, result_msg)

    msg_embeds = []
    msg_warn = []

    for arg in cleaned_args:
        if not arg:
            continue
        fish_name, fish_hp, fish_description, fish_footer, fish_image, fish_color, add_msg = await fish_master(arg, simplified=not detailed)

        msg_warn.append(add_msg)
        if fish_name is None:
            continue

        embed = discord.Embed(title=fish_name, color=fish_color)
        if detailed:
            embed.add_field(name=fish_hp, value=fish_description, inline=True)
        else:
            embed.description = fish_description
        embed.set_footer(text=fish_footer)
        msg_embeds.append(embed)

    return await send_multiple_embeds(interaction, msg_embeds, msg_warn)


@bot.tree.command(name='fishroll', description=commands_dict["fishroll"])
async def fishroll(interaction: discord.Interaction, environment: typing.Literal["Abstract Space", "Corporate-Approved", "G4MERZ 0NLY", "RealSim", "The Undernet"], x: typing.Literal[-2, -1, 0, 1, 2], y: typing.Literal[-2, -1, 0, 1, 2], population: typing.Literal["Low", "Normal", "High"], size: typing.Literal["size variance", "no size variance"]):
    x = max(-2, min(x, 2))
    y = max(-2, min(y, 2))

    if population == "Low":
        rolls = 2
    elif population == "High":
        rolls = 4
    else:
        rolls = 3

    if environment == "Abstract Space":
        fish_env = nf_abstract_df
        if x < 0:
            attenuation_1 = "Silly"
        if x > 0:
            attenuation_1 = "Serious"
        if x == 0:
            attenuation_1 = "Silly / Serious Neutral"
        if y < 0:
            attenuation_2 = "Blocky"
        if y > 0:
            attenuation_2 = "Round"
        if y == 0:
            attenuation_2 = "Blocky / Round Neutral"
    if environment == "Corporate-Approved":
        fish_env = nf_corporate_df
        if x < 0:
            attenuation_1 = "Friendly"
        if x > 0:
            attenuation_1 = "Sterile"
        if x == 0:
            attenuation_1 = "Friendly / Sterile Neutral"
        if y < 0:
            attenuation_2 = "New"
        if y > 0:
            attenuation_2 = "Old"
        if y == 0:
            attenuation_2 = "New / Old Neutral"
    if environment == "G4MERZ 0NLY":
        fish_env = nf_gamers_df
        if x < 0:
            attenuation_1 = "Casual"
        if x > 0:
            attenuation_1 = "Hardcore"
        if x == 0:
            attenuation_1 = "Casual / Hardcore Neutral"
        if y < 0:
            attenuation_2 = "Sci-fi"
        if y > 0:
            attenuation_2 = "Fantasy"
        if y == 0:
            attenuation_2 = "Sci-fi / Fantasy Neutral"
    if environment == "RealSim":
        fish_env = nf_realsim_df
        if x < 0:
            attenuation_1 = "Lo-fi"
        if x > 0:
            attenuation_1 = "Hi-fi"
        if x == 0:
            attenuation_1 = "Lo-fi / Hi-fi Neutral"
        if y < 0:
            attenuation_2 = "Rainy"
        if y > 0:
            attenuation_2 = "Sunny"
        if y == 0:
            attenuation_2 = "Rainy / Sunny Neutral"
    if environment == "The Undernet":
        fish_env = nf_undernet_df
        if x < 0:
            attenuation_1 = "Ravelike"
        if x > 0:
            attenuation_1 = "Gravelike"
        if x == 0:
            attenuation_1 = "Ravelike / Gravelike Neutral" # we crypt of the necrodancer now
        if y < 0:
            attenuation_2 = "Vast"
        if y > 0:
            attenuation_2 = "Narrow"
        if y == 0:
            attenuation_2 = "Vast / Narrow Neutral"


    fish_chart = {
        "empty": "if this is showing up please bug amon",
    }

    results_list = []

    for _ in range(rolls):
        # Roll two dice and apply modifiers
        die_1 = random.randint(1, 6) + x
        die_2 = random.randint(1, 6) + y

        fish_result = get_fish_from_environment(fish_env, die_1, die_2, size)

        if fish_result:
            results_list.append(fish_result)
        else:
            results_list.append(fish_chart["empty"])

    result_text = "\n ".join(results_list)

    embed = discord.Embed(title="__Rolling Up Your Fish__",
                          description=f"_{interaction.user.mention} rolled to find fish in **{environment}**..._\n\nGot:\n {result_text} \nEnvironment Attenuation: {attenuation_1}, {attenuation_2}",
                          color=cc_color_dictionary["NetFishing"])
    return await interaction.response.send_message(embed=embed)


def get_fish_from_environment(fish_env: DataFrame, die_1: int, die_2: int, size: str) -> str:
    max_row_index, max_col_index = fish_env.shape
    size_score = 0

    if die_1 < 0:
        die_1 = max_row_index + die_1
    if die_2 < 0:
        die_2 = max_col_index + die_2

    if 0 <= die_1 <= max_row_index and 0 <= die_2 <= max_col_index:
        fish = fish_env.iloc[die_1, die_2]

        if fish == "":
            return "> _Nothing showed up_"

        if "!!" in str(fish):
            return f"> _Virus:_ {str(fish).replace('!!', ':bangbang: ')}"
        elif "%" in str(fish):
            return f"> _Battlechip or NCP:_ {str(fish).replace('%', ':star: ')}"
        elif "" in str(fish):
            return f"> _Mystery Data:_ {str(fish).replace('', ':large_blue_diamond: ')}"
        else:
            if size == "no size variance":
                return f"> _Fish:_ {fish}"
            if size == "size variance":
                size_score = roll_size_variance()
                if size_score <= 4:
                    fish = f"{fish} **(Extra Small!!!)**"
                elif size_score >= 10:
                    fish = f"{fish} **(Extra Large!!!)**"
        return f"> _Fish:_ {fish}"
    else:
        return None

def roll_size_variance():
        rolls = [random.randint(1, 6) for _ in range(3)]
        rolls.sort()
        size_score = rolls[0] + rolls[2]

        return size_score


users_fishing = set()

@bot.tree.command(name='fishtimer', description=commands_dict["fishtimer"])
async def fishtimer(interaction: discord.Interaction):
    if interaction.user.id in users_fishing:
        return await interaction.response.send_message("You're already fishing!", ephemeral=True)

    users_fishing.add(interaction.user.id)

    messages = [
        "You cast your line into the water... something tugs!",
        "The water ripples as your bait simmers in the cool abyss..",
        "A mysterious splash nearby... could it be? A fish?",
        "The fish are quiet today... but you catch a glimpse of something moving below.",
        "You feel your fishing pole tremble on the coasts of the water.",
        "You wait patiently... but the fish seem to be in hiding today.",
        "The water is calm..",
        "Man.. you love fishing.",
        "A big splash!!",
        "The line is tugging...",
        "A fish leaps from the water in a dazzling display before slipping back in!",
        "Your bait sinks deep..",
        "A shadow swims past, but your bait doesn’t seem to attract it.",
        "The water is eerily still... but you feel a subtle tug on the line.",
        "Something's lurking beneath... the line pulls tight, but it's gone before you can react.",
        "Your bait disappears under the water... a good sign, but no fish in sight yet.",
        "Your pole shakes.. something's out there. Just out of reach.",
        "You reel in slowly, feeling the tension in your arms... nothing yet.",
        "A shadow glides through the depths... but your bait isn't tempting enough.",
        "The stillness of the water holds... waiting for something to bite.",
        "The surface breaks with a splash... something huge is moving beneath!",
        "A flash of silver under the water, but it’s gone before you can react.",
        "Something's there, but it's playing coy. You know it.",
    ]

    rare_messages = [
        "Fish fear you.. viruses fear you.. navis turn their eyes away from you as you walk... you are alone on this barren network. Nevermind those Navis nearby."
        "The line tugs, but there’s no fight, just the weight of forgotten things weighing you down.",
        "The hum of empty data echoes through the void, your presence a ripple in a sea that no longer remembers its own waves.",
        "Code bends around you like a mirror cracked from too many reflections, and the silence settles deeper than any error ever could.",
        "You wonder if this is what the afterlife is like for a Navi.",
        "Time moves in slow motion here, each second stretching into eternity, but all that remains is a fading trace of what once mattered.",
        "The line trembles in your hands, but the water remains still, as if even the fish are hiding from the truth beneath the surface.",
        "The hook sinks slowly, but the waiting feels eternal, like the patience of the water itself has become a quiet kind of ambivalence.",
        "The fish swim below, just out of reach, and you begin to wonder if they can feel the same emptiness in the depths that you do when you reel in nothing but the weight of your own waiting.",
        "Bass Pro Shop.",
        "You feel the tug, faint at first, but it's enough - proof that even in the quietest moments, there is still life beneath the surface, waiting to connect.",
        "You're thinking about starting a business, and if so, what would you sell."
    ]

    if random.random() < 0.97:
        result_message = random.choice(messages)
    else:
        result_message = random.choice(rare_messages)

    embed = discord.Embed(title="__Fishin'__...",
                          description=f"_{interaction.user.mention} has gone fishin'..._\n\n{result_message}",
                          color=cc_color_dictionary["NetFishing"])

    initial_message = await interaction.response.send_message(embed=embed)

    await send_fish_activity(interaction, initial_message, interaction.user)


async def send_fish_activity(interaction, initial_message, initial_user):
    delay = random.randint(3, 600)
    await asyncio.sleep(delay)

    caught_messages = [
        "And something's tugging on the fishing pole!",
        "Something big's coming!",
        "The line's starting to pull hard!",
        "You feel that? You've got a bite!",
        "The tension’s building... something's on the hook!",
        "Get ready, something's on the line!",
        "The rod's bending, it’s a big one!",
        "You've got a strong one fighting back!",
        "It’s a big catch, keep reeling!",
        "Something massive is pulling at the line!"
    ]

    users_fishing.discard(initial_user.id)

    user_name = initial_user.mention

    if delay < 60:
        follow_up_message = f"> {delay} seconds have passed for {user_name}...\n> {random.choice(caught_messages)}"
    else:
        minutes = delay // 60
        seconds = delay % 60
        follow_up_message = f"> {minutes} minute(s) and {seconds} second(s) have passed for {user_name}...\n> {random.choice(caught_messages)}"

    await interaction.followup.send(follow_up_message)