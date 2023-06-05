import BOT_setup
import json

import discord
from organizari_bot import org_channel

'''

—————————————————————————————————————————————————————————————————————————————————————————————————
                    Set-up
—————————————————————————————————————————————————————————————————————————————————————————————————

'''
_temp_list = list(BOT_setup.ORG_DETAILS.keys())
_temp_list.extend(['Cancel'])
global button_labels
button_labels = {
    'First': _temp_list,
    'Second': ['Tier 1', 'Tier 2', 'Tier 3', 'Tier 4'],  # optiuni pe baza tipului de activitate
    'Third': ['Next', 'Edit', 'Cancel'],  # timp
    'Fifth': ['Add Info', 'Finish', 'Cancel']  # final
}


def rand_id():
    from random import randint
    return ''.join([str(randint(0, 9)) for i in range(4)])


async def compare_users(interaction, author, user):
    if author == user:
        return 1
    else:
        await interaction.response.send_message(content='Nu esti utilizatorul principal!', ephemeral=True)
        return 0


def time_flagger(date_string, org_dict):
    from datetime import datetime

    # Parse the user's input datetime and localize it to Bucharest timezone
    user_datetime = datetime.fromtimestamp(float(org_dict['Datetime']))

    # Calculate the minute_difference between the current time and the event's server datetime
    current_server_time = datetime.now()
    time_difference = user_datetime - current_server_time
    minute_difference = int(time_difference.total_seconds() / 60)
    print(f'-- Diferenta timp {minute_difference}')

    org_dict['Org_info']['Reminder'] = 0
    if 30 < minute_difference < 60:
        org_dict['Org_info']['Reminder'] = 1
    if 29 < minute_difference < 30:
        org_dict['Org_info']['Reminder'] = 2
    if minute_difference < 15:
        org_dict['Org_info']['Reminder'] = 3

    return org_dict


def get_org_by_id(org_id: str):
    with open('./organizari_bot/organizari.json', 'r') as f:
        _temp = json.load(f)

    org_data = _temp['org']
    for org in org_data:
        if org["ID"] == org_id:
            return org
    else:
        return {}


'''

—————————————————————————————————————————————————————————————————————————————————————————————————
                    Comenzi
—————————————————————————————————————————————————————————————————————————————————————————————————

'''


async def create(interaction, bot, author):
    await interaction.response.defer()

    global _bot, _author
    _author = author
    _bot = bot

    author_details = [''.join([author.nick if author.nick else author.name]), author.id]

    id_nr = rand_id()
    _temp_success = True
    with open('./organizari_bot/organizari.json', 'r') as f:
        orgs = json.load(f)
        while True:
            for org in orgs['org']:
                if id_nr == org['ID']:
                    _temp_success = False
            if _temp_success:
                break
            id_nr = rand_id()

    org_dict = {
        'ID': id_nr,
        'Activity': '',
        'Type': '',
        'Datetime': '',
        'Info': '',
        'Max Number': '',
        'Message_id': '',
        'Class': {},
        'Participants': {'Author': author_details, 'Participants': [], 'Queue': [author_details], 'Reserve': []},
        'Org_info': {'Active': True, 'Reminder': 0},  # reminder: (0, 1, 2, 3, 4) = (none, 1h, 30m, 15m, dat tot)
        'Org_utils': '',
        'Editing': False
    }

    global message
    message = await interaction.followup.send(content='', embed=FirstEmbed(), view=FirstView(author, org_dict))


async def edit(interaction, bot, author, org_id):
    await interaction.response.defer()

    global _bot
    _bot = bot

    author_details = [''.join([author.nick if author.nick else author.name]), author.id]

    org_dict = get_org_by_id(org_id)
    if not org_dict:
        await interaction.followup.send(content='Nu exita aceasta organizare!', ephemeral=True)
        return

    if org_dict['Participants']['Author'] != author_details:
        await interaction.followup.send(content='Nu esti autorul organizarii!', ephemeral=True)
        return

    org_dict['Editing'] = True

    global message
    message = await interaction.followup.send(content='', embed=SecondEmbed(org_dict), view=SecondView(author, org_dict))


