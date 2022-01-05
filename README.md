# ProgBot
A Python bot made to help with NetBattlers, a tabletop roleplaying game inspired by MegaMan Battle Network, made by Will Uhl.

To add ProgBot to your server, click [this link](https://discordapp.com/oauth2/authorize?client_id=572878200397627412&scope=bot&permissions=0)! https://discordapp.com/oauth2/authorize?client_id=572878200397627412&scope=bot&permissions=0 

### Dependencies
- `discord.py` (1.2+)
- `pandas` (1.1+)
- `rply` (0.7+)
- `python-dotenv` (0.10+)
- `requests`

### How to Setup a Local Instance
- Clone or fork ProgBot, downloading the files.
- Download [Python](https://www.python.org/downloads/) 3.6+ onto your system and set it up.
- Add the Python directory with the executable to PATH environment variable
   - [Windows Guide](https://www.educative.io/edpresso/how-to-add-python-to-path-variable-in-windows), [Mac Guide](https://www.educative.io/edpresso/how-to-add-python-to-the-path-variable-in-mac)
   - Otherwise, you will have to substitute the executable filepath in place of `python` calls.
- In Command Line, change directory to location of ProgBot Code Dump with: `cd [filepath_to_progbot]`
- In Command Line, install all dependencies using pip: `python -m pip install -r dependencies.txt`. 
    - You may need additional flags. If so, try `python -3 -m pip install -Iv [package]==[version]`
- Generate a bot token via the [Discord Developer Portal](https://discordapp.com/developers/applications/)
     - [Link to Guide](https://www.writebots.com/discord-bot-token/)
- Create a new file called `.env` in the ProgBot code repository, and add the text below:
    ``` bash
    # env
    DISCORD_TOKEN=[PASTE TOKEN HERE, REPLACING BRACKETS AS WELL]
    ```
- Start the bot using: `python main.py`
    - If successful, it will output the following after a few seconds, in the command line:
     ```
     Jacking In! 
     Name: [Bot Name] 
     ID: [Bot ID]
     ```
    - If there's other errors... Godspeed. All errors will be printed out in the Command Line.
- In the [Discord Dev portal](https://discordapp.com/developers/applications/), go to **Oauth2** and generate an invite link by checking Bot and Send Messages
- Go to that link and invite bot to a server (probably a test one)
- The bot will now respond to commands in the server!

### Contributing
Fork a branch from master and submit pull requests!

### Commands
Default command prefix is `>`.

`oops`
Undoes the last bot output from the user.

`changeprefix`
Changes the prefix of the bot (server owner only)

`command`/`commands`
Displays all known commands.

`help`
Outputs help messages for commands or various rule tidbits. Can pull up a list of all help messages available with `help all`/`help list`.

`invite`
Generates an invite link for ProgBot.

`roll`/`r`
Rolls dice. Supports comments and basic NetBattlers macros.

`repeatroll`/`repeatr`/`repeat`/`rr`
Repeats a roll command. Supports comments and basic NetBattlers macros.

`chip`/`chips`
Pulls up chip information. Can also be used to query chips by Category, Tag, or Source (i.e. ChitChat).

`power`/`powers`
Pulls up Power information. Can also be used to query powers by Skill, Type, and Navi/Virus.

`ncp`
Pulls up NaviCust Part information. Can also be used to query NCPs by EB.

`virus`
Pulls up basic Virus information: Name, Description, Image (if present), or Source. Can also be used to query by Category, Tag, and Source (i.e. ChitChat). 

`virusx`
Pulls up detailed Virus information, including statblocks and powers. 

`tag`
Pulls up information on Categories and Tags for Viruses and Chips.

`query`
Queries for information. (Goes through Chip, Power, NCP, Virus, NPUs, and Daemons.)

`bond`/`bondpower`
Pulls up information on Bond Powers. 

`mysterydata`/`md`/`mysteryreward`
Rolls Mystery Data. `mysteyreward` only includes Chips and NCPs.

`rulebook`
Shows rulebook links.

`element`
Rolls on the Element Generation table.

`virusr`/`virusrandom`
Rolls random viruses. Can specify the number and categories you want to roll.

`repo`/`playermade`/`pmc`/`pmr`
Searches and pulls up download links from the player-made content on Notion.

`adventure`
Creates a randomized adventure starter.

`fight`
Creates a randomized enemy Navi fight.

`sheet`
Pulls up the link to the blank, official character sheet.

`spotlight`/`spot`/`checklist`
Starts a Spotlight Tracker in the current text channel.

`glossary`
Searches and pulls up the ProgBot output for a Glossary term.

`find`/`search`
Searches through Chips, NPCs, and Powers for information all at once.

`daemon`
(NetBattlers Advance) Pulls up Daemon information.

`upgrade`/`npu`
(NetBattlers Advance) Searches for a Navi Power's upgrades.

`networkmod`/`mod`
(NetBattlers Advance) Pulls up information on a NetWork Mod. 

`audience`/`cheer`/`jeer`
(NetBattlers Advance) Rolls Cheers/Jeers. Can also track Cheer/Jeer Points for a text channel.

`weather`/`cyberweather`
(NetBattlers Advance content) Pulls up information for CyberWeather.

`achievement`/`achievements`/`achieve`
(NetBattlers Advance content) Pulls up information for an Achievement.

`crimsonnoise`
(Unofficial content from Genso Network) Rolls CrimsonNoise. 

`xcard`/`x`/`ocard`/`o`/`ncard`/`n`
Use the X, N, or O card. (TTRPG Safety Tools)

`rewind`/`fastforward`/`ffwd`/`fwd`/`pause`/`break`/`fbf`/`slow`
Use one of the Script Change tools: Rewind, Fast Forward, Pause, Frame-by-Frame. (TTRPG Safety Tools)

`line`/`veil`
Notify that a Line or Veil has been crossed. (TTRPG Safety Tools)

`luxton`
Request a Luxton Technique discussion. (TTRPG Safety Tools)

`opendoor`
Notify that you are utilizing the Open Door Policy. (TTRPG Safety Tools)

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