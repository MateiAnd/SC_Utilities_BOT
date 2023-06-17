import blizzardapi


client_id = '81f3fad6e7eb4285b84454d179f551c7'

client_secret = '5EmlRd7XsTuZzfIqp1zEfhO742MinCzm'

data = {
    'access_token': 'EUMecThGuNqd7VQGv2VDIp4OGOI7V7CRRm',
    'token_type': 'bearer',
    'expires_in': 86399,
    'sub': '81f3fad6e7eb4285b84454d179f551c7'
}


api_client = blizzardapi.BlizzardApi(client_id, client_secret)

test = api_client.battlenet.oauth.get_user_info(region='eu', access_token='EUMecThGuNqd7VQGv2VDIp4OGOI7V7CRRm')
print(test)



# import requests
#
#
# def create_access_token(client_id, client_secret, region='eu'):
#     data = {'grant_type': 'client_credentials'}
#     response = requests.post('https://%s.battle.net/oauth/token' % region, data=data, auth=(client_id, client_secret))
#     return response.json()
#
#
# response = create_access_token(client_id, client_secret)
# print(response)
