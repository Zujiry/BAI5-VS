import json

import requests
from quests.utils.election_algorithm import start_election
from quests.client.taverna.groups import send_assignment_to_group
from quests.utils import get_config, change_config
from quests.utils.paths_names import util_group, util_recv_tokens, util_user
from quests.client.utilities import divide_line


def solve_quests(quest, quest_no, auth_header):
    # Questing
    location_url, task = lookup_task(auth_header)
    quest_host = search_location(auth_header, task)
    int_quest_no = int(quest_no)
    print(str(int_quest_no))

    if int_quest_no == 1:
        deliver_token = visit_throneroom(auth_header, quest_host, location_url)
        deliver(auth_header, deliver_token, quest_no, quest['tasks'])
    elif int_quest_no == 2:
        deliver_token = visit_rats(auth_header, quest_host, location_url)
        deliver(auth_header, deliver_token, quest_no, quest['tasks'])
    elif int_quest_no == 3 and get_config()[util_group] != '':
        deliver_token = visit_wounded(auth_header, quest_host, location_url)
        deliver(auth_header, deliver_token, quest_no, quest['tasks'])
    elif int_quest_no == 4 and get_config()[util_group] != '':
        print('There should be at least 2 people with a running server in your group and one that can be connected during the quest and is higher in order by name')
        print('String order: A < a, itoo < itoo2')
        deliver_token = visit_elves(auth_header, quest_host, location_url)
        if type(deliver_token) == list:
            deliver(auth_header, deliver_token[1], quest_no, quest['tasks'])
        else:
            deliver(auth_header, deliver_token, quest_no, quest['tasks'])
    elif int_quest_no == 5:
        deliver_token = visit_northern_wilds(auth_header, quest_host, location_url)
    else:
        print('Sorry, you do not have the required requirements to solve this. Back to the Main UI.')


def lookup_task(headers):
    print()
    task_no = input('Which task are we looking for again? \n[Should be written in the tasks of the quest above]\n > ')
    task_resp = requests.get(get_config()['server'] + get_config()['blackboard_url'] + '/tasks/' + task_no, headers=headers)
    if task_resp.status_code == 200:
        print('### This task exists! You are making me proud Heroy! ###')
        print()
        print(task_resp.json()['object']['name'])
        print()
        print(task_resp.json()['object']['description'])
        if task_resp.json()['object'].get('required_players'):
            print('Required Players: ' + str(task_resp.json()['object'].get('required_players')))
        print('It seems we have to go to: ' + str(task_resp.json()['object']['location']))
        print('And there to: ' + str(task_resp.json()['object']['resource']))
    return str(task_resp.json()['object']['resource']), task_no


def search_location(auth_header, task):
    print()
    print('## Lets look this up on the map ##')
    map_resp = requests.get(get_config()['server'] + get_config()['map_url'], headers=auth_header)
    map = ''
    print()
    look_at_map(auth_header)
    print()
    for map_item in map_resp.json()['objects']:
        if int(task) in map_item['tasks']:
            print('What do we have here...! The place we have to go: ' + str(map_item['host']))
            map = map_item['host']
            break
    input('Ready to go? \n> So ready!')
    return map


def look_at_map(auth_header):
    print()
    print('Lets look at our map')
    map_resp = requests.get(get_config()['server'] + get_config()['map_url'], headers=auth_header)
    print()
    if map_resp.json()['status'] == 'success':
        print('Map: \n')
        for location in map_resp.json().get('objects'):
            print('Name:     ' + location['name'])
            print('Host:     ' + location['host'])
            print('Tasks:    ' + str(location['tasks']))
            print('Visitors: ' + str(location['visitors']))
            divide_line()
    print()
    return


def deliver(headers, deliver_token, quest_no, task_uris):
    print()
    print('Quest: Now let us deliver our token. Back to the blackboard!')
    for task_uri in task_uris:
        token = '{"' + task_uri + '":"' + deliver_token + '"}'
        data = '{"tokens":' + token + '}'
        print('Lets give our quest back to: ' + get_config()['server'] + get_config()['blackboard_url'] + get_config()['quest_url'] + '/' + str(quest_no) + get_config()['deliver_url'])
        last_resp = requests.post(get_config()['server'] + get_config()['blackboard_url'] + get_config()['quest_url'] + '/' + str(quest_no) + get_config()['deliver_url'],
                              headers=headers, data=data)
    try:
        print(last_resp.json()['message'])
        if last_resp.json().get('status') == 'success':
            print("Quest successfully closed! Herrrrroooooooooy Jeeeeenkiiiiiins!!")
        else:
            print(last_resp.json()['error'])
    except Exception as ex:
        print('', end='')
        print('Quest: Could not be completed, caught exception - ' + str(ex))


def visit_throneroom(headers, quest_host, location_url):
    print()
    print('Quest: Finally, we arrived at {0}{1}. Lets see what we can find at this place!'.format(quest_host,
                                                                                                   location_url))
    visit_resp = requests.post('http://' + quest_host + location_url, headers=headers)
    print(visit_resp.json()['message'] + ' with token: ' + visit_resp.json()['token_name'])
    throneroom_token = visit_resp.json()['token']
    print()
    print('You acquired the token! \n' + str(throneroom_token))
    return throneroom_token


