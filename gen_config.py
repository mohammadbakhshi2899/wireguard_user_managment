import os
from db_functions import find_last_id


def gen_config():
    id = find_last_id() + 1
    os.mkdir(f'users/{id}')
    os.umask(0o077)
    os.system(f'wg genkey > users/{id}/private.key')
    os.system(f'wg pubkey < users/{id}/private.key > users/{id}/public.key')
    with open(f'users/{id}/private.key', 'r') as fd:
        client_private_key = fd.read()
    with open('public.key', 'r') as fd:
        server_public_key = fd.read()
    with open(f'users/{id}/public.key', 'r') as fd:
        client_public_key = fd.read()

    config_file = f'[Interface]\nAddress = 10.0.0.{id}/32\nPrivateKey = {client_private_key}\nDNS = 1.1.1.1\n\n[' \
                  f'Peer]\nPublicKey = {server_public_key}\nEndpoint = SERVER_ADDRESS:PORT\nAllowedIPs = 0.0.0.0/0\n '

    with open(f'users/{id}/sina_a_m.conf', 'w') as fd:
        fd.write(config_file)

    # Uncomment for adding config file to wireguard service

    # os.system('wg-quick down wg0')
    # with open('/etc/wireguard/wg0.conf', 'a') as fd:
    #   fd.write(f'[Peer]\nPublicKey={client_public_key}\nAllowedIPs=10.0.0.{id}/32')
    # os.system('wg-quick up wg0')

    return f'users/{id}/sina_a_m.conf'


if __name__ == '__main__':
    gen_config()
