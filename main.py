import discord #discord.py and its usability-improving extension.
from discord.ext import commands
import datetime as dt #duh. Handles dates and times.
import asyncio #We use this for sleeps, but there's more than can be done too.
import csv #Handles the CSV format.
import random #duh. RNG.
import time #duh. Makes time counters.
import re #Regular Expressions. Basically, custom checks for strings.
import logging #Extremely buff printf.
import logging.config #even more buff printf stuff: take config from a file and output to file etc.
import logging.handlers
import json #duh. Handles JSONs.
import getmac #unique device identification
import win32api #windows-specific way of detecting exit events, because apparently windows blows dick at cross compatibility
import requests #HTTP requests to interact with Riot API
import subprocess #for interactions with command line
import base64 #encoding of password to communicate with league client
from PIL import Image #neat image processing lib, to concat champ icons for clash ban preview
import math #duh. math.

from pydrive.auth import GoogleAuth #these all are required for GDrive integration
from pydrive.drive import GoogleDrive
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io #duh. Input/Output.
import os #duh. Operating System operations (deleting files, joining paths)
import shutil #advanced operating system operations (copying files)
from tempfile import NamedTemporaryFile

gauth = GoogleAuth()
gauth.LoadClientConfigSettings()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)
service = build('drive', 'v3', credentials=gauth.credentials)

logging.config.fileConfig('logging.conf')
sizzler = logging.getLogger("intbot.bot.sizzle")
logger = logging.getLogger("intbot.bot")

ROLEFILTER = "^(top|jgl|mid|bot|sup|jungle|middle|bottom|support|toplane|midlane|botlane|jg|jung|adc|adcarry|supp)"
COMMANDS = [ "hello", "help", "assertchamp", "imain", "iplay", "mypool", "confidence", "terminate" ]
COLOUR_SUCCESS = 0x00FF00
COLOUR_FAILURE = 0xFF0000
COLOUR_DEFAULT = 0x7289da

ALEX = 225678449790943242
ALEXMAC = "00:d8:61:14:48:d3"
ALEXMAC2 = "2c:fd:a1:61:63:c2"
SIZZLE = 140129710268088330
SIZZLEMAC = "2c:f0:5d:24:ac:02"
BOTHANDLER = 777947935698583562
BOTUSER = 789912991159418937

LOL_champion_translation_dict = False

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='.', intents=intents)
fp = open("thresh.png", "rb")
pfp = fp.read()

self_mac = getmac.get_mac_address()

currentAuthor = ""
currentChannel = 0

os.system("title Thresh (intbot)")

killBool = False

@bot.event
async def on_message(message):
    role = discord.utils.find(lambda r: r.name == 'Nice People', message.guild.roles)
    if message.author.id == 225678449790943242 and role in bot.get_guild(713343823962701897).get_member(message.author.id).roles:
        await message.channel.send("Nice try annoying the Boss")
    elif (role in bot.get_guild(713343823962701897).get_member(message.author.id).roles or (message.channel.id == 827166243035021362 and message.author.id != 785566806509223939)) and len(message.attachments) == 0:
        if "@" in message.content:
            newMsg = message.content
        else:
            msg = message.content
            newMsg = []
            for i in range(len(msg)):
                newMsg.append(msg[-i - 1])
            newMsg = "".join(newMsg)
        channel = message.channel
        await channel.purge(limit=1)
        global currentAuthor
        global currentChannel
        if message.author != currentAuthor or message.channel.id != currentChannel:
            id = message.author.id
            name = bot.get_guild(713343823962701897).get_member(id)
            #if type(name.nick) is str:
                #await channel.send("__**"+name.nick+"**__")
            #else:
                #await channel.send("__**"+message.author.name+"**__")
            currentAuthor = message.author
            currentChannel = message.channel.id
        #await channel.send(newMsg)
        await channel.send("The Joke's On YOU!!")
        await channel.send("https://static.wikia.nocookie.net/leagueoflegends/images/3/31/Shaco_OriginalCircle.png/revision/latest/smart/width/250/height/250?cb=20171112102952")
    await bot.process_commands(message)


@bot.event
async def on_ready():
    if bot.user.avatar != "3359691b5526f7a02f330d9b69d0c8dc":
        await bot.user.edit(avatar=pfp)
    logger.info(f'Self mac address {self_mac}')
    botstatus = discord.Game("League of Legends")
    if self_mac == ALEXMAC or self_mac == ALEXMAC2: #alex
        botstatus = discord.Activity(type=discord.ActivityType.listening, name="everyone")
    elif self_mac == SIZZLEMAC: #sizzle
        botstatus = discord.Game("with souls")
    if bot.activity != botstatus:
        await bot.change_presence(status=discord.Status.online, activity=botstatus)
    logger.info('Thresh is ready to lantern')
    bot.loop.create_task(clashCheckLoop())
    bot.loop.create_task(timer())


async def timer():
    await bot.wait_until_ready()
    channel = bot.get_channel(713343824641916971)
    msg_sent = False
    refresh = False
    while True:
        time = dt.datetime.now()
        if time.hour == 18 and time.minute == 0 and time.second == 0 and msg_sent is False:
            # shortened this to call remind
            await remind(channel)
            msg_sent = True
        elif time.minute == 0 and time.second == 0 and refresh is False:
            gauth.Refresh()
            refresh = True
        else:
            msg_sent = False
            refresh = False
            await asyncio.sleep(1)


@bot.command()
async def flip(ctx, *args):
    if not args:
        messages = await ctx.channel.history(limit=2).flatten()
        msg = messages[-1].content
    else:
        msg = " ".join(args)
    newMsg = []
    for i in range(len(msg)):
        newMsg.append(msg[-i - 1])
    newMsg = "".join(newMsg)
    await ctx.send(newMsg)


@bot.command()
@commands.has_role(BOTHANDLER)
async def mute(ctx, user):
    user = interpretUser(ctx, user)
    role = discord.utils.get(ctx.message.guild.roles, name="MUTED")
    await user.add_roles(role)
    reply = f"{user.name} has been muted"
    await replywithembed(reply, ctx)


@bot.command()
@commands.has_role(BOTHANDLER)
async def unmute(ctx, user):
    user = interpretUser(ctx, user)
    role = discord.utils.get(ctx.message.guild.roles, name="MUTED")
    await user.remove_roles(role)
    reply = f"{user.name} has been unmuted"
    await replywithembed(reply, ctx)


@bot.command()
@commands.has_role(BOTHANDLER)
async def check(ctx):
    file = await download("media.csv")
    with open("media.csv", "wb") as f:
        f.write(file.read())
        f.close()
    with open("media.csv", "r+", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",", quotechar="|")
        for row in reader:
            await ctx.send(row[1])


async def upload(target, mimeType="text/csv"):
    file1 = drive.CreateFile({"mimeType": mimeType})
    file1.SetContentFile(target)
    file1.Upload()  # Upload the file.
    logger.info('Created file %s with mimeType %s' % (file1['title'], file1['mimeType']))


