import asyncio
import sys
import traceback

import discord
import os
from discord.ext import commands
from discord.ext.commands import NotOwner, CommandNotFound, NoPrivateMessage
import logging

logging.basicConfig(level=logging.INFO, filename='botlog.log', filemode='a', format='%(asctime)s | %(message)s', datefmt='%d-%b-%y %H:%M:%S')

intents = discord.Intents.default()


client = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)

client.remove_command("help")

with open('Private/Discord.txt', 'r') as g:
    token: str = g.read()


@client.event
async def on_ready():
    await client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.competing, name='BravoOscarTango v2 is here! (/help)'))
    # client.tree.copy_global_to(guild=discord.Object(id=810950175983140915))
    # await client.tree.sync()
    print('Bot is ready')

@client.command()
@commands.is_owner()
async def test(ctx):
    await ctx.send(f'Startup check succesful, check console for ping, commands on /help')
    return print(f'{round(client.latency * 1000)} ms')


@client.hybrid_command(name='invite', description='Invite the bot to your server')
async def invite(ctx):
    await ctx.reply(
        'Thank you! You can invite the bot to your server with this link:\n'
        'https://discord.com/api/oauth2/authorize?client_id=728998963054903388&permissions=1374389595142&scope=bot%20applications.commands',
        mention_author=False)


@client.hybrid_command(name='donate', description='Help the development of the bot')
async def donate(ctx):
    don_embed = discord.Embed(
        title='Thank you for your support!',
        description='You can support the development of BravoOscarTango even with a small donation!\n[Visit ko-fi](https://ko-fi.com/yearning9) for more info',
        colour=discord.Colour.from_rgb(97, 0, 215)
    )

    don_embed.set_thumbnail(
        url='https://cdn.discordapp.com/attachments/1013895628331417681/1022950931194720307/ezgif.com-gif-maker_14.gif')
    don_embed.set_image(url='https://storage.ko-fi.com/cdn/useruploads/13a29cb7-e55d-4162-83e1-9fbb1093c58b.png')

    await ctx.reply(embed=don_embed, mention_author=False)


@client.hybrid_command(name='support', description='Get support or provide feedback')
async def support(ctx):
    await ctx.reply(
        'Need support or want to provide feedback?\n'
        '[Support/Feedback] Join our support server at <https://discord.com/invite/AQVArQVD66>\n'
        '[Feedback/Review] Let us know your opinion on the bot at https://top.gg/bot/728998963054903388',
        mention_author=False)

@client.command()
@commands.is_owner()
async def sync(ctx, guild=None):

    if guild is None:
        await ctx.bot.tree.sync()
        print('done globally')
        return await ctx.send(f'Synced globally')

    else:
        await client.tree.sync(guild=discord.Object(guild))
        print(f'done to guild {guild}')
        return await ctx.send(f'Synced to {guild}')

# Logging

@client.event
async def on_command_completion(ctx):
    logging.info(f'Used {ctx.command.name}')

# Error Handling

@test.error
async def test_error(ctx, error):
    if isinstance(error, NotOwner):
        await ctx.send("This command is only intended for use by owner")

@client.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.NoPrivateMessage):
        try:
            await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
        except discord.HTTPException:
            pass

    elif isinstance(error, CommandNotFound):
        await ctx.send(f'Command does not exist, check /help for a list of commands')
    else:
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        logging.error(f'ERROR | {error}')

@test.error
async def test_error(ctx, error):
    if isinstance(error, NotOwner):
        await ctx.send('This command can only be used by the owner')

@sync.error
async def sync_error(ctx, error):
    if isinstance(error, NotOwner):
        await ctx.send('This command can only be used by the owner')
    if isinstance(error, NoPrivateMessage):
        await ctx.send('This command cannot be used in DMs')


async def main():
    async with client:
        for filename in os.listdir('./Cogs'):
            if filename.endswith('.py'):
                await client.load_extension(f'Cogs.{filename[:-3]}')
                print(f'Loaded {filename[:-3]}')
        await client.start(token)


if __name__ == '__main__':
    asyncio.run(main())
