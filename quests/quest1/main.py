from quests.utils.config_manager import set_server_url_via_udp
from quests.quest1.ui import main_ui
from quests.quest1.user import authentication, whoami
from quests.quest1.utilities import exit_check, divide_line
from quests.utils import get_config
from quests.utils.paths_util import auth_token as token


def main():
    divide_line()
    if get_config()['server'] != '':
        research = input('Do you want to research for the blackboard host? [y] \n> ')
        if research == 'y':
            set_server_url_via_udp()
    else:
        set_server_url_via_udp()

    # Authentication
    do_it_yourself, already_logged = False, False
    divide_line()
    print('Authentication')
    if get_config().get(token) != '':
        print('- You are already logged in!')
        print()
        hand_login = input('Still... Do you want to login yourself? [y]\n> ')
        if hand_login == 'y':
            do_it_yourself = True
        else:
            already_logged = True
            auth_header = get_config()[token]
            whoami(auth_header)
            divide_line()
    if do_it_yourself or not already_logged:
        user_authenticated = False
        while not user_authenticated:
            exit, auth_header = authentication()
            exit_check(exit)
            user_authenticated = whoami(auth_header)
        print()
    print('Authentication Token: ' + str(auth_header))
    divide_line()
    while True:
        main_ui(auth_header)


if __name__ == '__main__':
    main()