async def download(target):
    #fileList = drive.ListFile({'q': "trashed=false"}).GetList()
    fileList = service.files().list().execute()["files"]
    file_List = fileList
    while "nextPageToken" in fileList:
        fileList = service.files().list(pageToken=fileList["nextPageToken"]).execute()
        file_List = file_List + fileList["files"]
    for file in file_List:
        logger.info('Google Drive File: %s, ID: %s' % (file['name'], file['id']))
        # Get the folder ID that you want
        if (file['name'] == target):
            fileID = file['id']
    try:
        fileID
    except NameError:
        #we try to access a local backup; this can be out of date, but it'll have to do
        #if that doesn't exist either, welp, we have to error out with no file found
        logger.warning(f'Could not download file {target}, checking for a potentially outdated local backup')
        try:
            with open("backups/"+target) as file:
                return file.read()
        except FileNotFoundError:
            logger.warning(f'Local backup not found either; alerting user and passing None')
            return None
    else:
        request = service.files().get_media(fileId=fileID)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            logger.info("Download %d%%." % int(status.progress() * 100))
        fh.seek(0)
        # pitfall: group() can fail if the search fails. But search should only fail on names without extensions, and those would error on the google drive search before this line is even reached, so I'm keeping it short and risky with no error handling - S.
        extension = re.search("(\.[a-z]*)$", target).group()[1:]
        if extension == "csv":
            return fh
        elif extension == "json":
            return fh.getvalue()
        else:
            return fh


async def update(target, mimeType="text/csv"):
    #fileList = drive.ListFile({'q': "trashed=false", "maxResults": 3}).GetList()
    fileList = service.files().list().execute()["files"]
    file_List = fileList
    while "nextPageToken" in fileList:
        fileList = service.files().list(pageToken=fileList["nextPageToken"].execute())
        file_List = file_List + fileList["files"]
    logger.info(fileList)
    for file in fileList:
        logger.info('Google Drive File: %s, ID: %s' % (file['name'], file['id']))
        # Get the folder ID that you want
        if (file['name'] == target):
            fileID = file['id']

    request = service.files().update(fileId=fileID, media_body=target, media_mime_type=mimeType).execute()

    #improved this
    #copies the file into backups folder while preserving all metadata
    #should keep backups more up-to-date, though this is still not guaranteed; there's a reason we try drive first! - S.
    shutil.copy2(target, 'backups')
    os.remove(target)


@bot.command()
async def hi(ctx, user=None):
    if user is None:
        await replywithembed(f"Hi {ctx.message.author.mention}, I'm Thresh!", ctx)
    else:
        await replywithembed(f"Hi {user}, I'm Thresh!", ctx)


@bot.command()
@commands.has_role(BOTUSER)
async def remind(ctx, user=None):
    # rewrote this a bit
    # user accepts nickname, username or UID
    # by default it's me, so normal .remind's work as usual - S.
    if user == None: #assignment has to be done manually to avoid a TypeError
        user = SIZZLE
    user = interpretUser(ctx, user)
    logger.info("Reminding %s", user.name)
    await ctx.send("https://cdn.discordapp.com/attachments/713343824641916971/777559744273317888/Morg_Q.gif")
    await replywithembed(f"{user.mention} Daily Reminder!", ctx)


@bot.command()
@commands.has_role(BOTUSER)
async def save(ctx, id, media=None):
    if media is None:
        if len(ctx.message.attachments) > 0:
            media = ctx.message.attachments[0].url
        else:
            return

    file = await download("media.csv")
    with open("media.csv", "wb") as f:
        f.write(file.read())
        f.close()
    with open("media.csv", "a+", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL)
        writer.writerow([id, media])
    await update("media.csv")
    await replywithembed(f"Saved as ID: {id}", ctx)


@bot.command()
@commands.has_role(BOTUSER)
async def delete(ctx, id):
    lines = []
    file = await download("media.csv")
    with open("media.csv", "wb") as f:
        f.write(file.read())
        f.close()
    with open("media.csv", "r+", newline="") as out:
        reader = csv.reader(out, delimiter=",", quotechar="|")
        for row in reader:
            if row[0] != id:
                lines.append(row)
    with open("media.csv", "w+", newline="") as inp:
        writer = csv.writer(inp, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL)
        writer.writerows(lines)
    await replywithembed(f"Deleted ID: {id}", ctx)
    await update("media.csv")


@bot.command()
async def gimme(ctx, id):
    file = await download("media.csv")
    with open("media.csv", "wb") as f:
        f.write(file.read())
        f.close()
    with open("media.csv", "r+", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",", quotechar="|")
        media = " "
        for row in reader:
            if row[0] == id:
                media = row[1]
        await ctx.send(media)
    os.remove("media.csv")


@bot.command()
async def raman(ctx):
    await replywithembed("Congrats on Imperial! <@305035084468191232>", ctx)


@bot.command()
async def gimmeList(ctx):
    file = await download("media.csv")
    with open("media.csv", "wb") as f:
        f.write(file.read())
        f.close()
    with open("media.csv", "r+", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",", quotechar="|")
        string = ""
        for row in reader:
            string += row[0]
            string += ", "
        await replywithembed(string[:-2], ctx)
    os.remove("media.csv")


@bot.command()
@commands.has_role(BOTUSER)
async def bday(ctx, user=SIZZLE):
    # same ol' thingamajig here; now accepts user as an argument
    user = interpretUser(ctx, user)
    for server in bot.guilds:
        logger.info(server.name)
        for channel in server.channels:
            if channel.type == discord.ChannelType.text:
                for i in range(10):
                    await channel.send("https://cdn.discordapp.com/attachments/498040249218236416/780150571197005824/bday.gif")
                await channel.send(f"{user} Happy Birthday!")


@bot.command()
@commands.has_role(BOTUSER)
async def clear(ctx, number=1):
    number = int(number)
    if 25 >= number > 0:
        await ctx.channel.purge(limit=number + 1)
    else:
        await replywithembed("Not a valid clear number", ctx)


@bot.command()
@commands.has_role(BOTUSER)
async def disco(ctx):
    await bot.wait_until_ready()
    currentTime = time.perf_counter()
    count = 0
    await ctx.send("https://cdn.discordapp.com/attachments/784087009974681650/785576009230450759/disco.gif")
    while count < 5:
        futureTime = time.perf_counter()
        if currentTime + 0.5 < futureTime:
            count += 1
            currentTime = time.perf_counter()
            newColour = discord.Colour.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            guild = bot.get_guild(713343823962701897)
            role = discord.utils.get(guild.roles, name="Colours")
            await role.edit(colour=newColour)
    newColour = discord.Colour.from_rgb(242, 117, 55)
    await role.edit(colour=newColour)


