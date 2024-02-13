import discord
from discord.ext import commands
from discord import app_commands
import requests
from PIL import Image
import os
import asyncio

class Slap_(commands.Cog):

    def __init__(self,bot):
        self.bot= bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('slap cog loaded')

    @app_commands.command(name='slap',description='Slap your friend for fun')
    async def slap(self,itr: discord.Interaction,user_id:discord.User):
        await itr.response.defer()
        a1 = itr.user.display_avatar.url
        response = requests.get(a1)
        if response.status_code == 200:
            with open(f"slapc/{itr.user.name}.png", "wb") as file:
                file.write(response.content)
            
        a1 = user_id.display_avatar.url
        response = requests.get(a1)
        if response.status_code == 200:
            with open(f"slapc/{user_id.name}.png", "wb") as file:
                file.write(response.content)

        base_image = Image.open("slapc/base.jpg").convert("RGBA")
        p1 = Image.open(f"slapc/{itr.user.name}.png").convert("RGBA").resize((60,60))
        p2 = Image.open(f"slapc/{user_id.name}.png").convert("RGBA").resize((60,60))
        mask=Image.open("slapc/m2.png")

        final_image = Image.new("RGBA", base_image.size)
        final_image.paste(base_image, (0, 0))

        final_image.paste(p2, (30, 25), mask=mask)
        final_image.paste(p1, (165, 35), mask=mask)
        
        fname=itr.user.name+user_id.name
        final_image.save(f"slapc/{fname}.png")
        with open(f"slapc/{fname}.png",'rb') as f:
            await itr.followup.send(file=discord.File(f))
        await asyncio.sleep(2)
        os.remove(f"slapc/{fname}.png")
        os.remove(f"slapc/{itr.user.name}.png")
        os.remove(f"slapc/{user_id.name}.png")
        # await itr.channel.send(f"<@!{itr.user.id}> gave a big smack to <@!{user_id.id}> !")
        

        

async def setup(bot):
    await bot.add_cog(Slap_(bot))