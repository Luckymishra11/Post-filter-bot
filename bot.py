import asyncio
import contextlib
from telethon import TelegramClient, events, Button
from telethon.tl.functions.messages import (
    ExportChatInviteRequest,
    ImportChatInviteRequest,
)
from telethon.errors.rpcerrorlist import (
    UserAlreadyParticipantError,
    UserNotParticipantError,
    FloodWaitError,
)
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import PeerChannel
from telethon.sessions import StringSession
from database import *
from config import Config
import traceback
from datetime import datetime
from utils import grt, valid_args

api_id = Config.API_ID
api_hash = Config.API_HASH
bot_token = Config.BOT_TOKEN
bot = TelegramClient("filterbot", api_id, api_hash).start(bot_token=bot_token)
session = Config.STRINGSESSION
client = TelegramClient(StringSession(session), api_id=api_id, api_hash=api_hash)
SUBSCRIPTION_TIME = Config.SUBSCRIPTION_TIME * 86400

print(
    """
Bot Started...
Running...
"""
)


async def get_user_join(userid, channel):
    ok = True
    try:
        await bot(GetParticipantRequest(channel=channel, participant=userid))
        ok = "True"
    except UserNotParticipantError:
        ok = "False"
    except Exception:
        ok = "startpm"
    return ok


async def filter_pm(event, text):
    channels = Config.DATABASE_CHANNELS
    messages = []
    args = valid_args(text)
    print(
        f"""Query: {args}
Type: PM
User: {event.sender.first_name} - [{event.sender_id}]

"""
    )
    if not args:
        return

    procmsg = await event.reply(f'**Searching For "{args}"...🔍**')
    for channel in channels:
        try:
            channelobj = await client.get_entity(channel)
        except Exception:
            print(traceback.format_exc())
            return
        async for msg in client.iter_messages(channelobj, search=args, limit=10):
            link = f"https://t.me/{channelobj.username}/{msg.id}"
            # link = f"t.me/c/{channel}/{msg.id}"
            title = (
                msg.text.split("\n")[0]
                .replace("**", "")
                .replace("__", "")
                .replace("`", "")
            )
            textmessage = f"""**🍿 {title}
👉 {link}

**"""
            messages.append(textmessage)

    if not messages:
        replytext = f"""**No Results Found For {text}**
**Type Only Movie Name 💬**
**Check Spelling On Google** 🔍"""
        buttons = [
            [
                Button.url(
                    "Click To Check Spelling ✅",
                    f'http://www.google.com/search?q={text.replace(" ", "%20")}%20movie',
                )
            ],
            [
                Button.url(
                    "Click To Check Release Date 📅",
                    f'https://www.google.com/search?q={text.replace(" ", "%20")}%20Movie%20Release%20Date',
                )
            ],
        ]


        try:
            msgg = await event.reply(replytext, buttons=buttons)
            await procmsg.delete()
        except Exception:
            await procmsg.delete()
            return
        if not is_autodelete():
            return
        await asyncio.sleep(Config.DELETE_DELAY)
        await bot.delete_messages(event.chat_id, message_ids=msgg.id)
        return
    messageids = []
    txt = ""
    for message in messages:
        txt += message
        if len(txt) > 4000:
            msgg = await event.reply(txt, link_preview=False)
            messageids.append(msgg.id)
            await asyncio.sleep(0.3)
            txt = ""

    await procmsg.delete()
    messageids.append(event.id)
    if not is_autodelete():
        return
    await asyncio.sleep(Config.DELETE_DELAY)
    await bot.delete_messages(event.chat_id, message_ids=messageids)
    return