'''

—————————————————————————————————————————————————————————————————————————————————————————————————
                    Primul mesaj
—————————————————————————————————————————————————————————————————————————————————————————————————

'''


class FirstEmbed(discord.Embed):
    def __init__(self):
        super().__init__(title="Selecteaza tipul de organizare.",
                         description="Alege activitatea pe care vrei sa o faci",
                         color=0xFF2D00)


class FirstView(discord.ui.View):
    def __init__(self, author, org_dict):
        super().__init__(timeout=None)

        # Se initializeaza cu lista label butoane pentru First
        _lista_elemente = button_labels.get('First')

        for elem in _lista_elemente:
            button = FirstMsgButtons(elem, author, org_dict)
            self.add_item(button)


class FirstMsgButtons(discord.ui.Button):
    def __init__(self, button_label, author, org_dict):
        self.button_lable = button_label

        if self.button_lable == 'Cancel':
            super().__init__(label=self.button_lable, style=discord.ButtonStyle.danger, custom_id="test")

            async def click(interaction: discord.Interaction):
                if await compare_users(interaction, author, interaction.user):
                    await interaction.response.defer()
                    await message.edit(content='Creare organizare anulata.', embed=None, view=None)

        else:
            super().__init__(label=self.button_lable, style=discord.ButtonStyle.blurple)

            async def click(interaction: discord.Interaction):
                if await compare_users(interaction, author, interaction.user):
                    await interaction.response.defer()

                    org_dict['Activity'] = button_label

                    await message.edit(content='', embed=SecondEmbed(org_dict),
                                       view=SecondView(author=author, org_dict=org_dict))

        self.callback = click


'''

—————————————————————————————————————————————————————————————————————————————————————————————————
                    Al doilea mesaj
—————————————————————————————————————————————————————————————————————————————————————————————————

'''


class SecondEmbed(discord.Embed):
    def __init__(self, org_dict):
        super().__init__(title=f"Selecteaza tipul de {org_dict['Activity']} dorit.",
                         description="Selecteaza din lista ce activitate doresti sa creezi",
                         color=0xff5e00)


