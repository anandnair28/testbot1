import discord
import os
import json
from dotenv import load_dotenv
from models import Database

load_dotenv(verbose=True)

client = discord.Client()

data_file = open("data.json")
data = json.load(data_file)

db = Database()


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message):

    if message.content.startswith("$sup"):
        print(message.author)
        print(str(message.author))
        res = db.find_user(str(message.author))
        print(res)
        await message.channel.send(res)
    # if message.content.startswith('$leaderboard'):
    if message.content.startswith("$clue"):
        clue = db.get_clue(str(message.author))
        await message.channel.send(clue)
    if message.content.startswith("$hint"):
        hint = db.get_hint(str(message.author))
        await message.channel.send(hint)

    if message.content.startswith("$hello"):
        # intro_text = data["intro"].format(str(message.author))
        # await message.channel.send(intro_text)
        await message.channel.send(file=discord.File("thtest.png"))
        if db.start_hunt(str(message.author)):
            await message.channel.send("This is the intro message")
            await message.channel.send("This is the help message")
            await message.channel.send("print $clue to start")
        else:
            await message.channel.send("not viewing for first time, say smth else")

    # if message.content.startswith("$clue"):

    #     clueid = users.get(str(message.author), 0)

    #     if clueid < 3:
    #         await message.channel.send(data["clues"][clueid])

    #     else:
    #         await message.channel.send(data["next_stage_toast"])

    if message.content.startswith("$ans "):
        ans = message.content.split(" ")
        # check if the ans is of the correct format
        print(ans)
        if len(ans) == 2 and ans[0] == "$ans":
            # ans is of the correct format
            res = db.check_ans(str(message.author), ans[1])
            await message.channel.send(res)

    # if message.content.startswith("$ans"):

    #     ans_words = message.content.split(" ")
    #     answerid = users.get(str(message.author), 0)

    #     if answerid >= len(data["answers"]):
    #         await message.channel.send(data["next_stage_toast"])

    #     elif len(ans_words) != 2 or ans_words[0] != "$ans":
    #         await message.channel.send(data["wrong_format_toast"])

    #     else:
    #         if ans_words[1] == data["answers"][answerid]:
    #             users[str(message.author)] = users.get(str(message.author), 0) + 1
    #             with open("userdata.json", "w") as outfile:
    #                 json.dump(users, outfile)
    #             await message.channel.send(data["correct_answer_toast"])

    #             if answerid < len(data["answers"]) - 1:
    #                 await message.channel.send(data["next_clue_toast"])

    #             else:
    #                 await message.channel.send(data["next_stage_toast"])

    #         else:
    #             await message.channel.send(data["wrong_answer_toast"])


client.run(os.getenv("TOKEN"))
