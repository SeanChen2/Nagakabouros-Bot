import discord, os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from discord.ext import commands as cmd
from responses import get_response
from random import choice
from uggscraper import UggScraper
from table2ascii import table2ascii, Alignment
from paginationviews import LeaderboardView, CounterView
from data import ILLAOI_QUOTES

# Constants
BOT_NAME = "Nagakabouros"
BOT_PREFIX = "??"
WELCOME_CHANNEL_ID = 1267955205715005514

# Load bot token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up the bot
intents = Intents.default()
intents.message_content = True
intents.members = True
client = Client(intents=intents)

# Create an object to scrape u.gg data
ugg_scraper = UggScraper()

# Message functionality
async def send_message(message, user_message):
    if not user_message:
        print("User message is empty")
        return
    
    try:
        response = get_response(user_message)

        if response:
            await message.channel.send(response)
    except Exception as e:
        print(e)


# Detect when the bot starts up
@client.event
async def on_ready():
    print(f"{BOT_NAME} is up!")
    print("--------------------------------")


# Respond to messages
@client.event
async def on_message(message):
    message_text = message.content

    if message_text[:2] == BOT_PREFIX:
        cmd = message_text[2:]

        if cmd == "":
            await message.channel.send("That is not a valid command.")
        elif cmd == "qotd":
            await message.channel.send(choice(ILLAOI_QUOTES))
        elif cmd[:6] == "champs":
            await send_champ_leaderboard(cmd[7:] if len(cmd) > 7 else "All", message)
        elif cmd[:7] == "counter":
            await send_counter_list(cmd[8:] if len(cmd) > 8 else None, message)
        
    else:

        # Make sure the bot doesn't respond to itself
        if message.author == client.user:
            return

        print(f'[{message.channel}] {message.author}: "{message_text}"')
        await send_message(message, message_text)


# Welcome a user to the server
@client.event
async def on_member_join(member):
    channel = client.get_channel(WELCOME_CHANNEL_ID)
    await channel.send(f"Welcome, {member}!")


async def send_champ_leaderboard(champ_role, message):

    roles = ugg_scraper.champ_roles
    champ_role = champ_role.lower().capitalize()

    # Exception: if the role is ADC, capitalize ALL letters
    if champ_role == "Adc":
        champ_role = "ADC"

    # Handle invalid role requests
    if champ_role != "All" and champ_role not in roles:
        await message.channel.send(f"That is not a valid role. The searchable roles are: {', '.join(roles)}")
        return

    leaderboard = LeaderboardView()
    leaderboard.data = get_leaderboard_table(champ_role)
    await leaderboard.send(message)


def get_leaderboard_table(role):
    
    champions = ugg_scraper.champions
    
    # Translate the champions dictionary into tabular format
    champions_table = []

    for champ in champions:

        # Only add this champion if all roles were requested, or if this champion fits under the specifically requested role
        if role == "All" or champ["role"] == role:
            champions_table.append([champ["rank"], champ["name"], champ["role"], champ["tier"], champ["win_rate"], champ["pick_rate"], champ["ban_rate"]])

    return champions_table


async def send_counter_list(champ_str, message):

    champ_str = champ_str.lower()

    # Get sets of possible champ names and roles for validation purposes
    champ_names = ugg_scraper.champ_names
    champ_roles = ugg_scraper.champ_roles

    # If the string is empty, show the user how to format the command
    if not champ_str:
        await message.channel.send(f'The correct format is: "??counter [champion name] [optional champion role]".\nThe searchable roles are: {", ".join(champ_roles)}')
        return

    # Split the champ string into the champion's name and role (role is optional), and fetch matchup data
    if (len(champ_str.split()) > 1):
        champ_name, champ_role = champ_str.split()
        champ_name = champ_name.lower().capitalize()
        champ_role = champ_role.lower().capitalize()

        # Exception: if the role is ADC, capitalize ALL letters
        if champ_role == "Adc":
            champ_role = "ADC"

        # Validate the name and role
        if champ_name not in champ_names or champ_role not in champ_roles:
            await message.channel.send(f'Invalid. The correct format is: "??counter [champion name] [optional champion role]".\nThe searchable roles are: {", ".join(champ_roles)}')
            return
        
        champ_role, counters = ugg_scraper.get_matchup_data(champ_name, champ_role)

    else:
        champ_name = champ_str.strip().lower().capitalize()

        # Validate the name
        if champ_name not in champ_names:
            await message.channel.send(f'Invalid. The correct format is: "??counter [champion name] [optional champion role]".\nThe searchable roles are: {", ".join(champ_roles)}')
            return

        champ_role, counters = ugg_scraper.get_matchup_data(champ_name)

    counter_view = CounterView()
    counter_view.setup(champ_name, champ_role, counters)
    await counter_view.send(message)
    

# Load all Illaoi quotes from the .txt file
def load_illaoi_quotes():
    file = open("illaoiQuotes.txt")
    quotes = file.read().split("\n")

    for quote in quotes:
        ILLAOI_QUOTES.append(quote)


# Main function: load Illaoi quotes, then run the bot
if __name__ == '__main__':
    load_illaoi_quotes()
    client.run(TOKEN)
    ugg_scraper.quit()
