import discord
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import time
from discord.ext import commands
import logging

# TODO
# Organize main.py into multiple files (Some of these commands don't exist yet)
# File 1: Tokens (View, set, add, remove)
# File 2: Shop commands (Shop list, can buy, select items, purchase)
# File 3: Automated (Daily messages, count score, rule check)
# File 4: Admin (Set teams, set users, set habits)

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
#sudoTasks = tasks.Bot(intents=intents, command_prefix='=')
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
    await ctx.send("Daily Habit Challenge\n Family August Competition\n Hello fam!!\n\n This is your daily reminder that it's time to log your habits!!\n",view=Buttons(ctx))

@sudo.event
async def on_ready():
    print("checking print statement!")
    print(discord.__version__)
    print("Logged in as a bot {0.user}".format(sudo))

@sudo.command()
async def setTeam(ctx, arg):
    doc_ref = db.collection('teams').document("Team 1")
    doc_ref.set({
        'team name': arg,
        'points: ': 0,
        'members' : "",
    })
    await ctx.send(f"team {arg} was successfully made")

#sets each person's username, team name, tokens, and habits are set
@sudo.command()
async def setUser(ctx):
    doc_ref = db.collection('teams').document("Team 1")
    doc_ref.set({
        'user': ctx.author,
        'team': "",
        'tokens': doc_ref.get().get("tokens"),
        'habit': "",
    })
    await ctx.send(f"user, ")

@sudo.command()
async def dailyMessage(ctx):
    n = 0
    while (n < 5):
        await ctx.send("this message repeats every 5 seconds")
        n += 1
        time.sleep(5)



#sets user token amount
@sudo.command()
async def setToken(ctx, arg):
    doc_ref = db.collection('users').document(str(ctx.author.id))
    doc_ref.set({
        'tokens': int(arg),
    })
    tokens = doc_ref.get().get("tokens")

    await ctx.send(f"{ctx.author} tokens were set to {tokens} tokens")

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

#views user token amount
@sudo.command()
async def viewToken(ctx, arg=None):
    user = ctx.author
    doc_ref = db.collection('users').document(str(user.id))
    tokens = doc_ref.get().get("tokens")
    print("ctx is: ", ctx)
    await ctx.send(f"{user} currently has {tokens} tokens")

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