@bot.command()
@commands.has_role(BOTUSER)
async def spam(ctx, tag, *args):
    if not killBool:
        print("Tag")
        found = ""
        for i in args:
            if str(ALEX) in i:
                found = ALEX
            elif str(SIZZLE) in i:
                found = SIZZLE
        if str(ALEX) in tag:
            found = ALEX
            await replywithembed(f"Hahaha! I wouldn't let you ping <@{found}>!", ctx)
            await asyncio.sleep(2)
            await replywithembed(f"Oh wait...", ctx)
        elif str(SIZZLE) in tag:
            found = SIZZLE
            await replywithembed(f"Hahaha! I wouldn't let you ping <@{found}>!", ctx)
            await asyncio.sleep(2)
            await replywithembed(f"Oh wait...", ctx)
        elif found:
            await replywithembed(f"Hahaha! I wouldn't let you ping <@{found}>!", ctx)
            await asyncio.sleep(2)
            await replywithembed(f"Oh wait...", ctx)
        elif tag[0] == ".":
            for i in range(10):
                await globals()[tag[1:]](ctx, *args)
        else:
            print("String")
            for i in range(10):
                await ctx.send(tag + " " + " ".join(args))


@bot.command()
async def ssjoin(ctx):
    with open("secretsanta.csv", "r", newline="") as file:
        reader = csv.reader(file, delimiter=",", quotechar="|")
        for row in reader:
            if row[0] == str(ctx.message.author.id):
                await replywithembed("Cannot join twice!", ctx)
                return
    with open("secretsanta.csv", "a+", newline="") as file:
        writer = csv.writer(file, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL)
        writer.writerow([ctx.message.author.id])
        await replywithembed("Joined the Secret Santa!", ctx)


@bot.command()
async def sswishlist(ctx, *args):
    tempfile = NamedTemporaryFile('w+t', newline='', delete=False)
    with open("secretsanta.csv", "r", newline="") as file, tempfile:
        reader = csv.reader(file, delimiter=",", quotechar="|")
        writer = csv.writer(tempfile, delimiter=",", quotechar="|")
        for row in reader:
            if row[0] == str(ctx.message.author.id):
                x = " ".join(args)
                if len(row) > 1:
                    row[1] = x
                else:
                    row.append(x)
                await replywithembed(f"Your wishlist is now: {x}", ctx)
            writer.writerow(row)
    shutil.move(tempfile.name, "secretsanta.csv")


@bot.command()
@commands.has_role(BOTHANDLER)
async def ssgo(ctx):
    with open("secretsanta.csv", "r", newline="") as file:
        reader = csv.reader(file, delimiter=",", quotechar="|")
        ids = []
        for row in reader:
            ids.append(row[0])
    x = random.randint(1, len(ids) - 1)
    for i in range(x):
        ids.append(ids.pop(0))
    pos = 0
    with open("secretsanta.csv", "r", newline="") as file:
        reader = csv.reader(file, delimiter=",", quotechar="|")
        for row in reader:
            print("here")
            id = ids[pos]
            pos += 1
            for member in bot.get_all_members():
                if member.id == int(id):
                    print(id)
                    await member.send(f"Secret Santa: {bot.get_user(int(row[0])).name}")
                    if len(row) > 1:
                        await member.send(f"Their wishlist: {row[1]}")
                    else:
                        await member.send(f"This person did not specify a wishlist")


@bot.command()
@commands.has_role(BOTHANDLER)
async def kill(ctx):
    global killBool
    killBool = True
    await asyncio.sleep(10)
    killBool = False



# --------------------------------------------------#
# --------------------------------------------------#
# --------------------------------------------------#
# ---------------------vvvvvvvv---------------------#
# -------------------->commands<--------------------#
# ---------------------^^^^^^^^---------------------#
# --------------------------------------------------#
# --------------------------------------------------#
# --------------------------------------------------#

# -- CLASH block -- #

# Send a request to Riot API, signed with the Dev API Key
# Params:
#   endpt (str) - part of the URL to access, example "lol/summoner/v4/summoners/by-name/Sand%20Baggins"
#   routing (str, optional) - server to forward the request to. Either shards (br, ru, euw1) or regions (europe, americas)
# Outputs:
#   res (json) or False - body of the response on success, False on error
#   status_code (numeric) - 1xx INFO, 2xx OK, 3xx REDIRECT, 4xx INPUT ERROR, 5xx SERVER ERROR
async def requestRiot(endpt, routing="euw1", retry = -1):
    API_key = "RGAPI-137b8ffc-ce57-4e21-ab59-fcaa355050a9"
    
    res = requests.get(f"https://{routing}.api.riotgames.com/{endpt}", headers={"X-Riot-Token": API_key})

    if res.ok:
        return res.json(), res.status_code
    else:
        if res.status_code == 429: # rate limiting protection
            # experimental: non-terminal rate limiter handling
            seconds = res.headers["Retry-After"]
            logger.info(f"429 - triggered rate limiter. Blocking for {seconds} seconds.")
            await asyncio.sleep(int(seconds))
            return await requestRiot(endpt, routing) # retry
        elif res.status_code == 503: # service unavailable
            if retry == 0:
                logger.info(f"503 - service unavailable at endpoint {endpt}. Max retries reached, proceeding.")
                return False, res.status_code
            elif retry == -1:
                retry = 3
            logger.info(f"503 - service unavailable at endpoint {endpt}. Attempting a retry.")
            retry -= 1
            return await requestRiot(endpt, routing, retry)
        else:
            logger.warning(f"Recorded an HTTP error: {res.status_code} - { res.json()['status']['message'] }")
        return False, res.status_code

# Send a request to LCU API (local instance of League Client)
# Params:
#   endpt (str) - part of the URI to access, example "lol-clash/v1/bracket/123456"
# Outputs:
#   res (json) or False - body of the response on success, False on error
#   status_code (numeric) - 1xx INFO, 2xx OK, 3xx REDIRECT, 4xx INPUT ERROR, 5xx SERVER (LCU) ERROR
async def requestClient(endpt):
    # windows specific, https://stackoverflow.com/questions/4760215/running-shell-command-and-capturing-the-output
    shell = str(subprocess.Popen(
        "wmic PROCESS WHERE name='LeagueClientUx.exe' GET commandline", 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE).communicate()[0])
    # amidst the shell output, we have to regex-filter out the useful stuff
    port = re.search("(?<=--app-port\=)[0-9]{1,5}", shell).group()
    password = re.search("(?<=--remoting-auth-token\=)[a-zA-Z0-9_\-]*", shell).group() #K2K27vvHVodOUEvW8J8Ohw#
    url = f"https://127.0.0.1:{port}/{endpt}"
    res = requests.get(url, auth=requests.auth.HTTPBasicAuth("riot", password), verify=False)
    if res.ok:
        return res.json(), res.status_code
    else:
        return False, res.status_code