async def filter_message(event, text, chatid):
    channels = get_channels(chatid)
    if not channels:
        return
    messages = []
    args = valid_args(text)
    print(
        f"""Query: {text}
Type: Group
Chat: {event.chat.title} - [{event.chat_id}]

"""
    )
    if not args:
        return
    procmsg = await event.reply(f'**Searching For "{args}"...🔍**')
    for channel in channels:
        try:
            channelobj = await client.get_entity(PeerChannel(channel))
        except Exception:
            print(traceback.format_exc())
            return
        async for msg in client.iter_messages(channelobj, search=args, limit=10):
            link = f"https://t.me/{channelobj.username}/{msg.id}"
            # link = f"t.me/c/{channel}/{msg.id}"
            title = (
                msg.text.split("\n")[0]
                .replace("**", "")
                .replace("__", "")
                .replace("`", "")
            )
            textmessage = f"""**🍿 {title} 
👉 {link}
**"""
            messages.append(textmessage)

    if not messages:
        replytext = f"""**No Results Found For {text}**
**Type Only Movie Name 💬**
**Check Spelling On Google** 🔍"""
        buttons = [
            [
                Button.url(
                    "Click To Check Spelling ✅",
                    f'http://www.google.com/search?q={text.replace(" ", "%20")}%20movie',
                )
            ],
            [
                Button.url(
                    "Click To Check Release Date 📅",
                    f'https://www.google.com/search?q={text.replace(" ", "%20")}%20Movie%20Release%20Date',
                )
            ],
        ]

        try:
            msgg = await event.reply(replytext, buttons=buttons)
            await procmsg.delete()
        except Exception:
            await procmsg.delete()
            return
        if not is_autodelete():
            return
        await asyncio.sleep(Config.DELETE_DELAY)
        await bot.delete_messages(event.chat_id, message_ids=msgg.id)
        return
    txt = "\n\n".join(messages)
    msgg = await event.reply(txt, link_preview=False)
    messageids = [msgg.id]
    await asyncio.sleep(0.3)
    txt = ""

    await procmsg.delete()
    messageids.append(event.id)
    if not is_autodelete():
        return
    await asyncio.sleep(Config.DELETE_DELAY)
    await bot.delete_messages(event.chat_id, message_ids=messageids)
    return


@bot.on(events.NewMessage(pattern="/start"))
async def starthandler(event):
    userid = event.sender_id
    username = event.sender.username
    add_user(userid, username)
    if event.is_group:
        add_chat(event.chat_id)
        text = f"""**Hey {event.sender.first_name} 👋**
    
__I am **{(await bot.get_me()).first_name}**
I will filter your channel posts automatically and send it in your group chat when someone needs it.__

**NOTE: please make me an admin of this group then click on /start 👈**"""
        return await event.reply(text)
    else:
        if event.text.replace("/start ", "") == "adduser":
            return await event.reply(
                """**Success ✅**
**Please search your movie in the group again!**"""
            )
        sender = await event.get_sender()
        checkjoin = await get_user_join(sender.id, Config.FORCESUB_CHANNEL)
        if not checkjoin:
            channel = await bot.get_entity(Config.FORCESUB_CHANNEL)
            text = f"""**Hey! {event.sender.first_name} 😃**

**You Have To Join My Channel To Use Me ✅**

**Click The Button To Join Now.👇🏻**"""
            buttons = [Button.url("Join", f"https://t.me/{channel.username}")]
            return await event.reply(text, buttons=buttons)
        text = f"""**Hey {event.sender.first_name} 👋**
    
__I am **{(await bot.get_me()).first_name}**! I will filter your channel posts automatically and send it in your group chat when someone needs it.__

**Press /help for more info!**"""
        buttons = [[Button.inline("Buy Subscription", "buysubscription")]]
    return await event.reply(text, buttons=buttons)


@bot.on(events.CallbackQuery(func=lambda event: event.data.decode() in ["buysubscription", "inrprice"]))
async def buysubscription(event):
    data = event.data.decode()
    if data == "buysubscription":
        text = """**These are the prices in USD:**

`1.2 USD` - per Month 
`6.2 USD` - per 6 Months
`12.3 USD` - per Year

Click on the `Buy` button to contact the owner."""
        buttons = [
            [Button.url("Buy Now", f"https://t.me/{Config.OWNER_USERNAME}")],
            [Button.inline("INR Price", "inrprice")],
        ]
    else:
        text = """
        **These are the prices in INR:**

`99 INR` - per Month 
`599 INR` -  per 6 Months
`1000 INR` -  per Year

Click on the `Buy` button to contact the owner."""
        buttons = [
            [Button.url("Buy Now", f"https://t.me/{Config.OWNER_USERNAME}")],
            [Button.inline("USD Price", "buysubscription")],
        ]
    return await event.edit(text, buttons=buttons)


@bot.on(events.NewMessage(pattern="/auth"))
async def authuser(event):
    if event.sender_id != Config.OWNER_ID:
        return await event.delete()
    if event.text == "/auth":
        return await event.reply("Give me an ID or username!")
    user = event.text.replace("/auth ", "")
    try:
        user = int(user)
    except Exception:
        user = user.replace("@", "")
    try:
        user = await bot.get_entity(user)
    except Exception:
        return await event.reply(
            "This user has not started me in PM.\nTell them to do that first!"
        )
    try:
        dt = datetime.now()
        time = dt.timestamp()
        authenticate_user(user.id, time)
    except AttributeError:
        return await event.reply("Please tell this user to /start me in PM once again!")
    return await event.reply(
        f"`{user.first_name}` successfully authorised for 31 days!"
    )


