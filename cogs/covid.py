import discord
import json
import requests
import requests_cache
import us
from discord.ext import commands


def load_json(token):
    with open('./covid.json') as f:
        config = json.load(f)
    return config.get(token)


class Covid(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('COVID cog ready')

    @commands.command(aliases=['covid19', 'covid-19', 'coronavirus', 'corona', 'rona', 'c19'])
    async def covid(self, ctx, state=None):
        update_covid_json()

        # Get all of US stats
        if state is None:
            us_json = load_json('US')
            keys = sorted(us_json.keys())  # Sort the JSON elements by name

            embed = discord.Embed()
            index = 0
            for i in keys:
                if i == 'All' or i == 'Recovered':
                    continue

                curr = us_json[i]  # Current state
                value = f"Confirmed: {curr.get('confirmed')}\nDeaths: {curr.get('deaths')}"

                embed.add_field(name=i, value=value)
                index += 1
                # Create a new Embed every 12 states
                if i == keys[len(keys) - 1] or index % 12 == 0:
                    index = 0
                    await ctx.send(embed=embed)
                    embed = discord.Embed()

        else:
            try:
                state = us.states.lookup(state).name
            except AttributeError:
                await ctx.send('Please enter a valid state')
                return

            if state is None:
                await ctx.send('Please enter a valid state')
                return

            js = load_json('US').get(state)
            embed = discord.Embed(
                title=state
            )
            embed.add_field(name='Confirmed', value=js.get('confirmed'))
            embed.add_field(name='Deaths', value=js.get('deaths'))
            embed.set_footer(text=js.get('updated'))

            await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Covid(client))


requests_cache.install_cache('covid_cache', expire_after=3600)


def update_covid_json():
    url = "https://covid-api.mmediagroup.fr/v1/cases"

    response = requests.request("GET", url)
    json_response = response.json()

    with open('covid.json', 'w', encoding='utf-8') as json_file:
        json.dump(json_response, json_file, ensure_ascii=False, indent=4)