# Fetch list of summoner IDs of a player's team
# Params:
#   playername (str, optional) - League display name of target player. If not supplied, looks for our own clash team.
# Output:
#   summonerIds (list of str) - List of summoner IDs forming the target team. If player is not in a team, list returns empty.
async def getClashTeamByPlayer(playername=""):
    # step 1 - get one of our own accounts, an "anchor" through which we can find our team

    # try a couple usernames, I guess
    # in order of likelihood
    usernames = ["Alex664410690", "TreePredator", "Sand%20Baggins", "Rambos1234", "Ch0s3N121", "kevxlue", "Yuumi%202%20good", "Nick6756", "RosalindwKzPsR", "J3LLYF1SH", "Grizziebeth"]
    if playername != "":
        playername = playername.strip('"')
        usernames = []
        usernames.append(playername)
    for handle in usernames:
        response, errorcode = await requestRiot("lol/summoner/v4/summoners/by-name/"+handle)
        if not response:
            if errorcode == 403:
                logger.error("Invalid API key! Use .updateAPIKey to provide a valid one.")
                return
            # ... perhaps other errors can be treated here as well
        else:
            anchor_name = handle
            anchor_id = response["id"]
            # now fetch that guy in the clash API (if they're in a team)
            response, errorcode = await requestRiot("lol/clash/v1/players/by-summoner/"+anchor_id)
            if response == False:
                # ... possibly handle these somehow again
                pass
            elif response == []: # player is not registered for clash
                team_id = ""
                pass
            else:
                # logger.info(str(response))
                team_id = response[0]["teamId"]
                break

    # if there is no team ID, then there is no team I guess lol
    if playername != "" and team_id == "":
        return [], ""
    elif team_id == "":
        return [], ""

    # step 2 - fetch the team
    response, errorcode = await requestRiot("lol/clash/v1/teams/"+team_id)
    if response == False:
        # ... handle these somehow again
        return [], ""
    else:
        # OK -- team found
        team = response
        # team.name, team.abbreviation, team.tier available here
        # team.players - list of [summonerId, position (role/lane), role (captain/member)]
        players = []
        for player in team["players"]:
            players.append([player["summonerId"], player["position"]])

    for player in players:
        sumId = player[0]
        response, errorcode = await requestRiot("lol/summoner/v4/summoners/"+sumId)
        if response:
            player.append(response["summonerLevel"])

    return players, team["abbreviation"] + " | " + team["name"]

# Gets the list of champions a player played recently
# MISLEADING NAME: technically, returns a *dictionary*
# Params:
#   sumId (str) - Summoner ID to check
# Outputs:
#   champDict (dict)
#       championName (str) - KEY of champion (close to display name, but not quite)
#       gamesPlayed (num) - number of games target summoner played on the champion
async def getPlayerChampList(sumId):
    champTranslation = await fetchChampData()

    champDict = {}
    reqn = 1
    response, errorcode = await requestRiot(f"lol/summoner/v4/summoners/{sumId}")
    if not response:
        pass
    else:
        puuid = response["puuid"]
        reqn += 1

    t = round(time.time()) - 9000000

    response, errorcode = await requestRiot(f"lol/match/v5/matches/by-puuid/{puuid}/ids?type=ranked&startTime={t}&count=35", "europe")
    response2, errorcode2 = await requestRiot(f"lol/match/v5/matches/by-puuid/{puuid}/ids?queue=400&startTime={t}&count=15", "europe")
    if not response:
        pass
    else:
        matchList = response
        for match in response2:
            matchList.append(match)
        reqn += 1
        for match in matchList:
            response, errorcode = await requestRiot(f"lol/match/v5/matches/{match}", "europe")
            if not response:
                pass
            else:
                matchData = response
                i = 0
                for player in matchData["metadata"]["participants"]:
                    if player == puuid:
                        break
                    else:
                        i += 1
                championId = matchData["info"]["participants"][i]["championId"]
                champion = champTranslation[str(championId)][1] # translate key to display name
                # possibly collect other data here - gold, xp, kda, etc
                if champion in champDict:
                    champDict[champion] += 1
                else:
                    champDict[champion] = 1
    if errorcode >= 400:
        return f"HTTP error encountered during request #{reqn}: {errorcode}"
    return champDict

# Gets a dict of champion masteries for a particular summoner ID
# Params:
#   sumId (str) - Summoner ID to check
# Outputs:
#   masteryDict (dict)
#       championName (str) - name of champion (as displayed, in client language)
#       masteryPoints (str) - amount of mastery points target summoner has on the champion
async def getMastery(sumId):
    response, errorcode = await requestRiot(f"lol/champion-mastery/v4/champion-masteries/by-summoner/{sumId}")
    if not response:
        pass
    else:
        champTranslation = await fetchChampData()
        masteryDict = {}
        for champion in response:
            champName = champTranslation[str(champion["championId"])][1]
            masteryDict[champName] = champion["championPoints"]
        return masteryDict


