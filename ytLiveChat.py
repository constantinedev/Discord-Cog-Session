import pytchat, discord, asyncio
from deep_translator import GoogleTranslator

from discord import app_commands
from discord.ext import commands, tasks

async def setup(bot):
	await bot.add_cog(YTChatCog(bot))

class YTChatCog(commands.Cog):
	def __init__ (self, bot:commands.Bot):
		self.bot = bot
		self.chat = None
		self.is_running = False
		self.task = None
		self.current_video_id = None
		self.discord_channel = None
	
	async def _start(self, video_id:str, discord_channel):
		if self.is_running:
			return "Live Chat service are running."
		try:
			self.chat = pytchat.create(video_id=video_id)
			if not self.chat.is_alive():
				self.chat = None
				return "Live Chat is not available for this video."
			self.is_running = True
			self.current_video_id = video_id
			self.discord_channel = discord_channel
			self.task = asyncio.create_task(self._fetch_chat(discord_channel))
			return f"▶️ YT Live Chat start VID: [{video_id}]"
		except Exception as e:
			return f"Error starting chat: {e}"

	async def _stop(self):
		if not self.is_running:
			return "🟥 Chat is not running."
		self.is_running = False
		if self.task:
				self.task.cancel()
		self.chat = None
		self.current_video_id = None
		self.discord_channel = None
		return "⏹ 已手動停止 YouTube 直播聊天室。"

	async def _fetch_chat(self, channel):
		while self.is_running and self.chat and self.chat.is_alive():
			try:
				messages = self.chat.get().sync_items()
				for message in messages:
					if not self.is_running or channel is None:
						print("⏹ Channel 已失效或已停止，退出 loop")
						self.is_running = False
						break
					formatted_message = f"[{message.author.name}]: {message.message}"
					try:
						result_msg = GoogleTranslator(source='auto', target='zh-TW').translate(message.message)
					except Exception as trans_e:
						print(f"❌ 翻譯錯誤: {trans_e}")
						result_msg = message.message
					translate_msg = f"[{message.author.name}]: {result_msg}"
					try:
						await channel.send(f"[YT] {formatted_message[:2000]}")
						await channel.send(f"[YT][翻譯] {translate_msg[:2000]}")
					except discord.errors.Forbidden:
						await channel.send("⚠️ Bot 無權限發送訊息在此頻道，已停止操作。")
						self.is_running = False
						break
					except Exception as send_e:
						print(f"🔁 發送訊息失敗: {send_e}")
				await asyncio.sleep(1)
			except Exception as e:
				print(f"❌ Fetch 錯誤: {e}")
				await asyncio.sleep(5)
		self.is_running = False
		self.chat = None
		self.current_video_id = None
		self.discord_channel = None
		try:
			await channel.send("⏹ YouTube 直播聊天室已結束或斷線，聊天室停止。")
		except:
			pass
		print("⏹ Chat fetching stopped.")
	
	@commands.command(name="ytchat", brief="!ytchat [start/stop] [video_id]")
	@app_commands.default_permissions(administrator=True)
	@commands.has_permissions(administrator=True)
	@commands.bot_has_permissions(administrator=True)
	async def _ytchat(self, ctx, action: str = None, video_id: str = None):
		if action is None:
			return await ctx.send("用法：\n`!ytchat start <video_id>` 開始轉發\n`!ytchat stop` 停止轉發")
		if action.lower() == "start":
			if video_id is None:
				return await ctx.send("請輸入 video_id，例如：`!ytchat start [video_id]`")
			result = await self._start(video_id, ctx.channel)
			await ctx.send(result)
		elif action.lower() == "stop":
			result = await self._stop()
			return await ctx.send(result)
		else:
			await ctx.send("未知動作，只支援 `start` 或 `stop`\n用法：`!ytchat start [video_id]` 或 `!ytchat stop`")
