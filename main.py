import discord
import os
import json
from dotenv import load_dotenv
from models import Database, QUIZ_COMPLETED_TOAST

load_dotenv(verbose=True)

client = discord.Client()

data_file = open("data.json")
data = json.load(data_file)

db = Database()

WRONG_FORMAT_TOAST = (
    "The command you entered is not valid||Enter $help to view valid commands"
)
HELP_TOAST = "`$hello`: _To get hello reply from bot_||\
    `$clue`: _To get your next clue_||\
    `$ans<SPACE>your_answer_here`: _To enter answer after viewing clue_||\
    `$hint`: _To get a hint for your current clue_"

HELLO_MESSAGE = "Hello there, welcome to treasure hunt, enter `$clue` to start your journey||\
    Use `$help` to know the bot commands."


HELLO_AGAIN_MESSAGE = "Hello again, why are you wasting your time ?||\
    If you are confused use `$help`."


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message):

    # retrun if the bot is sending command
    if message.author == client.user:
        return

    print(message.content, " - ", str(message.author))

    if message.content.startswith("$ans "):
        ans = message.content.split(" ")
        # check if the ans is of the correct format
        print(ans)
        if len(ans) == 2 and ans[0] == "$ans":
            # ans is of the correct format
            res = db.check_ans(str(message.author), ans[1])
            await send_message(res, message)
        else:
            await send_message(WRONG_FORMAT_TOAST, message)

    elif message.content == "$clue":
        clue = db.get_clue(str(message.author))
        await send_message(clue, message)

    elif message.content == "$hint":
        hint = db.get_hint(str(message.author))
        await send_message(hint, message)

    elif message.content == "$hello":
        res = db.start_hunt(str(message.author))
        if res == 0:
            await send_message(HELLO_MESSAGE, message)
        elif res == 1:
            await send_message(HELLO_AGAIN_MESSAGE, message)
        else:
            await send_message(QUIZ_COMPLETED_TOAST, message)

    elif message.content == "$help":
        await send_message(HELP_TOAST, message)

    elif message.content == "$leaderboard":
        await message.channel.send(db.get_leaderboard())

    else:
        await send_message(WRONG_FORMAT_TOAST, message)


async def send_message(message_string, message):
    for element in message_string.split("||"):
        if element.startswith("files/"):
            await message.channel.send(file=discord.File(element))
        else:
            await message.channel.send(element)
    # return


client.run(os.getenv("TOKEN"))
