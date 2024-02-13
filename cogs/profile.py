
import discord
from discord.ext import commands
from discord import app_commands
from requests_html import HTMLSession
import json
import aiosqlite
import requests


class User:
    def __init__(self,username=None,platform=None):
        self.__username = username
        self.__platform = platform
    def codechef(self):
        url = "https://codechef.com/users/{}".format(self.__username)
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

        
        max_rating = rating_header.find('small')[0].text[1:-1].split()[2]
        rating_star = len(r.html.find(".rating-star",first=True).find('span'))
        ranks = r.html.find('.rating-ranks',first=True).find('strong')
        global_rank = ranks[0].text
        country_rank = ranks[1].text

        # print(rating,max_rating,rating_star,global_rank,country_rank,ranks)

        data['status']='OK'
        data['handle']=self.__username
        data['platform']=self.__platform
        data['rating']=rating
        data['maxRating']=max_rating
        data['star']=rating_star
        data['global']=global_rank
        data['country']=country_rank

        return data
    def codeforces(self):
        url = 'https://codeforces.com/api/user.info?handles={}'.format(self.__username)
        r = requests.get(url,timeout=10)
        data  = dict()
        if r.status_code !=200:
            data['status']='failed'
            return data
        r_data = r.json()
        if r_data['status']!='OK':
            data['status']='failed'
            return data
        data['status'] = 'OK'
        data.update(r_data['result'][0])
        data['platform']=self.__platform
        return data
    def get_info(self):
        if self.__platform=='codechef':
            return self.codechef()
        if self.__platform=='codeforces':
            return self.codeforces()
        return {'status':'failed'}

def get_user_data(name,plat):
    obj = User(name,plat)
    return(obj.get_info())


class profile_(commands.Cog):

    def __init__(self,bot):
        self.bot= bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.db=await aiosqlite.connect("profs.db")
        print('profile cog loaded')
    

    @app_commands.command(name='details',description='Shows details of the User. Leave blank to see details of the members.')
    @app_commands.describe(platform='Platforms to choose from')
    @app_commands.choices(platform=[
        discord.app_commands.Choice(name='CodeForces',value=0),
        discord.app_commands.Choice(name='CodeChef',value=1),
    ])
    async def details(self,itr: discord.Interaction,platform: discord.app_commands.Choice[int],user: str):
        if platform.value==1:
            data=get_user_data(user,"codechef")

            if data['status']=='failed':
                text="Failed to fetch data."
                color=discord.Colour.red()
            else:
                text=f"""**Name: **{data['handle']}
**Platform: **{data['platform']}
**Rank: **{data['star']}:star:
**Rating: **{data['rating']}
**Max Rating: **{data['maxRating']}
**Country Rank: **{data['country']}
**Global Rank: **{data['global']}
**Url: **https://codechef.com/users/{data['handle']}"""
                color=discord.Colour.green()
        elif platform.value==0:
            data=get_user_data(user,"codeforces")

            if data['status']=='failed':
                text="Failed to fetch data."
                color=discord.Colour.red()
            else:
                text=f"""**Name: **{data['handle']}
**Platform: **{data['platform']}
**Rank: **{data['rank']}
**Max Rank: **{data['maxRank']}
**Rating: **{data['rating']}
**Max Rating: **{data['maxRating']}
**Url: **https://codeforces.com/profile/{data['handle']}"""
                color=discord.Colour.green()
        embed=discord.Embed(title=f"__{user}'s {platform.name} Profile__",description=text,color=color)
        await itr.followup.send(embed=embed)
    
    @app_commands.command(name='profile',description='Shows profile details of the member. Leave blank to see yours')
    async def profile(self,itr:discord.Interaction,user_id:discord.User=None):
        if user_id is None:
            user_id=itr.user
        await itr.response.defer()
        async with self.db.cursor() as cursor:
            d=await cursor.execute(f"SELECT cc,cf,ps,dw FROM prof WHERE id={user_id.id}")
            unames=await d.fetchone()
            if unames==None:
                await cursor.execute("INSERT INTO prof(id,uname) VALUES(?,?)",(user_id.id,user_id.name))
                await self.db.commit()
                unames=[None,None,0,0]
        text=f"""

**__Code Together profile__**
POTDs Solved: {unames[2]} 🎯
Duels Won: {unames[3]} 🏆
"""

        if unames[0] is not None:
            data=get_user_data(unames[0],'codechef')
            text+=f"""
**__Codechef__**
**Name: **{data['handle']}
**Platform: **{data['platform']}
**Rank: **{data['star']}:star:
**Rating: **{data['rating']}
**Max Rating: **{data['maxRating']}
**Country Rank: **{data['country']}
**Global Rank: **{data['global']}
**Url: **https://codechef.com/users/{data['handle']}
"""     
        if unames[1] is not None:
            data=get_user_data(unames[1],'codeforces')
            text+=f"""
**__CodeForces__**
**Platform: **{data['platform']}
**Rank: **{data['rank']}
**Max Rank: **{data['maxRank']}
**Rating: **{data['rating']}
**Max Rating: **{data['maxRating']}
**Url: **https://codeforces.com/profile/{data['handle']}
"""
        embed=discord.Embed(title=f"__{user_id.name}'s Profile__",description=text,color=discord.Colour.green())
        await itr.followup.send(embed=embed)
    
async def setup(bot):
    await bot.add_cog(profile_(bot))