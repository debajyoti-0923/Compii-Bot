from requests_html import HTMLSession
import json
import requests
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from discord.ui import Button,View
import aiosqlite
from bs4 import BeautifulSoup as bs

tval={
    "600":10,
    "800":15,
    "1000":20,
    "1200":30,
    "1200+":50
}
cat_id=None
dps={}

async def get_dif(cid,pid):
    URL = f"https://codeforces.com/contest/{cid}/problem/{pid}"
    r = requests.get(URL)
    s=bs(r.content,'html5lib')
    dif=str(s.find('span',attrs = {'title':'Difficulty'})).split('\n')
    return int(dif[1].strip()[1:])


async def chk_sub(p1,p2,pid,cid):
    
    sol=[0,0]
    url=f'https://codeforces.com/api/user.status?handle={p1}&from=1&count=3'
    r=requests.get(url,timeout=10)
    if r.status_code!=200:
        pass
    else:
        r_data=r.json()
        if r_data['status']!='OK':
            pass
        else:
            r_data=r_data['result']
            for k in r_data:
                c_id=k['problem']['contestId']
                ind=k['problem']['index']
                v=k['verdict']
                if c_id==pid[0] and ind==pid[1] and v=='OK':
                    sol[0]=int(k['creationTimeSeconds'])
                    break


    url=f'https://codeforces.com/api/user.status?handle={p2}&from=1&count=3'
    r=requests.get(url,timeout=10)
    if r.status_code!=200:
        pass
    else:
        r_data=r.json()
        if r_data['status']!='OK':
            pass
        else:
            r_data=r_data['result']
            for k in r_data:
                c_id=k['problem']['contestId']
                ind=k['problem']['index']
                v=k['verdict']
                if c_id==cid[0] and ind==cid[1] and v=='OK':
                    sol[1]=int(k['creationTimeSeconds'])
                    break

    return sol
