import BOT_setup
import copy
import json

import discord
from discord.ext import commands
from copy import deepcopy

from evidenta_populatiei.beginner_db import get_beginner_status
from organizari_bot.functions import get_org_by_msg_id, data_updater


'''

—————————————————————————————————————————————————————————————————————————————————————————————————
                    Functii
—————————————————————————————————————————————————————————————————————————————————————————————————

'''


def data_reader():
    with open('./organizari_bot/organizari.json', 'r') as f:
        _temp = json.load(f)
        return _temp


def data_logger(org_dict):
    with open('./organizari_bot/organizari.json', 'w') as f:
        json.dump(org_dict, f)


def data_manager(org_dict, mode='a'):
    changes = None
    _temp = data_reader()
    if mode == 'a':
        _temp["org"].append(org_dict)
    elif mode == 'r':
        _temp["org"].remove(org_dict)
    elif mode == 'u':
        for org in _temp["org"]:
            if org['ID'] == org_dict['ID']:
                changes = get_changes(org, org_dict)
                print(f'--- Updated org {org["ID"]}')
                _temp["org"].remove(org)
                _temp["org"].append(org_dict)
    data_logger(_temp)
    if changes:
        return changes


def get_changes(org_old, org_new):
    changes = {}
    for key in org_old:
        if key == 'Org_info' or key == 'Editing' or key == 'Participants' or key == 'Class':
            continue
        if org_new[key] != org_old[key]:
            changes[key] = [org_new[key], org_old[key]]
    return changes


def get_org_by_id(_org_id: str):
    org_data = data_reader()['org']
    for org in org_data:
        if org["ID"] == _org_id:
            return org
    else:
        return {}


async def compare_users(interaction, author, user):
    if author == user:
        return 1
    else:
        await interaction.response.send_message(content='Caca nu e voie!', ephemeral=True)
        return 0


async def get_message(_bot, org_dict):
    org_channel = await _bot.fetch_channel(BOT_setup.ORG_CHANNEL)
    if not org_dict['Message_id']:
        message = await org_channel.send(content='temp')
        org_dict['Message_id'] = message.id
    else:
        message = await org_channel.fetch_message(org_dict['Message_id'])

    return org_dict, message


async def org_refresher(bot, org_channel_id):
    with open('./organizari_bot/organizari.json', 'r') as f:
        _temp = json.load(f)

    orgs = _temp['org']
    if not orgs:
        return

    _org_channel = await bot.fetch_channel(org_channel_id)
    for org in orgs:
        print(org['ID'])
        message = await _org_channel.fetch_message(org['Message_id'])
        await edit_mesaj(bot, message, org)


async def create_part_stings(org_dict: dict):
    temp_part_list = []
    queue_rez_list = []
    max_number = int(org_dict['Max Number'])

    if org_dict['Participants']['Queue']:
        for exp in org_dict['Participants']['Queue']:
            if len(org_dict['Participants']['Participants']) < max_number:
                org_dict['Participants']['Participants'].append(exp)
                org_dict['Participants']['Queue'].remove(exp)
            else:
                pass
    _org = deepcopy(org_dict)
    participants = _org['Participants']
    author = participants['Author']

    if participants['Participants']:
        for exp in participants['Participants']:
            if exp[1] == author[1]:
                exp[0] = f"{exp[0]}👑"
            temp_part_list.append(f'{exp[0]} {BOT_setup.CLASSES[org_dict["Class"][str(exp[1])]]}')
        part_list = '\n'.join(temp_part_list)
    else:
        part_list = '-'

    temp_rez_list = deepcopy(org_dict['Participants']['Queue'])

    if temp_rez_list:
        for rez in temp_rez_list:
            if rez[1] == author[1]:
                rez[0] = f"{rez[0]}👑"
            queue_rez_list.append(f'{rez[0]} {BOT_setup.CLASSES[org_dict["Class"][str(rez[1])]]}')

    if participants['Reserve'] or queue_rez_list:
        reserve_queue = '\n'.join(queue_rez_list)
        reserve_list = reserve_queue + '\n' + '\n'.join([f'{rez[0]} {BOT_setup.CLASSES[org_dict["Class"][str(rez[1])]]}' for rez in participants['Reserve']])
    else:
        reserve_list = '-'

    return part_list, reserve_list, org_dict

