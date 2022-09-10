#BOT FILES
commands_table_name = "commands.tsv"
settings_table_name = "settings.txt"
user_levels_table_name = "userlevels.txt"
customresponsestablename = "customresponses.txt"
log_file = "log.txt"
formattedlogfile = "formattedlog.txt"
debug_log_file_name = "discord.log"

prefixfile = "prefixes.json"
chipfile = "chipdata.tsv"
powerfile = "powerncpdata.tsv"
virusfile = "virusdata.tsv"
daemonfile = "daemondata.tsv"
bondfile = "bonddata.tsv"
tagfile = "tagdata.tsv"
mysterydatafile = "mysterydata.tsv"
networkmodfile = "networkmoddata.tsv"
crimsonnoisefile = "crimsonnoisedata.tsv"
audienceparticipationfile = "audiencedata.tsv"
elementfile = "elementdata.tsv"
helpfile = "helpresponses.tsv"
pmc_chipfile = "playermade_chipdata.tsv"
pmc_powerfile = "playermade_powerdata.tsv"
pmc_virusfile = "playermade_virusdata.tsv"
pmc_daemonfile = "playermade_daemondata.tsv"
nyx_chipfile = "nyx_chipdata.tsv"
nyx_ncpfile = "nyx_powerdata.tsv"
rulebookfile = "rulebookdata.tsv"
adventurefile = "adventuredata.tsv"
fightfile = "fightdata.tsv"
weatherfile = "weatherdata.tsv"
achievementfile = "achievementdata.tsv"
glossaryfile = "glossarydata.tsv"
autolootfile = "autolootdata.tsv"


#BOT SETTINGS
botname = "ProgBot"
token = ""
commandprefix = ">"
param_delim = ","
masteradmin = ""
default_user_level = 1
max_user_level = 3
log_format = "{timestamp}\t{type}\t{server_id}\t{server_name}\t{channel_id}\t{channel_name}\t{user_id}\t{discord_tag}\t{nickname}\t{message_content}\t{data}\t{extra}"
channel_cooldown = 1000  # technically unused rn
ignore_cd_level = 2
user_cooldown_0 = 60000  # in milliseconds; technically unused
user_cooldown_1 = 200  # in milliseconds; technically unused
output_history_size = 10
background_task = None
background_task_interval = 10 # TODO: Figure out background tasks with new koduck
enable_debug_logger = False
enable_run_command = False
run_command_name = "run"
run_command_description = "Run a prefix command"
run_command_default_response = "Command ran successfully"
purge_search_limit = 100

#HARDCODED LINKS
character_sheet = r"https://docs.google.com/spreadsheets/d/158iI4LCpfS4AGjV5EshHkbKUD4GxogJCiwZCV6QzJ5s/edit#gid=295914024"
common_md_image = r"https://raw.githubusercontent.com/gskbladez/meddyexe/master/virusart/commonmysterydata.png"
uncommon_md_image = r"https://raw.githubusercontent.com/gskbladez/meddyexe/master/virusart/uncommonmysterydata.png"
rare_md_image = r"https://raw.githubusercontent.com/gskbladez/meddyexe/master/virusart/raremysterydata.png"
gold_md_image = r"https://raw.githubusercontent.com/gskbladez/PROGBOT_CODE_DUMP/master/virusart/goldmysterydata.png"
violet_md_image = r"https://raw.githubusercontent.com/gskbladez/PROGBOT_CODE_DUMP/master/virusart/violetmysterydata.png"
sapphire_md_image = r"https://raw.githubusercontent.com/gskbladez/PROGBOT_CODE_DUMP/master/virusart/sapphiremysterydata.png"
sunny_md_image = r"https://raw.githubusercontent.com/gskbladez/PROGBOT_CODE_DUMP/master/virusart/sunnymysterydata.png"
bug_image = r"https://raw.githubusercontent.com/gskbladez/meddyexe/master/virusart/bug.png"
invite_link = r"https://discordapp.com/oauth2/authorize?client_id=572878200397627412&scope=bot&permissions=0"
notion_collection_id = "97e4a870-4673-4fc7-a2c7-3fb876e4d837"
notion_collection_view_id = "085a4095-0668-4722-a8ec-91ae6f56640c"
notion_collection_space_id = "678b1442-260b-497a-9bf3-0d6ab3938e0d"
notion_query_link = r"https://www.notion.so/api/v3/queryCollection"
#CUSTOM EMOJI SUPPORT
source_guild_id = 556291542206382080
custom_emojis = {"instant": r"<:instant:892170110465363969>", "cost": r"<:cost:892170110364680202>",
                 "roll": r"<:roll:892170110377295934>", "underflow": r"<:underflow:901995743752106064>",
                 "KissRaffi": r"<:KissRaffi:911806713496223775>", "HappyRaffi": r"<a:HappyRaffi:911806713890476032>"}

#MESSAGES
message_something_broke = ":warning::warning: **SOMETHING BROKE** :warning::warning:"
message_unknown_command = "Command not recognized"
message_unhandled_error = "Unhandled error ({})"
message_result_too_long = "Sorry, the result was too long to output ({}/{} characters)"
message_embed_too_long = "Sorry, the embed was too long to output ({} {}/{} characters)"
message_embed_empty_field = "The output embed was invalid ({} can't be empty)"
message_cooldown_active = "Cooldown active"
message_restricted_access = "You do not have permission to use this command"
message_missing_params = "Missing required parameters: {}"
message_oops_failed = "No last output from this user to delete"
message_oops_success = "Deleted last output from this user"
message_addresponse_success = "Added a custom response: '{}' -> '{}'"
message_addresponse_failed = "Failed to add custom response!"
message_addresponse_noparam = "Missing parameters to add response"
message_removeresponse_success = "Removed a custom response"
message_removeresponse_failed = "'{}' doesn't seem to have a corresponding custom response"
message_removeresponse_noparam = "Missing parameters to remove response"
message_addsetting_success = "Successfully added setting"
message_addsetting_failed = "That setting name already exists"
message_updatesetting_success = "Setting updated!"
message_updatesetting_failed = "That setting name doesn't seem to exist or you don't have permission to edit it"
message_updatesetting_noparam = "Need parameters for setting update!"
message_removesetting_success = "Successfully removed setting"
message_removesetting_failed = "That setting name doesn't seem to exist or you don't have permission to edit it"
message_removesetting_noparam = "Need parameters to remove setting"
message_nomentioneduser = "I need exactly one mentioned user!	"
message_addadmin_success = "<@!{}> is now an admin!"
message_addadmin_failed = "That user is already an admin"
message_removeadmin_success = "<@!{}> is no longer an admin"
message_removeadmin_failed = "That user is not an admin"
message_purge_invalidparam = "Please give me an integer number of bot messages to purge"
message_restrict_success = "<@!{}> is now restricted from using {} commands"
message_restrict_failed = "That user is already restricted"
message_restrict_failed2 = "{} admins cannot be restricted"
message_unrestrict_success = "<@!{}> is now unrestricted from using {} commands"
message_unrestrict_failed = "That user is not restricted"
message_nomentioneduser = "I need exactly one mentioned user!"
message_nomentioneduser2 = "I need exactly zero or one mentioned user!"
message_sendmessage_noparam = "Need a message to send!"
message_refresh_commands_success = "Commands refreshed successfully"
message_refresh_commands_errors = "There were some errors while refreshing commands:"
bugreport_channel_id = 704684798584815636
errorlog_channel_id	= 623686382237384707