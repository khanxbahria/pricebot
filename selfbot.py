import requests
from settings import Settings


class SelfBot:
    def __init__(self):
        self.settings = Settings()
        self.token = self.settings.selfbottoken
        self.headers = {
            'authority': 'discord.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'x-super-properties': 'eyJvcyI6IkxpbnV4IiwiYnJvd3NlciI6IkNocm9tZSIsImRldmljZSI6IiIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChYMTE7IExpbnV4IHg4Nl82NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzc5LjAuMzk0NS4xMzAgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6Ijc5LjAuMzk0NS4xMzAiLCJvc192ZXJzaW9uIjoiIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjcwNzgxLCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==',
            'authorization': self.token,
            'accept-language': 'en-US',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
            'accept': '*/*',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'referer': 'https://discord.com/channels/748300874786406522/748488707304063036',
            # 'accept-encoding': 'gzip, deflate, br',
            'cookie': '_ga=GA1.2.3443953.1600794819; __cfduid=d6331ed3573ca3a495753337a541a1a611603939343; locale=en-US; __cfruid=caec6362891c8599ea4703e32866ed72ef87ed14-1604591757',
        }

    def get_msgs(self,channel,limit=50):
        params = (
            ('limit', str(limit)),
        )
        response = requests.get(f'https://discord.com/api/v8/channels/{channel}/messages', headers=self.headers, params=params)
        return response.json()

