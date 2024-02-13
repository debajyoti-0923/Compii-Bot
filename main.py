import discord
import asyncio
from dotenv import load_dotenv,find_dotenv
import os
from discord.ext import commands,tasks
import json
import requests
import aiosqlite

load_dotenv(find_dotenv())
TOKEN=os.getenv("TOKEN")
APP_ID=os.getenv("APPID")
curr_id=""
curr_index=""
solved_today=[]
streak_update=0

ids={
    "admin-mod-chat":None,
    "problem_of_the_day":None
}

def set_ids():
    for i in ids:
        channel = discord.utils.get(bot.get_all_channels(), name=i)
        ids[i]=channel.id

intents=discord.Intents.default()
intents.message_content=True
bot=commands.Bot(command_prefix='.',intents=intents,application_id=APP_ID)

@bot.event
async def on_ready():
    print("is ready")
    set_ids()
    bot.db=await aiosqlite.connect("profs.db")
    await asyncio.sleep(1)
    async with bot.db.cursor() as cursor:
        await cursor.execute('''CREATE TABLE IF NOT EXISTS prof(
id INTEGER,
cf TEXT NULL,
cc TEXT NULL,
cfrank INTEGER DEFAULT 0,
ccrank INTEGER DEFAULT 0,
ps INTEGER DEFAULT 0,
dw INTEGER DEFAULT 0,
uname TEXT 
)''')
    await bot.db.commit()
    print("database ready")
    # await bot.db.close()
    await bot.change_presence(activity=discord.Game("/help for Help"))
    
async def chk_solve():
    async with bot.db.cursor() as cursor:
        await cursor.execute(f"SELECT id,cf FROM prof WHERE cf IS NOT NULL")
        data=await cursor.fetchall()

    if len(data)==0:
        return

    for i in data:
        if i[0] not in solved_today:
            url=f'https://codeforces.com/api/user.status?handle={i[1]}&from=1&count=20'
            r=requests.get(url,timeout=10)
            if r.status_code!=200:
                continue
            r_data=r.json()
            if r_data['status']!='OK':
                continue
            else:
                r_data=r_data['result']
                for k in r_data:
                    c_id=k['problem']['contestId']
                    ind=k['problem']['index']
                    v=k['verdict']
                    if c_id==int(curr_id) and ind==curr_index and v=='OK':
                        solved_today.append(i[0])
                        break

@tasks.loop(seconds=20,count=180)
async def solved():
    async with bot.db.cursor() as cursor:
        await cursor.execute(f"SELECT id,cf FROM prof WHERE cf IS NOT NULL")
        data=await cursor.fetchall()

    if len(data)==0:
        return

    for i in data:
        if i[0] not in solved_today:
            url=f'https://codeforces.com/api/user.status?handle={i[1]}&from=1&count=3'
            r=requests.get(url,timeout=10)
            if r.status_code!=200:
                continue
            r_data=r.json()
            if r_data['status']!='OK':
                continue
            else:
                r_data=r_data['result']
                for k in r_data:
                    c_id=k['problem']['contestId']
                    ind=k['problem']['index']
                    v=k['verdict']
                    if c_id==int(curr_id) and ind==curr_index and v=='OK':
                        solved_today.append(i[0])
                        channel=bot.get_channel(ids['problem_of_the_day'])
                        await channel.send(f"<@!{i[0]}> solved the problem!! :partying_face:  #POTD")
                        break

async def update_streak():
    if curr_id is None:
        return
    global solved_today
    await chk_solve()
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT id,ps,uname FROM prof WHERE cf IS NOT NULL")
        data=await cursor.fetchall()
        text=""
        c=1
        for x,i in enumerate(data):
            if i[0] in solved_today:
                await cursor.execute("UPDATE prof SET ps=(?) WHERE id=(?)",(i[1]+1,i[0]))
                text+=f"{c}. {i[2]} (Solved -- **{i[1]+1}**)\n"
                c+=1
    
    await bot.db.commit()
    solved_today=[]
    embed=discord.Embed(title="**__Last day POTD result:__**",description=text,color=discord.Colour.green())
    embed.set_footer(text="Can't find yourself? Try /register Codeforces_id")
    channel=bot.get_channel(ids['problem_of_the_day'])
    await channel.send(embed=embed)


