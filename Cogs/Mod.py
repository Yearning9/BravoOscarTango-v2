import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import MissingPermissions, BotMissingPermissions
from discord.ext.commands import MissingRequiredArgument, MemberNotFound, BadArgument
from datetime import timedelta
import math
import time


class Mod(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def clear(self, ctx, amount=1, *, reason=None):

        await ctx.channel.purge(limit=amount + 1, reason=str(reason))
        await ctx.send(f'Deleted {amount} message(s) with reason:\n`{reason}`', delete_after=10)

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def timeout(self, ctx, user: discord.Member, days: int = 0, hours: int = 12, *, reason=None):

        if user.timed_out_until is not None:
            return await ctx.send('User is already timed out')

        if days == 0 and hours == 0:
            return await ctx.send('Please choose a different amount of time')

        days = abs(days)
        hours = abs(hours)

        if days > 27:
            return await ctx.send('Please select a lower amount of days')
        elif hours > 24:
            days_n = days
            days = int(hours / 24)
            if days > 27:
                return await ctx.send('Please select a lower amount of days')
            hours = int(math.ceil(((hours / 24) - days) * 24))
            days = days_n + days
            delta: timedelta = timedelta(days=days, hours=hours)
            await user.timeout(delta, reason=str(reason))
            return await ctx.send(
                f"The user {user.mention} has been put in timeout for {days} day(s) and {hours} hour(s). Reason:\n`{reason}`")
        else:
            delta: timedelta = timedelta(days=days, hours=hours)
            await user.timeout(delta, reason=str(reason))
            return await ctx.send(
                f"The user {user.mention} has been put in timeout for {days} day(s) and {hours} hour(s). Reason:\n`{reason}`")

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def rem_timeout(self, ctx, user: discord.Member):
        if user.timed_out_until is None:
            return await ctx.send('That user is not timed out')
        else:
            await user.timeout(None)
            return await ctx.send(f'User {user.mention} is no longer timed out')

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, *, reason=None):
        await user.ban(reason=reason, delete_message_days=0)
        await ctx.send(f'Banned {user.mention}. Reason for ban: {reason}')

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, *, reason=None):
        await user.kick(reason=reason)
        await ctx.send(f'Kicked {user.mention}. Reason for kick: {reason}')

    # Error Handling

    # @mute.error
    # async def mute_error(self, ctx, error):
    #     if isinstance(error, MissingPermissions):
    #         await ctx.send("You don't have the Manage Messages permission")
    #     else:
    #         await ctx.send("I need the Manage Roles permission to do that!")
    #
    # @unmute.error
    # async def unmute_error(self, ctx, error):
    #     if isinstance(error, MissingPermissions):
    #         await ctx.send("You don't have the Manage Messages permission")
    #     elif isinstance(error, BotMissingPermissions):
    #         await ctx.send("I need the Manage Roles permission to do that!")
    #     else:
    #         await ctx.send('An error occurred while unmuting')
    #         print(error)

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send("You don't have the Manage Messages permission")
        else:
            await ctx.send("I don't have the correct permission(s) to do that!")

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send("You don't have the Ban Members permission")
        elif isinstance(error, MissingRequiredArgument):
            await ctx.send('You need to specify a user to ban')
        elif isinstance(error, BotMissingPermissions):
            await ctx.send("I don't have the correct permission(s) to do that!")
        elif isinstance(error, MemberNotFound):
            await ctx.send("Couldn't find that user, please try again")
        else:
            await ctx.send('An error occurred while using this command')

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send("You don't have the Kick Members permission")
        elif isinstance(error, MissingRequiredArgument):
            await ctx.send('You need to specify a user to kick')
        elif isinstance(error, BotMissingPermissions):
            await ctx.send("I don't have the correct permission(s) to do that!")
        elif isinstance(error, MemberNotFound):
            await ctx.send("Couldn't find that user, please try again")
        else:
            await ctx.send('An error occurred while using this command')

    @timeout.error
    async def timeout_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send("You don't have the Moderate Members permission")
        elif isinstance(error, BotMissingPermissions):
            await ctx.send("I don't have the Moderate Members permission")
        elif isinstance(error, MemberNotFound):
            await ctx.send("Couldn't find that user, please try again")
        elif isinstance(error, BadArgument):
            await ctx.send("You entered some wrong values, please check how to use this command with /mod-commands")
        elif isinstance(error, TypeError):
            await ctx.send(
                "There's been an error with the amount of time you entered, please try again with different values")

    @rem_timeout.error
    async def rem_timeout_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send("You don't have the Moderate Members permission")
        elif isinstance(error, BotMissingPermissions):
            await ctx.send("I don't have the Moderate Members permission")
        elif isinstance(error, MemberNotFound):
            await ctx.send("Couldn't find that user, please try again")
        elif isinstance(error, BadArgument):
            await ctx.send("You entered some wrong values, please check how to use this command with /mod-commands")

    # Slash Commands

    @app_commands.command(name='clear', description='Clears a set amount of messages')
    @app_commands.guild_only()
    @app_commands.describe(amount='Amount of messages to delete', reason='Reason to delete the messages')
    async def clear(self, interaction: discord.Interaction, amount: int = 1, reason: str = 'None'):

        if not interaction.app_permissions.manage_messages:
            return await interaction.response.send_message("I need the Manage Messages permission to do that!",
                                                           ephemeral=True)
        if not interaction.user.resolved_permissions.manage_messages:
            return await interaction.response.send_message("You need the Manage Messages permission to do that!",
                                                           ephemeral=True)

        try:
            await interaction.response.defer(thinking=True)
            await interaction.channel.purge(limit=amount + 1, reason=str(reason))
            time.sleep(1)
            await interaction.response.send_message(f'Deleted {amount} message(s) with reason:\n`{reason}`')

        except discord.app_commands.MissingPermissions or discord.app_commands.BotMissingPermissions or discord.errors.Forbidden:
            await interaction.response.send_message(
                "Permissions error! Check that both you and the bot have the Manage Messages permission",
                ephemeral=True)

    # @app_commands.command(name='timeout',
    #                       description='Time out a user for a set amount of time, or remove timeout for a user')
    # @app_commands.guild_only()
    # @app_commands.describe(user='The user to timeout', days='Amount of days to timeout for',
    #                        hours='Amount of hours to timeout for, set to 0 to remove timeout',
    #                        reason='Reason to timeout user')
    # async def timeout(self, interaction: discord.Interaction, user: discord.Member, days: int = 0, hours: int = 12,
    #                   reason: str = 'None'):
    #
    #     if not interaction.app_permissions.moderate_members:
    #         return await interaction.response.send_message("I need the Moderate Members permission to do that!",
    #                                                        ephemeral=True)
    #
    #     elif not interaction.channel.permissions_for(obj=discord.Object(interaction.user.id)).moderate_members:
    #         return await interaction.response.send_message("You need the Moderate Members permission to do that!",
    #                                                        ephemeral=True)
    #
    #     try:
    #
    #         if user.timed_out_until is not None:
    #             return await interaction.response.send_message(f'This user is already timed out', ephemeral=True)
    #
    #         if days == 0 and hours == 0:
    #             if user.timed_out_until is None:
    #                 return await interaction.response.send_message('This user is not timed out', ephemeral=True)
    #             else:
    #                 await user.timeout(None)
    #                 return await interaction.response.send_message(f'User {user.mention} is no longer timed out')
    #
    #         if days > 27:
    #             return await interaction.response.send_message('Please select a lower amount of days', ephemeral=True)
    #         elif hours > 24:
    #             days_n = days
    #             days = int(hours / 24)
    #             if days > 27:
    #                 return await interaction.response.send_message('Please select a lower amount of days',
    #                                                                ephemeral=True)
    #             hours = int(math.ceil(((hours / 24) - days) * 24))
    #             days = days_n + days
    #             delta: timedelta = timedelta(days=days, hours=hours)
    #             await user.timeout(delta, reason=str(reason))
    #             return await interaction.response.send_message(
    #                 f"The user {user.mention} has been put in timeout for {days} day(s) and {hours} hour(s). Reason:\n`{reason}`")
    #         else:
    #             delta: timedelta = timedelta(days=days, hours=hours)
    #             await user.timeout(delta, reason=str(reason))
    #             return await interaction.response.send_message(
    #                 f"The user {user.mention} has been put in timeout for {days} day(s) and {hours} hour(s). Reason:\n`{reason}`")
    #
    #     except MemberNotFound or TypeError:
    #         return await interaction.response.send_message(
    #             'There was an error with one of the parameters you gave, please try again or check /mod-commands to check how to use this command',
    #             ephemeral=True)


async def setup(client):
    await client.add_cog(Mod(client))
