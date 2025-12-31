import re, io, os, sys, ast, ssl, base64, json, csv, sqlite_utils
from sqlite_utils.utils import sqlite3
from datetime import datetime as DT, timezone as TZ, timedelta as TD, date, time
from typing import List

import discord
from discord import app_commands, Client, Intents, Interaction, Member, User, DMChannel, File, Embed, Button, TextStyle, ButtonStyle, HTTPException
from discord.ui import Modal, modal, View, Select, TextInput, button
from discord.ext import commands, tasks

################################################
## You must meed the setup(bot) to each 
## and the class need to follow in active.
################################################
async def setup(bot):
	await bot.add_cog(OEM(bot))

class OEM(commands.Cog):
	def __init__ (self, bot: commands.Bot):
		self.bot = bot
	
	@commands.command(name="kick", brief='!kick [@user] [reason]', pass_context=True)
	@app_commands.default_permissions(kick_members=True)
	@commands.has_permissions(kick_members=True)
	@commands.bot_has_permissions(kick_members=True)
	async def _kick(self, ctx, member: discord.Member, *, reason:str=None):
		if member.top_role >= ctx.author.top_role:
			return await ctx.send(f"❌ You can't kick higher roles then youself.", delete_after=5)
		if ctx.guild.me.guild_permissions.kick_members:
			if member is None:
				return await ctx.send(f"❌ Unknow **Member** CMD Usage: !kick @user", delete_after=5)
			else:
				await member.kick(reason=reason)
			return await ctx.send(f"✅🦶🏻 {member.mention} had been kicked.", delete_after=5)
		else:
			return await ctx.send(f"⚠️ {ctx.author.display_name} You have no right to user this CMD.")

	@commands.command(name="ban", brief="!ban [@user] [reason]", pass_context=True)
	@app_commands.default_permissions(ban_members=True)
	@commands.has_permissions(ban_members=True)
	@commands.bot_has_permissions(ban_members=True)
	async def _ban(self, ctx:commands.Context, member: Member, *, reason:str=None):
		if member.top_role >= ctx.author.top_role:
			return await ctx.send(f"❌ You can't edit higher roles then youself.", delete_after=5)
		if member == ctx.message.author:
			return await ctx.send("❌ You can ban yourself.", delete_after=5)
		if ctx.guild.me.guild_permissions.moderate_members:
			if member is None:
				return await ctx.send(f"❌ Unknow **Member**, CMD Usage: !ban @user.", delete_after=5)
			else:
				await ctx.guild.ban(member, reason=reason)
			return await ctx.send(f"✅⛔️ {member.mention} had been banned!", delete_after=10)
		else:
			return await ctx.send(f"⚠️ {ctx.author.display_name} You have no right to use this CMD.")

	@commands.command(name="unban", brief="!unban [@user] [reason]", pass_context=True)
	@app_commands.default_permissions(administrator=True)
	@commands.has_permissions(ban_members=True)
	@commands.bot_has_permissions(ban_members=True)
	async def _unban(self, ctx:commands.Context, member: str, reason:str=None):
		try:
			if member.startswith('<@') and member.endswtih(">"):
				user_id = int(member.strip("@!"))
			else:
				user_id = int(member)
			user = discord.Object(id=user_id)
			banned_users = [entry async for entry in ctx.guild.bans(limit=None)]
			if not any(entry.user.id == user_id for entry in banned_users(limit=None)):
				return await ctx.send(f"❌ Users **{member}** not in this Server", delete_after=5)
			### UNBAN USER
			await ctx.guild.unban(user, reason=reason)
			await ctx.send(f"✅🔓 Welcome back {user_id} unbanned!", delete_after=5)
			### UNBAN USER # ENG
		except ValueError:
			await ctx.send(f"❌ UserID input error, CMD：`!unban @user_id`", delete_after=5)
		except discord.Forbidden:
			await ctx.send(f"❌ {ctx.author.display_name} I have no permission in this channel.", delete_after=5)
		except HTTPException as e:
			await ctx.send(f"❌ HTTP Error", delete_after=5)
	@_unban.error
	async def _unban_error(self, ctx: commands.Context, error):
		if isinstance(error, commands.MissingPermissions):
			await ctx.send(f"⚠️ {ctx.author.display_name} You have no right to use this CMD.")
		elif isinstance(error, commands.BotMissingPermissions):
			await ctx.send(f"❌ I have no permission in this channel.", delete_after=5)
		else:
			print(f"❌ HTTP Error:\n{error}")

	@commands.hybrid_command(name="cleanmessage", brief="!cleanmessage [@user] [limit]")
	@app_commands.describe(member="@user", limit="int delete messages.")
	@app_commands.default_permissions(manage_messages=True)
	@commands.has_permissions(manage_messages=True)
	async def _cleanmessage(self, ctx:commands.Context, member:Member, *, limit:int = 5):
		await ctx.defer(ephemeral=False)
		def is_target(message: discord.Message):
			return message.author.id == member.id
		if limit is None:
			limit = 5
		else:
			limit = int(limit)
		try:
			deleted = await ctx.channel.purge(limit=limit+1, check=is_target, bulk=True)
			return await ctx.send(f"🚮 Complete clear ** {member.display_name}**, {len(deleted)} messages.", delete_after=8)
		except discord.Forbidden:
			return await ctx.send("❌ I have no permission in this channel.", delete_after=8)
		except discord.HTTPException as e:
			return await ctx.send(f"❌ **Remove** Error: {e}", ephemeral=True)
	@_cleanmessage.error
	async def cleanmessage_error(self, ctx: commands.Context, error: commands.CommandError):
		if isinstance(error, commands.MissingPermissions):
			return await ctx.send(f"⚠️ {ctx.author.display_name} You have no right to use this CMD.", delete_after=8)
		elif isinstance(error, commands.BotMissingPermissions):
			return await ctx.send(f"❌ I have no permission in this channel.", delete_after=8)
		elif isinstance(error, commands.BadArgument):
			return await ctx.send(f"❌ Unknow **Member** or member not in this channel.", ephemeral=True, delete_after=5)
		else:
			return await ctx.send(f"❌ **Remove** Error: {error}", ephemeral=True, delete_after=5)
