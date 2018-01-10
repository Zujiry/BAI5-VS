import requests
from quests.client.utilities import divide_line, logout
from quests.utils import paths_util, get_config, change_config
from quests.utils.paths_names import current_quest
from quests.client.questing import solve_quests


def quest_ui(auth_header):
    print('1: The ones I fulfill the requirements of')
    print('2: All')
    print('Else: Exit')
    return quest_filter(input('> '), auth_header)


def quest_filter(choice, auth_header):
    choice_filter = {
        '1': show_available_quests,
        '2': show_all_quests
    }
    if not choice_filter.get(choice):
        logout('')
    return choice_filter.get(choice)(auth_header)


def choose_quest(auth_header):
    divide_line()
    result = quest_ui(auth_header)
    print(str(result))
    print(result[0])
    if result[0]:
        quest_no, quest = result[0], result[1]
        if not quest_no:
            return
    else:
        print('Back to the main Menu')
        return
    response = requests.get(paths_util.quest_uri() + '/' + str(quest_no), headers=auth_header)
    quest_infos(response)
    change_config(current_quest, quest)
    return quest_starter(quest, quest_no, auth_header)


def quest_starter(quest, quest_no, auth_header):
    start = input('## Should we go on a journey to solve this quest or go back to the main menu? [y/n] ##\n> ')
    if start == 'y':
        return solve_quests(quest, quest_no, auth_header)
    else:
        return False


def show_available_quests(auth_header):
    response = requests.get(paths_util.quest_uri(), headers=auth_header)
    quests = []
    available_quests = []
    divide_line()
    print('Available quests: \n')
    for idx, quest in enumerate(response.json()['objects']):
        requirements_fullfilled = True
        if quest['requirements']:
            if type(quest['requirements']) == str:
                if quest['requirements'] not in get_config()['requirements']:
                    requirements_fullfilled = False
                    break
            else:
                for req in quest['requirements']:
                    if req not in get_config()['requirements']:
                        requirements_fullfilled = False
                        break
        if requirements_fullfilled:
            available_quests.append(idx)
            quests.append(quest)
            divide_line()
            print('Quest with index: ' + str(idx))
            print_quest(quest)
    quest_no = -1
    divide_line()
    print('Available quests: ' + str(available_quests))
    while int(quest_no) not in available_quests:
        quest_no = input('\nWhich quest do you want to tackle mighty Heroy? \n You can also go back to the main menu with [n] \n> ')
        if quest_no == 'n':
            return False
    quest = quests[int(quest_no)]
    return (int(quest_no) + 1), quest


def show_all_quests(auth_header):
    response = requests.get(paths_util.quest_uri(), headers=auth_header)
    available_quests = []
    quests = []
    for idx, quest in enumerate(response.json()['objects']):
        divide_line()
        available_quests.append(idx)
        quests.append(quest)
        print_quest(quest)
    divide_line()
    print('Available quests: ' + str(available_quests))
    quest_no = -1
    while int(quest_no) not in available_quests:
        quest_no = input('Which quest do you want to tackle mighty Heroy? \n You can also go back to the main menu with [n] \n> ')
        if quest_no == 'n':
            return False
    quest = quests[int(quest_no)]
    return (int(quest_no) + 1), quest


def print_quest(quest):
    print('Name:         ' + quest['name'])
    print('Description:  ' + quest['description'])
    print('URI:          ' + str(quest['_links']['self']))
    print('Tasks:        ' + str(quest['tasks']))
    print('Deliveries:   ' + str(quest['_links']['deliveries']))
    if quest['requirements']:
        print('Requirements: ' + str(quest['requirements']))


def show_users(auth_header):
    response = requests.get(paths_util.users_uri(), headers=auth_header)
    print('\nWhata bunch of people there are in here. How do we get through these hords?')
    divide_line()
    for user in response.json()['objects']:
        if user.get('name'):
            try:
                print(user['name'], end=', ')
            except UnicodeEncodeError:
                print('Unicode error :/ Bleep')
    print()
    return


def quest_infos(response):
    print('\nThe Quest we are going to solve!')
    object = response.json()['object']
    print(object['name'])
    print(object['description'])
    print()