import discord
import os
import random
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
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

client = discord.Client()

client = commands.Bot(command_prefix='!')

@client.event
async def on_ready():
    print("Logged in as a bot {0.user}".format(client))

@client.command()
async def setToken(message, arg):
    doc_ref = db.collection('users').document(str(message.author.id))
    doc_ref.set({
        'tokens': int(arg),
    })
    doc = doc_ref.get()
    await message.send(f"{message.author} has {doc.to_dict()}")

@client.command()
async def addToken(message, arg):
    doc_ref = db.collection('users').document(str(message.author.id))
    doc = doc_ref.get()

    await message.send(f"{message.author} had {doc.to_dict()}")
    tokens = doc_ref.get().get("tokens")
    doc_ref.set({
        'tokens': tokens + int(arg),
    })
    doc = doc_ref.get()
    await message.send(f"{message.author} now has {doc.to_dict()}")

@client.command()
async def viewToken(message):
    doc_ref = db.collection('users').document(str(message.author.id))
    doc = doc_ref.get()
    await message.send(f"{message.author} has {doc.to_dict()}")

    
client.run(token)