@bot.on(events.NewMessage(pattern="/unauth"))
async def authuser(event):
    if event.sender_id != Config.OWNER_ID:
        return await event.delete()
    if event.text == "/unauth":
        return await event.reply("Give me an ID or username!")
    user = event.text.replace("/unauth ", "")
    try:
        user = int(user)
    except Exception:
        user = user.replace("@", "")
    try:
        user = await bot.get_entity(user)
    except Exception:
        return await event.reply(
            "This user has not started me in PM.\nTell them to do that first!"
        )
    try:
        unauth = unauthenticate_user(user.id)
    except AttributeError:
        return await event.reply("Please tell this user to /start me in PM once again!")
    if unauth:
        return await event.reply(f"`{user.first_name}` successfully unauthorised!")


@bot.on(events.NewMessage(pattern="/enable"))
async def enable(event):
    if event.sender_id not in [Config.OWNER_ID, 1189238402]:
        return await event.delete()
    if event.text == "/enable":
        return await event.reply(
            "wrong format!\n**Format:** `/enable <group id> <user id>"
        )
    args = event.text.replace("/enable ", "").split(" ")
    grp = args[0]
    user = args[-1]
    try:
        checkid = int(grp) if grp.startswith("-100") else -(int(grp))
        grp = int(grp)
    except Exception:
        return await event.reply(
            "Please give me a valid chat ID!\nLike: `-100xxxxxxxxxxxx`"
        )
    try:
        grp = await bot.get_entity(grp)
    except Exception:
        return await event.reply(
            "I have not been added in this group.\nTell the user to /start after adding!"
        )
    try:
        user = int(user)
    except Exception:
        user = user.replace("@", "")
    try:
        user = await bot.get_entity(user)
    except Exception:
        return await event.reply("This user has not started me in PM!")
    if not (isauth := is_authenticated(user.id)):
        return await event.reply("This user is not authorised!\nPlease /auth first!")
    dt = datetime.now()
    time = dt.timestamp()
    valid = is_valid(user.id, time=time)
    if not valid:
        await bot.send_message(
            Config.OWNER_ID,
            f"{event.sender.first_name}'s subscription of 31 days has been expired!",
        )
        await bot.send_message(
            event.sender_id,
            f"Dear user,\nYour subscription of 31 days has been expired!\nPlease buy a new one!",
            buttons=Button.url("Buy Subscription", f"https://t.me/{Config.OWNER_USERNAME}"),
        )
        return await event.reply("This user's Subscription has ended!")
    try:
        auth = auth_group(user.id, checkid)
        if auth is not True:
            if auth == "no":
                return await event.reply(
                    "Either the user or the chat does not exist in my database!\nTell them to /start me!"
                )
            elif auth == "already":
                return await event.reply("This group is already authorised!")
    except AttributeError:
        return await event.reply(
            "Please tell this user to /start me in group once again!"
        )
    return await event.reply(
        f"`{grp.title}` successfully authorised for user {user.first_name}!"
    )


@bot.on(events.NewMessage(pattern="/disable"))
async def disabke(event):
    if event.sender_id != Config.OWNER_ID:
        return await event.delete()
    if event.text == "/disable":
        return await event.reply("Wrong format!\n**Format:** `/disable <group id>`")
    grpid = event.text.replace("/disable ", "")
    try:
        grp = int(grpid)
    except Exception:
        grp = grpid.replace("@", "")
    try:
        grp = await bot.get_entity(grp)
    except Exception:
        return await event.reply("I have not been added in this group.")
    grpid = int(grpid) if grpid.startswith("-100") else grp.id
    if unauth := unauth_group(grpid):
        return await event.reply(f"`{grp.title}` successfully unauthorised!")
    else:
        print("UNAUTH - ", unauth)


@bot.on(events.NewMessage(pattern="/info"))
async def info(event):
    if event.is_reply:
        replymsg = await event.get_reply_message()
        userid = replymsg.sender_id
    else:
        userid = event.sender_id
    if isauth := is_authenticated(userid):
        dt = datetime.now()
        time = dt.timestamp()
        valid = is_valid(userid, time=time)
        if not valid:
            await bot.send_message(
                Config.OWNER_ID,
                f"{event.sender.first_name}'s subscription of 31 days has been expired!",
            )
            await bot.send_message(
                event.sender_id,
                f"Dear user,\nYour subscription of 31 days has been expired!\nPlease buy a new one!",
                buttons=Button.url("Buy Subscription", f"https://t.me/{Config.OWNER_USERNAME}"),
            )
            return await event.reply(
                "Your subscription has been expired!\nPlease check your PM for more details!"
            )
        before = get_validity(userid)
        diff = round(time - before)
        time_left = grt(SUBSCRIPTION_TIME - diff)
        text = f"💎 {f'{replymsg.sender.first_name} is' if event.is_reply else 'You are'} a Premium User!\n\nValidity: `{time_left}`"
        chats = get_user_chats(userid)
        if len(chats) == 0:
            text += "\n\nNo chat's for this user!"
        else:
            text += f"\n\nChats: `{str(chats)}`"
    else:
        text = f"🚩 {f'{replymsg.sender.first_name} is' if event.is_reply else 'You are'} a Normal User!"
    return await event.reply(text)


