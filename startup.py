import discord
from discord.ext import commands
import asyncio
import os
import sys
import logging
import logging.config
import logging.handlers
import getmac
import win32api
from dotenv import dotenv_values

secureDict = dotenv_values(".env")  # take environment variables from .env.

def secure(varname): #shorthand to procure a secured variable
    if not "STR" in varname:
        try:
            retval = int(secureDict[varname])
        except ValueError:
            retval = secureDict[varname]
    else:
        retval = secureDict[varname]
    return retval

logging.config.fileConfig('logging.conf')

logger = logging.getLogger("intbot.status")

bot = commands.Bot(command_prefix='.', intents=discord.Intents.all())
bot.go = False
bot.veto = False # while a restart is queued, the statusbot's detection is paused
bot.vetocounter = 30 # if the restart is bugged or fails or whatever, detection is forcefully resumed after this time (in seconds)
#instead of global, ended up storing go locally in the class that was conveniently handed to us
#just as readable, but better efficiency & compatibility - S.
bot.IDguild = secure("GUILD_SID")
bot.IDbot = secure("THRESH_ID")
#while we're at it, store own and bot's IDs in there, that way can change them everywhere from here

os.system("title Thresh (status)")

@bot.event
async def on_ready():
    logger.info("Status checker now online")
    guild = bot.get_guild(bot.IDguild)
    user = guild.get_member(bot.IDbot)
    if str(user.status) == "offline":
        logger.info("IntBot detected as offline on launch")
        bot.go = True


@bot.event
async def on_member_update(before, after):
    await bot.wait_until_ready()
    logger.info("Detected update of member %s" % str(before))
    if before.id == bot.IDbot: #now checks by ID so name can be changed - S.
        if str(after.status) == "offline":
            if bot.veto == True:
                bot.veto = False
            else:
                logger.info("IntBot detected going offline")
                bot.go = True

async def run():
    await bot.wait_until_ready()
    while True:
        await asyncio.sleep(1) # second
        if bot.go:
            logger.info("Starting IntBot...")
            os.system("start /min main.py")
            await bot.change_presence(status=discord.Status.invisible)
            bot.go = False #should be redundant, but an okay failsafe
            await bot.close()
        if bot.veto == True: #if a restart is scheduled, veto flag is set, blocking running. During that time, a timer ticks down
            bot.vetocounter = bot.vetocounter - 1
        if bot.vetocounter < 0: #if the timer ticks to 0, veto flag is removed
            bot.vetocounter = 30
            bot.veto = False

@bot.command()
async def restart(ctx):
    if (ctx.message.author.id == secure("ALEX_ID") and getmac.get_mac_address() != secure("ALEX_MAC") and getmac.get_mac_address() != secure("ALEX_MAC_2")):
        logger.info("Alex requested a restart, this instance is Sizzle-side, so we wait")
        bot.veto = True
    if (ctx.message.author.id == secure("SIZZLE_ID") and getmac.get_mac_address() != secure("SIZZLE_MAC")):
        logger.info("Sizzle requested a restart, this instance is Alex-side, so we wait")
        bot.veto = True

def handle_exit(signal_type): #must accept a signal for Windows; 0 = CTRL-C, 1 = CTRL-BREAK, 2 = CLOSE, 5 = LOGOFF, 6 = SHUTDOWN
    async def do_exit():
        await bot.change_presence(status=discord.Status.invisible)
        await bot.close()

    asyncio.run(do_exit())

win32api.SetConsoleCtrlHandler(handle_exit, True)

bot.loop.create_task(run())
bot.run(secure("STR_STATUS"))