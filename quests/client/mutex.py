import requests
import time
from flask import json

from quests.client.utilities import divide_line, logout
from quests.utils import get_config, change_config, add_to
from quests.client.taverna.adventurers import get_all_adventureres
from quests.utils.paths_util import make_http

def mutex_ui(_):
    divide_line()
    print('Welcome to the Mutex UI.')
    print()
    print('1: Request Mutex')
    print('else to exit')
    return mutex_filter(input('\nWhat do you want to do?\n> '))

def mutex_filter(choice):
    choice_filter = {
        '1': request_mutex
    }
    if not choice_filter.get(choice):
        logout('')
    choice_filter.get(choice)()


def request_mutex():
    config = get_config()
    if config['state'] == 'wanting' or config['state'] == 'held':
        print('Already in a state of "wanting" or "held"')
        released =input('Change to released? [y]\n> ')
        if released == 'y':
            change_config('state', 'released')

    if config['state'] != 'wanting' or config['state'] != 'held':
        print('Sending requests to all adventureres')
        change_config('state','wanting')
        adventureres = get_all_adventureres()
        for idx, adventurer in enumerate(adventureres):
            try:
                if 'mutex' in adventurer['capabilities']:
                    response = requests.get(make_http(adventurer['url']), timeout=5)
                    adventurer_mutex_endpoint = response.json()['mutex']
                    data_json = json.dumps({
                        "msg": "request",
                        "time": get_config()['lamport_clock'],
                        "reply": config['own_address'] + config['mutex_url'],
                        "user": config['own_address'] + config['hero_url']
                    })
                    try:
                        response = requests.post(make_http(adventurer['url'] + adventurer_mutex_endpoint), data=data_json, timeout=5)
                        print('Posted mutex request to ' + str(adventurer['url'] + adventurer_mutex_endpoint))
                        change_config('lamport_clock', get_config()['lamport_clock'] + 1)
                        print(str(response.json()))
                        if not response.json().get('msg'):
                            add_to('waiting_answers', adventurer['user'])
                        else:
                            if not response.json().get('msg')== 'reply-ok':
                                add_to('waiting_answers', adventurer['user'])
                    except Exception as e:
                        print('Something is wrong! Just wrong: \n' + str(e))
                else:
                    print('Adventurer ' + str(idx) + ' is not worthy!')
            except Exception as e:
                print('Adventurer ' + str(idx) + ' with url ' + str(adventurer['url']) + ' could not be reached')
                print('But our messenger told us: ' + str(e))

        divide_line()
        tries = 0
        trymax = len(get_config()['waiting_answers'])
        while len(get_config()['waiting_answers']) != 0 and tries <= trymax:
            print('Waiting for ' + str(len(get_config()['waiting_answers'])) + ' answers')
            time.sleep(3)
            if tries == trymax and len(get_config()['waiting_answers']) != 0 :
                print('Did not receive all answers :C. Still entering critial_section')
            tries += 1
        divide_line()
        change_config('lampock_clock', 0)
        change_config('waiting_answers', [])
        print('Entering the critical section')
        change_config('state', 'held')
        time.sleep(3)
        try:
            requests.put(make_http(config['own_address'] + config['mutex_url']), data=json.dumps({"message":"release the kraken"}))
        except Exception as e:
            print('Put the kraken error: ' + str(e))
        print('Leaving the critical section')
        change_config('state', 'released')
        divide_line()