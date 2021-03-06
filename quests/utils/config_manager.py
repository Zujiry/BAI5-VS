import yaml, ast
from pathlib import Path
from socket import *
from .paths_names import util_req, util_own_server
__location__ = Path().cwd()


def get_assignment():
    with (__location__ / 'quests' / 'utils' / 'assignment.yaml').open('r') as stream:
        try:
            return yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def write_assignment(assignment):
    with (__location__ / 'quests' / 'utils' / 'assignment.yaml').open('w') as stream:
        try:
            yaml.dump(assignment, stream, default_flow_style=False)
        except yaml.YAMLError as exc:
            print(exc)


def get_config():
    with (__location__ / 'quests' / 'utils' / 'paths.yaml').open('r') as stream:
        try:
            return yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def write_config(paths):
    with (__location__ / 'quests' / 'utils' / 'paths.yaml').open('w') as stream:
        try:
            yaml.dump(paths, stream, default_flow_style=False)
        except yaml.YAMLError as exc:
            print(exc)


def change_config(path, data):
    config = get_config()
    config[path] = data
    write_config(config)


def add_to(token, data):
    config = get_config()
    config[token].append(data)
    write_config(config)


def rm_from(token, data):
    config = get_config()
    config[token].remove(data)
    write_config(config)


def get_server_url():
    s = socket(AF_INET, SOCK_DGRAM)
    s.settimeout(10)
    s.bind(('', 24000))
    try:
        udp_received = s.recvfrom(1024)
    except Exception as e:
        return '172.19.0.7', '5000'
    port_pre = udp_received[0]
    address_pre = udp_received[1]
    port = ast.literal_eval(port_pre.decode('utf-8'))['blackboard_port']
    address = address_pre[0]
    print('Config: Received {0} as address and {1} as port'.format(address, port))
    return address, port


def set_own_url():
    own_address = 'http://' + gethostbyname(gethostname()) + ':5000'
    change_config(util_own_server, own_address)
    print('Config: Set own address to: ' + own_address)


def set_server_url_via_udp():
    print('Config: Setting server_url')
    paths = get_config()
    server, port = get_server_url()
    server_url = 'http://{0}:{1}'.format(server, port)
    paths['server'] = server_url
    write_config(paths)
    return paths