@bot.on(events.NewMessage(pattern="/index"))
async def index(event):
    if event.is_private:
        return await event.reply("I only work in groups!")
    permissions = await bot.get_permissions(event.chat_id, event.sender_id)
    if not permissions.is_admin:
        return await event.reply("You should be an admin!")
    isauth = is_authenticated(event.sender_id)
    if isauth:
        dt = datetime.now()
        time = dt.timestamp()
        valid = is_valid(event.sender_id, time=time)
        if not valid:
            await bot.send_message(
                Config.OWNER_ID,
                f"{event.sender.first_name}'s subscription of 31 days has been expired!",
            )
            await bot.send_message(
                event.sender_id,
                f"Dear user,\nYour subscription of 31 days has been expired!\nPlease buy a new one!",
                buttons=Button.url("Buy Subscription", f"https://t.me/{Config.OWNER_USERNAME}"),
            )
            return await event.reply(
                "Your subscription has been expired!\nPlease check your PM for more details!"
            )
    isgrpauth = is_grp_auth(event.chat_id)
    if not isauth:
        return await event.reply(
            "Please get a subscription to Index Channels!",
            buttons=Button.url("Buy Subscription", f"https://t.me/{Config.OWNER_USERNAME}"),
        )
    if not isgrpauth:
        return await event.reply(
            "This group needs to be Authenticated!",
            buttons=Button.url(
                "Ask For Authentication", f"https://t.me/{Config.OWNER_USERNAME}"
            ),
        )
    if event.is_private:
        return await event.reply("This command only works in groups!")
    if event.text in ["/index", f"/index@{Config.BOT_USERNAME}"]:
        return await event.reply("Please give me a channel ID!")
    try:
        channelid = int(
            event.text.replace("/index ", "").replace(f"/index@{Config.BOT_USERNAME} ", "")
        )
    except Exception:
        return await event.reply("This is not a valid Channel ID!")
    try:
        channel = await bot.get_entity(channelid)
    except Exception:
        return await event.reply(
            "Is this a valid channel?\nMake sure the channel is not private and I have been added!"
        )
    if not channel.username:
        return await event.reply(
            "This is a private channel!\nHow will users see the links?"
        )
    fullchannel = await bot(ExportChatInviteRequest(channel))
    link = fullchannel.link
    with contextlib.suppress(UserAlreadyParticipantError):
        await client(ImportChatInviteRequest(link.replace("https://t.me/+", "")))
    connect_channel(event.chat_id, channelid)
    return await event.reply(f"`{channel.title}` is now indexed!")


@bot.on(events.NewMessage(pattern="/remove"))
async def removeindex(event):
    if event.is_private:
        return await event.reply("I only work in groups!")
    permissions = await bot.get_permissions(event.chat_id, event.sender_id)
    if not permissions.is_admin:
        return await event.reply("You should be an admin!")
    isauth = is_authenticated(event.sender_id)
    if isauth:
        dt = datetime.now()
        time = dt.timestamp()
        valid = is_valid(event.sender_id, time=time)
        if not valid:
            await bot.send_message(
                Config.OWNER_ID,
                f"{event.sender.first_name}'s subscription of 31 days has been expired!",
            )
            await bot.send_message(
                event.sender_id,
                f"Dear user,\nYour subscription of 31 days has been expired!\nPlease buy a new one!",
                buttons=Button.url("Buy Subscription", f"https://t.me/{Config.OWNER_USERNAME}"),
            )
            return await event.reply(
                "Your subscription has been expired!\nPlease check your PM for more details!"
            )
    if not isauth:
        return await event.reply(
            "Please get a subscription to Remove Indexed Channels!",
            buttons=Button.url("Buy Subscription", f"https://t.me/{Config.OWNER_USERNAME}"),
        )
    if event.is_private:
        return await event.reply("This command only works in groups!")
    channels = get_channels(event.chat_id)
    channelnames = []
    if not channels:
        return await event.reply("No channels have been indexed!")
    for channelid in channels:
        try:
            channel = await bot.get_entity(channelid)
            channelname = channel.title
        except Exception:
            channelname = f"REMOVED [{channelid}]"
        channelnames.append(channelname)
    buttons = [
        [Button.inline(channelnames[i], data=f"rm_{channels[i]}")]
        for i in range(len(channels))
    ]
    return await event.reply(
        'Select a channel.\n**Note:** If you see a "REMOVED" name. Please click on it so I know I have been removed!',
        buttons=buttons,
    )


