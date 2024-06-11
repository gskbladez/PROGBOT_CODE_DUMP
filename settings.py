import os
from dotenv import load_dotenv
#BOT FILES

load_dotenv()
bot_token = os.getenv('DISCORD_TOKEN')
notion_pmc_token = os.getenv('PMC_KEY')

commands_table_name = "tables/commands.tsv"
user_levels_table_name = "tables/user_levels.tsv"
log_file = "progbot.log"
#prefixfile = "prefixes.json"

#BOT SETTINGS
default_status = "NetBattlers RPG"

#NETBATTLER DATA FILES
chipfile = "tables/chipdata.tsv"
powerfile = "tables/powerncpdata.tsv"
virusfile = "tables/virusdata.tsv"
daemonfile = "tables/daemondata.tsv"
bondfile = "tables/bonddata.tsv"
tagfile = "tables/tagdata.tsv"
mysterydatafile = "tables/mysterydata.tsv"
networkmodfile = "tables/networkmoddata.tsv"
crimsonnoisefile = "tables/crimsonnoisedata.tsv"
audienceparticipationfile = "tables/audiencedata.tsv"
elementfile = "tables/elementdata.tsv"
helpfile = "tables/helpresponses.tsv"
pmc_chipfile = "tables/playermade_chipdata.tsv"
pmc_powerfile = "tables/playermade_powerdata.tsv"
pmc_virusfile = "tables/playermade_virusdata.tsv"
pmc_daemonfile = "tables/playermade_daemondata.tsv"
nyx_chipfile = "tables/nyx_chipdata.tsv"
nyx_ncpfile = "tables/nyx_powerdata.tsv"
rulebookfile = "tables/rulebookdata.tsv"
adventurefile = "tables/adventuredata.tsv"
fightfile = "tables/fightdata.tsv"
weatherfile = "tables/weatherdata.tsv"
achievementfile = "tables/achievementdata.tsv"
glossaryfile = "tables/glossarydata.tsv"
autolootfile = "tables/autolootdata.tsv"

audiencesave = "save/audiences.json"
spotlightsave = "save/spotlights.json"

#HARDCODED LINKS
character_sheet = "https://docs.google.com/spreadsheets/d/158iI4LCpfS4AGjV5EshHkbKUD4GxogJCiwZCV6QzJ5s/edit#gid=295914024"
common_md_image = "https://raw.githubusercontent.com/gskbladez/meddyexe/master/virusart/commonmysterydata.png"
uncommon_md_image = "https://raw.githubusercontent.com/gskbladez/meddyexe/master/virusart/uncommonmysterydata.png"
rare_md_image = "https://raw.githubusercontent.com/gskbladez/meddyexe/master/virusart/raremysterydata.png"
gold_md_image = "https://raw.githubusercontent.com/gskbladez/PROGBOT_CODE_DUMP/master/virusart/goldmysterydata.png"
violet_md_image = "https://raw.githubusercontent.com/gskbladez/PROGBOT_CODE_DUMP/master/virusart/violetmysterydata.png"
sapphire_md_image = "https://raw.githubusercontent.com/gskbladez/PROGBOT_CODE_DUMP/master/virusart/sapphiremysterydata.png"
sunny_md_image = "https://raw.githubusercontent.com/gskbladez/PROGBOT_CODE_DUMP/master/virusart/sunnymysterydata.png"
bug_image = "https://raw.githubusercontent.com/gskbladez/meddyexe/master/virusart/bug.png"
invite_link = "https://discordapp.com/oauth2/authorize?client_id=572878200397627412&scope=bot&permissions=0"
notion_pmc_id = "dc469d3ae5f147cab389b6f61bce102e"
bugreport_image = "https://raw.githubusercontent.com/gskbladez/meddyexe/master/virusart/bug.png"
bugreport_channel_id = 704684798584815636

#CUSTOM EMOJI SUPPORT
source_guild_id = 556291542206382080
custom_emojis = {"instant": r"<:instant:892170110465363969>", "cost": r"<:cost:892170110364680202>",
                 "roll": r"<:roll:892170110377295934>", "underflow": r"<:underflow:901995743752106064>",
                 "KissRaffi": r"<:KissRaffi:911806713496223775>", "HappyRaffi": r"<a:HappyRaffi:911806713890476032>", "devilish": r"👿"}

# /home/bladez/update-proggers

#NETBATTLER CONSTANTS