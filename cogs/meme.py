import discord
from discord.ext import commands
from discord import app_commands
import asyncpraw
from random import choice

reddit=asyncpraw.Reddit(
    client_id="5vYkpjajVjLiX6bZyAESaw",
    client_secret="6DnE_unUolcXG-Dh7XrkdCMyWgiHcw",
    username="No-Impression9089",
    password="EAH.YnRU2A33cvw",
    user_agent="memer"
)

class Meme_(commands.Cog):

    def __init__(self,bot):
        self.bot= bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('memer cog loaded')

    @app_commands.command(name='meme',description='What do you think it does?')
    async def meme(self,itr: discord.Interaction):
        await itr.response.defer()
        subr=await reddit.subreddit("programming_memes+coding_memes+program_memes")

        subs=[]
        async for i in subr.hot():
            if i.url[-3:] in ['gif','png','jpg','jpeg']:
                subs.append(i)
    
        k=choice(subs)
        embed=discord.Embed(title=f"{k.title}",color=discord.Color(int("36393F",16)))
        embed.set_image(url=k.url)
        embed.set_footer(text="Here's a freshly brewed")
        await itr.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Meme_(bot))