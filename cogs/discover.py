import discord
import json
from discord.ext import commands
from pymongo import MongoClient


def load_json(token):
    with open('./config.json') as f:
        config = json.load(f)
    return config.get(token)


cluster = MongoClient(load_json('db_address'))
db = cluster['Discord']


class Discover(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Discover cog ready')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id != load_json('bot_id'):
            try:
                image = message.attachments[0].url
                suffix_list = ['jpg', 'jpeg', 'png', 'gif']
                if image.casefold().endswith(tuple(suffix_list)):
                    collection = db[str(message.channel.id)]
                    post = {"url": image}
                    collection.insert_one(post)
                else:
                    pass
            except IndexError:
                pass

    # Randomly posts an image that has been posted before
    @commands.command(aliases=['Discover', 'pick', 'd', 'p'])
    async def discover(self, ctx, num=1):
        # Discover up to 3 images
        if num > 3:
            num = 3
        collection = db[str(ctx.channel.id)]
        images = collection.aggregate([{"$sample": {"size": num}}])
        for image in images:
            await ctx.send(image['url'])

    @commands.command(aliases=['Remove', 'Delete', 'delete', 'del', 'rm'])
    async def remove(self, ctx, url):
        collection = db[str(ctx.channel.id)]
        result = collection.delete_one({"url": url})
        if result.deleted_count == 1:
            await ctx.send("Image removed")
        elif result.deleted_count == 0:
            await ctx.send("Failed to remove image")
        else:
            await ctx.send("Something bad happened")


def setup(client):
    client.add_cog(Discover(client))
