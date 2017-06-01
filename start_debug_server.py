#!/usr/bin/env python

from os import environ
from subprocess import call
from subprocess import Popen
import sys

if __name__ == '__main__':
    print('\033[36mBE SURE TO HAVE YOUR SECRETS EXPOSED!\033[0m')

    if '--ngrok' in sys.argv:
        print('\033[36mgetting a tunnel so you can test GitHub webhooks...'
              '\033[0m')
        call(['killall', 'lt'])
        Popen(['lt', '-s', 'testgitmate', '-p', '8000'])
        environ['HOOK_DOMAIN'] = 'testgitmate.localtunnel.me'

    print('\033[36mprecautiously attempting to migrate database...\033[0m')
    call(['python3', 'manage.py', 'migrate'])

    print('\033[36mupmating plugins...\033[0m')
    call(['python3', 'manage.py', 'upmate'])

    environ['DJANGO_DEBUG'] = 'True'

    print('\033[36mstarting the server, you are now on your own. '
          '\033[32mGood Luck.\033[0m')
    call(['python3', 'manage.py', 'runserver'])
