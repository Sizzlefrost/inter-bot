import discord
import asyncio
from discord.ext import tasks
import os
import sys

bot = discord.Client(intents=discord.Intents.all())
go = False


@bot.event
async def on_ready():
    guild = bot.get_guild(713343823962701897)
    user = guild.get_member(785566806509223939)
    if str(user.status) == "offline":
        print("done")
        global go
        go = True


@bot.event
async def on_member_update(before, after):
    await bot.wait_until_ready()
    print("Update")
    if str(before) == "IntersBot#3117":
        if str(after.status) == "offline":
            print("Done")
            global go
            go = True
            return


async def run():
    await bot.wait_until_ready()
    while True:
        await asyncio.sleep(1)
        global go
        if go:
            print("starting...")
            os.startfile("main.py")
            sys.exit(0)


bot.loop.create_task(run())
bot.run('Nzc3ODA0OTc4MzY1OTIzMzU4.X7IxVQ.09pKfYFM9qnLAI9jUukI0hwOHbg')