# Fetches suggested bans for a particular team
# Params:
#   playerList (list of list)
#       sumId (str) - summoner ID to check
#       position (str) - role; may be FILL or UNSELECTED
#   team (str, optional) - team name, e.g. "INT | Divern"
#   ctx (numeric, optional) - context to send resulting message into. Defaults to #pregame-draft
# Outputs:
#   none (programmatic)
#   a formatted message to #pregame-draft channel
async def getBans(playerList, team="??? | Unknown", ctx=""):
    if ctx=="":
        channel = bot.get_channel(713356398490288158) #pregame-draft 784087009974681650) #ddos_domain
    else:
        channel = ctx.channel
    with open("champion_preferences.json", "r", newline="") as file:
        preferences = json.load(file)
    banWeights = {}
    masteryRecommendations = {}
    totalLevel = 0
    for player in playerList:
        totalLevel += player[2]
    for player in playerList:
        sumId = player[0]
        role = player[1]
        level = player[2]
        logger.info(f"Attempting to get bans for summoner {sumId}")
        champDict = await getPlayerChampList(sumId)
        if type(champDict) != type({"dict":True}):
            return await ctx.send(str(champDict))
        logger.info(f"Champion history in hand")
        masteryDict = await getMastery(sumId)

        levelMult = player[2] / totalLevel + 0.8 # % of total level - 20%, plus 1 (base multiplier)

        unitedDict = {}
        for lane, champData in preferences.items():
            if role != "UNSELECTED" and role != "FILL" and role != lane:
                continue
            for champName, preference in champData.items():
                unitedDict[champName] = {"preference": preference}
        for champName, gamesPlayed in champDict.items():
            if champName not in unitedDict:
                unitedDict[champName] = {}
            unitedDict[champName]["gamesPlayed"] = 6*math.log(gamesPlayed + 1)
        for champName, mastery in masteryDict.items():
            if champName not in unitedDict:
                unitedDict[champName] = {}
            # mastery multiplier
            if mastery <= 10000:
                mastery = 10000
            elif mastery >= 300000:
                #logger.info(champName + ": " + str(mastery))
                unitedDict[champName]["highMastery"] = mastery
            unitedDict[champName]["masteryMult"] = math.log(mastery / 5000) # 50k -> x1

        for champName, data in unitedDict.items():
            #logger.info(champName + ": " + str(data))
            if "gamesPlayed" in data:
                if "preference" in data: #if not, then it's the wrong role
                    banWeights[champName] = round(data["gamesPlayed"] * data["preference"] * data["masteryMult"] * levelMult,2)
            if "highMastery" in data:
                masteryRecommendations[champName] = data["highMastery"]
    logger.info(f"Ban fetch complete")

    champTranslation = await fetchChampData()
    version = champTranslation["version"]

    message = ""
    image = Image.new(mode="RGBA", size=(0,0))
    banWeights = dict(sorted(banWeights.items(), key=lambda item: -item[1]))
    #logger.info(str(banWeights))
    keys = list(banWeights.keys())
    values = list(banWeights.values())
    logger.info(str(banWeights))
    if len(banWeights) < 15:
        champs = len(banWeights)
    else:
        champs = 15
    for i in range(champs):
        champ, value = keys[i], values[i]
        for ID, data in champTranslation.items():
            if data[1] == champ:
                key = data[0]
        URL = requests.get(f"http://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{key}.png")
        img = Image.open(io.BytesIO(URL.content))
        if i < 5:
            w = image.width + img.width
        else:
            w = 120 * 5
        h = 120 * (i // 5 + 1)
        newImage = Image.new("RGBA", (w, h))
        newImage.paste(image)
        newImage.paste(img, (120 * (i % 5), 120 * (i // 5)))
        image = newImage
        message += champ+": "+str(value)+"\n"
    image.save("BanList.png")
    await channel.send(file=discord.File("BanList.png"))
    os.remove("BanList.png")

    if masteryRecommendations:
        message += "\n\nMastery highlights:"

    e = discord.Embed(
        title=f"Clash report for team {team}", 
        description=message, 
        colour=COLOUR_DEFAULT)

    for champ, pts in masteryRecommendations.items():
        e.add_field(name=champ, value=pts)

    await channel.send(embed=e)

# Returns a conversion dict for champion keys, IDs and display names
# Params:
#   none
# Outputs:
#   champs (dict)
#       ID (numeric) - champion ID, e.g. 161
#       data (list)
#           key (str) - champion key, e.g. "Velkoz"
#           name (str) - champion display name, e.g. "Vel'Koz"
async def fetchChampData():
    global LOL_champion_translation_dict

    if LOL_champion_translation_dict == False:
        logger.info("Generating a new champion translation dict")
        # I have a very rudimentary system in place to avoid errors
        version = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()[0]
        champs = requests.get(f"http://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json").json()
        champData = champs["data"]
        champs = {}
        for champion, data in champData.items():
            champs[str(data["key"])] = [data["id"], data["name"]]
        champs["version"] = version
        #logger.info("FOLLOWING CHAMPION DATA RECOVERED: \n"+str(champs.items()))
        LOL_champion_translation_dict = champs
    else:
        logger.info("Champion translation dict found")

    return LOL_champion_translation_dict 

@bot.command()
async def clashTest(ctx):
    #Siz Id: ziqjWlU1QoISHplVyEQfUjB-wqeqkOXV9o3MQ2VfHCwRRHWx
    #Alex Id: _Yt4y8rx-Fwnsbm1V-p5Ay6moKYDoEJvpvq2c1CaI2-TJizu
    #players, team = await getClashTeamByPlayer("Sand Baggins")
    return await getBans([["_Yt4y8rx-Fwnsbm1V-p5Ay6moKYDoEJvpvq2c1CaI2-TJizu", "JUNGLE", 100]])

# Main loop. Every 30s, checks tournament summary for status.
# If SCOUTING detected, trigger ban-fetching logic.
# Params:
#   none
# Outputs:
#   none
async def clashCheckLoop():
    global LOL_champion_translation_dict # very cringe error protection system
    LOL_champion_translation_dict = False # at launch, clear previous champion definitions
    previousId = 0
    bracketId = ""
    while True:
        summary, error = await requestClient("lol-clash/v1/tournament-summary")
        if summary == False:
            logger.info("Not in Clash")
            await asyncio.sleep(30)
            logger.info("Finished")
            continue
        if bracketId == "":
            bracketId = summary[0]["bracketId"]
        bracket, error = await requestClient(f"lol-clash/v1/bracket/{bracketId}")
        ownRosterId = summary[0]["rosterId"]
        rosterId = 0
        for game in bracket["matches"]:
            if game["status"] == "UPCOMING":
                if game["rosterId1"] == ownRosterId:
                    rosterId = game["rosterId2"]
                elif game["rosterId2"] == ownRosterId:
                    rosterId = game["rosterId1"]
        if rosterId != 0 and previousId != rosterId:
            #rosterId = 5254350 #5351069
            roster, error = await requestClient(f"lol-clash/v1/roster/{rosterId}")
            summonerId = roster["members"][0]["summonerId"]
            player, error = await requestClient(f"lol-hovercard/v1/friend-info-by-summoner/{summonerId}")
            name = player["name"]
            players, team = await getClashTeamByPlayer(name)
            await getBans(players, team)
            previousId = rosterId
        await asyncio.sleep(30)

@bot.command()
async def confidence(ctx, champ="None", level="None", role=""):
    # confidence <champ> <level> <role>
    # assert that champ and level are provided
    if champ == "None" or level == "None":
        await reporterror(107, ctx, COMMANDS[6])
        return
    if role != "":
        role = standardizeRole(role)
    champ = await crossCheckChamp(champ)
    if champ == None:  # bad champ, throw 105
        await reporterror(105, ctx, champ)
    level = standardizeConf(level)
    if level == None:  # bad confidence level, no dedicated error for that, throw 107 invalid syntax instead
        await reporterror(107, ctx, COMMANDS[6])

    file = await download("champ_pools.json")
    users = json.loads(file)
    for index in users:
        if users[index]['UID'] == str(ctx.message.author.id):
            table = users[index]["roles"]
            try:
                role
            except NameError:
                sizzler.info("CONFIDENCE: Role not found, iterating on every instance of the champ")
            finally:
                # if role exists
                # if it doesn't, we gotta sweep through everything
                try:
                    fail = True
                    n = 0
                    while n <= len(table[role]) - 1:
                        if table[role][n]["name"] != champ:
                            n = n + 1
                            continue
                        else:
                            table[role][n]["confidence"] = level
                            fail = False
                            break
                    # champ not found in array, throw 109
                    if fail == True:
                        await reporterror(109, ctx, champ)
                except:
                    fail = True
                    for role in table:
                        n = 0
                        while n <= len(table[role]) - 1:
                            if table[role][n]["name"] != champ:
                                n = n + 1
                                continue
                            else:
                                table[role][n]["confidence"] = level
                                fail = False
                                break
                    # champ not found in array, throw 109
                    if fail == True:
                        await reporterror(109, ctx, champ)
                finally:
                    # upload to file
                    with open("champ_pools.json", "w") as file:
                        file.write(json.dumps(users, indent=3))
                    await update("champ_pools.json", "application/json")

                    await replywithembed("Done! Confidence for {}'s {} set to {}".format(ctx.message.author.name, champ, level), ctx, COLOUR_SUCCESS)
                    return
        else:
            continue
    await reporterror(106, ctx)
    return


# --------------------------------------------------#
# --------------------------------------------------#
@bot.command()
async def mypool(ctx):
    # display what I play in the different roles and at what levels of confidence
    # format: ml
    # comfort(able)/main = "cyan"
    # normal/playable = no formatting, capitalized (yellow)
    # shaky/learning/planning = 'red'
    champArr = {}
    CNL = """
"""  # compatible newline; \n might not work inside ``` code syntax
    output = "```ml"

    sizzler.info("About to open file")
    file = await download("champ_pools.json")
    users = json.loads(file)
    sizzler.debug("File opened, users loaded %s" % users)
    for index in users:
        if users[index]['UID'] == str(ctx.message.author.id):
            table = users[index]["roles"]
            for role in table:
                if len(table[role]) > 0:
                    champArr.update({role: table[role]})
    if len(champArr) > 0:
        for role in champArr:
            output = output + CNL + role.capitalize() + ": "
            n = 0
            while n <= len(champArr[role]) - 1:
                # role: [ {"name" = <champ>, "confidence" = <comfort/normal/shaky>}, {-/-}, {-/-} ]
                champ = champArr[role][n]["name"].title()
                if champArr[role][n]["confidence"] == "comfort":
                    champ = "\"" + champ + "\""
                elif champArr[role][n]["confidence"] == "shaky":
                    champ = "'" + champ + "'"
                output = output + champ + ", "
                n = n + 1
            output = output[:len(output) - 2]
    output = output + "```"

    if output == "```ml```":
        output = "```ml" + CNL + "Empty!```"

    await ctx.send(" ```fix\nChampion pool for {}:```{}".format(ctx.message.author.name.capitalize(), output))


# --------------------------------------------------#
# --------------------------------------------------#
@bot.command()
async def imain(ctx, role="None"):
    if role == "None":  # no role, throw error 102
        await reporterror(102, ctx)
        return
    if re.search(ROLEFILTER, role) == None:  # role is invalid, throw error 103
        await reporterror(103, ctx)
        return
    role = standardizeRole(role)

    file = await download("champ_pools.json")
    users = json.load(file)
    for index in users:
        if users[index]['UID'] == str(ctx.message.author.id):
            users[index]["mainrole"] = role
            await replywithembed("Done! {}'s main role updated to {}.".format(ctx.message.author.name, role), ctx,
                                 COLOUR_SUCCESS)
            return
    users[len(users) + 1] = {
        "UID": str(ctx.message.author.id),
        "mainrole": role,
        "roles": {
            "top": [],
            "jungle": [],
            "middle": [],
            "bottom": [],
            "support": [],
        }
    }
    with open("champ_pools.json", "w") as file:
        file.write(json.dumps(users, indent=3))
    await update("champ_pools.json", "application/json")

    await replywithembed("Done! {}'s main role confirmed as {}.".format(ctx.message.author.name, role), ctx,
                         COLOUR_SUCCESS)


# --------------------------------------------------#
# --------------------------------------------------#
@bot.command()
async def iplay(ctx, *args):
    args = " " + " ".join(args)
    if " -r" in args or " -role" in args or " in" in args:
        role = re.search("(-r|-role|in)\s(\w+)", args)
        if role == None:  # arg supplied but no actual role, throw error 102
            await reporterror(102, ctx)
            return
        role = re.search("(\w+)$", role.group()).group()
        if re.search(ROLEFILTER, role) == None:  # arg supplied but the role is invalid, throw error 103
            await reporterror(103, ctx)
            return
        else:
            # role is valid
            role = standardizeRole(role)

    if (" -d" in args or " -del" in args or " -delete" in args):
        adding = False
    else:
        adding = True

    if " -c" in args or " -champs" in args or " -champions" in args:
        champs = re.search("-(c|champs)(\s+(\w+)(a{0}|,|;))+", args)  # ({0}|,|;)
        sizzler.info("champs: %s" % champs.group())
        if champs == None:  # arg supplied but no actual champs, throw error 104
            await reporterror(104, ctx)
            return
        champs = re.search("(\s+(\w+)(a{0}|,|;))+", champs.group()).group()
        champs = re.split("\s", champs)[1:]
        for champ in champs:
            if champ == "in":
                i = champs.index("in")
                while True:
                    try:
                        champs.pop(i)
                    except:
                        break
        n = 0
        champArr = []
        while champs:
            # Loop through champs, put valid ones into ChampArr, raise 105 for invalid ones
            found = await crossCheckChamp(champs.pop(0))
            champArr.append(found)

        file = await download("champ_pools.json")
        users = json.load(file)

        found = False
        for index in users:
            # find user
            if users[index]["UID"] == str(ctx.message.author.id):
                table = users[index]["roles"]
                if adding == True:
                    try:
                        role
                    except NameError:
                        role = users[index]["mainrole"]
                    finally:
                        for champ in champArr:
                            n = 0
                            while n <= len(table[role]) - 1:
                                if table[role][n]["name"] != champ:
                                    n = n + 1
                                    continue
                                else:
                                    break
                            if n == len(table[role]):
                                champdata = {"confidence": "normal", "name": champ}
                                table[role].append(champdata)
                else:
                    for champ in champArr:
                        try:
                            if role != None:
                                n = 0  # EV 0 to len(table[role]) - 1
                                while n <= len(table[role]) - 1:
                                    if table[role][n]["name"] == champ:
                                        table[role].pop(n)
                                    n = n + 1
                        except:
                            for role in table:
                                n = 0  # EV 0 to len(table[role]) - 1
                                while n <= len(table[role]) - 1:
                                    if table[role][n]["name"] == champ:
                                        table[role].pop(n)
                                    n = n + 1
                found = True
                break
        if found == False:
            await reporterror(106, ctx)
            return

        with open("champ_pools.json", "w") as file:
            file.write(json.dumps(users, indent=3))
        await update("champ_pools.json", "application/json")

        await replywithembed(
            "Done! {}'s champion pool adjustments confirmed and completed.".format(ctx.message.author.name), ctx,
            COLOUR_SUCCESS)

        await mypool(ctx)


# --------------------------------------------------#
# --------------------------------------------------#
# --------------------------------------------------#
# --------------------vvvvvvvvv---------------------#
# ------------------->technical<--------------------#
# --------------------^^^^^^^^^---------------------#
# --------------------------------------------------#
# --------------------------------------------------#
# --------------------------------------------------#
async def reporterror(errorcode=101, ctx="", data=""):
    errormsg = " "

    if errorcode == 100 or ctx == "":  # no_channel
        sizzler.error('Internal Error 100: Attempting to message or report an error without a destination channel')
        return
    if errorcode == 101:  # generic
        sizzler.warning('Internal Error 101: Generic Error')
        errormsg = 'Sorry, I can\'t process this command. There\'s been a generic error.'
    if errorcode == 102:  # no_role
        sizzler.warning('Internal Error 102: Expected a role designator and received none')
        errormsg = 'Sorry, I can\'t process this command because you\'ve supplied no role! Make sure to specify which role you are referring to; valid ones are top, jgl, mid, bot, sup, jungle, middle, bottom, support, toplane, midlane, botlane, jg, jung, adc, adcarry, supp.'
    if errorcode == 103:  # bad_role
        sizzler.warning('Internal Error 103: Expected a role designator, received an invalid one')
        errormsg = 'Sorry, I can\'t process this command because you\'ve supplied an invalid role! Please check that the role is valid, aka one of: top, jgl, mid, bot, sup, jungle, middle, bottom, support, toplane, midlane, botlane, jg, jung, adc, adcarry, supp.'
    if errorcode == 104:  # no_champ
        sizzler.warning('Internal Error 104: Expected a champ designator and received none')
        errormsg = 'Sorry, I can\'t process this command because you\'ve supplied no champion! Please type a champ name (if you\'re using `mychamps -c, you may type several at once, but note that you\'ll need to shorten multiword names into one word [e.g. leesin, xinzhao]). I have a pretty extensive vocabulary and will try to understand a lot of them.'
    if errorcode == 105:  # bad_champ
        sizzler.warning('Internal Error 105 (non-interrupting): Expected a champ designator, received an invalid one')
        errormsg = 'Sorry, while processing your latest request, I couldn\'t understand which champion {} would be. I\'m usually pretty good at this, but this time my vocabulary fails me.'.format(data)
    if errorcode == 106:  # no_user
        sizzler.warning(
            'Internal Error 106: New user submitted a champ pool amendment without a main role to fall back on')
        errormsg = 'Sorry, I can\'t process this command. As a new Galactical user, you need to be registered into the file; for that, I need to know your main role, in case you\'ll submit champs without specifying which role you\'ll be playing them in. Please use `imain <role> to specify your main role, then try again.'
    if errorcode == 107:  # incorrect_syntax
        sizzler.warning('Internal Error 107: Received command with bad arguments')
        errormsg = 'Sorry, I can\'t process this command. I need arguments that haven\'t been supplied. See below: '
        await replywithembed(errormsg, ctx, COLOUR_FAILURE)
        await help(ctx, data)
        return
    if errorcode == 108:  # unrecognized_command
        sizzler.warning('Internal Error 108: Received unrecognized command')
        errormsg = 'Sorry, I don\'t know such a command. `help lists all my commands.'
    if errorcode == 109:  # no_such_champ_in_pool
        sizzler.warning('Internal Error 109: Champion doesn\'t exist in the user\'s pool')
        errormsg = 'Sorry, I can\'t process this command. The champion {} was not found. You may have specified the wrong role or forgot to add the champion to your pool first. In the latter case, use `iplay -c {} -r <role>'.format(data, data)

    await replywithembed(errormsg, ctx, COLOUR_FAILURE)


# --------------------------------------------------#
# --------------------------------------------------#
@bot.command()
async def replywithembed(content="I'm supposed to send an empty message? Odd.", ctx="", colour=COLOUR_DEFAULT):
    # send a cute embed-formatted message
    if ctx == "":
        await reporterror(100)
        return
    e = discord.Embed(title="THRESH", description=content, colour=colour)
    await ctx.send(embed=e)


# --------------------------------------------------#
# --------------------------------------------------#
bot.remove_command("help")


@bot.command()
async def help(ctx, cmdname=""):
    # given a cmd name, return its usage
    # use a normal message rather than embed
    # if cmd name is not valid, throw error 108 no such command
    # if no cmd is given, return usage of `help, followed by a list of supported commandsFalse
    # assert valid cmd name
    found = False
    if cmdname == "":
        found = 1
    cmdStr = ""
    for cmd in COMMANDS:
        cmdStr = cmdStr + cmd + ", "
        if cmd == cmdname:
            found = COMMANDS.index(cmdname)
    cmdStr = cmdStr[:len(cmdStr) - 2] + "."
    if found == False:
        await reporterror(108, ctx)
        return
    if found == 0:
        content = f"**INTBOT HELP UTILITY**\n\n``.{COMMANDS[0]}``\n\nA greeting. Human tradition, you type hello, I greet you back. Makes people feel better, apparently.\n\nSYNTAX: `` `hello``"
    if found == 1:
        content = f"**INTBOT HELP UTILITY**\n\n``.{COMMANDS[1]}``\n\nThe command to call this utility. Without arguments, displays this message. Supplied with a command, I'll explain how to use that command.\nSYNTAX: `` `help <optional single command>``\n\nOTHER AVAILABLE COMMANDS: %s" % cmdStr
    if found == 2:
        content = f"**INTBOT HELP UTILITY**\n\n``.{COMMANDS[2]}``\n\nChecks whether I know the champ. Make sure to give me something to work with. Can be an alias, I know some common community names for the champs. I'm still a bot though, so would be nice if you'd give me the official, full champ name.\n\nSYNTAX: `` `assertchamp <single champion name>``"
    if found == 3:
        content = f"**INTBOT HELP UTILITY**\n\n``.{COMMANDS[3]}``\n\nSets your main role to what you say. If you're not in the database yet, this is the way I'll be adding you. I need to know your main role so that when you use other commands and forget to specify a role, I'll just fall back on it; so make sure to call this at least once, so you're in the file, then I'll be able to serve you fully.\n\nSYNTAX: `` `imain <single role name>``"
    if found == 4:
        content = f"**INTBOT HELP UTILITY**\n\n``.{COMMANDS[4]}``\n\nSets up your champions in the pool. This command can get confusing, bear with me. -c, or -champs, can be followed by any amount of champion names, and I'll add those to the list. If you also specify a -r (-role), I'll add them under that role: so `` `iplay -c eve karthus -r jungle`` adds these champions to the jungle for you. You can also say 'in' instead of '-r', so like `` `iplay zed in midlane``. Now if you also say -delete, or -del or -d, I'll delete the champs from the pool instead of adding them.\n\nNote that if you need to type in a multiword champion name, like 'Lee Sin', I'll interpret it as two champs, so make sure to drop it as a single word instead, 'Leesin' would do.\n\nSYNTAX: `` `iplay <-c|-champs [any amount of single-word champion names]> <-r|-role|in [single optional role]> <-d|-del|-delete optional>``"
    if found == 5:
        content = f"**INTBOT HELP UTILITY**\n\n``.{COMMANDS[5]}``\n\nDisplays your champion pool. It's also displayed after you make any champion changes with `` `iplay``. It's gonna be formatted into roles and coloured, so champs you're confident in show up in cyan, champs you feel shaky on will be red, and the rest are yellow. You can set up confidence levels with `` `confidence``.\n\nSYNTAX: `` `mypool`"
    if found == 6:
        content = f"**INTBOT HELP UTILITY**\n\n``.{COMMANDS[6]}``\n\nLets you set up how confident you are on a champ. Accepts the champion you're changing - it must already be in your pool - the level to change to, it can be comfortable, normal or shaky, and I understand some other aliases for it; and the role, optionally, otherwise all roles you play the champ in will be affected.\n\nSYNTAX: `` `confidence <single champion name> <[confidence]> <optional role>``\n\nAcceptable confidence levels: \n`high || comfort(able) || main(ing) || great`\n`normal || ok || good || solid || average || playing`\n`low || poor || shaky || practice / practicing || learning`"
    if found == 7:
        content = f"**INTBOT HELP UTILITY**\n\n``.{COMMANDS[7]}``\n\nSuper secret nuclear option.\n\nSYNTAX: `` `confidence ???``"

    await ctx.send(content)

    return

# --------------------------------------------------#
# --------------------------------------------------#
# --------------------------------------------------#
# ---------------------vvvvvvv----------------------#
# -------------------->closure<---------------------#
# ---------------------^^^^^^^----------------------#
# --------------------------------------------------#
# --------------------------------------------------#
# --------------------------------------------------#

def asyncwrapper(wrapped, pre = "", post = ""):
	#this allows us to run async function before and/or after target async function, when that target is called
	#I'm using it to assign more functionality to bot.close(), the code of which is normally inaccessible

	#WARNING: the async wrapper can only wrap async functions and only ones with no arguments!
	#It will ignore synchronous functions and it does not take arguments because I mean, 
	#who knows how many are supposed to be expected

	#of course with this implementations, errors in the wrapped stuff are silenced. Too bad!

	async def run():
		try:
			await pre
		except:
			pass
		try:
			await wrapped
		except:
			pass
		try:
			await post
		except:
			pass

	return run

# --------------------------------------------------#
# --------------------------------------------------#
#make bot.close() first set the status to offline (except we can't do that, but we can do invisible
#and functionally it's good for what we need)

#we could call it every time obviously, but it seems more usable for the future to just integrate it
bot.close = asyncwrapper(bot.close(), bot.change_presence(status=discord.Status.invisible))

# --------------------------------------------------#
# --------------------------------------------------#

@bot.command()
async def terminate(ctx):
    if ctx.message.author.id == ALEX or ctx.message.author.id == SIZZLE:  # cheers <3 -S.
        await replywithembed("Bot Terminating", ctx)
        await bot.close()
    else:
        await replywithembed("Yea, almost got me.", ctx)

@bot.command()
@commands.has_role(BOTHANDLER)
async def restart(ctx):
    await replywithembed("Bot Restarting", ctx)
    await bot.close()
    os.startfile("startup.py") #launch statusbot before closing

# --------------------------------------------------#
# --------------------------------------------------#

def handle_exit(signal_type): #must accept a signal for Windows; 0 = CTRL-C, 1 = CTRL-BREAK, 2 = CLOSE, 5 = LOGOFF, 6 = SHUTDOWN
	async def do_exit():
		await bot.close()

	asyncio.run(do_exit())

win32api.SetConsoleCtrlHandler(handle_exit, True)

# --------------------------------------------------#
# --------------------------------------------------#
# --------------------------------------------------#
# --------------------vvvvvvvvv---------------------#
# ------------------->utilities<--------------------#
# --------------------^^^^^^^^^---------------------#
# --------------------------------------------------#
# --------------------------------------------------#
# --------------------------------------------------#
def standardizeRole(role):
    # this function assumes role is already valid, it only translates aliases to the proper role name
    role = preprocessName(role)

    if role == "top" or role == "toplane":
        return "top"
    if role == "jg" or role == "jgl" or role == "jung" or role == "jungle":
        return "jungle"
    if role == "mid" or role == "middle" or role == "midlane":
        return "middle"
    if role == "bot" or role == "bottom" or role == "botlane" or role == "adc" or role == "adcarry":
        return "bottom"
    if role == "sup" or role == "supp" or role == "support":
        return "support"


# --------------------------------------------------#
# --------------------------------------------------#
def standardizeConf(conf):
    # this function assumes conf is already valid, it only translates aliases to the proper role name
    conf = preprocessName(conf)

    if conf == "comfort" or conf == "comfortable" or conf == "main" or conf == "maining" or conf == "great" or conf == "high":
        return "comfort"
    elif conf == "normal" or conf == "playing" or conf == "ok" or conf == "average" or conf == "good" or conf == "solid":
        return "normal"
    elif conf == "shaky" or conf == "learning" or conf == "practice" or conf == "practicing" or conf == "poor" or conf == "low":
        return "shaky"
    else:
        return None


# --------------------------------------------------#
# --------------------------------------------------#
async def crossCheckChamp(testChamp):
    # check that the given champ name/alias exists in the database, then return the actual champion reference
    # on failure, return None
    # practically like the above function, but for champs instead of roles and DOES do a validity check
    file = await download("champs.json")
    champs = json.loads(file)
    for champ in champs:
        if preprocessName(champ) == preprocessName(testChamp):
            return champ
        for alias in champs[champ]:
            if preprocessName(alias) == preprocessName(testChamp):
                return champ
    return None


# --------------------------------------------------#
# --------------------------------------------------#
def preprocessName(name):
    # strips human syntax from the name to return a bot processible result
    # removes 's, spaces, -s, and 'the's (but not in the middle of a word).
    if re.search("($|\s)the\s", name.lower()) == None:
        result = name.lower()
    else:
        result = name.lower().replace("the", "")
    return result.replace(" ", "").replace('\'', "").replace("-", "")


# --------------------------------------------------#
# --------------------------------------------------#

def interpretUser(ctx, value=None):
    # value could be an ID, a nickname or a username
    # it could be a mention, so preceded by an @, or a normal name
    # returns "<@IDINTEGER>"
    if value == None:
        return None
    if type(value) is int:  # this is an ID
        return ctx.guild.get_member(value)
    elif type(value) is str:  # this is a nick or a proper name potentially with discriminator
        if value[0] == "@":  # remove @ before lookup
            value = value[1:]
        return ctx.guild.get_member_named(value)
    else:
        logger.info("User interpretation failed, supplied value is of the wrong type")
        return

# --------------------------------------------------#
# --------------------------------------------------#

def getBotToken():
    with open("token.csv", "r") as f:
        token = f.read()
        logger.info("Token verified: " + str(token))
        f.close()
        return str(token)

# --------------------------------------------------#
# --------------------------------------------------#

bot.run(getBotToken())
