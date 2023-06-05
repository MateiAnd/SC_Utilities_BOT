import BOT_setup
import discord.ext.commands


global admin_cmd, donator_cmd, user_cmd, exp_cmd
admin_cmd=''' Aceste comenzi se vor da numai pe <#1075455825205800971>

`/curatenie_generala role_call: rol_clan` — comanda va verifica membri din clan contra membri de pe discord si va afisa membri inactivi peste 30 de zile si membri absenti/ neinregistrati de pe discord.

`/donator_check` — Va genera un raport al donatorilor

`/donator_add @member year:int month:int day:int` — Adauga manual o persoana pe lista de donatori cu data de expirare rol
'''

donator_cmd='''Aceste comenzi se for apela numai pe <#1075455825549742158>

`/trasnfer #voice_channel` — Aceasta comanda te va transfera pe un canal voce indiferent de numarul de membri activi in canal. Exemplu utilizare: Vrei sa intri pe ROOM (3)-3 dar sunt deja 3 persoane, intra pe orice canal voce si apeleaza `/transfer ROOM (3)-3`.

`/lock_channel` — Comanda va restrange user limit-ul pentru canalele de activitati la numarul actual de membri din canal, ca sa nu fiti deranjati cat timp faceti activitati. Restrangerea se reseteaza la inchiderea canalului.
'''

user_cmd = '''Aceste comenzi se for apela numai pe <#1075455825549742158>

`/organizare create` — Programeaza o organizare de Raid / Dungeon / Nightfall / PVP / Gambit / Sezonal care va fi postata pe <#1101037441999179827>. Orice membru al serverului se paote alatura organizarii.

`/organizare edit id:int` — Modifica o organizare creata de tine 
'''

exp_cmd = '''Aceste comenzi se for apela numai pe <#1075455825549742158>

`/sherpa create` — Programeaza o organizare de SHERPA Raid / Dungeon care va fi postata pe <#1101037441999179827>. Orice membru al serverului se paote alatura organizarii. Vei primit un rol temporar cu care ai posibilitati de administrare a canalului special creat pentru activitate

`/sherpa edit id:int` — Modifica o organizare SHERPA creata de tine 


Aceasta comanda se poate apela numai pe <#1101408260642320428>:

`/support_gpt` — Comanda va crea un thread unde ai acces la ChatBro. El este antrenat sa raspunda la intrebarile desrpe serverul de discord si Destiny pana la data de 21 Septembie 2021.
'''


async def init_help(interaction: discord.Interaction, bot: discord.ext.commands.Bot):
    await interaction.response.defer()

    # setup bot
    server = await bot.fetch_guild(BOT_setup.GUILD_ID)
    server_booster = server.get_role(BOT_setup.SERVER_BOOSTER)
    donator_role = server.get_role(BOT_setup.DONATOR_ROLE)
    admin_role = server.get_role(SETUP.ADMIN_ROLE)

    admin_class, donator_class = False, False

    if admin_role in interaction.user.roles:
        admin_class = True

    if server_booster in interaction.user.roles:
        donator_class = True
    elif donator_role in interaction.user.roles:
        donator_class = True

    try:
        await interaction.user.send(content='', embed=HelpMessage(admin_class, donator_class, interaction.user))
        await interaction.followup.send(content='Verifica mesajele private', ephemeral=True)
    except:
        await interaction.followup.send(content='Nu am putut sa iti trimit mesaj, verifica daca ai setarea de privacy pentru servere pe `Allow direct messages from server members` ', ephemeral=True)

class HelpMessage(discord.Embed):
    def __init__(self, admin_class, donator_class, user):
        super().__init__(title=f"Meniu Help KH",
                         description=f'Salut {user.mention}! Iata comenzile botilor nostri la care ai acces:',
                         color=0xf28f06)

        if admin_class:
            self.add_field(name='Ai rol administrativ',
                           value=admin_cmd,
                           inline=False)

            self.add_field(name='‎',
                           value='‎',
                           inline=False)

        if donator_class:
            self.add_field(name='Esti donator, multumim!',
                           value=donator_cmd,
                           inline=False)

            self.add_field(name='‎',
                           value='‎',
                           inline=False)

        self.add_field(name='Comenzi sherpa',
                       value=user_cmd,
                       inline=False)

        self.add_field(name='‎',
                       value='‎',
                       inline=False)

        self.add_field(name='Bot experimental',
                       value=exp_cmd,
                       inline=False)
