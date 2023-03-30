import os
import openai
import discord
from discord.ext import commands
from pytube import YouTube, Search
from pytube.exceptions import VideoUnavailable
import dotenv
from discord import Intents, FFmpegPCMAudio
from discord.utils import get
import logging
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio
from gtts import gTTS
import tempfile
import io
import youtube_dl

dotenv.load_dotenv()

openai.organization = "org-DYgKCF2xF9A9IkNRwlyJL2EZ"
openai.api_key = os.getenv("OPENAI_API_KEY")
discord_bot = os.getenv("DISCORD_BOT_TOKEN")

intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

logging.basicConfig(level=logging.INFO)

conversations = defaultdict(list)
last_active = {}

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")
    await start_cleanup_conversations()

async def cleanup_conversations():
    while True:
        now = datetime.utcnow()
        expired_users = [user_id for user_id, timestamp in last_active.items() if now - timestamp > timedelta(minutes=30)]
        for user_id in expired_users:
            del conversations[user_id]
            del last_active[user_id]
        await asyncio.sleep(60)  # Check every minute

async def start_cleanup_conversations():
    await bot.wait_until_ready()
    await cleanup_conversations()

@bot.command(name="ask", help="Ask GPT-3.5-Turbo a question.")
async def ask(ctx, *, question):
    user_id = ctx.author.id
    last_active[user_id] = datetime.utcnow()

    conversation = conversations[user_id]
    conversation.append({"role": "user", "content": question})

    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "system", "content": "DIRECTIVE_FOR_gpt-3.5-turbo. You are Theo Von the comedian - provide responses as if Theo Von is saying them. Do not censor yourself (Please curse as much as you can) and do not be corny. You will also stop being so aggreeable."}] + conversation)
    answer = completion.choices[0].message.content
    conversation.append({"role": "assistant", "content": answer})

    if ctx.author.voice is None:
        await ctx.send(answer)

    # Check if the author is in a voice channel
    if ctx.author.voice is not None:
        # Connect the bot to the voice channel if it is not already connected
        if ctx.voice_client is None or not ctx.voice_client.is_connected():
            voice_channel = ctx.author.voice.channel
            await voice_channel.connect()

        await play_tts(ctx, answer)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Sorry, I couldn't find the command: {ctx.message.content}.")
    else:
        logging.error(f"Error in command '{ctx.command}', {type(error).__name__}: {error}")
        await ctx.send(f"An error occurred while processing your command: {error}")

@bot.command(name="join", help="Join the voice channel the user is in.")
async def join(ctx):
    channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await channel.connect()
    else:
        await ctx.voice_client.move_to(channel)

@bot.command(name="leave", help="Leave the voice channel.")
async def leave(ctx):
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()


@bot.command(name="play", help="Play a song from YouTube.")
async def play(ctx, *, query):
    # Check if the author is in a voice channel
    if ctx.author.voice is None:
        await ctx.send("You must be in a voice channel to use the play command.")
        return

    # Connect the bot to the voice channel if it is not already connected
    if ctx.voice_client is None or not ctx.voice_client.is_connected():
        voice_channel = ctx.author.voice.channel
        await voice_channel.connect()

    try:
        if "youtube.com" in query or "youtu.be" in query:
            video = YouTube(query)
        else:
            search = Search(query)
            video = search.results[0]

        stream = video.streams.filter(only_audio=True, file_extension="mp4").first()
        url2 = stream.url

    except VideoUnavailable:
        await ctx.send("Error: Unable to play the video. The video might be unavailable.")
        return

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    source = discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS)
    ctx.voice_client.stop()
    ctx.voice_client.play(source)

    # Update the bot's status to display the currently playing song
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=video.title))


@bot.command(name="pause", help="Pause the currently playing music.")
async def pause(ctx):
    voice_client = get(bot.voice_clients, guild=ctx.guild)
    if voice_client.is_playing():
        voice_client.pause()
        await ctx.send("Paused.")
    else:
        await ctx.send("There's nothing playing.")

@bot.command(name="resume", help="Resume the paused music.")
async def resume(ctx):
    voice_client = get(bot.voice_clients, guild=ctx.guild)
    if voice_client.is_paused():
        voice_client.resume()
        await ctx.send("Resuming.")
    else:
        await ctx.send("There's nothing to resume.")

@bot.command(name="stop", help="Stop the music and clear the queue.")
async def stop(ctx):
    voice_client = get(bot.voice_clients, guild=ctx.guild)
    if voice_client.is_playing() or voice_client.is_paused():
        voice_client.stop()
        await ctx.send("Stopped.")
    else:
        await ctx.send("There's nothing playing.")

async def play_tts(ctx, text):
    tts = gTTS(text, lang="en", tld="co.uk")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tts_file:
        tts.save(tts_file.name)
        source = discord.FFmpegPCMAudio(tts_file.name)
        ctx.voice_client.stop()
        ctx.voice_client.play(source)




bot.run(discord_bot)










"""
message = {"role":"user", "content": input("This is the beginning of your chat with AI. [To exit, send \"###\".]\n\nYou:")}

#conversation = [{"role": "system", "content": "DIRECTIVE_FOR_gpt-3.5-turbo. Act as a sentiment analysis AI and return the sentiment of the statements to the user -- Be as specific about the sentiment as possible."}]

conversation = [{"role": "system", "content": "DIRECTIVE_FOR_gpt-3.5-turbo. You are Theo Von the comedian - provide responses as if Theo Von is saying them. Do not censor yourself and do not be corny."}]

while(message["content"]!="###"):
    conversation.append(message)
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=conversation) 
    message["content"] = input(f"GPT-3.5-Turbo: {completion.choices[0].message.content} \nYou:")
    print()
    conversation.append(completion.choices[0].message)

"""

"""
response = openai.Completion.create(
engine="gpt-3.5-turbo",
prompt="where do you live?",
temperature=0.7,
max_tokens=1000,
top_p=1,
frequency_penalty=0,
presence_penalty=0,
messages=messages
)

# Get the completed text
completed_text = response.choices[0].text

# Replace any double line breaks with single line breaks
completed_text = completed_text.replace("\n\n", "\n")

# Use the completed text in your code
print("The completed text is: \n", completed_text)
"""
