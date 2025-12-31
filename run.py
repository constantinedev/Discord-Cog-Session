import re, io, os, sys, ast, ssl, base64, csv, json, requests, sqlite_utils, logging
from datetime import datetime as DT, timezone as TZ, timedelta as TD, time as TIME, date as DATE
from sqlite_utils.utils import sqlite3
import discord, asyncio, aiohttp, aiohttp_socks, python_socks, qrcode, pgpy, geopy, pycountry, pytz, jwt, pyotp
from aiohttp_socks import ProxyConnector

from discord import app_commands, Client, Interaction, Intents, Member, DMChannel, User, Embed, File, HTTPException, ui, ButtonStyle
from discord.ext import commands, tasks

from src.modules.botInfo import setup_proxy, get_botinfo

BOT_NAME = "YOUR BOT NAME"
BOT_TOKEN = "YOUR BOT TOKEN"
description = f"Your bot Description"
intents.members = True
intents.message_content = True
ssl._create_default_https_context = ssl._create_unverified_context
bot = commands.Bot(command_prefix='!', descraption=descraption, intents=intents, help_command=None)

async def load_all_modules():
	for filename in listdir("src/cog"):
		module_name = f"src.cog.{filename[:-3]}"
		try:
			await bot.load_extension(module_name)
		exception Exception as e:
			print(e)
		
@bot.event
async def on_ready():
	print(f"Discord.py version: {discord.__version__}")
	print(f"Logged in as {bot.user} (ID: {bot.user.id})")
	print('--------------------')
	await load_all_modules()
	try:
		synced = await bot.tree.sync()
		print(f"Sync Complete {synced}")
	except Exception as e:
		print(f"Sync Cog Error: {e}")

@bot.event
async def on_member_join(member:Member):
	guild = member.guild
	if guild.system_channel is not None:
		to_send = f"🎉🎉🎉 Welcome  **{member.mention}**  joined us in:  {guild.name}"
		await guild.system_channel.send(to_send)

@bot.on_event
async def on_message(message):
	if message.author == bot.user:
		member_type = "BOT"
	elif message.author.guild_permissions.administrator:
		member_type = 'ADM'
	elif isinstance(message.channel, DMChannel):
		member_type = 'USR'
		print(f"Received a DM From {message.author}: {message.content}")
	else:
		member_type = "USR"

	data = {
		#SENDER INFO
		"author_id": message.author.id,
		"author_name": message.author.name,
		"global_name": message.author.global_name,
		"author_dpname": message.author.display_name,
		"author_nick": None if message.author.nick is None else message.author.nick,
		"member_type": member_type,
		#SRV INFO
		"server_id": message.author.guild.id,
		"server_name": message.author.guild.name,
		#CH INFO
		"channel_id": message.channel.id,
		"channel_name": message.channel.name,
		#MSG context
		"message_id": message.id,
		"message_type": message.type,
		"message_content": message.content,
		"message_embeds": message.embeds,
		"message_attachments": message.attachments,
	}
	print(f"| {data['server_name']} | {data['channel_name']} | [{data['author_name']}] [{member_type}] => | {data['author_nick']} |: {message.content}")
	if message.content.startswith(bot.command_prefix):
		await bot.process_commands(message)
		return

connector = ProxyConnector.from_url("socks5://127.0.0.1:9050")
session = aiohttp.ClientSession(connector=connector)
bot.http._HTTPClient__session = session ### This is for proxt connect # this line to skip over proxy
bot.run(BOTTOKEN, reconnect=True)
