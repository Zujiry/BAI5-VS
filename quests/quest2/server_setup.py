from flask import Flask, request
from flask_restful import Api
import socket
from quests.utils import change_config
from quests.utils.paths_names import util_own_server


def setup_flask():
    app = Flask(__name__)
    api = Api(app)
    return app, api


from quests.quest2.resources import HeroysCallMeMaybeBack, HeroyJenkins, HeroysDiary, HeroysMightyTasks, HeroyPresident


def add_api(paths, api):
    api.add_resource(HeroyJenkins, paths['hero_url'])
    api.add_resource(HeroysDiary, paths['diary_url'])
    api.add_resource(HeroysMightyTasks, paths['assignment_url'])
    api.add_resource(HeroyPresident, paths['election_url'])
    api.add_resource(HeroysCallMeMaybeBack, paths['callback_url'])
