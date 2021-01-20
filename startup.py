import discord
from discord.ext import commands
import asyncio
from discord.ext import tasks
import os
import sys
import logging
import logging.config
import logging.handlers

logging.config.fileConfig('logging.conf')

logger = logging.getLogger("intbot.status")

bot = commands.Bot(commands_prefix='-', intents=discord.Intents.all())
bot.go = False
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
            logger.info("IntBot detected going offline")
            bot.go = True


async def run():
    await bot.wait_until_ready()
    while True:
        await asyncio.sleep(1)
        if bot.go:
            logger.info("Starting IntBot...")
            os.startfile("main.py")
            sys.exit(0)


@bot.command()
async def force():
    logger.info("Forced start of IntBot")
    bot.go = True


bot.loop.create_task(run())
bot.run('Nzc3ODA0OTc4MzY1OTIzMzU4.X7IxVQ.09pKfYFM9qnLAI9jUukI0hwOHbg')