async def handle_duel(ctx,channel,op,maxr,og,uids):
    # print(type(uids),uids)
    text=f"**Welcome <@!{ctx.user.id}> and <@!{op.id}> to a CP Duel  ⚔️!**"
    await channel.send(text)
    text=f"\n**__Instructions ( How to play? ):__**\n**1.**You have to **post** a codeforces question **link** which you will give to your opponent in this channel.\n**2.**Wait till your opponent posts a question.\n**3.**Then enter **/show** to reveal your cp problem and **/surrender** to leave the challenge .\n**4.**Solve the codeforces link within the time limit to win.\n**5.**First to solve will be the winner !"
    await channel.send(text)
    
    dps[channel.id]=[0,0,ctx.user.id,op.id,'','',maxr,[],[],0]

    text=f"**Waiting for players to submit questions.** The question must have a **Max difficulty of `{maxr}`** 🕓\n🔴{ctx.user.name} -- {'🚫' if dps[channel.id][0]==0 else '✅'}\n🔵{op.name} -- {'🚫' if dps[channel.id][1]==0 else '✅'}"
    k=await channel.send(text)
    c=0
    while 1:
        text=f"**Waiting for players to submit questions.** The question must have a **Max difficulty of `{maxr}`....** 🕓\n🔴{ctx.user.name} -- {'🚫' if dps[channel.id][0]==0 else '✅'}\n🔵{op.name} -- {'🚫' if dps[channel.id][1]==0 else '✅'}"
        await k.edit(content=text)
        await asyncio.sleep(1)
        if dps[channel.id][0]==0 or dps[channel.id][1]==0:
            pass
        else:
            break
        c+=1

        if c==120:
            text="**Questions were not submitted! This channel will close...**"
            await k.edit(content=text)
            ov=discord.PermissionOverwrite(send_messages=False)
            await channel.set_permissions(ctx.user, overwrite=ov)
            await channel.set_permissions(op, overwrite=ov)
            await asyncio.sleep(5)
            await channel.delete()
            msg=await og.original_response()
            await msg.delete()
            return 0

    await k.delete()
    text=f"**🔰 Both players submitted the questions 🔰**\n\nTimer has **started ⌛...**\n When you are ready, Enter **/show to see your question.**"
    sent=await channel.send(text)
    t=tval[maxr]
    text=f"<@!{ctx.user.id}> <@!{op.id}> **Duel ends in -- {t} minutes!**"
    msg=await channel.send(text)
    w=0
    for i in range(t):
        text=f"<@!{ctx.user.id}> <@!{op.id}> **Duel ends in -- {t-i} minutes!**"
        await msg.edit(content=text)
        for j in range(3):
            if dps[channel.id][9]!=0:
                if dps[channel.id][9]==1:
                    w=2
                else :
                    w=1
                break
            z=await chk_sub(uids[0][0],uids[1][0],dps[channel.id][8],dps[channel.id][7]) 
            if z[0]==0 and z[1]==0:
                pass
            elif z[0]==0:
                w=2
                break
            elif z[1]==0:
                w=1
                break
            else:
                w=2 if z[0]>z[1] else 1
                break
            await asyncio.sleep(20)
        if w!=0:
            break            
    
    await msg.delete()
    msg=await og.original_response()
    await msg.delete()
    await sent.delete()

    if w==0:
        text=f"**This Duel ended in a Tie! Since Noone could submit in time ! ⌛** "
    elif w==1:
        if dps[channel.id][9]!=0:
            text=f"**<@!{op.id}> surrendered! \n<@!{ctx.user.id}> Won the Duel !🏆**"
        else:
            text=f"**<@!{ctx.user.id}> just solved the problem. 🙌🏼 \n<@!{ctx.user.id}> Won the Duel !🏆**"
        await og.channel.send(f"**🏆 <@!{ctx.user.id}> Won a Duel against <@!{op.id}> !**")
    else:
        if dps[channel.id][9]!=0:
            text=f"**<@!{ctx.user.id}> surrendered! \n<@!{op.id}> Won the Duel !🏆**"
        else:
            text=f"**<@!{op.id}> just solved the problem. 🙌🏼 \n<@!{op.id}> Won the Duel !🏆**"
        await og.channel.send(f"**🏆 <@!{op.id}> Won a Duel against <@!{ctx.user.id}> !**")
    await channel.send(text)
    await channel.send("**This channel will close. See Ya in another Duel ! Keep Coding.. ✌🏼** ")

    await asyncio.sleep(20)
    await channel.delete()   
    dps.pop(channel.id)
    return w


async def create_channel(ctx,x):
    global cat_id
    category_name="🎯_duels"
    category = discord.utils.get(ctx.guild.categories, name=category_name)
    if category is None:
        category = await ctx.guild.create_category(category_name)
        
    if cat_id is None:
        cat_id=category.id

    channel_name = f"CP Duel #{ctx.user.name}"
    channel = await ctx.guild.create_text_channel(channel_name,category=category)

    overwrite = discord.PermissionOverwrite()
    overwrite.read_messages = True
    overwrite.send_messages = True

    await channel.set_permissions(ctx.user, overwrite=overwrite)
    await channel.set_permissions(x, overwrite=overwrite)

    return channel
    