class SecondDropdown(discord.ui.Select):
    def __init__(self, author, org_dict):
        elem_list = button_labels['Second']
        self.selected = None
        self.author = author

        options = list()
        for elem in elem_list:
            _temp = discord.SelectOption(label=elem)
            options.append(_temp)

        if org_dict['Type']:
            super().__init__(placeholder=f"{org_dict['Type']}", min_values=1, max_values=1,
                             options=options)
        else:
            super().__init__(placeholder=f'Alege activitatea {org_dict["Activity"]} dorita', min_values=1, max_values=1,
                             options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if await compare_users(interaction, self.author, interaction.user):
            self.selected = f'{self.values[0]}'

    def call(self):
        return self.selected


class SecondView(discord.ui.View):
    def __init__(self, author, org_dict):
        super().__init__(timeout=None)

        dropdown = SecondDropdown(author, org_dict)
        self.add_item(dropdown)

        # Se initializeaza cu lista label butoane pentru First
        _lista_elemente = ['Next', 'Cancel']

        for elem in _lista_elemente:
            button = SecondMsgButtons(elem, author, org_dict, dropdown)
            self.add_item(button)


class SecondMsgButtons(discord.ui.Button):
    def __init__(self, button_label, author, org_dict, dropdown):
        self.button_lable = button_label

        if self.button_lable == 'Cancel':
            super().__init__(label=self.button_lable, style=discord.ButtonStyle.danger)

            async def click(interaction: discord.Interaction):
                if await compare_users(interaction, author, interaction.user):
                    await interaction.response.defer()
                    await message.edit(content='Creare organizare anulata.', embed=None, view=None)

        else:
            super().__init__(label=self.button_lable, style=discord.ButtonStyle.blurple)

            async def click(interaction: discord.Interaction):
                if await compare_users(interaction, author, interaction.user):
                    await interaction.response.defer()

                    if org_dict['Type']:
                        pass
                    elif dropdown.call():
                        org_dict['Type'] = dropdown.call()
                        org_dict['Max Number'] = BOT_setup.ORG_DETAILS[org_dict['Activity']]["MAX_PLAYERS"]
                    else:
                        await interaction.followup.send(content='Trebuie sa selectezi ceva!', ephemeral=True)
                        return
                    await third_message(org_dict=org_dict, author=author)

        self.callback = click

'''

—————————————————————————————————————————————————————————————————————————————————————————————————
                    Al treilea mesaj
—————————————————————————————————————————————————————————————————————————————————————————————————

'''


async def third_message(org_dict, author, string=None):
    if not string and org_dict['Datetime']:
        string = org_dict['Datetime']

    if not string:
        import datetime

        # Get the current server's time (naive datetime)
        current_server_time_naive = datetime.datetime.now().timestamp()

        # Add 15 min
        after_15_min = current_server_time_naive + 15*60  # calculate 15 minutes after current datetime

        # Get the epoch time
        epoch_time = int(after_15_min)
        string = str(epoch_time)
    org_dict['Datetime'] = string

    org_dict = time_flagger(org_dict['Datetime'], org_dict)

    await message.edit(content='', embed=ThirdEmbed(org_dict),
                       view=ThirdView(author=author, org_dict=org_dict))


class ThirdEmbed(discord.Embed):
    def __init__(self, org_dict):
        super().__init__(title=f"Seteaza timpul pentru organizarea {org_dict['Activity']} {org_dict['Type']} .",
                         description=f"Modifica data si ora organizarii\n"
                                     f"Selectat actual: <t:{int(round(float(org_dict['Datetime']),0))}:f>",
                         color=0xffa600)


class ThirdView(discord.ui.View):
    def __init__(self, author, org_dict):
        super().__init__(timeout=None)

        _lista_elemente = button_labels['Third']

        for elem in _lista_elemente:
            button = ThirdMsgButtons(elem, author, org_dict)
            self.add_item(button)


class ThirdMsgButtons(discord.ui.Button):
    def __init__(self, button_label, author, org_dict):
        self.button_lable = button_label

        if self.button_lable == 'Cancel':
            super().__init__(label=self.button_lable, style=discord.ButtonStyle.danger)

            async def click(interaction: discord.Interaction):
                if await compare_users(interaction, author, interaction.user):
                    await interaction.response.defer()
                    await message.edit(content='Creare organizare anulata.', embed=None, view=None)

        elif self.button_lable == 'Edit':
            super().__init__(label=self.button_lable, style=discord.ButtonStyle.blurple)

            async def click(interaction: discord.Interaction):
                if await compare_users(interaction, author, interaction.user):
                    modal = ThirdModal(org_dict=org_dict, author=author)
                    await interaction.response.send_modal(modal)

        else:
            super().__init__(label=self.button_lable, style=discord.ButtonStyle.blurple)

            async def click(interaction: discord.Interaction):
                if await compare_users(interaction, author, interaction.user):
                    await interaction.response.defer()
                    await message.edit(content='', embed=ForthEmbed(),
                                       view=ForthView(author=author, org_dict=org_dict))

        self.callback = click


class ThirdModal(discord.ui.Modal):  # , title='Adauga ora si data'
    def __init__(self, org_dict, author):
        self.org_dict = org_dict
        self.author = author

        import datetime
        import pytz

        # Get the current server's time (naive datetime)
        current_server_time_naive = datetime.datetime.now()

        # Localize the current server's time to the server's timezone
        server_timezone = pytz.utc.localize(current_server_time_naive)

        # Convert the server's current time to Bucharest timezone
        bucharest_timezone = pytz.timezone("Europe/Bucharest")
        bucharest_time = server_timezone.astimezone(bucharest_timezone)

        # Add 15 min
        after_15_min = bucharest_time + datetime.timedelta(minutes=15)  # calculate 15 minutes after current datetime
        formatted_datetime = after_15_min.strftime('%d/%m/%Y %H:%M')
        data_str, ora_str = formatted_datetime.split(' ')

        ora = discord.ui.TextInput(
            label='Adauga ora [RO] - format 24h hh:mm',
            placeholder='Ex: 20:00',
            default=ora_str,
            required=True,
        )

        data = discord.ui.TextInput(
            label='Adauga data [RO] - format DD/MM/YYYY',
            placeholder='Ex: 15/12/2020',
            default=data_str,
            required=True,
        )
        super().__init__(title='Adauga data si ora')

        self.add_item(ora)
        self.add_item(data)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        import datetime, pytz

        ora, data = self.children
        timp_str = f'{data.value} {ora.value}'
        datetime_obj = datetime.datetime.strptime(timp_str, '%d/%m/%Y %H:%M')
        source_tz = pytz.timezone("Europe/Bucharest")
        dt = source_tz.localize(datetime_obj)

        # Convert the datetime object to epoch time in the server's local timezone
        epoch_time = dt.timestamp()

        if datetime.datetime.now().timestamp() < epoch_time:
            await third_message(org_dict=self.org_dict, author=self.author, string=str(int(epoch_time)))
        else:
            await interaction.response.send_modal(ThirdModal(self.org_dict, self.author))


'''

—————————————————————————————————————————————————————————————————————————————————————————————————
                    Al patrulea mesaj
—————————————————————————————————————————————————————————————————————————————————————————————————

'''


class ForthEmbed(discord.Embed):
    def __init__(self):
        super().__init__(title=f"Selecteaza clasa cu care te inscri",
                         description=f'''Selecteaza clasa cu care te inscri in organizarea ta''',
                         color=0xddff00)


class ForthDropdown(discord.ui.Select):
    def __init__(self, author, org_dict):
        elem_list = BOT_setup.CLASSES

        if org_dict['Editing']:
            self.selected = None
        else:
            self.selected = None
        self.author = author

        options = list()
        for elem, emoji in elem_list.items():
            _temp = discord.SelectOption(label=elem, emoji=emoji)
            options.append(_temp)

        super().__init__(placeholder=f'Alege clasa dorita', min_values=1, max_values=1,
                         options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if await compare_users(interaction, self.author, interaction.user):
            self.selected = f'{self.values[0]}'

    def call(self):
        return self.selected


class ForthView(discord.ui.View):
    def __init__(self, author, org_dict):
        super().__init__(timeout=None)

        dropdown = ForthDropdown(author, org_dict)
        self.add_item(dropdown)

        # Se initializeaza cu lista label butoane pentru First
        _lista_elemente = ['Next', 'Cancel']

        for elem in _lista_elemente:
            button = ForthMsgButtons(elem, author, org_dict, dropdown)
            self.add_item(button)


class ForthMsgButtons(discord.ui.Button):
    def __init__(self, button_label, author, org_dict, dropdown):
        self.button_lable = button_label

        if self.button_lable == 'Cancel':
            super().__init__(label=self.button_lable, style=discord.ButtonStyle.danger)

            async def click(interaction: discord.Interaction):
                if await compare_users(interaction, author, interaction.user):
                    await interaction.response.defer()
                    await message.edit(content='Creare organizare anulata.', embed=None, view=None)

        else:
            super().__init__(label=self.button_lable, style=discord.ButtonStyle.blurple)

            async def click(interaction: discord.Interaction):
                if await compare_users(interaction, author, interaction.user):

                    if dropdown.call():
                        await interaction.response.defer()
                        org_dict['Class'][str(author.id)] = dropdown.call()
                        await fifth_message(org_dict, author)
                    else:
                        await interaction.response.send_message(content='Trebuie sa selectezi o clasa!', ephemeral=True)
                        return

        self.callback = click


'''

—————————————————————————————————————————————————————————————————————————————————————————————————
                    Al cincilea mesaj
—————————————————————————————————————————————————————————————————————————————————————————————————

'''


async def fifth_message(org_dict, author, string=None):
    if not string:
        string = '-'
        if org_dict['Info'] != '-':
            string = org_dict['Info']
    org_dict['Info'] = string
    await message.edit(content='', embed=FifthEmbed(org_dict),
                       view=FifthView(author=author, org_dict=org_dict))


class FifthEmbed(discord.Embed):
    def __init__(self, org_dict):
        super().__init__(title=f"Setari finale organizare.",
                         description=f'''ID: {org_dict["ID"]}
                         Activitate: {org_dict["Activity"]}
                         Tier: {org_dict["Type"]}
                         Data si ora: <t:{org_dict["Datetime"]}:f>
                         Info: {org_dict["Info"]}''',
                         color=0x48ff00)


class FifthView(discord.ui.View):
    def __init__(self, author, org_dict):
        super().__init__(timeout=None)

        _lista_elemente = button_labels['Fifth']

        for elem in _lista_elemente:
            button = FifthMsgButtons(elem, author, org_dict)
            self.add_item(button)


class FifthMsgButtons(discord.ui.Button):
    def __init__(self, button_label, author, org_dict):
        self.button_lable = button_label

        if self.button_lable == 'Cancel':
            super().__init__(label=self.button_lable, style=discord.ButtonStyle.danger)

            async def click(interaction: discord.Interaction):
                if await compare_users(interaction, author, interaction.user):
                    await interaction.response.defer()
                    await message.edit(content='Creare organizare anulata.', embed=None, view=None)

        elif self.button_lable == 'Add Info':
            super().__init__(label=self.button_lable, style=discord.ButtonStyle.blurple)

            async def click(interaction: discord.Interaction):
                if await compare_users(interaction, author, interaction.user):
                    modal = FifthModal(org_dict=org_dict, author=author)
                    await interaction.response.send_modal(modal)

        else:
            super().__init__(label=self.button_lable, style=discord.ButtonStyle.success)

            async def click(interaction: discord.Interaction):
                if await compare_users(interaction, author, interaction.user):
                    await interaction.response.defer()

                    if org_dict['Editing']:
                        await org_channel.init_edit(bot=_bot, org_dict=org_dict)
                        await message.edit(content='Organizare modificata cu succes!', embed=None, view=None)
                        org_dict['Editing'] = False
                        return

                    # if not org_dict['Org_utils']:
                    #     guild = await _bot.fetch_guild(BOT_setup.GUILD_ID)
                    #     org_role = await guild.create_role(name=f'Part_{org_dict["ID"]}', mentionable=True,
                    #                                           reason=f'Rol creat pentru org sherpa {org_dict["ID"]}')
                    #
                    #     await author.add_roles(org_role, reason=f'Adaugat roluri pentru creatorul org {org_dict["ID"]}')
                    #
                    #     org_dict['Org_utils'] = {
                    #         'Part': org_role.id
                    #     }

                    await org_channel.initializare_mesaj(bot=_bot, org_dict=org_dict)
                    await message.edit(content=f'Organizare de {org_dict["Activity"]} {org_dict["Type"]} cu ID {org_dict["ID"]} a fost creata cu succes!', embed=None, view=None)

        self.callback = click


class FifthModal(discord.ui.Modal):
    def __init__(self, org_dict, author):
        self.org_dict = org_dict
        self.author = author

        if self.org_dict['Info']:
            info = discord.ui.TextInput(
                label='Adauga info:',
                style=discord.TextStyle.long,
                placeholder='-',
                default=self.org_dict['Info'],
                required=True,
            )
        else:
            info = discord.ui.TextInput(
                label='Adauga info:',
                style=discord.TextStyle.long,
                placeholder='-',  # datetime.now(
                required=True,
            )
        super().__init__(title='Adauga informatii')

        self.add_item(info)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        text = self.children[0]
        text_response = text.value

        if text_response:
            await fifth_message(org_dict=self.org_dict, author=self.author, string=text_response)
        else:
            await fifth_message(org_dict=self.org_dict, author=self.author, string='-')
