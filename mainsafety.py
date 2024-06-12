import typing
import discord
from maincommon import bot, commands_dict

@bot.tree.command(name='safety', description=commands_dict["safety"])
async def safety(interaction: discord.Interaction, 
                 tool:typing.Literal['X-Card', 'N-Card', 'O-Card', 'Luxton', 'Line', 'Veil', 'Open Door', 'Fast Foward', 'Rewind', 'Pause', 'Play', 'Resume', 'Frame-by-Frame']):
    arg = tool.lower().strip()
    if arg == 'x-card':
        msg = ":x: **A participant has used an X-card.** Stop the scene and talk it out."
    elif arg == 'n-card':
        msg = ":warning: **A participant has used an N-card.** Consider pausing to talk to your table about the direction of the scene to discuss adjustments."
    elif arg == 'o-card':
        msg = ":white_check_mark: A participant has used an O-card. Keep going!"
    elif arg == 'luxton':
        msg = ":exclamation:**A participant would like to discuss a problem with the current content with the table.** Listen to their needs and wants, and consider giving them control over said content, then continue to play accomodating their requests."
    elif arg == 'line':
        msg = ":octagonal_sign: **A participant has discovered a new Line.** You should pause to talk about it, and adjust things as necessary."
    elif arg == 'veil':
        msg = ":cloud: **A participant has discovered a new Veil.** Consider toning down the detail in the current scene, and pause to talk to your table about it."
    elif arg == 'open door':
        msg = ":door: **A participant needs to take a break, stop listening, or leave the game for safety reasons.**"
    elif arg == 'fast forward':
        msg = ":fast_forward: A participant would like to advance past the current scene."
    elif arg == 'rewind':
        msg = ":rewind: A participant would like to rewind certain details of a scene."
    elif arg == 'pause':
        msg = ":pause_button: A participant would like to take a break."
    elif arg == 'resume' or arg == 'play':
        msg = ":arrow_forward: A participant is ready to resume play."
    elif arg == 'frame-by-frame':
        msg = ":warning: A participant would like to take it slow during the oncoming scene. Continue as planned with caution."
    else:
        return await interaction.response.send_message(content="Sorry, didn't recognize that safety tool! Try communicating the topic to your group directly, or notify a trusted friend; you can do it!", ephemeral=True)
    return await interaction.response.send_message(msg)