@bot.on(events.NewMessage(pattern="/sub"))
async def fsub(event):
    if event.text in ["/suboff", f"/suboff@{Config.BOT_USERNAME}"]:
        return
    if event.is_private:
        return await event.reply("I only work in groups!")
    permissions = await bot.get_permissions(event.chat_id, event.sender_id)
    if not permissions.is_admin:
        return await event.reply("You should be an admin!")
    isauth = is_authenticated(event.sender_id)
    if isauth:
        dt = datetime.now()
        time = dt.timestamp()
        valid = is_valid(event.sender_id, time=time)
        if not valid:
            await bot.send_message(
                Config.OWNER_ID,
                f"{event.sender.first_name}'s subscription of 31 days has been expired!",
            )
            await bot.send_message(
                event.sender_id,
                f"Dear user,\nYour subscription of 31 days has been expired!\nPlease buy a new one!",
                buttons=Button.url("Buy Subscription", f"https://t.me/{Config.OWNER_USERNAME}"),
            )
            return await event.reply(
                "Your subscription has been expired!\nPlease check your PM for more details!"
            )
    isgrpauth = is_grp_auth(event.chat_id)
    if not isauth:
        return await event.reply(
            "Please get a subscription to add Force Sub!",
            buttons=Button.url("Buy Subscription", f"https://t.me/{Config.OWNER_USERNAME}"),
        )
    if not isgrpauth:
        return await event.reply(
            "This group needs to be Authenticated!",
            buttons=Button.url(
                "Ask For Authentication", f"https://t.me/{Config.OWNER_USERNAME}"
            ),
        )
    if event.is_private:
        return await event.reply("This command only works in groups!")
    if event.text in [
        "/sub",
        "/sub@RoyalFilterRobot",
        "/suboff@RoyalFilterRobot",
    ]:
        return await event.reply("Please give me a channel ID!")
    args = event.text.replace("/sub ", "").replace(f"/sub@{Config.BOT_USERNAME}", "")
    if is_force_sub(event.chat_id):
        return await event.reply(
            "You have already enabled Force Sub for this group!\nTurn it off by using /sub off"
        )
    try:
        channelid = int(args)
    except Exception:
        return await event.reply("This is not a valid Channel ID!")
    try:
        channel = await bot.get_entity(channelid)
    except Exception:
        return await event.reply(
            "Is this a valid channel?\nMake sure the channel is not private and I have been added!"
        )
    if forcesub := enable_force_sub(event.chat_id, channel.id):
        return await event.reply(
            f"Force Sub enabled for `{channel.title}`!\nTurn it off with /suboff"
        )


@bot.on(events.NewMessage(pattern="/suboff"))
async def fsuboff(event):
    if event.is_private:
        return await event.reply("I only work in groups!")
    permissions = await bot.get_permissions(event.chat_id, event.sender_id)
    if not permissions.is_admin:
        return await event.reply("You should be an admin!")
    isauth = is_authenticated(event.sender_id)
    if isauth:
        dt = datetime.now()
        time = dt.timestamp()
        valid = is_valid(event.sender_id, time=time)
        if not valid:
            await bot.send_message(
                Config.OWNER_ID,
                f"{event.sender.first_name}'s subscription of 31 days has been expired!",
            )
            await bot.send_message(
                event.sender_id,
                f"Dear user,\nYour subscription of 31 days has been expired!\nPlease buy a new one!",
                buttons=Button.url("Buy Subscription", f"https://t.me/{Config.OWNER_USERNAME}"),
            )
            return await event.reply(
                "Your subscription has been expired!\nPlease check your PM for more details!"
            )
    isgrpauth = is_grp_auth(event.chat_id)
    if not isauth:
        return await event.reply(
            "Please get a subscription to add Force Sub!",
            buttons=Button.url("Buy Subscription", f"https://t.me/{Config.OWNER_USERNAME}"),
        )
    if not isgrpauth:
        return await event.reply(
            "This group needs to be Authenticated!",
            buttons=Button.url(
                "Ask For Authentication", f"https://t.me/{Config.OWNER_USERNAME}"
            ),
        )
    if event.is_private:
        return await event.reply("This command only works in groups!")
    if not is_force_sub(event.chat_id):
        return await event.reply("I have not enabled Force Sub here yet!")
    if forcesub := disable_force_sub(event.chat_id):
        return await event.reply("Success! I have turned Force Sub off.")


