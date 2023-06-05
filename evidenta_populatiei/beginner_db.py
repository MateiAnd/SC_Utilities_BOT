import aiosqlite
import discord
from discord.ext import commands
import os


async def create_db():
    async with aiosqlite.connect('./evidenta_populatiei/user_role.db') as connection:
    # connection = sqlite3.connect('user_role.db')

        cursor = await connection.cursor()

        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS UserRoles (
            user_id INTEGER PRIMARY KEY,
            KF INTEGER,
            DSC INTEGER,
            GOS INTEGER,
            LW INTEGER,
            VOG INTEGER,
            VOD INTEGER,
            RON INTEGER,
            SOTW INTEGER,
            DUAL INTEGER,
            GOA INTEGER,
            PIT INTEGER,
            PROPH INTEGER,
            ST INTEGER,
            GOTD INTEGER
            );
            ''')

        # cursor.execute('''
        # INSERT INTO UserRoles (user_id, KF, DSC, GOS, LW, VOG, VOD, RON, SOTW, DUAL, GOA, PIT, PROPH, ST, GOTD)
        # VALUES (1111, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1);
        # ''')
        await connection.commit()

binding_dict = {
    'KF': 1075455824748621840,
    'DSC': 1075455824765394986,
    'GOS': 1075455824765394988,
    'LW': 1075455824765394990,
    'VOG': 1075455824765394984,
    'VOD': 1075455824748621842,
    'RON': 1101410490363686952,
    'SOTW': 1075455824731852844,
    'DUAL': 1075455824731852846,
    'GOA': 1075455824731852848,
    'PIT': 1075455824748621836,
    'PROPH': 1075455824748621834,
    'ST': 1075455824748621838,
    'GOTD': 1111895978350497882
}

async def populate_db(bot:commands.Bot, GUILD_ID):
    guild = await bot.fetch_guild(GUILD_ID)
    # members = guild.fetch_members()
    write_list = []
    async for member in guild.fetch_members(limit=None):
        user_write = [member.id]
        for _, value in binding_dict.items():
            if value in [role.id for role in member.roles]:
                user_write.append(1)
            else:
                user_write.append(0)
        write_list.append(user_write)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'evidenta_populatiei/user_role.db')
    if os.path.isfile(file_path):
        pass
    else:
        await create_db()

    async with aiosqlite.connect('./evidenta_populatiei/user_role.db') as connection:
        cursor = await connection.cursor()

        query = '''
            INSERT OR REPLACE INTO UserRoles (user_id, KF, DSC, GOS, LW, VOG, VOD, RON, SOTW, DUAL, GOA, PIT, PROPH, ST, GOTD)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        '''

        await cursor.executemany(query, write_list)

        await connection.commit()

    print('Done')


async def get_beginner_status(part_list, role_id):

    if role_id == 77777777777:
        return await session_beginner(part_list)

    activity_key = None
    for key, value in binding_dict.items():
        if value == role_id:
            activity_key = key

    if not activity_key:
        return [False for _ in range(len(part_list))]

    async with aiosqlite.connect('./evidenta_populatiei/user_role.db') as connection:
        cursor = await connection.cursor()

        results = dict()

        for user_id in part_list:
            # Prepare the query
            query = f'SELECT "{activity_key}" FROM UserRoles WHERE user_id = {user_id[1]}'

            # Execute the query
            await cursor.execute(query)

            # Fetch the result
            result = await cursor.fetchone()

            # If a result is found, store it in the dictionary
            if result is not None:
                results[user_id[1]] = bool(result[0])

        return results


async def session_beginner(part_list):
    """ Mai bine o pun sus ca role_id specific sesiunii de raid"""
    async with aiosqlite.connect('./evidenta_populatiei/user_role.db') as connection:
        cursor = await connection.cursor()

        results = dict()

        for user_id in part_list:
            # Prepare the query
            query = f'SELECT KF, DSC, GOS, LW, VOG, VOD, RON FROM UserRoles WHERE user_id = {user_id[1]}'

            # Execute the query
            await cursor.execute(query)

            # Fetch the result
            result = await cursor.fetchone()

            # If a result is found, store it in the dictionary
            for status in result:
                if not bool(status):
                    results[user_id[1]] = False
                    break
            else:
                results[user_id[1]] = True

        return results

