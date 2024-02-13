import requests
import discord
from discord.ext import commands
from discord import app_commands

class Contest(commands.Cog):

    def __init__(self,bot):
        self.bot= bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('contest cog loaded')
    

    @app_commands.command(name='contest',description='List of upcoming contests.')
    @app_commands.describe(platform='Platforms to choose from')
    @app_commands.choices(platform=[
        discord.app_commands.Choice(name='CodeForces',value=0),
        discord.app_commands.Choice(name='CodeChef',value=1),
        discord.app_commands.Choice(name='LeetCode',value=2),
    ])
    async def contest(self,interaction: discord.Interaction, platform: discord.app_commands.Choice[int]):
        await interaction.response.defer()
        if platform.value==0:
            plat='codeforces'
        elif platform.value==1:
            plat='code_chef'
        elif platform.value==2:
            plat='leet_code'
        try:
            response=requests.get(f'https://kontests.net/api/v1/{plat}')
            data=response.json()
            embedList=[]
            for i in data:
                dt=i['start_time'].split()[0] if platform.value==1 else i['start_time'].split('T')[0]
                embed=discord.Embed(title=i['name'],description=f"**Date: **{dt}\n**Url: **<{i['url']}>",color=discord.Colour.green())
                embedList.append(embed)
                if(len(embedList)==10):
                    await interaction.followup.send(embeds=embedList)
                    embedList=[]
                    break
            else:
                await interaction.followup.send(embeds=embedList)
                embedList=[]
        except:
            embed=discord.Embed(description="No data found!",color=discord.Colour.red())
            await interaction.followup.send(embed=embed)
    
async def setup(bot):
    await bot.add_cog(Contest(bot))