@bot.on(events.NewMessage(pattern="/channels"))
async def channelist(event):
    if event.is_private:
        return await event.reply("I only work in groups!")
    permissions = await bot.get_permissions(event.chat_id, event.sender_id)
    if not permissions.is_admin:
        return await event.reply("You should be an admin!")
    isauth = is_authenticated(event.sender_id)
    if isauth:
        dt = datetime.now()
        time = dt.timestamp()
        valid = is_valid(event.sender_id, time=time)
        if not valid:
            await bot.send_message(
                Config.OWNER_ID,
                f"{event.sender.first_name}'s subscription of 31 days has been expired!",
            )
            await bot.send_message(
                event.sender_id,
                f"Dear user,\nYour subscription of 31 days has been expired!\nPlease buy a new one!",
                buttons=Button.url("Buy Subscription", f"https://t.me/{Config.OWNER_USERNAME}"),
            )
            return await event.reply(
                "Your subscription has been expired!\nPlease check your PM for more details!"
            )
    if not isauth:
        return await event.reply(
            "Please get a subscription to View Indexed Channels!",
            buttons=Button.url("Buy Subscription", f"https://t.me/{Config.OWNER_USERNAME}"),
        )
    if event.is_private:
        return await event.reply("This command only works in groups!")
    channels = get_channels(event.chat_id)
    if not channels:
        return await event.reply("No channels indexed!")
    output = "**Connected Channels**\n\n"
    for i in range(len(channels)):
        try:
            channel = await bot.get_entity(channels[i])
            channelname = channel.title
        except Exception:
            channelname = f"REMOVED [{channels[i]}]"
        output += f"{i + 1}➤ `{channelname}`\n"
    return await event.reply(output)


@bot.on(events.CallbackQuery(func=lambda event: event.data.decode().startswith("rm_")))
async def discchannelhandler(event):
    isauth = is_authenticated(event.sender_id)
    if not isauth:
        return await event.answer("You are not a Premium User!", alert=True)
    permissions = await bot.get_permissions(event.chat_id, event.sender_id)
    if not permissions.is_admin:
        return await event.answer("You should be an admin!", alert=True)
    channelid = int(event.data.decode().replace("rm_", ""))
    try:
        channelobj = await bot.get_entity(channelid)
        if disconnect := disconnect_channel(event.chat_id, channelid):
            return await event.edit(
                f"`{channelobj.title}` has been successfully disconnected!"
            )
    except Exception:
        if disconnect := disconnect_channel(event.chat_id, channelid):
            return await event.edit("The channel has been successfully disconnected!")


@bot.on(events.NewMessage(pattern="/getid"))
async def getid(event):
    return await bot.send_message(event.chat_id, str(event.chat_id))


@bot.on(events.NewMessage(pattern="/dashboard"))
async def dashboard(event):
    if event.sender_id != Config.OWNER_ID:
        return await event.delete()
    buttons = [
        [
            Button.inline("Filter PM", "filterpm"),
            Button.inline("Auto Delete", "autodelete"),
        ],
        [Button.inline("Statistics", "statistics"), Button.inline("Users", "users")],
        [Button.inline("Group Filter", "grpfilter"), Button.inline("🗑", "close")],
    ]
    return await event.reply("Bot settings:", buttons=buttons)


@bot.on(events.CallbackQuery(pattern="close"))
async def close(event):
    if event.sender_id != Config.OWNER_ID:
        return
    else:
        return await event.delete()


@bot.on(events.NewMessage(pattern="/buy"))
async def buy(event):
    return await event.reply(
        "Buy your subscription from here!",
        buttons=Button.url("Buy Subscription", f"https://t.me/{Config.OWNER_USERNAME}"),
    )


@bot.on(events.CallbackQuery(func=lambda event: event.data == b"statistics"))
async def stats(event):
    if event.sender_id != Config.OWNER_ID:
        return
    chats = len(get_all_chats())
    channels = len(get_cha())
    users = len(get_users())
    output = f"""**Current Bot Statistics:**

Total Chats: `{chats}`
Total Channels: `{channels}`
Total Users: `{users}`"""
    buttons = [Button.inline("Back", "dashboard")]
    return await event.edit(output, buttons=buttons)


