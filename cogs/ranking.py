from requests_html import HTMLSession
import json
import requests
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import aiosqlite
from table2ascii import table2ascii as t2a, PresetStyle

def get_cc_rank(name):
    url = "https://codechef.com/users/{}".format(name)
    session = HTMLSession()
    r = session.get(url,timeout=10)
    data=dict()
    if r.status_code!=200:
        data['status']='failed'
        return data
    try:
        rating_header = r.html.find(".rating-header",first=True)
    except:
        data['status']='failed'
        return data

    try:
        rating = rating_header.find(".rating-number",first=True).text
    except:
        data['status']='failed'
        return data

    data['status']='OK'
    data['rating']=rating.split('?')[0]

    return data

def get_cf_rank(name):
    url = 'https://codeforces.com/api/user.info?handles={}'.format(name)
    r = requests.get(url,timeout=20)
    data  = dict()
    if r.status_code !=200:
        data['status']='failed1'
        return data
    r_data = r.json()
    # print(r_data,r)
    if r_data['status']!='OK':
        data['status']='failed2'
        return data
    data['status'] = 'OK'
    if 'rating' in r_data['result'][0]:
        data['rating']=r_data['result'][0]['rating']
    else:
        data['rating']=0
    return data
class Ranking(commands.Cog):

    def __init__(self,bot):
        self.bot= bot
        self.is_running=False

    @commands.Cog.listener()
    async def on_ready(self):
        self.db=await aiosqlite.connect("profs.db")
        print('Ranking cog loaded')
    
    def close(self):
        self.db.close()
    
    def cog_unload(self):
        self.close()
    
    async def update_ranks(self,data,val):
        if self.is_running==True:
            return
        self.is_running=True
        try:
            new_data=[]
            for i in data:

                if val=='cc':
                    r_data=get_cc_rank(i[1])
                    user = await self.bot.fetch_user(i[0])
                else:
                    r_data=get_cf_rank(i[1])
                    user = await self.bot.fetch_user(i[0])
                    
                if r_data['status']=='OK':
                    new_data.append((i[0],int(r_data['rating']),user.name))
                
            async with self.db.cursor() as cursor:
                for i in new_data:
                    await cursor.execute(f"UPDATE prof SET {val}rank={i[1]},uname=(?) WHERE id={i[0]}",(i[2],))
            await self.db.commit()
            print("updated")
        finally:
            self.is_running=False
        
    @app_commands.command(name='rank',description='Get your ranking in the Code Together Community.')
    @app_commands.describe(option='Options to choose from')
    @app_commands.choices(option=[
        discord.app_commands.Choice(name='CodeChef',value='cc'),
        discord.app_commands.Choice(name='CodeForces',value='cf'),
        discord.app_commands.Choice(name='POTD',value='p'),
        discord.app_commands.Choice(name='Duels',value='d'),
    ])
    async def rank(self,itr: discord.Interaction,option: discord.app_commands.Choice[str]):
        await itr.response.defer()
        async with self.db.cursor() as cursor:
            if option.value in ['cc','cf']:
                text=""

                await cursor.execute(f"SELECT uname,{option.value},{option.value}rank,id FROM prof WHERE {option.value} IS NOT NULL ORDER BY {option.value}rank DESC")
                data=await cursor.fetchall()
                # print(data)

                if len(data)>0:
                    out_data=[]
                    # if option.value=='cc':
                    #     pr_url="https://www.codechef.com/users/"
                    # else:
                    #     pr_url="https://codeforces.com/profile/"
                    for i,x in enumerate(data):
                        # if i==0:
                        #     text+=f"**:star: {x[0]}** -- [**{x[2]}**]({pr_url+x[1]}) \n"
                        # else:
                        #     text+=f"{i+1}. **{x[0]}** -- [**{x[2]}**]({pr_url+x[1]}) \n"
                        out_data.append([i+1,x[0],x[2]])
                    output=t2a(
                        header=["Rank","User","Rating"],body=out_data,first_col_heading=True
                    )
                    
                    embed=discord.Embed(title=f"**__{option.name} Rank List:__**",description=f"```\n{output}\n```",color=discord.Colour.green())
                    embed.set_footer(text = "Can't find yourself? Try /register")
                else:
                    embed=discord.Embed(title=f" *Cricket Noises..* **No registered id. Try /register**",color=discord.Colour.red())
                await itr.followup.send(embed=embed)
                
                await cursor.execute(f"SELECT id,{option.value} FROM prof WHERE {option.value} IS NOT NULL")
                data=await cursor.fetchall()
                await self.update_ranks(data,option.value)
            elif option.value=='p':
                await cursor.execute(f"SELECT ps,uname FROM prof WHERE ps>0 ORDER BY ps DESC")
                data=await cursor.fetchall()
                print(data)
                text=""

                if len(data)>0:
                    out_data=[]
                    for i,x in enumerate(data):
                        # user = await self.bot.fetch_user(int(x[0]))
                        # if i==0:
                        #     text+=f"**:star: {x[1]}** ( Solved -- **{x[0]}** )\n"
                        # else:
                        #     text+=f"{i+1}. **{x[1]}** ( Solved -- **{x[0]}** )\n"
                        out_data.append([i+1,x[1],x[0]])
                    output=t2a(
                        header=["Rank","User","Solved"],body=out_data,first_col_heading=True
                    )
                    
                    embed=discord.Embed(title=f"**__{option.name} solved Rank List:__**",description=f"```\n{output}\n```",color=discord.Colour.green())
                else:
                    embed=discord.Embed(title="*Cricket Noises..* **No POTD Streaks!**",color=discord.Colour.red())
                embed.set_footer(text = "Can't find yourself? Try /register Codeforces_id")
                await itr.followup.send(embed=embed)
            elif option.value=='d':
                await cursor.execute(f"SELECT dw,uname FROM prof WHERE dw>0 ORDER BY dw DESC")
                data=await cursor.fetchall()
                print(data)
                text=""

                if len(data)>0:
                    out_data=[]
                    for i,x in enumerate(data):
                        # if i==0:
                        #     text+=f"**:star: {x[1]}** ( Duels won -- **{x[0]}** )\n"
                        # else:
                        #     text+=f"{i+1}. **{x[1]}** ( Duels won -- **{x[0]}** )\n"
                        out_data.append([i+1,x[1],x[0]])
                    output=t2a(
                        header=["Rank","User","Duels-Won"],body=out_data,first_col_heading=True
                    )
                    embed=discord.Embed(title=f"**__{option.name} won Rank List:__**",description=f"```\n{output}\n```",color=discord.Colour.green())
                else:
                    embed=discord.Embed(title="*Cricket Noises..* **No Data!**",color=discord.Colour.red())
                embed.set_footer(text = "Can't find yourself? Try /register Codeforces_id")
                await itr.followup.send(embed=embed)


    # @app_commands.command(name='register',description='Register yourself with your cp profile to get ranking in the Code Together Community.')
    # @app_commands.describe(option='Options to choose from')
    # @app_commands.choices(option=[
    #     discord.app_commands.Choice(name='CodeChef',value='cc'),
    #     discord.app_commands.Choice(name='CodeForces',value='cf'),
    # ])
    # async def register(self,itr: discord.Interaction,option: discord.app_commands.Choice[str],user_id:str):
    #     await itr.response.defer(ephemeral=True)

    #     async with self.db.cursor() as cursor:
    #         await cursor.execute(f'SELECT * FROM prof WHERE id={int(itr.user.id)}')
    #         data= await cursor.fetchone()

    #         if option.value=='cc':
    #             r_data=get_cc_rank(user_id)
    #             if r_data['status']=='OK':
    #                 val=r_data['rating']
    #             else:
    #                 val=0
    #         else:
    #             r_data=get_cf_rank(user_id)
    #             if r_data['status']=='OK':
    #                 val=r_data['rating']
    #             else:
    #                 val=0

    #         if data is None:

    #             if option.value=='cc':
    #                 await cursor.execute("INSERT INTO prof(id,cc,ccrank,uname) VALUES(?,?,?,?)",(itr.user.id,user_id,val,itr.user.name))
    #             else:
    #                 await cursor.execute("INSERT INTO prof(id,cf,cfrank,uname) VALUES(?,?,?,?)",(itr.user.id,user_id,val,itr.user.name))
    #         else:
    #             if option.value=='cc':
    #                 await cursor.execute("UPDATE prof SET cc=(?),ccrank=(?) WHERE id=(?)",(user_id,val,itr.user.id))
    #             else:
    #                 await cursor.execute("UPDATE prof SET cf=(?),cfrank=(?) WHERE id=(?)",(user_id,val,itr.user.id))

    #     await self.db.commit()
    #     await itr.followup.send("Registered.")

    
async def setup(bot):
    await bot.add_cog(Ranking(bot))

