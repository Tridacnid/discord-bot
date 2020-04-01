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
                    collection = db[str(message.guild.id)]
                    post = {"channel": message.channel.id, "url": image, "op": message.author.id}
                    collection.insert_one(post)
                else:
                    pass
            except IndexError:
                pass

    # Randomly posts an image that has been posted before
    @commands.command(aliases=['Discover', 'pick', 'd', 'p'])
    async def discover(self, ctx, num=1):
        """Discover up to 3 images"""
        if num < 1:
            num = 1
        elif num > 3:
            num = 3
        collection = db[str(ctx.guild.id)]
        query = [{"$match": {"channel": ctx.channel.id}}, {"$sample": {"size": num}}]
        images = collection.aggregate(query)
        for image in images:
            await ctx.send(image['url'])

    @commands.command(aliases=['Remove', 'Delete', 'delete', 'del', 'rm'])
    async def remove(self, ctx, url):
        """remove the URL of an image: !rm <url>"""
        collection = db[str(ctx.guild.id)]
        query = {"channel": ctx.channel.id, "url": url}
        result = collection.delete_one(query)
        if result.deleted_count == 1:
            await ctx.send("Image removed")
        elif result.deleted_count == 0:
            await ctx.send("Failed to remove image")
        else:
            await ctx.send("Something bad happened")

    @commands.command()
    async def posted(self, ctx, url):
        """See who originally posted an image: !posted <url>"""
        collection = db[str(ctx.guild.id)]
        query = {"channel": ctx.channel.id, "url": url}
        op = collection.find_one(query)
        try:
            user = self.client.get_user(op['op'])
            await ctx.send(f'That was originally posted by: {user.display_name}')
        except:
            await ctx.send('I\'m not sure who posted that.')

    # todo get stats of single user

    @commands.command()
    async def stats(self, ctx):
        """See how many images are in the database"""
        # Guild data
        collection_str = str(db[str(ctx.guild.id)].name)
        dbstats = db.command('collstats', collection_str, {"match": {"channel": ctx.channel.id}})
        data_size = dbstats['size'] / 1024
        count = dbstats['count']

        # Channel data
        collection = db[str(ctx.guild.id)]
        query = {"channel": ctx.channel.id}
        channel_results = collection.find(query).explain()['executionStats']

        await ctx.send(f'Channel Images: {channel_results["nReturned"]}\nServer Images: {count}\nServer Data Size: {data_size} KB')


def setup(client):
    client.add_cog(Discover(client))
