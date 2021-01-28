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

logging.config.fileConfig('logging.conf')

logger = logging.getLogger("intbot.status")

bot = commands.Bot(command_prefix='.', intents=discord.Intents.all())
bot.go = False
bot.veto = False # while a restart is queued, the statusbot's detection is paused
bot.vetocounter = 30 # if the restart is bugged or fails or whatever, detection is forcefully resumed after this time (in seconds)
#instead of global, ended up storing go locally in the class that was conveniently handed to us
#just as readable, but better efficiency & compatibility - S.
bot.IDself = 713343823962701897
bot.IDbot = 785566806509223939
#while we're at it, store own and bot's IDs in there, that way can change them everywhere from here

os.system("title Thresh (status)")

@bot.event
async def on_ready():
    logger.info("Status checker now online")
    guild = bot.get_guild(bot.IDself)
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
            await bot.change_presence(status=discord.Status.invisible)
            bot.go = False #should be redundant, but an okay failsafe
            await bot.close()
            os.startfile("main.py")
        if bot.veto == True: #if a restart is scheduled, veto flag is set, blocking running. During that time, a timer ticks down
            bot.vetocounter = bot.vetocounter - 1
        if bot.vetocounter < 0: #if the timer ticks to 0, veto flag is removed
            bot.vetocounter = 30
            bot.veto = False

@bot.command()
async def restart(ctx):
    if (ctx.message.author.id == 225678449790943242 and getmac.get_mac_address() != "00:d8:61:14:48:d3"):
        logger.info("Alex requested a restart, this instance is Sizzle-side, so we wait")
        bot.veto = True
    if (ctx.message.author.id == 140129710268088330 and getmac.get_mac_address() != "2c:f0:5d:24:ac:02"):
        logger.info("Sizzle requested a restart, this instance is Alex-side, so we wait")
        bot.veto = True

def handle_exit(signal_type): #must accept a signal for Windows; 0 = CTRL-C, 1 = CTRL-BREAK, 2 = CLOSE, 5 = LOGOFF, 6 = SHUTDOWN
    async def do_exit():
        await bot.change_presence(status=discord.Status.invisible)
        await bot.close()

    asyncio.run(do_exit())

win32api.SetConsoleCtrlHandler(handle_exit, True)

bot.loop.create_task(run())
bot.run('Nzc3ODA0OTc4MzY1OTIzMzU4.X7IxVQ.09pKfYFM9qnLAI9jUukI0hwOHbg')