import random
import requests
import json
import urllib
import re
import os
from markovbot import MarkovBot
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import MissingRequiredArgument, CommandOnCooldown, Parameter

funbot = MarkovBot()

dirname = os.path.dirname(os.path.abspath(__file__))

book = os.path.join(dirname, u'../Utils/manifesto.txt')

with open('Private/APIkey.txt', 'r') as e:
    apikey: str = e.read()


lmt = 1


class Fun(commands.Cog):

    def __init__(self, client):
        self.client = client

    headers = {'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'}


    @commands.hybrid_command(name='markov', description='Generate some funny text')
    async def markov(self, ctx):
        funbot.read(book)
        n = random.randint(2, 40)
        text = funbot.generate_text(n)
        await ctx.send(text)

    @commands.hybrid_command(name='pic', description='Look for an image')
    @commands.cooldown(1, 5)
    @app_commands.describe(image_query='What should I look for')
    async def pic(self, ctx, *, image_query: str):

        request_url = 'https://www.bing.com/images/async?q=' + urllib.parse.quote_plus(image_query) \
                      + '&first=' + '0' + '&count=' + '3' \
                      + '&adlt=' + 'True' + '&qft=' + ''
        await ctx.defer()
        request = urllib.request.Request(request_url, None, headers=self.headers)
        response = urllib.request.urlopen(request)
        html = response.read().decode('utf8')
        links = re.findall('murl&quot;:&quot;(.*?)&quot;', html)
        i = 0
        try:
            while i <= 2:
                if requests.get(links[i]).status_code != 200:
                    i += 1
                    continue
                else:
                    return await ctx.reply(f'Search term: {image_query}\n{links[i]}', mention_author=False)
        except IndexError:
            return await ctx.reply(f"Couldn't find any images matching `{image_query}`, please try a different search", mention_author=False)
        return await ctx.reply(f"Couldn't find any images matching `{image_query}`, please try a different search", mention_author=False)

    @commands.hybrid_command(name='garloc', description='Praise the garlic')
    async def garloc(self, ctx):
        await ctx.defer()
        with open('Utils/messages.txt', 'r') as f:
            messages = [line.rstrip() for line in f]
        await ctx.send(f'{random.choice(messages)}')

    @commands.hybrid_command(name='gif', description='Look up a gif')
    async def gif(self, ctx, *, search_term: str = Parameter(description='What should i look for', name='search_term', kind=Parameter.POSITIONAL_OR_KEYWORD)):

        r = requests.get("https://api.tenor.com/v1/search?q=%s&key=%s&limit=%s&contentfilter=medium" % (search_term, apikey, lmt))
        if r.status_code == 200:
            gifs = json.loads(r.content)
            url = gifs["results"][0]["url"]
            await ctx.reply(url, mention_author=False)
        else:
            await ctx.reply("Couldn't find a GIF", mention_author=False)

    @gif.error
    async def gif_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await ctx.reply('https://cdn.discordapp.com/attachments/356779184393158657/737319352654757888/ezgif.com-optimize.gif', mention_author=False)

    @pic.error
    async def pic_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await ctx.reply('You need to specify an image to search', mention_author=False)
        if isinstance(error, CommandOnCooldown):
            await ctx.reply('Command on cooldown, please wait a few seconds', mention_author=False)

async def setup(client):
    await client.add_cog(Fun(client))
