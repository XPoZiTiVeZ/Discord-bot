import discord
import os
import sys
import asyncio
import typing
import json
import DiscordUtils
import ffmpeg
from discord import FFmpegPCMAudio, PCMVolumeTransformer
from discord.ext import commands, tasks
from config import settings
from itertools import cycle

status = cycle(["Test","Testing"])
intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix = settings['prefix'], intents=intents)
# bot.remove_command( 'help' )

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}

@bot.event
async def on_ready():
	changeStatus.start()
	print("Bot is online!")

@tasks.loop(seconds=5)
async def changeStatus():
	await bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.Activity(type=discord.ActivityType.playing, name=next(status)))

@bot.command(description="Gives the role to the specified user")
async def upgrade (ctx, role:discord.Role, member:discord.Member):
	if ctx.message.author.id == 566691282106318878:
		mod = discord.utils.get(ctx.message.guild.roles,name = str(role))
		await member.add_roles(mod)
		await ctx.channel.purge(limit=1)
		BotLog = open("BotLog.txt", "a")
		BotLog.write(f"{member} получил роль {role}");
		BotLog.close()
		print(f"{member} получил роль {role}")

@bot.command(description="Takes away the role at the specified user")
async def degrade (ctx, role:discord.Role, member:discord.Member):
	if ctx.message.author.id == 566691282106318878:
		mod = discord.utils.get(ctx.message.guild.roles,name = str(role))
		await member.remove_roles(mod)
		await ctx.channel.purge(limit=1)
		BotLog = open("BotLog.txt", "a")
		BotLog.write(f"{member} потерял роль {role}");
		BotLog.close()
		print(f"{member} потерял роль {role}")

@bot.command(discription="Kicks the specified user")
async def kick(ctx, member: discord.Member, *, reason=None):
	if ctx.message.author.id == 566691282106318878:
		await member.kick(reason=reason)
		await ctx.channel.purge(limit=1)
		BotLog = open("BotLog.txt", "a")
		BotLog.write(f"{member} был кикнут из {ctx.guild}");
		BotLog.close()
		print(f"{member} был кикнут из {ctx.guild}")

@bot.command(desription="Bans the specified user")
async def ban(ctx, member: discord.Member, *, reason=None):
	if ctx.message.author.id == 566691282106318878:
		await member.ban(reason=reason)
		await ctx.channel.purge(limit=1)
		BotLog = open("BotLog.txt", "a")
		BotLog.write(f"{member} был забанен в {ctx.guild}");
		BotLog.close()
		print(f"{member} был забанен в {ctx.guild}")

@bot.command(description="Unban the specified user")
async def unban(ctx, *, member):
	if ctx.message.author.id == 566691282106318878:
		banned_users = await ctx.guild.bans()
		member_name, member_discriminator = member.split('#')
		for ban_entry in banned_users:
			user = ban_entry.user
		if (user.name, user.discriminator) == (member_name, member_discriminator):
			await ctx.guild.unban(user)
			await ctx.channel.purge(limit=1)
			BotLog = open("BotLog.txt", "a")
			BotLog.write(f"{member} был разбанен в {ctx.guild}");
			BotLog.close()
			print(f"{member} был разбанен в {ctx.guild}")
		return

@bot.command(description="Mutes the specified user.")
async def mute(ctx, member: discord.Member, *, mute_minutes: typing.Optional[int] = 0, reason=None):
	if ctx.message.author.id == 566691282106318878:
		guild = ctx.guild
		mutedRole = discord.utils.get(guild.roles, name="Muted")
		await ctx.channel.purge(limit=1)
		if not mutedRole:
			mutedRole = await guild.create_role(name="Muted")
		for channel in guild.channels:
			await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=True	)
		await member.add_roles(mutedRole, reason=reason)
		BotLog = open("BotLog.txt", "a")
		BotLog.write(f"{member} был замучен в {ctx.guild}");
		BotLog.close()
		print(f"{member} был замучен в {ctx.guild}")
		if mute_minutes > 0:
			await asyncio.sleep(mute_minutes * 60)
			await member.remove_roles(mutedRole, reason = "time's up")


