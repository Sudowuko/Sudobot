import discord
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from discord.ext import commands
from discord.utils import get
# from discord_components import DiscordComponents, Button, Select, SelectOption, Component
# from discord_components import *

import logging

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

with open("config.json") as f:
    config = json.load(f)
    token = config["TOKEN"]
    project_id = config["PROJECT_ID"]

# Use the application default credentials
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
  'projectId': project_id,
})

db = firestore.client()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

sudo = commands.Bot(intents=intents, command_prefix='!')
ACount = 0
BCount = 0
CCount = 0

class Buttons(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    # Team A
    @discord.ui.button(label='Green', style=discord.ButtonStyle.green, custom_id='persistent_view:green')
    async def green(self, interaction: discord.Interaction, button: discord.ui.Button):
        ACount = ACount + 1
        await interaction.response.send_message(f'This is green. Count is {ACount}', ephemeral=True)

    # Team B
    @discord.ui.button(label='Red', style=discord.ButtonStyle.red, custom_id='persistent_view:red')
    async def red(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f'This is red. Count is {addCount(BCount)}', ephemeral=True)

    # Team C
    @discord.ui.button(label='Grey', style=discord.ButtonStyle.grey, custom_id='persistent_view:grey')
    async def grey(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f'This is grey. Count is {addCount(CCount)}', ephemeral=True)

def addCount(count):
    count += 1
    return count

@sudo.command()
async def buttons(ctx):
    print("user is: ", ctx.author)
    await ctx.send(f"Daily Habit Challenge\n Family August Competition\n Hello fam!!\n\n This is your daily reminder that it's time to log your habits!!\n",view=Buttons(ctx))

@sudo.event
async def on_ready():
    print("checking print statement!")
    print(discord.__version__)
    print("Logged in as a bot {0.user}".format(sudo))

# @sudo.command()
# async def setTeams(ctx, arg):
#     doc_ref = db.collection('teams').document("Team 1")
#     await ctx.send(f"{int(arg)} teams were made")

#Takes in user points based on specific reactions
@sudo.command()
async def react(ctx):
    count = 0
    def check(reaction, user):  # Our check for the reaction        
        return user == ctx.message.author  # We check that only the authors reaction counts

    await ctx.send("Please react to the message!")  # Message to react to

    reaction = await sudo.wait_for("reaction_add", check=check)  # Wait for a reaction
    count += 1
    await ctx.send(f"count increased by 1, it is currently {count} ")
    await ctx.send(f"You reacted with: {reaction[0]}")  # With [0] we only display the emoji

#adds user token amount
@sudo.command()
@commands.has_permissions(administrator=True)
async def addToken(ctx, arg):
    doc_ref = db.collection('users').document(str(ctx.author.id))
    tokens = doc_ref.get().get("tokens") + int(arg)
    doc_ref.set({
        'tokens': tokens,
    })
    await ctx.send(f"Added {int(arg)} tokens. {ctx.author} now has {tokens} tokens")

#sets user token amount
@sudo.command()
async def setToken(ctx, arg):
    doc_ref = db.collection('users').document(str(ctx.author.id))
    doc_ref.set({
        'tokens': int(arg),
    })
    tokens = doc_ref.get().get("tokens")

    await ctx.send(f"{ctx.author} tokens were set to {tokens} tokens")

#sets user quests count
@sudo.command()
async def setQuestCount(ctx, arg):
    doc_ref = db.collection('users').document(str(ctx.author.id))
    doc_ref.set({
        'quests': int(arg),
    })
    quests = doc_ref.get().get("quests")

    await ctx.send(f"{ctx.author} quests count is set to {quests}")

#sets user habit
@sudo.command()
async def setHabit(ctx, arg):
    doc_ref = db.collection('users').document(str(ctx.author.id))
    doc_ref.set({
        'habit': arg,
    })
    habit = doc_ref.get().get("habit")

    await ctx.send(f"{ctx.author} habit was set to {habit}")

#sets user monthly logs
@sudo.command()
async def setLogs(ctx, arg):
    doc_ref = db.collection('users').document(str(ctx.author.id))
    doc_ref.set({
        'mlogs': int(arg),
    })
    mlogs = doc_ref.get().get("mlogs")

    await ctx.send(f"Logs for the month set to {mlogs}")

#sets user team
@sudo.command()
async def setTeam(ctx, arg):
    doc_ref = db.collection('users').document(str(ctx.author.id))
    doc_ref.set({
        'team': arg,
    })
    team = doc_ref.get().get("team")

    await ctx.send(f"Team set to {team}")

#views user token amount
# should be able to view the following
# Tokens: 
# Quests: 
# Habit:
# Monthly Logs: 
# Team: 
@sudo.command()
async def viewToken(ctx, arg=None):
    user = ctx.author
    doc_ref = db.collection('users').document(str(user.id))
    print(db.collection('users'))
    print("doc_ref part 1: ", doc_ref.get("tokens"))
    print("doc_ref tokens: ", doc_ref.get().get("tokens"))
    tokens = doc_ref.get().get("tokens")
    print("tokens test")
    print("ctx is: ", ctx)
    await ctx.send(f"{user} currently has {tokens} tokens")
    # user = ctx.author
    # doc_ref = db.collection('users').document(str(ctx.author.id))
    # user = doc_ref.get()
    # tokens = doc_ref.get().get("tokens")
    # # quests = user.get("quests")
    # # habit = user.get("habit")
    # # mlogs = user.get("mlogs")
    # # team = user.get("team")
    # await ctx.send(f"tokens: {tokens}")
    #await ctx.send(f"User: {user} \n Habit: {habit} \n Tokens: {tokens} \n Monthly Logs: {mlogs} \n Quests: {quests} \n Team: {team}") 

@sudo.command()
async def checkUsername(ctx):
    doc_ref = db.collection('users').document(str(ctx.author.id))
    username = doc_ref.get().get("username")
    print("ctx is: ", ctx)
    await ctx.send(f"Username is {username}")

@sudo.command()
async def listusers(ctx):
    users = ctx.guild.members
    await ctx.send(f"{[str(i) for i in users]}")


def user_search(guild, userkey):
    """user_search searches for a user in a guild by username#discriminator, username, or user_id"""
    users = guild.members
    results = []
    for i in users:
        if i.name == userkey:
            results.append(i)
            continue
        if i.id == userkey:
            results.append(i)
            continue
        if str(i) == userkey:
            results.append(i)
            continue
    return results

#mass updates user tokens by taking in an import list 
@sudo.command()
@commands.has_permissions(administrator=True)
async def importtokens(ctx):
    message = ctx.message.content
    errors = []
    message_list = message.split("\n")[1:]
    users = {}
    for i, row in enumerate(message_list):
        columns = row.rsplit(maxsplit=1)
        if len(columns) != 2:
            errors.append(f"could not parse row {i+1}, must have 1 username and 1 token value per row")
        username = columns[0]
        try:
            tokens = int(columns[1])
        except ValueError:
            errors.append(f"{username} is ambiguous on row {i+1}")
        usermatch = user_search(ctx.guild, username)
        if len(usermatch) > 1:
            errors.append(f"{username} is ambiguous on row {i+1}")
            continue
        elif len(usermatch) == 0:
            errors.append(f"{username} not found on row {i+1}")
            continue
        else:
            user = usermatch[0]
            users[str(user.id)] = tokens
    if len(errors) > 0:
        await ctx.send(f"Error(s) parsing import command: {errors}")
    batch = db.batch()
    for i, v in users.items():
        doc_ref = db.collection('users').document(i)
        batch.set(doc_ref, {"tokens": v}, merge=True)
    batch.commit()
    await ctx.send("Updated user tokens")

# Creates a list of all the users with their token value
@sudo.command()
@commands.has_permissions(administrator=True)
async def listtokens(ctx):
    members = ctx.guild.members
    tokens_table = [("Name", "Tokens")]
    for i in members:
        if i.bot:
            continue
        doc_ref = db.collection('users').document(str(i.id))
        user = doc_ref.get()
        if user.exists:
            token = user.get('tokens')
        else:
            token = 0
        tokens_table.append((str(i), token))
    tokens_table[1:] = sorted(tokens_table[1:], key=lambda x: x[1], reverse=True)
    message = [f"{name:<30}{tokens:<10}" for name, tokens in tokens_table]
    await ctx.send("```" + "\n".join(message) + "```")

sudo.run(token, log_handler=handler)
