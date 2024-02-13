import discord
from discord.ext import commands
from discord import app_commands

class Help_(commands.Cog):

    def __init__(self,bot):
        self.bot= bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('help cog loaded')
    
    @commands.command()
    async def sync(self,ctx)->None:
        fmt=await ctx.bot.tree.sync()
        await ctx.send(f"synced {len(fmt)}")
        return

    @app_commands.command(name='help',description='help commands for Compii.')
    @app_commands.describe(cmd='Commands to choose from')
    @app_commands.choices(cmd=[
        discord.app_commands.Choice(name='all',value=0),
        discord.app_commands.Choice(name='contest',value=1),
        discord.app_commands.Choice(name='profile',value=2),
        discord.app_commands.Choice(name='details',value=7),
        discord.app_commands.Choice(name='rank',value=3),
        discord.app_commands.Choice(name='challenge',value=8),
        discord.app_commands.Choice(name='potd',value=4),
        discord.app_commands.Choice(name='register',value=5),
        discord.app_commands.Choice(name="admin,Mod",value=6)
    ])
    async def help(self,itr: discord.Interaction,cmd: discord.app_commands.Choice[int]):
        await itr.response.defer(ephemeral=True)
        if cmd.value==0:
            embed=discord.Embed(description="This bot is a Competitive Programming helper. Happy Coding..\n**__Commands:__**\n**contests <platform>** --> Returns upcoming contests on the given platform.\n**profile <member>** --> Returns profile details of the member.\n**details <platform> <username>** --> Returns profile details of the external username.\n**rank <platform>** --> See your ranking in Code Together Community.\n**challenge <discord member> <difficulty>** --> Its a minigame where you challenge your friend in CP question battle. Just select your friend to challenge and set the difficulty. And the battle is on!\n**potd** --> Problem of the day\n**register** --> Register yourself to participate in rankings.",color=discord.Colour.green())
            await itr.followup.send(embed=embed)
        elif cmd.value==1:
            embed=discord.Embed(description="**contests <platform>** --> Returns upcoming contests on the given platform.",color=discord.Colour.green())
            await itr.followup.send(embed=embed)
        elif cmd.value==2:
            embed=discord.Embed(description="**profile <discord member>** --> Returns complete profile details of the registered member.",color=discord.Colour.green())
            await itr.followup.send(embed=embed)
        if cmd.value==3:
            embed=discord.Embed(description="**rank <platform>** --> See your ranking in Code Together Community.",color=discord.Colour.green())
            await itr.followup.send(embed=embed)
        if cmd.value==4:
            embed=discord.Embed(description="**potd** --> Problem of the day",color=discord.Colour.green())
            await itr.followup.send(embed=embed)
        if cmd.value==5:
            embed=discord.Embed(description="**register** --> Register yourself to participate in rankings.",color=discord.Colour.green())
            await itr.followup.send(embed=embed)
        if cmd.value==6:
            embed=discord.Embed(description=""".sync
.potd_start
.potd_stop
.potd_solved
.potd_list
.potd_add
.potd_remove
.users""",color=discord.Colour.green())
            await itr.followup.send(embed=embed)
        
        if cmd.value==7:
            embed=discord.Embed(description="**details <platform> <username>** --> Returns profile details of the external username.",color=discord.Colour.green())
            await itr.followup.send(embed=embed)
        if cmd.value==8:
            embed=discord.Embed(description="**challenge <discord member> <difficulty>** --> Its a minigame where you challenge your friend in CP question battle. Just select your friend to challenge and set the difficulty. And the battle is on! ",color=discord.Colour.green())
            await itr.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Help_(bot))