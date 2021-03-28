import discord
import os
import json

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

    if message.content.startswith('$cluetest'):
        
        clueid = users.get(str(message.author), 0)
        
        if clueid < 3:
          cluestring = data["clues"][clueid]
          for element in cluestring.split('||'):
            if element.startswith('images/'):
              await message.channel.send(file=discord.File(element))
            elif element.startswith('files/'):
              await message.channel.send(file=discord.File(element))
            else:
              await message.channel.send(element)
        
        else:
          await message.channel.send(data["next_stage_toast"])
    
    if message.content.startswith('$anstest'):
        
        ans_words = message.content.split(' ')
        answerid = users.get(str(message.author), 0)

        if answerid >= len(data["answers"]):
            await message.channel.send(data["next_stage_toast"])
        
        elif len(ans_words) != 2 or ans_words[0] != "$anstest":
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