@bot.command(description="Unmutes a specified user.")
async def unmute(ctx, member: discord.Member):
	if ctx.message.author.id == 566691282106318878:
		mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")
		await member.remove_roles(mutedRole)
		await ctx.channel.purge(limit=1)
		BotLog = open("BotLog.txt", "a")
		BotLog.write(f"{member} был размучен в {ctx.guild}");
		BotLog.close()
		print(f"{member} был размучен в {ctx.guild}")

@bot.command(description="Warns the intruder")
async def warn(ctx,user:discord.User,*reason:str):
  if not reason:
    await client.say("Please provide a reason")
    return
  reason = ' '.join(reason)
  for current_user in report['users']:
    if current_user['name'] == user.name:
      current_user['reasons'].append(reason)
      break
  else:
    report['users'].append({
      'name':user.name,
      'reasons': [reason,]
    })
  with open('reports.json','w+') as f:
    json.dump(report,f)

@bot.command(pass_context = True)
async def warnings(ctx,user:discord.User):
  for current_user in report['users']:
    if user.name == current_user['name']:
      await client.say(f"{user.name} has been reported {len(current_user['reasons'])} times : {','.join(current_user['reasons'])}")
      break
  else:
    await client.say(f"{user.name} has never been reported")  

@warn.error
async def kick_error(error, ctx):
  if isinstance(error, MissingPermissions):
      text = "Sorry {}, you do not have permissions to do that!".format(ctx.message.author)
      await client.send_message(ctx.message.channel, text)

@bot.command(description = "Clears the messages")
async def clear(ctx, purge):
	try:
		await ctx.channel.purge(limit=int(purge) + 1)
		ctx.channel.send(f"{ctx.author} had cleared {purge} messages")
		print(f"{ctx.author} had cleared {purge} messages")
	except discord.ext.commands.errors.MissingRequiredArgument:
		ctx.channel.send('No value for clear')
		
music = DiscordUtils.Music()

@bot.command()
async def join(ctx):
    await ctx.author.voice.channel.connect() #Joins author's voice channel

@bot.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()

@bot.command()
async def play(ctx, *, url):
    player = music.get_player(guild_id=ctx.guild.id)
    if not player:
        player = music.create_player(ctx, ffmpeg_error_betterfix=True)
    if not ctx.voice_client.is_playing():
        await player.queue(url, search=True)
        song = await player.play()
        await ctx.send(f"Playing {song.name}")
    else:
        song = await player.queue(url, search=True)
        await ctx.send(f"Queued {song.name}")

@bot.command()
async def pause(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    song = await player.pause()
    await ctx.send(f"Paused {song.name}")

@bot.command()
async def resume(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    song = await player.resume()
    await ctx.send(f"Resumed {song.name}")

@bot.command()
async def stop(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    await player.stop()
    await ctx.send("Stopped")

@bot.command()
async def loop(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    song = await player.toggle_song_loop()
    if song.is_looping:
        await ctx.send(f"Enabled loop for {song.name}")
    else:
        await ctx.send(f"Disabled loop for {song.name}")

@bot.command()
async def queue(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    await ctx.send(f"{', '.join([song.name for song in player.current_queue()])}")

@bot.command()
async def np(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    song = player.now_playing()
    await ctx.send(song.name)

@bot.command()
async def skip(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    data = await player.skip(force=True)
    if len(data) == 2:
        await ctx.send(f"Skipped from {data[0].name} to {data[1].name}")
    else:
        await ctx.send(f"Skipped {data[0].name}")

@bot.command()
async def volume(ctx, vol):
    player = music.get_player(guild_id=ctx.guild.id)
    song, volume = await player.change_volume(float(vol) / 100) # volume should be a float between 0 to 1
    await ctx.send(f"Changed volume for {song.name} to {volume*100}%")

@bot.command()
async def remove(ctx, index):
    player = music.get_player(guild_id=ctx.guild.id)
    song = await player.remove_from_queue(int(index))
    await ctx.send(f"Removed {song.name} from queue")

bot.run(settings['token'])
