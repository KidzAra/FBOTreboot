
import discord
from discord.ext import commands
import json 

intents = discord.Intents.all()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("$"),
    intents=intents,
)

@bot.command()
async def ticket(ctx, *, args = None):

    await bot.wait_until_ready()

    if args == None:
        message_content = "Уже создаём ваш тикет!"
    
    else:
        message_content = "".join(args)

    with open("data.json") as f:
        data = json.load(f)

    ticket_number = int(data["ticket-counter"])
    ticket_number += 1

    ticket_channel = await ctx.guild.create_text_channel("ticket-{}".format(ticket_number))
    await ticket_channel.set_permissions(ctx.guild.get_role(ctx.guild.id), send_messages=False, read_messages=False)

    for role_id in data["valid-roles"]:
        role = ctx.guild.get_role(role_id)

        await ticket_channel.set_permissions(role, send_messages=True, read_messages=True, add_reactions=True, embed_links=True, attach_files=True, read_message_history=True, external_emojis=True)
    
    await ticket_channel.set_permissions(ctx.author, send_messages=True, read_messages=True, add_reactions=True, embed_links=True, attach_files=True, read_message_history=True, external_emojis=True)

    em = discord.Embed(title="новый тикет {}#{}".format(ctx.author.name, ctx.author.discriminator), description= "{}".format(message_content), color=0x00a8ff)

    await ticket_channel.send(embed=em)

    pinged_msg_content = ""
    non_mentionable_roles = []

    if data["pinged-roles"] != []:

        for role_id in data["pinged-roles"]:
            role = ctx.guild.get_role(role_id)

            pinged_msg_content += role.mention
            pinged_msg_content += " "

            if role.mentionable:
                pass
            else:
                await role.edit(mentionable=True)
                non_mentionable_roles.append(role)
        
        await ticket_channel.send(pinged_msg_content)

        for role in non_mentionable_roles:
            await role.edit(mentionable=False)
    
    data["ticket-channel-ids"].append(ticket_channel.id)

    data["ticket-counter"] = int(ticket_number)
    with open("data.json", 'w') as f:
        json.dump(data, f)
    
    created_em = discord.Embed(title="FBOT", description="Ваш тикет: {}".format(ticket_channel.mention), color=0x00a8ff)
    
    await ctx.send(embed=created_em)

@bot.command()
async def ticketclose(ctx):
    with open('data.json') as f:
        data = json.load(f)

    if ctx.channel.id in data["ticket-channel-ids"]:

        channel_id = ctx.channel.id

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel and message.content.lower() == "закрыть"

        try:

            em = discord.Embed(title="FBOT", description="Вы хотите закрыть тикет? Если да то напишите 'закрыть' в чат тикета", color=0x00a8ff)
        
            await ctx.send(embed=em)
            await bot.wait_for('message', check=check, timeout=60)
            await ctx.channel.delete()

            index = data["ticket-channel-ids"].index(channel_id)
            del data["ticket-channel-ids"][index]

            with open('data.json', 'w') as f:
                json.dump(data, f)
        
        except asyncio.TimeoutError:
            em = discord.Embed(title="FBOT", description="К сожадению время подтверждения истекло, используйте команду снова", color=0x00a8ff)
            await ctx.send(embed=em)

        

@bot.command()
async def addaccess(ctx, role_id=None):

    with open('data.json') as f:
        data = json.load(f)
    
    valid_user = False

    for role_id in data["verified-roles"]:
        try:
            if ctx.guild.get_role(role_id) in ctx.author.roles:
                valid_user = True
        except:
            pass
    
    if valid_user or ctx.author.guild_permissions.administrator:
        role_id = int(role_id)

        if role_id not in data["valid-roles"]:

            try:
                role = ctx.guild.get_role(role_id)

                with open("data.json") as f:
                    data = json.load(f)

                data["valid-roles"].append(role_id)

                with open('data.json', 'w') as f:
                    json.dump(data, f)
                
                em = discord.Embed(title="FBOT", description="роль добавлена в роли администратора `{}` ".format(role.name), color=0x00a8ff)

                await ctx.send(embed=em)

            except:
                em = discord.Embed(title="FBOT", description="Неправильный или несуществующий ID роли.")
                await ctx.send(embed=em)
        
        else:
            em = discord.Embed(title="FBOT", description="Эта роль уже имеет доступ администратора!", color=0x00a8ff)
            await ctx.send(embed=em)
    
    else:
        em = discord.Embed(title="FBOT", description="У вас нет прав на исполнение этой команды.", color=0x00a8ff)
        await ctx.send(embed=em)

