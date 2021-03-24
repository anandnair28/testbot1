import discord
import os
import json
# import  "./database"
import database.database as db

client = discord.Client()

data_file = open('data.json')
data = json.load(data_file)

userdata_file = open('userdata.json')
users = json.load(userdata_file)
userdata_file.close()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        intro_text = data["intro"].format(str(message.author))
        await message.channel.send(intro_text)
        await message.channel.send(file=discord.File('thtest.png'))

    if message.content.startswith('$items'):
        db.hello_world()
        # conn = database.init_db()
        # items = conn.execute("SELECT id, name, age from USER")
        # for row in items:
        #     print("Id= ", row[0])
        #     print("name= ", row[1])
        #     print("age= ", row[2])

        print("Operations done successfully")
        await message.channel.send("done")
    

    if message.content.startswith('$clue'):
        
        clueid = users.get(str(message.author), 0)
        
        if clueid < 3:
          await message.channel.send(data["clues"][clueid])
        
        else:
          await message.channel.send(data["next_stage_toast"])
    
    if message.content.startswith('$ans'):
        
        ans_words = message.content.split(' ')
        answerid = users.get(str(message.author), 0)

        if answerid >= len(data["answers"]):
            await message.channel.send(data["next_stage_toast"])
        
        elif len(ans_words) != 2 or ans_words[0] != "$ans":
            await message.channel.send(data["wrong_format_toast"])
          
        else:
            if ans_words[1] == data["answers"][answerid]:
                users[str(message.author)] = users.get(str(message.author), 0) + 1
                with open("userdata.json", "w") as outfile:
                    json.dump(users, outfile)
                await message.channel.send(data["correct_answer_toast"])
            
                if answerid < len(data["answers"]) - 1:
                    await message.channel.send(data["next_clue_toast"])
            
                else:
                    await message.channel.send(data["next_stage_toast"])
          
            else:
                await message.channel.send(data["wrong_answer_toast"])

client.run(os.getenv('TOKEN'))