@bot.on(events.CallbackQuery(func=lambda event: event.data == b"filterpm"))
async def filterpm(event):
    if event.sender_id != Config.OWNER_ID:
        return
    if isfilter := is_filter_pm():
        buttons = [Button.inline("✅", "filteroff"), Button.inline("Back", "dashboard")]
    else:
        buttons = [Button.inline("❌", "filteron"), Button.inline("Back", "dashboard")]
    return await event.edit("Filer PM Settings: ", buttons=buttons)


@bot.on(events.CallbackQuery(func=lambda event: event.data == b"autodelete"))
async def autodelete(event):
    if event.sender_id != Config.OWNER_ID:
        return
    if isdelete := is_autodelete():
        buttons = [Button.inline("✅", "autodeloff"), Button.inline("Back", "dashboard")]
    else:
        buttons = [Button.inline("❌", "autodelon"), Button.inline("Back", "dashboard")]
    return await event.edit("Auto Delete Settings: ", buttons=buttons)


@bot.on(events.CallbackQuery(func=lambda event: event.data == b"users"))
async def users(event):
    if event.sender_id != Config.OWNER_ID:
        return
    authusers = get_auth_users()
    output = f"**Current Authorised Users:**\n\n"
    for user in authusers:
        output += f"⇨ @{id_to_username(user)}\n"
    buttons = [Button.inline("Back", "dashboard")]
    return await event.edit(output, buttons=buttons)


@bot.on(events.CallbackQuery(func=lambda event: event.data == b"grpfilter"))
async def autodelete(event):
    if event.sender_id != Config.OWNER_ID:
        return
    if isdelete := is_grpfilter():
        buttons = [
            Button.inline("✅", "grpfilteroff"),
            Button.inline("Back", "dashboard"),
        ]
    else:
        buttons = [
            Button.inline("❌", "grpfilteron"),
            Button.inline("Back", "dashboard"),
        ]
    return await event.edit("Group Filter Settings: ", buttons=buttons)


@bot.on(events.CallbackQuery(func=lambda event: event.data == b"dashboard"))
async def filterpm(event):
    if event.sender_id != Config.OWNER_ID:
        return
    buttons = [
        [
            Button.inline("Filter PM", "filterpm"),
            Button.inline("Auto Delete", "autodelete"),
        ],
        [Button.inline("Statistics", "statistics"), Button.inline("Users", "users")],
        [Button.inline("Group Filter", "grpfilter"), Button.inline("🗑", "close")],
    ]
    return await event.edit("Bot settings:", buttons=buttons)


@bot.on(events.CallbackQuery(func=lambda event: event.data in [b"filteron", b"filteroff"]))
async def controlfilter(event):
    if event.sender_id != Config.OWNER_ID:
        return
    on = False
    if event.data == b"filteron":
        allow_filter_pm()
        on = True
    else:
        disable_filter_pm()
    if on:
        buttons = [Button.inline("✅", "filteroff"), Button.inline("Back", "dashboard")]
    else:
        buttons = [Button.inline("❌", "filteron"), Button.inline("Back", "dashboard")]
    return await event.edit("Filer PM Settings: ", buttons=buttons)


@bot.on(events.CallbackQuery(func=lambda event: event.data in [b"grpfilteron", b"grpfilteroff"]))
async def grpfiltercontrol(event):
    if event.sender_id != Config.OWNER_ID:
        return
    on = False
    if event.data == b"grpfilteron":
        allow_grpfilter()
        on = True
    else:
        disable_grpfilter()
    if on:
        buttons = [
            Button.inline("✅", "grpfilteroff"),
            Button.inline("Back", "dashboard"),
        ]
    else:
        buttons = [
            Button.inline("❌", "grpfilteron"),
            Button.inline("Back", "dashboard"),
        ]
    return await event.edit("Group Filter Settings: ", buttons=buttons)


@bot.on(events.CallbackQuery(func=lambda event: event.data in [b"autodelon", b"autodeloff"]))
async def controldelete(event):
    if event.sender_id != Config.OWNER_ID:
        return
    on = False
    if event.data == b"autodelon":
        allow_autodelete()
        on = True
    else:
        disable_autodelete()
    if on:
        buttons = [Button.inline("✅", "autodeloff"), Button.inline("Back", "dashboard")]
    else:
        buttons = [Button.inline("❌", "autodelon"), Button.inline("Back", "dashboard")]
    return await event.edit("Auto Delete Settings: ", buttons=buttons)


