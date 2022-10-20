import discord
from discord.ext import commands


class Extra(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Help Embed
    help_embed = discord.Embed(
        title='***List of commands***',
        colour=discord.Colour.from_rgb(97, 0, 215),
        description="Select the command list you're interested in with the dropdown menu below!"
    )

    help_embed.set_thumbnail(
        url='https://cdn.discordapp.com/attachments/736887056344678441/1032479805016375356/ezgif.com-gif-maker_8.gif')
    help_embed.set_footer(text='You can also access these commands by tagging the bot, such as @BravoOscarTango help')
    # help_embed.add_field(name=f'/flight-commands :airplane_departure:', value='List of flight sim commands',
    #                      inline=False),
    # help_embed.add_field(name=f'/mod-commands :tools:',
    #                      value='List of mod commands, all require special permissions',
    #                      inline=False)
    # help_embed.add_field(name=f'/fun-commands :beach_umbrella:', value='List of fun commands', inline=False),
    # help_embed.add_field(name=f'/extra-commands :unlock:', value='List of extra commands', inline=False),
    help_embed.add_field(name=f'/invite :incoming_envelope:', value='Bot invite', inline=False)
    help_embed.add_field(name=f'/support :card_box:', value='Provide feedback or ask for support',
                         inline=False)
    help_embed.add_field(name=f'/donate :heart:', value='Donate to the bot', inline=False)

    # Fun Embed
    fun_embed = discord.Embed(
        title='***List of commands***',
        colour=discord.Colour.from_rgb(97, 0, 215)
    )

    fun_embed.set_footer(
        text=f'You can also access these commands by tagging the bot, such as @BravoOscarTango help')
    fun_embed.set_thumbnail(
        url='https://cdn.discordapp.com/attachments/736887056344678441/1032479805016375356/ezgif.com-gif-maker_8.gif')
    fun_embed.add_field(name=f'/markov',
                        value='Generates a sentence based on the Communist Manifesto :)', inline=False)
    fun_embed.add_field(name=f'/garloc',
                        value='Õ̷̗h̶̰̀ ̶̭̋m̷̥͌a̶̺͂n̷͓̊ ̵̫̒p̴̹͐ḻ̸̑s̷͈̋ ̷͍̾h̵̹̓e̴̻̽l̵̈́͜p̸̝̽ ̴̗̄w̷͇̐ĩ̸͇t̸͖̐h̸̗̀ ̴̜̀c̵̤̾o̷̢̚ṃ̴͝p̶̜̓u̵͜͠t̷̓͜e̷̗͆ŕ̶̩',
                        inline=False)

    # Mod Embed
    mod_embed = discord.Embed(
        title='List of mod commands',
        description='All of these need mod permissions',
        colour=discord.Colour.from_rgb(97, 0, 215)
    )

    mod_embed.set_footer(
        text=f'[*Only accessible via mentioning command] You can also access these commands by tagging the bot, such as @BravoOscarTango help')
    mod_embed.set_thumbnail(
        url='https://cdn.discordapp.com/attachments/736887056344678441/1032479805016375356/ezgif.com-gif-maker_8.gif')
    mod_embed.add_field(name=f'/clear [amount][reason]',
                        value='Clears messages, 1 by default, default reason is None', inline=False)
    mod_embed.add_field(name=f'ban* [member][reason]', value='Bans a member, default reason is None', inline=False)
    mod_embed.add_field(name=f'kick* [member][reason]', value='Kicks a member, default reason is None',
                        inline=False)
    mod_embed.add_field(name=f'timeout* [member][number of days][number of hours][reason]',
                        value='To timeout a member, default time is 12 hours and default reason is None, max time is 27 days',
                        inline=False)
    mod_embed.add_field(name=f'rem_timeout* [member]', value='Removes timeout for member',
                        inline=False)

    # Flight Sim Embed
    fs_embed = discord.Embed(
        title='List of aviation commands',
        colour=discord.Colour.from_rgb(97, 0, 215)
    )

    fs_embed.set_footer(
        text=f'You can also access these commands by tagging the bot, such as @BravoOscarTango help')
    fs_embed.set_thumbnail(
        url='https://cdn.discordapp.com/attachments/736887056344678441/1032479805016375356/ezgif.com-gif-maker_8.gif')
    fs_embed.add_field(name=f'/flight [Flight number]', value="Shows info for a live flight, or a list of past/scheduled flights if it's not currently live. Flight number is NOT the callsign (eg. FR1234 instead of RYR1234)",
                       inline=False)
    fs_embed.add_field(name=f'/metar [ICAO]', value='Fetches METAR for given airport ICAO',
                       inline=False)
    fs_embed.add_field(name=f'/charts [ICAO]', value='Returns PDF chart for given airport ICAO',
                       inline=False)
    fs_embed.add_field(name=f'/checklist [Aircraft ICAO]',
                       value='Returns checklist for supported aircraft ICAO', inline=False)
    fs_embed.add_field(name=f'/flightplan [Departure ICAO][Arrival ICAO]',
                       value='Calculates a flight plan between two given airports', inline=False)
    fs_embed.add_field(name=f'/simbrief [Username]',
                       value='Returns your last flight plan generated with SimBrief (WILL NOT GENERATE A FLIGHT PLAN, can be used in a private chat if you prefer to keep the username hidden)',
                       inline=False)
    fs_embed.add_field(name=f'/info [ICAO]', value='Shows various info about a given airport ICAO', inline=False)
    fs_embed.add_field(name=f'/notam [ICAO] [Page]',
                       value='Currently being updated', inline=False)  # TODO: fix this after the actual command

    # Extra Embed
    ex_embed = discord.Embed(
        title='List of extra commands',
        colour=discord.Colour.from_rgb(97, 0, 215)
    )

    ex_embed.set_footer(
        text=f'You can also access these commands by tagging the bot, such as @BravoOscarTango help')
    ex_embed.set_thumbnail(
        url='https://cdn.discordapp.com/attachments/736887056344678441/1032479805016375356/ezgif.com-gif-maker_8.gif')
    ex_embed.add_field(name=f'/gif [GIF search query]',
                       value='[Tenor] Searches and posts a GIF based on the given query', inline=False)
    ex_embed.add_field(name=f'/pic [Image search query]',
                       value="[Bing Images] Searches and posts a picture based on the given query", inline=False)

    @commands.hybrid_command(name='help', aliases=['commands'],
                             description="List of all commands, start here if you're confused")
    async def help(self, ctx):
        view = DropdownView()
        if ctx.interaction is None:
            view.message = await ctx.send(embed=self.help_embed, view=view, mention_author=False)
        else:
            await ctx.interaction.response.send_message(embed=self.help_embed, view=view)
            view.message = await ctx.interaction.original_response()

    # @commands.hybrid_command(name='fun-commands', description='List of fun commands')
    # async def funcommands(self, ctx):
    #     await ctx.reply(embed=self.fun_embed, mention_author=False)
    #
    # @commands.hybrid_command(name='mod-commands',
    #                          description='List of mod commands')
    # async def modcommands(self, ctx):
    #     await ctx.reply(embed=self.mod_embed, mention_author=False)
    #
    # @commands.hybrid_command(name='flight-commands',
    #                          description='List of aviation related commands')
    # async def flightcommands(self, ctx):
    #     await ctx.reply(embed=self.fs_embed, mention_author=False)
    #
    # @commands.hybrid_command(name='extra-commands', description='List of extra commands')
    # async def extracommands(self, ctx):
    #     await ctx.reply(embed=self.ex_embed, mention_author=False)
    #
    # @commands.command()
    # async def thelp(self, ctx):
    #     view = DropdownView()
    #     await ctx.send(embed=self.help_embed, view=view)

class Dropdown(discord.ui.Select):
    def __init__(self):

        options = [
            discord.SelectOption(label='Main Help Page', description="Main help page for the bot's commands", emoji='🏠', value='home'),
            discord.SelectOption(label='Aviation Commands', description='List of aviation related commands',
                                 emoji='🛫', value='flight'),
            discord.SelectOption(label='Fun Commands', description='List of fun commands', emoji='🏖', value='fun'),
            discord.SelectOption(label='Mod Commands', description='List of mod commands, all require special permissions', emoji='🧰', value='mod'),
            discord.SelectOption(label='Extra Commands', description='List of extra commands', emoji='🔓', value='extra')
        ]

        super().__init__(placeholder='Choose list...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == 'flight':
            await interaction.response.edit_message(embed=Extra.fs_embed)
        elif self.values[0] == 'fun':
            await interaction.response.edit_message(embed=Extra.fun_embed)
        elif self.values[0] == 'mod':
            await interaction.response.edit_message(embed=Extra.mod_embed)
        elif self.values[0] == 'extra':
            await interaction.response.edit_message(embed=Extra.ex_embed)
        elif self.values[0] == 'home':
            await interaction.response.edit_message(embed=Extra.help_embed)


class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.message = None
        self.add_item(Dropdown())

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(content='This interaction has expired, please use this command again', embed=None, view=self)

async def setup(client):
    await client.add_cog(Extra(client))