@bot.command()
async def delaccess(ctx, role_id=None):
    with open('data.json') as f:
        data = json.load(f)
    
    valid_user = False

    for role_id in data["verified-roles"]:
        try:
            if ctx.guild.get_role(role_id) in ctx.author.roles:
                valid_user = True
        except:
            pass

    if valid_user or ctx.author.guild_permissions.administrator:

        try:
            role_id = int(role_id)
            role = ctx.guild.get_role(role_id)

            with open("data.json") as f:
                data = json.load(f)

            valid_roles = data["valid-roles"]

            if role_id in valid_roles:
                index = valid_roles.index(role_id)

                del valid_roles[index]

                data["valid-roles"] = valid_roles

                with open('data.json', 'w') as f:
                    json.dump(data, f)

                em = discord.Embed(title="FBOT", description="роль администратора удалена `{}` ".format(role.name), color=0x00a8ff)

                await ctx.send(embed=em)
            
            else:
                
                em = discord.Embed(title="FBOT", description="доступ снят", color=0x00a8ff)
                await ctx.send(embed=em)

        except:
            em = discord.Embed(title="FBOT", description="Неправильный ID роли.")
            await ctx.send(embed=em)
    
    else:
        em = discord.Embed(title="FBOT", description="У вас нет прав на исполнение этой команды.", color=0x00a8ff)
        await ctx.send(embed=em)

@bot.command()
async def addpingrole(ctx, role_id=None):

    with open('data.json') as f:
        data = json.load(f)
    
    valid_user = False

    for role_id in data["verified-roles"]:
        try:
            if ctx.guild.get_role(role_id) in ctx.author.roles:
                valid_user = True
        except:
            pass
    
    if valid_user or ctx.author.guild_permissions.administrator:

        role_id = int(role_id)

        if role_id not in data["pinged-roles"]:

            try:
                role = ctx.guild.get_role(role_id)

                with open("data.json") as f:
                    data = json.load(f)

                data["pinged-roles"].append(role_id)

                with open('data.json', 'w') as f:
                    json.dump(data, f)

                em = discord.Embed(title="FBOT", description="Успешно!".format(role.name), color=0x00a8ff)

                await ctx.send(embed=em)

            except:
                em = discord.Embed(title="FBOT", description="Неправильный ID роли.")
                await ctx.send(embed=em)
            
        else:
            em = discord.Embed(title="FBOT", description="теперь эта роль получает упоминание при создании тикета.", color=0x00a8ff)
            await ctx.send(embed=em)
    
    else:
        em = discord.Embed(title="FBOT", description="У вас нет прав на исполнение этой команды.", color=0x00a8ff)
        await ctx.send(embed=em)

@bot.command()
async def removepingrole(ctx, role_id=None):

    with open('data.json') as f:
        data = json.load(f)
    
    valid_user = False

    for role_id in data["verified-roles"]:
        try:
            if ctx.guild.get_role(role_id) in ctx.author.roles:
                valid_user = True
        except:
            pass
    
    if valid_user or ctx.author.guild_permissions.administrator:

        try:
            role_id = int(role_id)
            role = ctx.guild.get_role(role_id)

            with open("data.json") as f:
                data = json.load(f)

            pinged_roles = data["pinged-roles"]

            if role_id in pinged_roles:
                index = pinged_roles.index(role_id)

                del pinged_roles[index]

                data["pinged-roles"] = pinged_roles

                with open('data.json', 'w') as f:
                    json.dump(data, f)

                em = discord.Embed(title="FBOT", description="Роль убрана из списка упоминаемых `{}` ".format(role.name), color=0x00a8ff)
                await ctx.send(embed=em)
            
            else:
                em = discord.Embed(title="FBOT", description="Эта роль уже получет упоминание при создании тикетов!", color=0x00a8ff)
                await ctx.send(embed=em)

        except:
            em = discord.Embed(title="FBOT", description="Неверный ID.")
            await ctx.send(embed=em)
    
    else:
        em = discord.Embed(title="FBOT", description="У вас нет прав на исполнение этой команды.", color=0x00a8ff)
        await ctx.send(embed=em)


@bot.command()
@commands.has_permissions(administrator=True)
async def addadminrole(ctx, role_id=None):

    try:
        role_id = int(role_id)
        role = ctx.guild.get_role(role_id)

        with open("data.json") as f:
            data = json.load(f)

        data["verified-roles"].append(role_id)

        with open('data.json', 'w') as f:
            json.dump(data, f)
        
        em = discord.Embed(title="FBOT", description="Роль добавлена `{}` ".format(role.name), color=0x00a8ff)
        await ctx.send(embed=em)

    except:
        em = discord.Embed(title="FBOT", description="Неправильный ID")
        await ctx.send(embed=em)

@bot.command()
@commands.has_permissions(administrator=True)
async def deladminrole(ctx, role_id=None):
    try:
        role_id = int(role_id)
        role = ctx.guild.get_role(role_id)

        with open("data.json") as f:
            data = json.load(f)

        admin_roles = data["verified-roles"]

        if role_id in admin_roles:
            index = admin_roles.index(role_id)

            del admin_roles[index]

            data["verified-roles"] = admin_roles

            with open('data.json', 'w') as f:
                json.dump(data, f)
            
            em = discord.Embed(title="FBOT", description="Роль успешно удалена `{}` ".format(role.name), color=0x00a8ff)

            await ctx.send(embed=em)
        
        else:
            em = discord.Embed(title="FBOT", description="Роль больше не получает упоминание!", color=0x00a8ff)
            await ctx.send(embed=em)

    except:
        em = discord.Embed(title="FBOT", description="Неправильный ID")
        await ctx.send(embed=em)

bot.run('MTA0MjQzNTk0OTc4MDU1Mzc3OA.GcyQuf.bLQYMceNyE1D1O3fElPR13xH65mqaVbn-3TIaE')