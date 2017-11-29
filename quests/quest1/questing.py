import requests
from quests.utils.config_manager import set_server_url_via_udp
from quests.quest2.questing_resources.authentification import authentification


def whoami(paths, headers):
    show = input('Show user info? [y/n]')
    if show == 'y' or show == 'yes':
        whoami_resp = requests.get(paths['server'] + paths['whoami_url'], headers=headers)
        print(whoami_resp.json())
        if whoami_resp.json().get('user'):
            print('## WhoAmI ##\n' +
              'Name: ' + str(whoami_resp.json()['user']['name']) + '\n' +
              'Finished deliverables: ' + str(whoami_resp.json()['user']['deliverables_done']) + '\n' +
              'Delivered: ' + str(whoami_resp.json()['user']['delivered']))
            print(whoami_resp.json().get('message'))
            return True
        else:
            print('You could not be authenticated')
            return False
    else:
        print('Not showing user info')
        return True


def quest(paths, headers):
    quest_resp = requests.get(paths['server'] + paths['blackboard_url'] + paths['quest_url'], headers=headers)
    quests = []
    available_quests = []
    print('Quest: Available quests: \n')
    for idx, quest in enumerate(quest_resp.json()['objects']):
        print('#################################')
        print('Quest with index: ' + str(idx))
        print(quest['name'])
        print(quest['description'])
        requirements_fullfilled = True
        if quest['requirements']:
            for req in quest['requirements']:
                if req not in paths['requirements']:
                    requirements_fullfilled = False
                    print('\n!!! The requirements for this quest are not fullfilled by our hero :C !!!')
                    break
        if requirements_fullfilled:
            available_quests.append(idx)
            quests.append(quest)
        print()
    quest_no = -1
    print('#################################')
    print('Available quests: ' + str(available_quests))
    while int(quest_no) not in available_quests:
        quest_no = input('Which quest do you want to tackle mighty Heroy? [Index starting from 0] \n > ')
    quest = quests[int(quest_no)]
    print('Quest: Accepted quest ' + quest['name'])
    print('Quest: This quest requires the tokens: ' + str(quest['requires_tokens']))
    print('and requires of you to open the task: ' + str(quest['tasks']))
    return str(int(quest_no) + 1), quest['tasks']


def lookup_task(paths, headers):
    print()
    task_no = input('Quest: Which task are we looking for again? \n > ')
    task_resp = requests.get(paths['server'] + paths['blackboard_url'] + '/tasks/' + task_no, headers=headers)
    if task_resp.status_code == 200:
        print('### This task exists! You are making me proud Heroy! ###')
        print(task_resp.json()['object']['description'])
        print('It seems we have to go to: ' + str(task_resp.json()['object']['location']))
        print('And there to: ' + str(task_resp.json()['object']['resource']))
    return str(task_resp.json()['object']['resource']), task_no


def map(paths, headers, task):
    print()
    print('Quest: Lets look this up on the map')
    map_resp = requests.get(paths['server'] + paths['map_url'], headers=headers)
    map = ''
    print()
    print('Quest: The map: \n' + str(map_resp.json()))
    print()
    for map_item in map_resp.json()['objects']:
        if int(task) in map_item['tasks']:
            print('What do we have here...! The place we have to go: ' + str(map_item['host']))
            map = map_item['host']
            break
    return map


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


def deliver(paths, headers, deliver_token, quest_no, task_uris):
    print()
    print('Quest: Now let us deliver our token. Back to the blackboard!')
    for task_uri in task_uris:
        token = '{"' + task_uri + '":"' + deliver_token + '"}'
        data = '{"tokens":' + token + '}'
        print('Lets give our quest back to: ' + paths['server'] + paths['blackboard_url'] + paths['quest_url'] + '/' + quest_no + paths['deliver_url'])
        last_resp = requests.post(paths['server'] + paths['blackboard_url'] + paths['quest_url'] + '/' + quest_no + paths['deliver_url'],
                              headers=headers, data=data)
        print(last_resp.json())
    try:
        print(last_resp.json()['message'])
        if last_resp.json().get('status') == 'success':
            print("Quest successfully closed! Herrrrroooooooooy Jeeeeenkiiiiiins!!")
        else:
            print(last_resp.json()['error'])
    except Exception as ex:
        print('', end='')
        print('Quest: Could not be completed, caught exception - ' + str(ex))


def exit_check(exit):
    if exit:
        raise Exception('Exiting')

def divide_line():
    print('#################################')

def main():
    divide_line()
    paths = set_server_url_via_udp()

    # Authentication
    user_authenticated = False
    while not user_authenticated:
        exit, headers = authentification('')
        exit_check(exit)
        user_authenticated = whoami(paths, headers)
    print('Authentication Token: ' + str(headers))

    # Questing
    quest_no, task_uris = quest(paths, headers)
    location_url, task = lookup_task(paths, headers)
    quest_host = map(paths, headers, task)
    int_quest_no = int(quest_no)
    if int_quest_no == 1:
        deliver_token = visit_throneroom(headers, quest_host, location_url)
        deliver(paths, headers, deliver_token, quest_no, task_uris)
    elif int_quest_no == 2:
        deliver_token = visit_rats(headers, quest_host, location_url)
        deliver(paths, headers, deliver_token, quest_no, task_uris)


if __name__ == '__main__':
    main()