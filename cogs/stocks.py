import discord
import json
import pyEX as p
from discord.ext import commands
import re


def load_json(token):
    with open('./config.json') as f:
        config = json.load(f)
    return config.get(token)


pattern_quote = re.compile(r'[$]([A-Za-z]+)[+]?')


class Stocks(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Stocks cog ready')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id != self.client.user.id:
            matches = re.findall(pattern_quote, message.content)
            c = p.Client(api_token=load_json('IEX_pub'), version='v1', api_limit=5)

            for ticker in matches:
                try:
                    quote = c.quote(ticker)
                    money = '${:,.2f}'.format(float(quote['latestPrice']))
                    await message.channel.send(f'{ticker.upper()}: {money}')
                except p.common.PyEXception:
                    await message.channel.send(f'Unknown symbol: {ticker}')


def setup(client):
    client.add_cog(Stocks(client))
