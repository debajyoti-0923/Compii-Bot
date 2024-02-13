from requests_html import HTMLSession
import json
import requests
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import aiosqlite
from table2ascii import table2ascii as t2a, PresetStyle
from random import choice
from datetime import datetime
from time import time
qs=[4,71,231,158,50,282,263,112,339,281,236,266,791,546,617,56,977,110,734,116]

cat_id=None

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

async def create_channel(ctx):
    global cat_id
    category_name="✅_verification"
    category = discord.utils.get(ctx.guild.categories, name=category_name)
    if category is None:
        category = await ctx.guild.create_category(category_name)
        
    if cat_id is None:
        cat_id=category.id

    channel_name = f"Register #{ctx.user.name}"
    channel = await ctx.guild.create_text_channel(channel_name,category=category)

    overwrite = discord.PermissionOverwrite()
    overwrite.read_messages = True
    overwrite.send_messages = True

    await channel.set_permissions(ctx.user, overwrite=overwrite)

    return channel

async def verify(ctx,use,cf):
    ct=time()
    global qs
    k=choice(qs)

    text=f"""Hello <@!{use.user.id}> welcome to Code Together Community!
This is a simple verification process to ensure the **IDs** you provide is indeed yours.
Follow through the following steps-"""
    await ctx.send(text)
    await ctx.send(f"1. **Open** this link ➡️ **<https://codeforces.com/problemset/problem/{k}/A>**")

    text='2. **Solve** the problem _OR_ **Download** and **Submit** this File in the codeforces link.'
    await ctx.send(text)

    #send file
    with open(f"veref.txt",'rb') as f:
        await ctx.send(file=discord.File(f))
    
    await ctx.send("**That's it! Thank You!**")

    sent=await ctx.send("Waiting for verification...")
    c=0
    while(1):
        c+=2
        #chk
        url=f'https://codeforces.com/api/user.status?handle={cf}&from=1&count=1'
        r=requests.get(url,timeout=10)
        
        if r.status_code!=200:
            continue

        r_data=r.json()
        if r_data['status']!='OK':
            continue
        else:
            st=r_data['result'][0]['creationTimeSeconds']
            r_data=r_data['result'][0]['problem']
        # print(ct,st)
        if r_data['contestId']==k and r_data['index']=='A' and st>ct:
            await sent.delete()
            await ctx.send("✅Verified!")
            await asyncio.sleep(5)
            await ctx.delete()
            return True
        
        if c==150:
            await ctx.send("Verification Failed! Try agian later.")
            await asyncio.sleep(5)
            await ctx.delete()
            return False
        # print(c)
        await asyncio.sleep(2)

class Register(commands.Cog):

    def __init__(self,bot):
        self.bot= bot
        self.is_running=False

    @commands.Cog.listener()
    async def on_ready(self):
        self.db=await aiosqlite.connect("profs.db")
        print('Register cog loaded')
    
    def close(self):
        self.db.close()
    
    def cog_unload(self):
        self.close()
    

    @app_commands.command(name='register',description='Register yourself with your cp profile to get ranking in the Code Together Community.')
    @app_commands.describe(option='Options to choose from')
    @app_commands.choices(option=[
        discord.app_commands.Choice(name='CodeChef',value='cc'),
        discord.app_commands.Choice(name='CodeForces',value='cf'),
    ])
    async def register(self,itr: discord.Interaction,option: discord.app_commands.Choice[str],user_id:str):
        await itr.response.defer(ephemeral=True)

        async with self.db.cursor() as cursor:
            await cursor.execute(f'SELECT * FROM prof WHERE id={int(itr.user.id)}')
            data= await cursor.fetchone()

            if option.value=='cc':
                r_data=get_cc_rank(user_id)
                if r_data['status']=='OK':
                    val=r_data['rating']
                else:
                    val=0
            else:
                chnl=await create_channel(itr)
                text=f"Follow the instructions in ➡️{chnl.mention}"
                await itr.followup.send(embed=discord.Embed(title=text,color=discord.Color.gold()))
                verified=await verify(chnl,itr,user_id)
                if verified==False:
                    msg=await itr.original_response()
                    await msg.edit(embed=discord.Embed(title="Verification Failed! Not registered.",color=discord.Color.red()))
                    return
                
                r_data=get_cf_rank(user_id)
                if r_data['status']=='OK':
                    val=r_data['rating']
                else:
                    val=0

            if data is None:

                if option.value=='cc':
                    await cursor.execute("INSERT INTO prof(id,cc,ccrank,uname) VALUES(?,?,?,?)",(itr.user.id,user_id,val,itr.user.name))
                else:
                    await cursor.execute("INSERT INTO prof(id,cf,cfrank,uname) VALUES(?,?,?,?)",(itr.user.id,user_id,val,itr.user.name))
            else:
                if option.value=='cc':
                    await cursor.execute("UPDATE prof SET cc=(?),ccrank=(?) WHERE id=(?)",(user_id,val,itr.user.id))
                else:
                    await cursor.execute("UPDATE prof SET cf=(?),cfrank=(?) WHERE id=(?)",(user_id,val,itr.user.id))

        await self.db.commit()
        # await itr.followup.send("Registered.")
        msg=await itr.original_response()
        await msg.edit(embed=discord.Embed(title="Registered!",color=discord.Color.green()))

    
async def setup(bot):
    await bot.add_cog(Register(bot))

