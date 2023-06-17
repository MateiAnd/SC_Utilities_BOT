import requests


class APiHandler:
    def __init__(self, client_id, client_secret):
        self.client_secret = client_secret
        self.client_id = client_id
        self.access_token = None

    def _create_access_token(self, region='eu'):
        """ Creare token de acces API si impachetat in format dict cu expirare"""
        from datetime import datetime
        data = {'grant_type': 'client_credentials'}
        response = requests.post('https://%s.battle.net/oauth/token' % region, data=data, auth=(self.client_id, self.client_secret))
        result = response.json()

        new_format = {
            'access_token': result.get('access_token', None),
            'token_type': result.get('token_type', 'error'),
            'expires_at': datetime.now().timestamp() + result.get('expires_in', 0),
            'sub': result.get('sub', 'error')
        }

        return new_format

    def _handle_access_token(self):
        """  """
        from datetime import datetime
        if self.access_token == None:
            self.access_token = self._create_access_token('eu')
        else:
            if self.access_token['expires_at'] < datetime.now().timestamp():
                self.access_token = self._create_access_token('eu')
        if self.access_token == None:
            return self._handle_access_token()


    def get_user_data(self):
        self._handle_access_token()

        url = 'https://eu.battle.net/oauth/userinfo'
        data = {
            'access_token': self.access_token['access_token'],
            'region': 'eu'
        }

        response = requests.get(url, data=data ,auth=(self.client_id, self.client_secret))

        return response.content


base_url = 'oauth.battle.net/{API path}'

client_id = '81f3fad6e7eb4285b84454d179f551c7'

client_secret = '5EmlRd7XsTuZzfIqp1zEfhO742MinCzm'

data = {
    'access_token': 'EUMecThGuNqd7VQGv2VDIp4OGOI7V7CRRm',
    'token_type': 'bearer',
    'expires_in': 86399,
    'sub': '81f3fad6e7eb4285b84454d179f551c7'
}

test = APiHandler(client_id, client_secret)

print(test.get_user_data())
