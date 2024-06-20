# ProgBot
A Python bot made to help with NetBattlers, a tabletop roleplaying game inspired by MegaMan Battle Network, made by Will Uhl.

To add ProgBot to your server, click [this link](https://discordapp.com/oauth2/authorize?client_id=572878200397627412&scope=bot&permissions=0)! 

### Dependencies
- `discord.py` (2.3+)
- `numpy` (1.24+)
- `pandas` (1.5+)
- `rply` (0.7+)
- `python-dotenv` (1.0+)
- `requests` (2.28+)

Run `pip install -r ./dependencies.txt` in the PROGBOT_CODE_DUMP folder to automatically install!

### Bot Permissions
- applications.commands
- bot

### How to Setup a Local Instance
- Clone or fork ProgBot, downloading the files.
- Download [Python](https://www.python.org/downloads/) 3.6+ onto your system and set it up.
- Add the Python directory with the executable to PATH environment variable
   - [Windows Guide](https://www.educative.io/edpresso/how-to-add-python-to-path-variable-in-windows), [Mac Guide](https://www.educative.io/edpresso/how-to-add-python-to-the-path-variable-in-mac)
   - Otherwise, you will have to substitute the executable filepath in place of `python` calls.
- In Command Line, change directory to location of ProgBot Code Dump with: `cd [filepath_to_progbot]`
- In Command Line, install all dependencies using pip: `python -m pip install -r dependencies.txt`. 
    - You may need additional flags. If so, try `python -3 -m pip install -Iv [package]==[version]`
- Go to the [Discord Developer Portal](https://discordapp.com/developers/applications/) and generate a bot token
     - [Link to Guide](https://www.writebots.com/discord-bot-token/)
- Create a new file called `.env` in the ProgBot code repository, and add the text below:
    ``` bash
    # env
    DISCORD_TOKEN=[PASTE TOKEN HERE, REPLACING BRACKETS AS WELL]
    PMC_KEY=[Different token needed by playermaderepo command; ask a dev if needed]
    ```
- Go back to the [Discord Developer Portal](https://discordapp.com/developers/applications/), then go to the **Oauth2** tab and generate an invite link by: 
    - Under Scopes, checking both `applications.commands` and `bot`
    - Then under Bot Permissions, check under Text Permissions:
        - `Send Messages`
        - `Send Messages in Threads`
        - `Use External Emojis`
        - `Add Reactions`
- Paste the invite link into your browser and invite bot to a server (probably a test one)
- Update the following fields in `settings.py`:
    - `admin_guild`: the server you want to dev-test this on
    - `bugreport_channel_id`: channel that you want to send test bug report messages to
    - `source_guild_id`: the server with special emojis (probably your dev-test server) (see [Custom Emoji Support](#custom-emoji-support))
    - `custom_emojis`: Special Emoji IDs (see [Custom Emoji Support](#custom-emoji-support))
- To allow usage of admin commands, add a new line to the end of `tables/user_levels.tsv`:
    ```
    [Your Discord user ID]	3	[your discord username]
    ```
- Start the bot using: `python main.py`
    - If successful, it will output the following after a few seconds, in the command line:
     ```
     Jacking In! 
     Name: [Bot Name] 
     ID: [Bot ID]
     ```
    - If there's other errors... Godspeed. All errors will be printed out in the Command Line.
- Run `/run command:refresh slash commands` in the server to get your bot to register the new slash commands
- Wait a few minutes (or an hour) for the slash commands to sync across Discord, and...
- You should be able to see slash commands in the server and start using them!

### Contributing
Fork a branch from master and submit pull requests!

Note: if GitHub seems to be flagging all lines in the .tsv as changed, this is likely due to cross-OS line ending discrepencies. If so, refer to [this guide](https://docs.github.com/en/get-started/getting-started-with-git/configuring-git-to-handle-line-endings) to address.

### Slash Commands

`run`
Runs admin/dev-level commands: update slash commands across all servers, change status, shut down (goodnight). (Note: need to be in `admin_guild` to do this)

`commands`
Displays all known commands.

`help`
Outputs help messages for commands or various rule tidbits. Can pull up a list of all help messages available with `help all`/`help list`.

`invite`
Generates an invite link for ProgBot.

`roll`
Rolls dice. Supports comments and basic NetBattlers macros (i.e. $N6, $H6).

`chip`
Pulls up chip information. Can also be used to query chips by Category, Tag, or Source (i.e. ChitChat).

`power`
Pulls up Power information. Can also be used to query powers by Skill, Type, and Navi/Virus.

`ncp`
Pulls up NaviCust Part information. Can also be used to query NCPs by EB.

`virus`
Pulls up basic Virus information: Name, Description, Image (if present), or Source. Can also be used to query by Category, Tag, and Source (i.e. ChitChat). 

`tag`
Pulls up information on Categories and Tags for Viruses and Chips.

`query`
Queries for information. (Goes through Chip, Power, NCP, Virus, NPUs, and Daemons.)

`bondpower`
Pulls up information on Bond Powers. 

`mysterydata`
Rolls Mystery Data. 

`rulebook`
Shows rulebook links.

`element`
Rolls on the Element Generation table.

`virusrandom`
Rolls random viruses. Can specify the number and categories you want to roll.

`playermaderepo`
Searches and pulls up download links from the player-made content on Notion.

`adventure`
Creates a randomized adventure starter.

`fight`
Creates a randomized enemy Navi fight.

`sheet`
Pulls up the link to the blank, official character sheet.

`spotlight`
Starts a Spotlight Tracker in the current text channel.

`glossary`
Searches and pulls up the ProgBot output for a Glossary term.

`find`
Searches through Chips, NPCs, and Powers for information all at once.

`daemon`
(NetBattlers Advance) Pulls up Daemon information.

`npu`
(NetBattlers Advance) Searches for a Navi Power's upgrades.

`networkmod`
(NetBattlers Advance) Pulls up information on a NetWork Mod. 

`audience`/`audiencecheer`/`audiencejeer`
(NetBattlers Advance) Rolls Cheers/Jeers. Can also track Cheer/Jeer Points for a text channel.

`weather`
(NetBattlers Advance content) Pulls up information for CyberWeather.

`weatherforecast`
(NetBattlers Advance content) Rolls random CyberWeather.

`achievement`
(NetBattlers Advance content) Pulls up information for an Achievement.

`crimsonnoise`
(Unofficial content from Genso Network) Rolls CrimsonNoise. 

`safety`
Pull up information on a recognized safety tool. (TTRPG Safety Tools)

`bugreport`
Submit a bugreport to ProgBot's bugreport channel.

`entropy`
Test Progbot's randomness. (Only works on prod machine)

### Custom Emoji Support
Some commands (mostly `ncp` and `power`, maybe more in the future?) have support for custom emoji displays. To set this up, there's a couple of emojis included in the `/emoji` directory that you can use and upload to your own Discord server. You only need to set them up in one place, afterwards ProgBot can use them in any server it's invited to in addition to the storage server.

Setting this up isn't necessary for functionality, and if you're forking for your own purposes, you can even change them to something else.

- Figure out where you'd like to set up your emojis. This can be an existing server or a new storage server.
- Get the server ID by first enabling `Developer Mode` in Advanced settings in your Discord client.
- Right click on the server's icon and click `Copy ID` in the menu.
- Go to `settings.py`, and under `source_guild_id`, change the ID to your server's ID.
- Upload the emojis to the server, then send a message in the server with the emojis you want to set up, and a backslash (\\) just before it
    - Example: `\:emoji:`
- This should give you an output like `<:emoji:891893856516317244>` when sending the message. This is the emoji's global ID.
- Back in `settings.py`, there's a list of hardcoded emojis just underneath `source_guild_id`. You'll want to paste the emoji ID exactly within the `r" "` lines. E.g. `r"<:emoji:891893856516317244>"`
- If everything works as it should and ProgBot is invited to the storage server, you should get a `Custom emojis enabled!` message when starting ProgBot.

### Additional Databases
- [Customized Mastersheet](https://docs.google.com/spreadsheets/d/1aB6bOOo4E1zGhQmw2muOVdzNpu5ZBk58XZYforc8Eqw/edit?usp=sharing)
    - Prepared by Riject, editable with the link.
    - Manages License lists and aliases for Chips, Powers, and Viruses.
        - Chips
        - Powers/NCPs
        - Viruses
- [ProgBot Tables](https://drive.google.com/drive/folders/1EUvHkzAcbOD9QZdNgDxmtbtDe8nLVKmo?usp=sharing)
    - Contains all the other tables ProgBot uses for information! (Export as `.tsv`)
        - Bond Powers
        - Help Responses
        - Tag/Category Information
        - Mystery Data Tables
        - Element Table
        - Rulebook Links
        - Cheer/Jeer Tables
        - Network Mod Information
        - Daemon Information
        - Adventure Generation
        - Player-Made Content Chips, Powers, NCPs, Viruses, etc.
        - Nyx Crossover Content
        - Crimson Noise
