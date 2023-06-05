import openai


async def ask_gpt(message_history) -> str:
    with open("./chat_gpt/api_key.txt", "r") as f:
        openai.api_key = f.read().strip('\n')

    reply = await openai.ChatCompletion.acreate(
        model='gpt-3.5-turbo',  # 'davinci:ft-personal-2023-03-30-10-48-13',  #
        messages=message_history,  # [{"role": "user", "content": message_history}]
        temperature=0
    )

    # print(reply)

    message_history.append({'role': 'assistant', 'content': reply.choices[0].message.content})

    tokens = reply.usage.total_tokens

    return message_history, tokens


async def init_gpt(message_history):
    reply = await openai.ChatCompletion.acreate(
        model='gpt-3.5-turbo',
        messages=message_history,  # [{"role": "user", "content": message_history}]
        temperature=0
    )

    message_history.append({'role': 'assistant', 'content': reply.choices[0].message.content})

    return message_history


async def hello_gpt(name) -> str:
    welcome_str = '''Esti asistentul virtual al celei mai mari comunitati de destiny 2, pe un server de discord. Genereaza un mesaj diferit in acelasi stil si aceleasi informatii cu modelul urmator, fara sa mentionezi Discord : 'Salut {nume} ! Registerul cu Warmind (Charlemange) este obligatoriu in cadrul comunitatii noastre, deci o sa fie nevoie să iți dai register ca să poți avea acces la canalele de pe server.
Te rog să mergi pe <#938290015195238400> și să urmezi pașii de acolo.
Dacă dai join pe unul dintre clanuri, te rog să dai tag responsabililor de clan pe <#938294344853647431>.
Dacă întâmpini probleme, te rog să vorbesti cu ChatBro in threadul de mai jos, este un bot foarte inteligent.'''
    reply = await openai.ChatCompletion.acreate(
        model='gpt-3.5-turbo',
        messages=[{"role": "user", "content": welcome_str.format(nume=name)}],
        temperature=0
    )

    # print(reply)

    return reply.choices[0].message.content
