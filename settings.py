import dotenv
import os
import json

from dotenv import load_dotenv
load_dotenv(dotenv_path='env.txt')


class Settings:
    def __init__(self):
        self.bottoken = os.getenv('BOT_TOKEN')
        self.selfbottoken = os.getenv('SELFBOT_TOKEN')
        self.servers = []
        self.channels = []

        self.load_json()
        
        self.messages_each = 100
        self.results_limit = 10




    def load_json(self):
        with open('servers.json') as fp:
            self.servers = json.load(fp)
        flatten = lambda t: [item for sublist in t for item in sublist]
        self.channels = flatten((item['channels'].values() for item in self.servers))

    def update_json(self):
        with open('servers.json', 'w') as fp:
            json.dump(self.servers, fp)


    def add_channel(self, server_name, channel_name, channel_id):
        server = next(server for server in self.servers if server["name"].lower() == server_name.lower())
        server["channels"][channel_name] = channel_id
        self.update_json()
        self.channels.append(channel_id)

    def delete_channel(self, channel_id):
        server = next(server for server in self.servers if channel_id in server["channels"].values())
        for key, value in dict(server["channels"]).items():
            if value == channel_id:
                shop = key
                del server["channels"][key]
        self.update_json()
        self.channels.remove(channel_id)
        return f"{shop} | {server['name']}"