import discord
import random
import json
from discord.ext import commands, tasks
from itertools import cycle
from pymongo import MongoClient


def load_json(token):
    with open('./config.json') as f:
        config = json.load(f)
    return config.get(token)


cluster = MongoClient(load_json('db_address'))
db = cluster['Discord']

client = commands.Bot(command_prefix=load_json('prefix'))


@client.event
async def on_ready():
    change_status.start()
    print('Bot is ready')


@client.event
async def on_message(message):
    if message.author.id != load_json('bot_id'):
        try:
            collection = db[str(message.channel.id)]
            post = {"url": message.attachments[0].url}
            collection.insert_one(post)
        except IndexError:
            pass

    await client.process_commands(message)


# Randomly posts an image that has been posted before
@client.command(aliases=['Discover', 'pick', 'd', 'p'])
async def discover(ctx, num=1):
    # Discover up to 3 images
    if num > 3:
        num = 3
    collection = db[str(ctx.channel.id)]
    images = collection.aggregate([{"$sample": {"size": num}}])
    for image in images:
        await ctx.send(image['url'])


@client.command(aliases=['Remove', 'Delete', 'delete', 'del', 'rm'])
async def remove(ctx, url):
    collection = db[str(ctx.channel.id)]
    result = collection.delete_one({"url": url})
    if result.deleted_count == 1:
        await ctx.send("Image removed")
    elif result.deleted_count == 0:
        await ctx.send("Failed to remove image")
    else:
        await ctx.send("Something bad happened")


@client.command(aliases=['Roll', 'dice', 'Dice', 'r', 'R'])
async def roll(ctx, user_roll):
    user_roll = user_roll.split('d')

    if len(user_roll) != 2:
        await ctx.send('check your dice')
        return

    try:
        dice = int(user_roll[0])
        sides = int(user_roll[1])
    except ValueError:
        await ctx.send('check your dice')
        return

    if sides < 1 or sides > 10000 or dice > 100 or dice < 1:
        await ctx.send('Limit of 100 dice and 10000 sides')
        return

    rolls = []
    total = 0
    for d in range(0, dice):
        rolled = random.randint(1, sides)
        rolls.append(rolled)
        total += rolled

    await ctx.send(f'You rolled: {rolls} for **{total}**')


@client.command(aliases=['8ball', '8Ball'])
async def _8ball(ctx, *, question):
    responses = load_json('8ball_responses')
    await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')


status = cycle(load_json('statuses'))


@tasks.loop(minutes=load_json('loop_time'))
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please pass in all required arguments.')
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Invalid Command')


client.run(load_json('token'))
