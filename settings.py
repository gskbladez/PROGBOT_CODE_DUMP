#BOT FILES
commands_table_name = "tables/commands.tsv"
user_levels_table_name = "tables/user_levels.txt"
log_file = "log.txt"
debug_log_file_name = "discord.log"
prefixfile = "prefixes.json"
settings_table_name = ""


#BOT SETTINGS
command_prefix = "/"
param_delim = " "
default_user_level = 1
max_user_level = 3
log_format = "{timestamp}\t{type}\t{server_id}\t{server_name}\t{channel_id}\t{channel_name}\t{user_id}\t{discord_tag}\t{nickname}\t{message_content}\t{data}\t{extra}"
channel_cooldown = 0
ignore_cd_level = 2
user_cooldown_0 = 0
user_cooldown_1 = 0
output_history_size = 10
background_task = None
enable_debug_logger = False
enable_run_command = True
run_command_name = "run"
run_command_description = "Run a prefix command"
run_command_default_response = "Command ran successfully"
default_status = "NetBattlers RPG"

#MESSAGES
message_something_broke = ":warning::warning: **SOMETHING BROKE** :warning::warning:"
message_unknown_command = "Command not recognized"
log_unhandled_error = "Unhandled error ({})"
message_result_too_long = "Sorry, the result was too long to output ({}/{} characters)"  # unused?
message_embed_too_long = "Sorry, the embed was too long to output ({} {}/{} characters)"   # unused?
message_embed_empty_field = "The output embed was invalid ({} can't be empty)"   # unused?
log_cooldown_active = "Cooldown active"
message_restricted_access = "You do not have permission to use this command"
message_missing_params = "Missing required parameters: {}"
message_refresh_app_commands_progress = "Slash commands refreshing..."

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
                 "KissRaffi": r"<:KissRaffi:911806713496223775>", "HappyRaffi": r"<a:HappyRaffi:911806713890476032>", 
                 "devilish": "👿"} # no smiling imp emoji

#TEST SUPPORT
bugreport_channel_id = 796498229872820314
source_guild_id = 668525535705694208
custom_emojis = {"instant": r"<:instant:892038392110534688>", "cost": r"<:costpower:892038391959539742>",
                 "roll": r"<:rollpower:892038392357994548>", "underflow": r"<:underflow:901981520321998849>",
                 "KissRaffi": r"<:KissRaffi:911806713496223775>", "HappyRaffi": r"<a:HappyRaffi:911806713890476032>", 
                 "devilish": "👿"}
background_task_interval = 0.5
# /home/bladez/update-proggers

#NETBATTLER CONSTANTS