class Duel(commands.Cog):
    def __init__(self,bot):
        self.bot= bot
        self.duel_channels=[]
        
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.db=await aiosqlite.connect("profs.db")
        print('duel cog loaded')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.category_id == cat_id:
            if message.author.bot:
                pass
            else:
                new_msg=message
                await message.delete()
                
                qs=str(new_msg.content).split('/')

                if ((qs[-1] in ['A','B','C','D','E','F','G','H'] )and qs[-3].isnumeric() and qs[-5]=="codeforces.com")==False:
                    k=await new_msg.channel.send(f"<@!{new_msg.author.id}> This link is **not valid**! Give a **valid codeforces link**. E.g. - <https://codeforces.com/contest/1095/problem/A>")
                    await asyncio.sleep(10)
                    await k.delete()
                    return
                else:
                    r=await get_dif(int(qs[-3]),qs[-1])
                    rr=dps[new_msg.channel.id][6]
                    if rr=="1200+":
                        rr=5000
                    else:
                        rr=int(rr)
                if r>rr:
                    k=await new_msg.channel.send(f"<@!{new_msg.author.id}> Question difficulty is too **high**! Max difficulty must be <{rr} you gave {r}")  
                    await asyncio.sleep(10)
                    await k.delete()
                    return
    
                if new_msg.author.id==dps[new_msg.channel.id][2]:
                    dps[new_msg.channel.id][0]=1            
                    dps[new_msg.channel.id][4]=new_msg.content            
                    dps[new_msg.channel.id][7]=[int(qs[-3]),qs[-1]]
                elif new_msg.author.id==dps[new_msg.channel.id][3]:
                    dps[new_msg.channel.id][1]=1
                    dps[new_msg.channel.id][5]=new_msg.content 
                    dps[new_msg.channel.id][8]=[int(qs[-3]),qs[-1]]

                k=await new_msg.channel.send(f"<@!{new_msg.author.id}> Submitted the Question ! ☑️")   
                await asyncio.sleep(10)
                await k.delete()


                
    @app_commands.command(name='show',description='Command in a Duel. Try /challenge')
    async def show(self,itr:discord.Interaction):
        await itr.response.defer(ephemeral=True)
        if itr.channel.category_id==cat_id:
            data=dps[itr.channel_id]
            if itr.user.id==data[2]:
                text=f"**Your question -- {data[5]}**"
            elif itr.user.id==data[3]:
                text=f"**Your question -- {data[4]}**"
            await itr.followup.send(text)
        else:
            await itr.followup.send("You must be in a Duel to use this command!")
    
    @app_commands.command(name='end',description='Command in a Duel. Try /challenge')
    async def surrender(self,itr:discord.Interaction):
        await itr.response.defer(ephemeral=True)
        if itr.channel.category_id==cat_id:
            data=dps[itr.channel_id]
            if itr.user.id==data[2]:
                dps[itr.channel_id][9]=1
            elif itr.user.id==data[3]:
                dps[itr.channel_id][9]=2
            await itr.followup.send("You surrendered !")
        else:
            await itr.followup.send("You must be in a Duel to use this command!")

    async def update_score(self,res,p1,p2):
        async with self.db.cursor() as cursor:
            if res==1:
                await cursor.execute(f'SELECT dw FROM prof WHERE id={p1}')
                id=p1
            else:
                await cursor.execute(f'SELECT dw FROM prof WHERE id={p2}')
                id=p2
            data= await cursor.fetchone()
            await cursor.execute(f"UPDATE prof SET dw={data[0]+1} WHERE id={id}")
        await self.db.commit()


    @app_commands.command(name='challenge',description='Challenge your friend in a CP Duel !')
    @app_commands.describe(max_difficulty='Maximum difficulty of problem')
    @app_commands.choices(max_difficulty=[
        discord.app_commands.Choice(name='600',value="600"),
        discord.app_commands.Choice(name='800',value="800"),
        discord.app_commands.Choice(name='1000',value="1000"),
        discord.app_commands.Choice(name='1200',value="1200"),
        discord.app_commands.Choice(name='1200+',value="1200+"),
    ])
    async def challenge(self,itr: discord.Interaction,opponent_user:discord.User,max_difficulty: discord.app_commands.Choice[str]):
        await itr.response.defer()
        if opponent_user.id==itr.user.id:
            text=f"⛔ You can't challenge yourself ! Challenge other friend. "
            embed=discord.Embed(title="Uhm! That's awkward..",description=text,colour=discord.Colour.red())
            await itr.followup.send(embed=embed)
            return
        if opponent_user.bot:
            text=f"⛔ You can't challenge a BOT for a Duel! Challenge other friend."
            embed=discord.Embed(title="Uhm! That's awkward..",description=text,colour=discord.Colour.red())
            await itr.followup.send(embed=embed)
            return
        data=[]
        async with self.db.cursor() as cursor:
            await cursor.execute(f'SELECT cf FROM prof WHERE cf IS NOT NULL AND id={itr.user.id}')
            data.append( await cursor.fetchone())
            await cursor.execute(f'SELECT cf FROM prof WHERE cf IS NOT NULL AND id={opponent_user.id}')
            data.append( await cursor.fetchone())
        print(data)
        if data[0] is None:
            text=f"⛔ <@!{itr.user.id}> doesn't seem to have a codeforces account.\n\nYou have to **register yourself to participate in a CP Duel**. Try /register <Your_codeforces_id>"
            embed=discord.Embed(title="Uhm! That's awkward..",description=text,colour=discord.Colour.red())
            await itr.followup.send(embed=embed)
            return
        if data[1] is None:
            text=f"⛔ <@!{opponent_user.id}> doesn't seem to have a codeforces account.\n\nYou have to **register yourself to participate in a CP Duel**. Try /register <Your_codeforces_id>"
            embed=discord.Embed(title="Uhm! That's awkward..",description=text,colour=discord.Colour.red())
            await itr.followup.send(embed=embed)
            return
        text=f"""
<@!{itr.user.id}> challenged <@!{opponent_user.id}> for a **CP Duel**!

🔴  `Red Corner        `: **{itr.user.name}**
🔵  `Blue Corner       `: **{opponent_user.name}**
⚔️  `Arena             `: **CodeForces**
💭  `Difficulty Rating `: **{max_difficulty.value}**
⏱️  `Time limit        `: **{tval[max_difficulty.value]}** minutes
        
<@!{opponent_user.id}> do you **accept** the **challenge?**"""
        embed=discord.Embed(title=":crossed_swords:  **__CP Duel__**  :crossed_swords:",description=text,colour=discord.Colour.gold())

        b1 = Button(label="Let's GO !",style=discord.ButtonStyle.green,emoji="✅")
        b2 = Button(label="Nah !",style=discord.ButtonStyle.red,emoji="✖️")
        
        async def b1_call(intr):
            await intr.response.defer()
            if intr.user.name==opponent_user.name:
                chnl=await create_channel(itr,opponent_user)
                self.duel_channels.append(chnl.id)
                text=f"\n🔥 <@!{opponent_user.id}> accepted the challenge!\n\n🚩 <@!{itr.user.id}> <@!{opponent_user.id}> Buckle up for a Duel!\n\n➡️ Follow the instructions on {chnl.mention}"
                embed=discord.Embed(title=":crossed_swords:  **__CP Duel__**  :crossed_swords:",description=text,colour=discord.Colour.gold())
                view.stop()
                msg=await itr.original_response()
                await msg.edit(view=None,embed=embed)
                res=await handle_duel(itr,chnl,opponent_user,max_difficulty.value,itr,data)

                if res!=0:
                    await self.update_score(res,itr.user.id,opponent_user.id)

            else:    
                await intr.channel.send(f"<@!{intr.user.id}> This challenge is not for you!")
            
        async def b2_call(intr):
            await intr.response.defer()
            if intr.user.name==opponent_user.name:
                text=f"\n⛔ <@!{opponent_user.id}> declined the challenge!"
                embed=discord.Embed(title=":crossed_swords:  **__CP Duel__**  :crossed_swords:",description=text,colour=discord.Colour.red())
                view.stop()
                msg=await itr.original_response()
                await msg.edit(view=None,embed=embed)

            else:
                await intr.channel.send(f"<@!{intr.user.id}> This challenge is not for you!")

        async def ontimeout():
            text=f"⏱️ <@!{opponent_user.id}> took too **long** to respond !\nTry challenging your other friends."
            embed=discord.Embed(title=":crossed_swords:  **__CP Duel__**  :crossed_swords:",description=text,colour=discord.Colour.red())
            view.stop()
            msg=await itr.original_response()
            await msg.edit(view=None,embed=embed)

        
        b1.callback=b1_call
        b2.callback=b2_call
        view= View()
        view = discord.ui.View(timeout=30)
        view.add_item(b1)
        view.add_item(b2)
        try:
            view.on_timeout=ontimeout
        except:
            pass

        await itr.followup.send(embed=embed,view=view)


    
async def setup(bot):
    await bot.add_cog(Duel(bot))