def visit_rats(headers, quest_host, location_url):
    print()
    print('Quest: Finally, we arrived at {0}{1}. Lets see what we can find at this place!'.format(quest_host,
                                                                                                  location_url))
    visit_resp = requests.get('http://' + quest_host + location_url, headers=headers)
    # print(visit_resp.json()['message'])
    print(visit_resp.json()['message'])
    tokens = []
    if visit_resp.json().get('next'):
        print('Seems there is another way: ' + visit_resp.json()['next'])
        tokens = visit_rats(headers, quest_host, visit_resp.json()['next'])
        tokens_string = '['
        for idx, token in enumerate(tokens):
            if idx == len(tokens)-1:
                tokens_string += '"' + token + '"]'
            else:
                tokens_string += '"' + token + '",'
        data = '{"tokens":' + tokens_string + '}'
        print('Uff... we finished fighting.')
        rat_resp = requests.post('http://' + quest_host + visit_resp.json()['next'], headers=headers, data=data)
        print(rat_resp.json()['message'])
        return rat_resp.json()['token']
    elif visit_resp.json().get('steps_todo'):
        print('Argh, there are other things to do here... : ' + str(visit_resp.json().get('steps_todo')))
        for step in visit_resp.json().get('steps_todo'):
            tokens.append(visit_rats(headers, quest_host, step)[0])
        return tokens
    else:
        print('So... We actually have to do something :O? Attack!!!')
        return fight_rats(headers, quest_host, location_url)


def fight_rats(headers, quest_host, step):
    visit_resp = requests.post('http://' + quest_host + step, headers=headers)
    print(visit_resp.json()['message'])
    print('We got something... ew: ' + visit_resp.json()['token_name'])
    return visit_resp.json()['token'], visit_resp.json()['token_name']


def visit_wounded(auth_header, quest_host, location_url):
    divide_line()
    print('We arrived at {0}{1}. Lets see what where we can help!'.format(quest_host, location_url))
    visit_resp = requests.get('http://' + quest_host + location_url, headers=auth_header)
    print(visit_resp.json())
    print()
    print('Message: ' + str(visit_resp.json()['message']))
    tokens = []
    if visit_resp.json().get('steps_todo'):
        change_config(util_recv_tokens,[])
        print('Next Steps: ' + str(visit_resp.json().get('steps_todo')))
        for step in visit_resp.json()['steps_todo']:
            step_result = visit_wounded(auth_header, quest_host, step)
            if step_result:
                tokens.append(step_result)
        divide_line()
        for tk in get_config()[util_recv_tokens]:
            tokens.append(tk)
        input('Received all tokens?')
        tokens_string = '['
        for idx, token in enumerate(tokens):
            if idx == len(tokens) - 1:
                tokens_string += '"' + token + '"]'
            else:
                tokens_string += '"' + token + '",'
        data = '{"tokens":' + tokens_string + '}'
        quest_resp = requests.post('http://' + quest_host + location_url, headers=auth_header, data=data)
        print(quest_resp)
        print(quest_resp.json())
        token = quest_resp.json()['token']
    else:
        divide_line()
        send_as = input('Send as an assignment? [y]\n> ')
        if send_as == 'y':
            send_assignment_to_group(auth_header, '', id=2, task='4', resource=quest_host + location_url,
                                 task_data='', method='POST',
                                 message='Help me with Quest 3 please! Send me the token to callback :)')
            return False
        else:
            post_to = requests.post('http://' + quest_host + location_url, headers=auth_header)
            print('Aquired Token! ' + post_to.json()['token_name'])
            return post_to.json()['token']
    return token


def visit_elves(auth_header, quest_host, location_url):
    divide_line()
    visit_resp = requests.get('http://' + quest_host + location_url, headers=auth_header)
    print(visit_resp.json()['message'])
    divide_line()
    assignment_data = {
        "id": 300000,
        "task": '/blackboard/tasks/7',
        "resource": (quest_host + location_url),
        "method": 'POST',
        "data": {"group":get_config()[util_group]},
        "callback": get_config()['callback_url'],
        "message": 'Help! Save the elves! Put on the ring!'
    }
    change_config(util_recv_tokens, [])
    start_election(job_data=assignment_data)
    divide_line()
    input('Did you get back the election result? Should have callbacked!\n> ')
    return get_config()[util_recv_tokens]
    '''
    data  = json.dumps({"group":get_config()[util_group]})
    leader_resp = requests.post('http://' + quest_host + location_url, headers=auth_header, data=data)
    print(leader_resp.status_code)
    print(leader_resp.json())
    data = json.dumps({"group": get_config()[util_group], "token": leader_resp.json()['token']})
    ok_resp =  requests.post('http://' + quest_host + location_url, headers=auth_header, data=data)
    print(ok_resp.json())
    '''


def visit_northern_wilds(auth_header, quest_host, location_url):
    divide_line()
    print('We arrived at {0}{1}. Lets see what where we can help!'.format(quest_host, location_url))
    visit_resp = requests.get('http://' + quest_host + location_url, headers=auth_header)
    print(visit_resp.json())
    print()
    print('Message: ' + str(visit_resp.json()['message']))
    if visit_resp.json().get('next'):
        visit_northern_wilds(auth_header, quest_host, visit_resp.json().get('next'))
    if visit_resp.json().get('critical_section'):
        print('Such wow, critical section')