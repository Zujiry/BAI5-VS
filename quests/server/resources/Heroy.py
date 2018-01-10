from flask import jsonify, request
from flask_restful import Resource, abort
from quests.utils import get_config, change_config


class Heroy(Resource):
    def __init__(self):
        self.idle = False

    def get(self):
        config = get_config()
        data = {
            "user": config['hero_url'],
            "idle": True,
            "group": config['group'],
            "hirings": config['hero_url'],
            "assignments": config['assignment_url'],
            "messages": config['diary_url'],
            "election": config['election_url'],
            "mutex": config['own_address'] + config['mutex_url'],
            "mutexstate": config['own_address'] + config['mutex_status_url']
        }
        return jsonify(data)

    def post(self):
        json_data = request.get_json(force=True)
        config = get_config()
        group = config['group']
        try:
            message = 'Mighty Heroy Jenkins does not take your pity quest'
            status_code = 418
            take_quest = ''
            while take_quest != 'y' and take_quest != 'n':
                take_quest = input(
                    "Do you want to take part in the quest: {0} of the group {1}? Message: {2}. If you do, you will "
                    "leave your current group and join theirs Answer with [y,n]".format(
                        json_data['quest'], json_data['group'], json_data['message']))
                if take_quest == 'n':
                    break
                elif take_quest == "y":
                    message = 'I\'m in the fun'
                    status_code = 200
                    print(json_data['group'])
                    #post_join_group(group_id)
                    change_config('group', json_data['group'])
                    break
            return jsonify({'message': message}), status_code
        except KeyError or TypeError:
            return abort(400)