@bot.on(events.NewMessage(pattern="/broadcast"))
async def broadcast(event):
    if event.sender_id != Config.OWNER_ID:
        return await event.delete()
    replymsg = await event.get_reply_message()
    if not replymsg:
        return await event.reply("Please reply to a message!")
    users = get_users()
    success = 0
    errors = 0
    proc = await event.reply("Broadcasting. Please wait!")
    for user in users:
        try:
            await bot.send_message(user, replymsg)
            success += 1
            await proc.edit(
                f"Broadcasting. Please wait!\nBroadcasted to: `{success}` chat(s)"
            )
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except Exception:
            errors += 1
    await proc.delete()
    return await event.reply(
        f"Successfully broadcasted your message!\n\nSuccess in: `{success}` chat(s)\nFailed in: `{errors}` chat(s)"
    )


@bot.on(events.NewMessage(pattern="/help"))
async def help(event):
    if not event.is_private:
        return await event.reply(
            "PM me. I will help you there!",
            buttons=Button.url("PM", f"https://t.me/{Config.BOT_USERNAME}?start=True"),
        )
    if event.sender_id == Config.OWNER_ID:
        text = f"""**Command For Owners**

Authorize a user with - /auth <ID or username>
**EXAMPLE:** `/auth @{Config.OWNER_USERNAME}`

Unauthorize a user with - /unauth <ID or Username>
**EXAMPLE:** `/unauth @{Config.OWNER_USERNAME}`


Authorize a Group with - /enable <chatid> <userid or username>
**EXAMPLE:** `/enable -100xxxxxxxxxxx @{Config.OWNER_USERNAME}`

Unauthorize a Group with - /disable <chatid>
**EXAMPLE:** `/disable -100xxxxxxxxx`


Get Owner Controls With - /dashboard

Broadcast to users with - /broadcast (reply to msg)"""
    else:
        text = """**How To Use Channel Filter Robot❓**

Buy Subscription With - /buy

Index A Database Channel With - /index <channel ID>
**EXAMPLE:** `/index -100xxxxxxxxxxx`
__Add Me In The Channel As Admin And Make Sure I Have All The Permissions!__


Remove a Channel with - /remove
__A message With All Your Channels Linked Will Come. Choose The Channel You Want To Remove.__

Add Force To Subscribe In Your Group With - /sub <Channel ID>
**EXAMPLE:** `/sub -100xxxxxxxxx`

Remove Force To Subscribe In Your Group With - /suboff
__Removes Force Sub__

Get Connected Channels With - /channels
__Gives A List Of Your Connected Channels__

Check your information with - /info
__Gives your Information and Validity of your Subscription__

Get ID Of Current Chat - /getid"""

    return await event.reply(text)


@bot.on(events.NewMessage(incoming=True))
async def filter(event):
    if event.text.startswith("/"):
        return
    if event.media:
        return
    if event.sender_id == 5880989143:
        return
    if event.is_private:
        sender = await event.get_sender()
        checkjoin = await get_user_join(sender.id, Config.FORCESUB_CHANNEL)
        if not checkjoin:
            channel = await bot.get_entity(Config.FORCESUB_CHANNEL)
            text = f"""**Hey! {event.sender.first_name} 😃**

**You Have To Join My Channel To Use Me ✅**

**Click The Button To Join Now.👇🏻**"""
            buttons = [Button.url("Join", f"https://t.me/{channel.username}")]
            return await event.reply(text, buttons=buttons)
        if not is_filter_pm():
            return
        print("pm filter triggered")
        return await filter_pm(event, event.text)
    fsub = is_force_sub(event.chat_id)
    chats = get_chats()
    if not is_grp_auth(event.chat_id):
        if isgrpfilter := is_grpfilter():
            print("grp filter triggered")
            return await filter_pm(event, event.text)
    if fsub:
        sender = await event.get_sender()
        check = await get_user_join(sender.id, fsub)
        if check == "startpm":
            text = f"""**Hey! {event.sender.first_name} 😃**

**You Have To Start me in PM To Use Me ✅**

**Click The Button To Start Now.👇🏻**"""
            buttons = [
                Button.url(
                    "Start in PM", f"https://t.me/{Config.BOT_USERNAME}?start=adduser"
                )
            ]
            xx = await event.reply(text, buttons=buttons)
            await asyncio.sleep(300)
            return await xx.delete()
        if check == "False":
            channel = await bot.get_entity(fsub)
            text = f"""**Hey! {event.sender.first_name} 😃**

**You Have To Join Our Channel To Use Me ✅**

**Click The Button To Join Now.👇🏻**"""
            buttons = [Button.url("Join", f"https://t.me/{channel.username}")]
            return await event.reply(text, buttons=buttons)
    if event.chat_id not in chats:
        return
    print("premium filter triggered")
    await filter_message(event, event.text, event.chat_id)


with client, bot:
    bot.run_until_disconnected()
    client.run_until_disconnected()