'''

—————————————————————————————————————————————————————————————————————————————————————————————————
                    Creare mesaj
—————————————————————————————————————————————————————————————————————————————————————————————————

'''


async def initializare_mesaj(bot: commands.Bot, org_dict):
    global _bot
    _bot = bot

    attribute_list = BOT_setup.ORG_DETAILS[org_dict['Activity']]

    org_dict, message = await get_message(_bot, org_dict)

    part_list, reserve_list, org_dict = await create_part_stings(org_dict)
    data_manager(org_dict=org_dict, mode='a')

    author_name = org_dict['Participants']['Author'][0]

    await message.edit(content='Organizare noua!', embed=OrgEmbed(org_dict, attribute_list, author_name, part_list, reserve_list),
                       view=OrgView())


async def init_edit(bot: commands.Bot, org_dict,):
    _, message = await get_message(bot, org_dict)
    changes = data_manager(org_dict=org_dict, mode='u')
    await edit_mesaj(_bot, message, org_dict=org_dict)
    await spam_on_edit(bot, org_dict, changes, message.jump_url)


async def edit_mesaj(bot: commands.Bot, message, org_dict, block=False):
    global _bot
    _bot = bot

    print('Initializare edit mesaj')
    attribute_list = BOT_setup.ORG_DETAILS[org_dict['Activity']]

    part_list, reserve_list, org_dict = await create_part_stings(org_dict)
    author_name = org_dict['Participants']['Author'][0]
    data_manager(org_dict=org_dict, mode='u')

    if org_dict['Org_info']['Active']:
        await message.edit(content='Organizare noua!', embed=OrgEmbed(org_dict, attribute_list, author_name, part_list, reserve_list),
                           view=OrgView())
    else:
        await message.edit(content='Organizarea a inceput!', embed=OrgEmbed(org_dict, attribute_list, author_name, part_list, reserve_list),
                           view=None)


class OrgEmbed(discord.Embed):
    def __init__(self, org_dict, attribute_list, author_name, part_list, reserve_list):
        super().__init__(title=f"{org_dict['Activity']} {org_dict['Type']}",
                         description=f'',
                         color=attribute_list["HEX_COLOR"])

        self.add_field(name='ID',
                       value=org_dict['ID'],
                       inline=True)

        self.add_field(name='‎',
                       value='‎',
                       inline=True)

        from datetime import datetime
        if int(org_dict['Datetime']) - datetime.now().timestamp() < 3600 * 5:
            date_str = f"<t:{org_dict['Datetime']}:R>"
        else:
            date_str = f"<t:{org_dict['Datetime']}:f>"

        self.add_field(name='Data si ora',
                       value=date_str,
                       inline=True)


        self.add_field(name='Info',
                       value=org_dict['Info'],
                       inline=False)

        self.add_field(name='‎',
                       value='‎',
                       inline=False)

        '''
        Tratare participanti
        '''

        self.add_field(name=f'Participanti',
                       value=f'{part_list}',
                       inline=True)

        self.add_field(name='‎',
                       value='‎',
                       inline=True)

        self.add_field(name=f'Rezerve',
                       value=reserve_list,
                       inline=True)

        self.set_thumbnail(url=r'https://cdn11.bigcommerce.com/s-5d127/images/stencil/1280x1280/products/781/1383/FS72927-24__72706__76945.1560535870.jpg?c=2')

        self.set_footer(text=f"Creat de {org_dict['Participants']['Author'][0]}")


