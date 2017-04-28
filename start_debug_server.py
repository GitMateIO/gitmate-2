from os import environ
from subprocess import call
from subprocess import Popen
from time import sleep

import requests

if __name__ == '__main__':
    print('\033[36mBE SURE TO HAVE YOUR SECRETS EXPOSED!\033[0m')

    print('\033[36mgetting a tunnel so you can test GitHub webhooks...\033[0m')
    call(['killall', 'ngrok'])
    Popen(['ngrok', 'http', '8000', '-log', 'stdout'])

    print('\033[36mprecautiously attempting to migrate database...\033[0m')
    call(['python3', 'manage.py', 'migrate'])

    print('\033[36mupmating plugins...\033[0m')
    call(['python3', 'manage.py', 'upmate'])

    print('\033[36mwaiting 2s for the tunnel to start\033[0m')
    sleep(2)
    resp = requests.get('http://127.0.0.1:4040/inspect/http')
    domain = resp.text[resp.text.find('\\"https://')+10:
                       resp.text.find('.ngrok.io') + 9]
    environ['HOOK_DOMAIN'] = domain

    print('\033[36mstarting the server, you are now on your own. '
          '\033[32mGood Luck.\033[0m')
    call(['python3', 'manage.py', 'runserver'])