@tasks.loop(hours=24)
async def send_potd():
    global curr_index,curr_id,streak_update

    if streak_update:
        await update_streak()
    streak_update=1

    with open('./cogs/potds.json', 'r') as f:
        data = json.load(f)
    
    if len(data['problems'])!=0:
        text=data['problems'].pop(0)
        data['active']=text
        with open('./cogs/potds.json', 'w') as f:
            json.dump(data,f)
        t=text.split("/")
        if "codeforces.com" in t:
            curr_id=t[-3]
            curr_index=t[-1]
            solved.start()
        else:
            curr_id=None
        channel=bot.get_channel(ids['problem_of_the_day'])
        embed=discord.Embed(title="**__#Problem Of The Day__**",description=f"<@&1037732041921413151> Url -- <{text}>",color=discord.Colour.blue())
        embed.set_footer(text="Solve within an Hour to get a Shoutout!! ;)")
        await channel.send(embed=embed)
        # print("send")
    else:
        channel=bot.get_channel(ids['admin-mod-chat'])
        text="No potd probelms available. Add More!"
        await channel.send(f"<@&1037731635736612915> {text}")
        

def admin_or_mod():
    async def predicate(ctx):
        # print(ctx.author.roles)
        return any(role.name in ['admin','Moderator'] for role in ctx.author.roles)
    return commands.check(predicate)


@bot.command()
@admin_or_mod()
async def potd_start(ctx):
    send_potd.start()
    await ctx.send("potd loop started")

@bot.command()
@admin_or_mod()
async def potd_stop(ctx):
    send_potd.cancel()
    solved.stop()
    streak_update=0
    solved_today=[]
    await ctx.send("potd loop stopped")

@bot.command()
@admin_or_mod()
async def potd_add(ctx,url):
    with open('./cogs/potds.json', 'r') as f:
        data = json.load(f)
    with open('./cogs/potds.json', 'w') as f:
        data['problems'].append(url)
        json.dump(data,f)

    await ctx.send("Added the problem")

@bot.command()
@admin_or_mod()
async def potd_list(ctx):
    with open('./cogs/potds.json', 'r') as f:
        data = json.load(f)
    print(data)
    text=""
    for i,x in enumerate(data['problems']):
        text+=f"{i+1}. <{x}>\n"
    
    await ctx.send(f"Potd list:\n{text}")

@bot.command()
@admin_or_mod()
async def potd_solved(ctx):
    await chk_solve()
    text="potd solved by: \n"
    for i,x in enumerate(solved_today):
        user = await bot.fetch_user(int(x))
        text+=f"{i+1}. {user.name}\n"
    await ctx.send(text)

@bot.command()
@admin_or_mod()
async def potd_remove(ctx,ind):
    with open('./cogs/potds.json', 'r') as f:
        data = json.load(f)
    data['problems'].pop(int(ind)-1)
    with open('./cogs/potds.json', 'w') as f:
        json.dump(data,f)

    await ctx.send("removed the problem")



@bot.command()
@admin_or_mod()
async def users(ctx):
    async with bot.db.cursor() as cursor:
        for z in ['cc','cf']:
            text=""
            await cursor.execute(f"SELECT uname,{z} FROM prof WHERE {z} IS NOT NULL")
            data=await cursor.fetchall()
            for i,x in enumerate(data):
                text+=f"{i+1}. {x[0]} -- {x[1]}\n"
            embed=discord.Embed(title=("__Codechef users:__" if z=='cc' else "__Codeforces users:__"),description=text,color=(discord.Colour.blue() if z=='cc' else discord.Colour.yellow() ))
            await ctx.send(embed=embed)



async def load():
    for file in os.listdir('./cogs'):
        if file.endswith('.py'):
            await bot.load_extension(f'cogs.{file[:-3]}')



async def main():
    await load()
    await bot.start(TOKEN)

asyncio.run(main())