from quests.utils import get_config
from quests.quest1.questing import search_location
from quests.quest1.blackboard import show_users, show_all_quests, show_available_quests, choose_quest
from quests.quest1.utilities import logout


def main_ui(auth_header, quest):
    print('\nNext Steps')
    print('1: Quests')
    print('2: Taverna')
    print('3: Users')
    print('4: Map')
    print('5: Logout')
    if bool(quest):
        print('6: Quest')
    if get_config()['group_uri'] != '':
        print('7: Group')
    print('else to exit')
    return main_filter(input('Where do you want to go: '), auth_header)


def authentication_ui():
    print('1: Register')
    print('2: Login')
    print('Else: Exit')
    return input('> ')


def main_filter(choice, auth_header):
    choice_filter = {
        '1': choose_quest,
        '3': show_users,
        '4': search_location,
        '5': logout
    }
    return choice_filter.get(choice)(auth_header)




def taverna_ui():
    print('\nTaverna')
    print('1: Adventurers')
    print('2: Groups')
    print('else to go back')
    return input('Which list do you want to see: ')




def group_ui(group_uri):
    print('\nid: to inspect group')
    if group_uri == '':
        print('new: to create new group')
    print('else to go back')
    return input('what do you want to do: ')


def invite_ui():
    print('id: invite to group')
    print('else to go back')
    return input('what to you want to do: ')


def groups(response):
    objects = response.json()['objects']
    print('\nGroups')
    print('\nID\tMembers\tOwner')
    ids = list()
    for group in objects:
        ids.append(str(group['id']))
        print(group['id'], '\t', len(group['members']), '\t', group['owner'])
    return ids


def group(response):
    group = response.json()['object']
    print('Group: ', group['id'], '\t', group['owner'])
    print('Members')
    for member in group['members']:
        print(member)
    return group['_links']['self']


def my_infos(response):
    print('\nMy Status\n')
    user = response.json()['user']
    user_name = user['name']
    print('Name: ', user['name'])
    print('Location: ', user['location'])
    print('Delivered: ', user['delivered'])
    print('Deliverables done: ', user['deliverables_done'])
    print('ip: ', user['ip'])
    return user_name


def users(response):
    print('\nAll Users')
    counter = 1
    for user in response.json()['objects']:
        [print() if ((counter % 10) == 0) else print('', end='')]
        try:
            print(user['name'], end=', ')
        except Exception:
            print('', end='')
        counter = counter + 1


def adventurers(response):
    print('\nAdventurers')
    return response.json()['objects']