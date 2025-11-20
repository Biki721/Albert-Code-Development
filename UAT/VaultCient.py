# Developer : Basil TT(basil.tt@hpe.com)
# Date: 25th March 2021
# Version: 2.0
#######################################

import getpass
import re
import uuid
import os
import socket
import json

# Fetch below values from config file
host_fqdn = 'd2wg10130.s10.its.hpecorp.net'
host_port = 443
environment = 'development'


class VaultAPIError(Exception):
    pass


def fetch_secret_from_vault(secret_name: str) -> dict:
    """
    method to fetch the secret from hashicorp vault
    :param secret_name: Name/Alias of the secret as string
    :return: username and password of the secret as dictionary
    """
    request_info = {"action": "retrieve",
                    "environment": environment,
                    "mac_id": ':'.join(re.findall('..', '%012x' % uuid.getnode())),
                    'username': getpass.getuser(),
                    'ip_address': socket.gethostbyname(socket.gethostname()),
                    'domain': os.environ['userdomain'],
                    'secret_name': secret_name}
    request_info_str = json.dumps(request_info)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host_fqdn, host_port))
        client.send(request_info_str.encode('ascii'))
        msg_from_server = client.recv(10240)
        msg_content = msg_from_server.decode('ascii')
        msg_content_dict = json.loads(msg_content)
        if "message" not in msg_content_dict:
            return msg_content_dict
        else:
            raise VaultAPIError(msg_content_dict["message"])
    except VaultAPIError:
        raise VaultAPIError(msg_content_dict["message"])
    except Exception as e:
        raise VaultAPIError(
            f'Unable to fetch secret from "{host_fqdn}:{host_port}" - {str(e)}')
