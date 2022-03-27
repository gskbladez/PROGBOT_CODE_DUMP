import koduck


async def xcard(context, *args, **kwargs):
    return await koduck.sendmessage(context["message"],
                                    sendcontent=":x: **A participant has used an X-card.** Stop the scene and talk it out.")


async def ncard(context, *args, **kwargs):
    return await koduck.sendmessage(context["message"],
                                    sendcontent=":warning: **A participant has used an N-card.** Consider pausing to talk to your table about the direction of the scene to discuss adjustments.")


async def ocard(context, *args, **kwargs):
    return await koduck.sendmessage(context["message"],
                                    sendcontent=":white_check_mark: A participant has used an O-card. Keep going!")


async def luxton(context, *args, **kwargs):
    return await koduck.sendmessage(context["message"],
                                    sendcontent=":exclamation:**A participant would like to discuss a problem with the current content with the table.** Listen to their needs and wants, and consider giving them control over said content, then continue to play accomodating their requests.")


async def line(context, *args, **kwargs):
    return await koduck.sendmessage(context["message"],
                                    sendcontent=":octagonal_sign: **A participant has discovered a new Line.** You should pause to talk about it, and adjust things as necessary.")


async def veil(context, *args, **kwargs):
    return await koduck.sendmessage(context["message"],
                                    sendcontent=":cloud: **A participant has discovered a new Veil.** Consider toning down the detail in the current scene, and pause to talk to your table about it.")


async def opendoor(context, *args, **kwargs):
    return await koduck.sendmessage(context["message"],
                                    sendcontent=":door: **A participant needs to take a break, stop listening, or leave the game for safety reasons.**")


async def ffwd(context, *args, **kwargs):
    return await koduck.sendmessage(context["message"],
                                    sendcontent=":fast_forward: A participant would like to advance past the current scene.")


async def rewind(context, *args, **kwargs):
    return await koduck.sendmessage(context["message"],
                                    sendcontent=":rewind: A participant would like to rewind certain details of a scene.")


async def pause(context, *args, **kwargs):
    return await koduck.sendmessage(context["message"],
                                    sendcontent=":pause_button: A participant would like to take a break.")


async def resume(context, *args, **kwargs):
    return await koduck.sendmessage(context["message"],
                                    sendcontent=":arrow_forward: A participant is ready to resume play.")


async def fbf(context, *args, **kwargs):
    return await koduck.sendmessage(context["message"],
                                    sendcontent=":warning: A participant would like to take it slow during the oncoming scene. Continue as planned with caution.")

