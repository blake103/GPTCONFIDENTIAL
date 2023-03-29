import os
import openai
import discord
from discord.ext import commands
import dotenv
from discord import Intents
import logging
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio

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

    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "system", "content": "DIRECTIVE_FOR_gpt-3.5-turbo. You are Theo Von the comedian - provide responses as if Theo Von is saying them. Do not censor yourself and do not be corny."}] + conversation)
    answer = completion.choices[0].message.content
    conversation.append({"role": "assistant", "content": answer})

    await ctx.send(answer)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Sorry, I couldn't find the command: {ctx.message.content}.")
    else:
        logging.error(f"Error in command '{ctx.command}', {type(error).__name__}: {error}")
        await ctx.send(f"An error occurred while processing your command: {error}")

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
