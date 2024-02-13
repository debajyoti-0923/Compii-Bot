import discord
from discord.ext import commands
from discord import app_commands
import json


class potd_(commands.Cog):

    def __init__(self,bot):
        self.bot= bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('potd cog loaded')
    
        
    @app_commands.command(name='potd',description='Problem of the day.')
    async def potd(self,itr: discord.Interaction):
        await itr.response.defer()
        with open('./cogs/potds.json', 'r') as f:
            data = json.load(f)
        if data['active']=="":
            text="No active POTD!"
            embed=discord.Embed(description=text,color=discord.Colour.red())
        else:
            text=data['active']
            embed=discord.Embed(description=f"__**Today's POTD**__ -- <{text}>",color=discord.Colour.blue())
        await itr.followup.send(embed=embed)            

async def setup(bot):
    await bot.add_cog(potd_(bot))