import requests
from flask import jsonify, request, abort, json
from flask_restful import Resource
from quests.utils import get_config, change_config, add_to


class HeroysMutex(Resource):
    states = ['released', 'wanting', 'held']

    def get(self):
        config = get_config()
        response = {
            'state': config['state'],
            'time': config['lamport_clock']
        }
        return jsonify(response)

    def post(self):
        print('Received mutex stuff')
        json_data = request.get_json(force=True)
        config = get_config()
        state = config['state']
        lamport_clock = config['lamport_clock']
        stored_requests = config['stored_requests']
        waiting_answers = config['waiting_answers']
        try:
            if json_data['msg'].lower() == 'reply-ok' and len(json_data) == 4:
                print('Received mutex reply-ok')
                print(str(waiting_answers))
                print(json_data['user'])
                if json_data['user'] in waiting_answers:
                    waiting_answers.remove(json_data['user'])
                change_config('waiting_answers', waiting_answers)
                return 200
            elif json_data['msg'].lower() == 'request' and len(json_data) == 4:
                print('Received mutex request')
                if state == 'released' or (state == 'wanting' and json_data['time'] >= lamport_clock):
                    message = 'reply-ok'
                else:
                    print(json_data['reply'])
                    if json_data['reply'] not in stored_requests:
                        stored_requests.append(json_data['reply'])
                    message = 'request'
            else:
                return abort(400)

            print('Lamport')
            if json_data['time'] > lamport_clock:
                lamport_clock = json_data['time']
            lamport_clock += 1

            print('Response build')
            response = {
                'msg': message,
                'time': lamport_clock,
                'user': config['own_address'],
                'reply': config['own_address'] + config['mutex_url']
            }

            change_config('stored_requests', stored_requests)
            change_config('lamport_clock', lamport_clock)
            print(str(response))
            return jsonify(response)
        except KeyError or TypeError as e:
            print('Error working on Mutex post: ' + str(e))
            return abort(400)

    def put(self):
        json_data = request.get_json(force=True)
        try:
            if json_data['message'] == 'release the kraken' and len(json_data) == 1:
                config = get_config()
                lamport_clock = config['lamport_clock']
                stored_requests = config['stored_requests']
                for single_request in stored_requests:
                    response = json.dumps({
                        'msg': 'reply-ok',
                        'time': lamport_clock,
                        'user': config['own_address'],
                        'reply': config['own_address'] + config['mutex_url']
                    })
                    try:
                        print(single_request)
                        response_req = requests.post(single_request, data=response)
                        print(response_req)
                    except Exception as e:
                        print(str(e))
                    lamport_clock += 1
                change_config('lamport_clock', lamport_clock)
                change_config('stored_requests', list())
                return 200
            if json_data['message'] == 'wanting' and len(json_data) == 1:
                change_config('state', 'wanting')
                return 200
            if json_data['message'] == 'released' and len(json_data) == 1:
                change_config('state', 'released')
                return 200
            if json_data['message'] == 'clock' and len(json_data) == 1:
                change_config('lamport_clock', get_config()['lamport_clock'] + 5)
                return 200
            return abort(400)
        except KeyError or TypeError as e:
            print('Error: ' + str(e))
            return abort(400)
