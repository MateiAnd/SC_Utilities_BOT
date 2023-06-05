import BOT_setup
import json
import aiofiles
import discord
from discord.utils import get


async def init(bot):
    # variabile locale
    manual_donator = []
    update_channel = await bot.fetch_channel(BOT_setup.PLAYER_UPDATES_CHANNEL)

    # setup bot
    members = bot.get_all_members()
    server = await bot.fetch_guild(BOT_setup.GUILD_ID)
    # server_booster = server.get_role(BOT_setup.SERVER_BOOSTER)
    donator_role = server.get_role(BOT_setup.DONATOR_ROLE)

    # citire donatori manual
    with open('./utilities/donator_db.json') as f:
        _temp = json.load(f)
        donator_list = _temp['data']
    for don in donator_list:
        manual_donator.append(don["id"])

    # executare pt server boost
    for member in members:
        if member.id in manual_donator:
            if donator_role not in member.roles:
                print(f'{"—" * 3} Adaugat donator lui {member.nick if member.nick else member.display_name}')
                try:
                    await update_channel.send(
                        content=f'Adaugat donator lui {member.mention} din lista de donatori concursuri')
                    await member.add_roles(donator_role)
                except:
                    await update_channel.send(content=f'Pula mea nu a mers')

        # elif server_booster in member.roles:
        #     if donator_role not in member.roles:
        #         print(f'{"—" * 3} Adaugat donator lui {member.nick if member.nick else member.display_name} din server boost')
        #         await update_channel.send(content=f'Adaugat donator lui {member.mention} din Server Boost')
        #         await member.add_roles(donator_role)

        # elif donator_role in member.roles:
        #     print(f'{"—" * 3} Scos donator lui {member.nick if member.nick else member.display_name}')
        #     await update_channel.send(content=f'Scos rol donator lui {member.mention}.')
        #     await member.remove_roles(donator_role)

    # executare pentru donatori manual
    for don in donator_list:
        from datetime import datetime
        donator = await server.fetch_member(don['id'])

        if donator_role in donator.roles:
            time_limit = datetime.strptime(don['time'], '%d/%m/%Y')
            if datetime.now() > time_limit:
                print(f'{"—" * 3} Scos donator lui {donator.nick if donator.nick else donator.display_name} din timp expirat')
                await update_channel.send(content=f'Scos rol donator lui {donator.mention} din expirare timp.')
                await donator.remove_roles(donator_role)
                donator_list.remove(don)

    with open('./utilities/donator_db.json', 'w') as f:
        _temp['data'] = donator_list
        json.dump(_temp, f, indent=4)


async def booster_manage(before:discord.Member, after:discord.Member, bot):
    update_channel = await bot.fetch_channel(BOT_setup.PLAYER_UPDATES_CHANNEL)

    if len(before.roles) < len(after.roles):
        # The user has gained a new role
        newRole = next(role for role in after.roles if role not in before.roles)

        if newRole.id == BOT_setup.SERVER_BOOSTER:
            server = await bot.fetch_guild(BOT_setup.GUILD_ID)
            donator_role = server.get_role(BOT_setup.DONATOR_ROLE)
            print(f'{"—" * 3} Adaugat donator lui {after.nick if after.nick else after.display_name} din server boost')
            await after.add_roles(donator_role)
            await update_channel.send(
                content=f'Adaugat donator lui {after.mention} din Server Boost')

    elif len(before.roles) > len(after.roles):
        # The user has lost a role
        lostRole = next(role for role in before.roles if role not in after.roles)

        manual_donator = []

        if lostRole.id == BOT_setup.SERVER_BOOSTER:

            # citire donatori manual
            async with aiofiles.open('./utilities/donator_db.json') as f:
                _temp = json.loads(await f.read())
                donator_list = _temp['data']
            manual_donator.append(don["id"] for don in donator_list)

            if after.id in manual_donator:
                return

            server = await bot.fetch_guild(BOT_setup.GUILD_ID)
            donator_role = server.get_role(BOT_setup.DONATOR_ROLE)
            print(
                f'{"—" * 3} Scos donator lui {after.nick if after.nick else after.display_name} din expirare server boost')
            await after.remove_roles(donator_role)
            await update_channel.send(
                content=f'Scos donator lui {after.mention} din expirare Server Boost')