class ClassDropdown(discord.ui.Select):
    def __init__(self):
        elem_list = BOT_setup.CLASSES

        self.selected = None

        options = list()
        for elem, emoji in elem_list.items():
            _temp = discord.SelectOption(label=elem, emoji=emoji)
            options.append(_temp)

        super().__init__(placeholder=f'Alege clasa dorita', min_values=1, max_values=1,
                         options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.selected = f'{self.values[0]}'

    def call(self):
        return self.selected


class OrgView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        dropdown = ClassDropdown()
        self.add_item(dropdown)

        # Se initializeaza cu lista label butoane pentru First
        _lista_elemente = ['Join', 'Leave', 'Reserve', 'Delete']

        for elem in _lista_elemente:
            button = OrgButtons(elem, dropdown)
            self.add_item(button)


class OrgButtons(discord.ui.Button):
    def __init__(self, button_label, dropdown: ClassDropdown):
        self.button_lable = button_label

        if self.button_lable == 'Delete':
            super().__init__(label=self.button_lable, style=discord.ButtonStyle.danger, custom_id="delete")

        elif self.button_lable == 'Join':
            super().__init__(label=self.button_lable, style=discord.ButtonStyle.success, custom_id="join")

        elif self.button_lable == 'Reserve':
            super().__init__(label=self.button_lable, style=discord.ButtonStyle.secondary, custom_id="reserve")

        elif self.button_lable == 'Leave':
            super().__init__(label=self.button_lable, style=discord.ButtonStyle.danger, custom_id="leave")

        async def click(interaction: discord.Interaction):
            message = await interaction.message.fetch()

            class_select = dropdown.call()
            if not class_select and (interaction.data['custom_id'] == 'join' or interaction.data['custom_id'] == 'reserve'):
                await interaction.response.send_message(content='Trebuie sa selectezi o clasa!', ephemeral=True)
                return
            try:
                org_dict = get_org_by_msg_id(int(message.id))
            except:
                raise ValueError('Nu exista log pentru aceasta org')

            await button_functions(interaction=interaction, label=interaction.data['custom_id'], org_dict=org_dict,
                                   guild=interaction.guild, message=message, sel_class=class_select)

        self.callback = click


'''

—————————————————————————————————————————————————————————————————————————————————————————————————
                    Functii butoane
—————————————————————————————————————————————————————————————————————————————————————————————————

'''


async def button_functions(interaction: discord.Interaction, label, org_dict, message, guild: discord.Guild, sel_class):
    print(f'{interaction.user.nick if interaction.user.nick else interaction.user.name} a incercat sa dea {label} la org {org_dict["ID"]}')
    await interaction.response.defer()
    button_label = label

    # org_role = guild.get_role(org_dict['Org_utils']['Part'])

    if button_label == 'delete':
        if org_dict['Participants']['Author'][1] == interaction.user.id:
            _, message = await get_message(_bot=_bot, org_dict=org_dict)

            # await org_role.delete()
            await spam_on_edit(interaction.client, org_dict, changes=[], deleted=True)
            await message.delete()

            data_updater(org_old=org_dict, org_new={})

    if button_label == 'join':
        author = interaction.user
        player_data = [''.join([author.nick if author.nick else author.name]), author.id]

        if player_data in org_dict['Participants']['Participants']:
            return

        if player_data in org_dict['Participants']['Queue']:
            return

        if player_data in org_dict['Participants']['Reserve']:
            org_dict['Participants']['Reserve'].remove(player_data)

        org_dict['Class'][str(author.id)] = sel_class

        org_dict['Participants']['Queue'].append(player_data)

        await edit_mesaj(_bot, message, org_dict=org_dict)
        return

    if button_label == 'reserve':
        author = interaction.user
        player_data = [''.join([author.nick if author.nick else author.name]), author.id]

        if player_data in org_dict['Participants']['Participants']:
            org_dict['Participants']['Participants'].remove(player_data)

        if player_data in org_dict['Participants']['Queue']:
            org_dict['Participants']['Queue'].remove(player_data)

        if player_data not in org_dict['Participants']['Reserve']:
            org_dict['Class'][str(author.id)] = sel_class
            org_dict['Participants']['Reserve'].append(player_data)

            # await author.add_roles(org_role)
            await edit_mesaj(_bot, message, org_dict=org_dict)

    if button_label == 'leave':
        author = interaction.user
        player_data = [''.join([author.nick if author.nick else author.name]), author.id]

        if player_data not in org_dict['Participants']['Participants'] and player_data not in org_dict['Participants']['Queue'] and player_data not in org_dict['Participants']['Reserve']:
            return

        if player_data in org_dict['Participants']['Participants']:
            org_dict['Participants']['Participants'].remove(player_data)

        if player_data in org_dict['Participants']['Queue']:
            org_dict['Participants']['Queue'].remove(player_data)

        if player_data in org_dict['Participants']['Reserve']:
            org_dict['Participants']['Reserve'].remove(player_data)

        del org_dict['Class'][str(author.id)]
        # await author.remove_roles(org_role)
        await edit_mesaj(_bot, message, org_dict=org_dict)
        data_manager(org_dict=org_dict, mode='u')

    # data_updater(org_old=org_old, org_new=org_dict)


'''

—————————————————————————————————————————————————————————————————————————————————————————————————
                    Notify Edit
—————————————————————————————————————————————————————————————————————————————————————————————————

'''


async def spam_on_edit(bot: commands.Bot, org_dict, changes, jump_url='', deleted=False):

    org_id = org_dict['ID']

    for member in org_dict['Participants']['Participants']:
        if member[1] == org_dict['Participants']['Author'][1]:
            continue
        member_obj = await bot.fetch_user(member[1])
        if deleted:
            await member_obj.send(content='', embed=DeleteEmbed(org_dict))
            continue
        await member_obj.send(content='', embed=EditEmbed(org_id, changes, jump_url))

    for member in org_dict['Participants']['Queue']:
        if member[1] == org_dict['Participants']['Author'][1]:
            continue
        member_obj = await bot.fetch_user(member[1])
        if deleted:
            await member_obj.send(content='', embed=DeleteEmbed(org_dict))
            continue
        await member_obj.send(content='', embed=EditEmbed(org_id, changes, jump_url))

    for member in org_dict['Participants']['Reserve']:
        if member[1] == org_dict['Participants']['Author'][1]:
            continue
        member_obj = await bot.fetch_user(member[1])
        if deleted:
            await member_obj.send(content='', embed=DeleteEmbed(org_dict))
            continue
        await member_obj.send(content='', embed=EditEmbed(org_id, changes, jump_url))


class EditEmbed(discord.Embed):
    def __init__(self, id, changes, jump_url):
        super().__init__(title=f"Organizare modificata!",
                         description=f'Salut, autorul organizarii {id} la care esti inscris a facut o modificare. {jump_url}',
                         color=0x1d3fa5)

        for key in changes:
            if key == 'Datetime':
                self.add_field(name='Data si ora',
                               value=f"<t:{changes[key][1]}:f>",
                               inline=True)
                self.add_field(name='',
                               value=f"——>",
                               inline=True)
                self.add_field(name='Data si ora noua',
                               value=f"<t:{changes[key][0]}:f>",
                               inline=True)
            else:
                self.add_field(name=key,
                               value=f"{changes[key][1]}",
                               inline=True)
                self.add_field(name='',
                               value=f"——>",
                               inline=True)
                self.add_field(name=f'{key} modificat',
                               value=f"{changes[key][0]}",
                               inline=True)


class DeleteEmbed(discord.Embed):
    def __init__(self, org_dict):
        super().__init__(title=f"Organizare anulata!",
                         description=f'Salut, organizarea la care erai inscris a stearsa de catre autor!',
                         color=0xff2506)

        org_id = org_dict['ID']

        self.add_field(name=f'Activitate - ID {org_id}',
                       value=f"{org_dict['Type']}",
                       inline=False)

        self.add_field(name='Info',
                       value=f"{org_dict['Info'] if org_dict['Info'] else '-'}",
                       inline=False)

        self.add_field(name='Data si ora',
                       value=f"<t:{org_dict['Datetime']}:f>",
                       inline=False)

        self.add_field(name='Autor',
                       value=f"{org_dict['Participants']['Author'][0]}",
                       inline=False)