import requests
import sys
import os
import re
import shutil
import datetime
import urllib3

def get_csrf_from_response(data):
    for line in data.splitlines():
        if 'csrfMagicToken' in line:
            c = re.compile('\\"[a-zA-Z0-9,:;]+\\"').search(line).group()
            return c.replace('"', '')
    raise Exception("No CSRF token found in response")

def print_help_and_exit():
    print('Usage: python3 ' + sys.argv[0] + ' <options>')
    print('')
    print('Note: All options can also be passed as environment variables with PFSENSE_<ARG NAME IN CAPS>')
    print('')
    print('Required options:')
    print(' --host <value>                  IP Address or hostname of the PFSense device')
    print(' --username <value>              Username for the PFSense device')
    print(' --password <value>              Password for the user.')
    print('')
    print('Optional options:')
    print(' --allow-untrusted-certificates  Disable TLS verification')
    print(' --encrypt-password <value>      Encrypt backups using this password')
    print(' --out-file <value>              Specify the path of the output file. Defaults to <host>_<date>.xml')
    sys.exit(1)

pfsense_host = os.environ.get('PFSENSE_HOST', '')
pfsense_username = os.environ.get('PFSENSE_USERNAME', '')
pfsense_password = os.environ.get('PFSENSE_PASSWORD', '')
pfsense_tls_verify = os.environ.get('PFSENSE_ALLOW_UNTRUSTED_CERTIFICATES', '') != ''
pfsense_encrypt_password = os.environ.get('PFSENSE_ENCRYPT_PASSWORD', '')
pfsense_backup_name = ''
i = 1
while i < len(sys.argv):
    arg = sys.argv[i]
    if arg == '--host':
        i += 1
        pfsense_host = sys.argv[i]
    elif arg == '--username':
        i += 1
        pfsense_username = sys.argv[i]
    elif arg == '--password':
        i += 1
        pfsense_password = sys.argv[i]
    elif arg == '--allow-untrusted-certificates':
        pfsense_tls_verify = False
    elif arg == '--encrypt-password':
        i += 1
        pfsense_encrypt_password = sys.argv[i]
    elif arg == '--out-file':
        i += 1
        pfsense_backup_name = sys.argv[i]
    else:
        print('Unknown argument ' + arg)
        print_help_and_exit()
    i += 1

if pfsense_host == '' or pfsense_username == '' or pfsense_password == '':
    print_help_and_exit()

if not pfsense_tls_verify:
    urllib3.disable_warnings()

if pfsense_backup_name == '':
    pfsense_backup_name = pfsense_host + '_' + str(datetime.date.today()) + '.xml'

pfsense_backup_url = 'https://' + pfsense_host + '/diag_backup.php'
http = requests.Session()

# 1. fetch the login page to get the CSRF token
response = http.get(pfsense_backup_url, verify=pfsense_tls_verify)
csrf_token = get_csrf_from_response(response.text)

# 2. login to the firewall and grab the new CSRF token
login_params = {
    "login": "Login",
    "usernamefld": pfsense_username,
    "passwordfld": pfsense_password,
    "__csrf_magic": csrf_token,
}
response = http.post(pfsense_backup_url, verify=pfsense_tls_verify, data=login_params)
csrf_token = get_csrf_from_response(response.text)

# 3. stream the backup xml to the output file
backup_params = {
    "download": "download",
    "donotbackuprrd": "yes",
    "__csrf_magic": csrf_token,
}
if pfsense_encrypt_password != '':
    backup_params['encrypt'] = 'yes'
    backup_params['encrypt_password'] = pfsense_encrypt_password

with open(pfsense_backup_name, 'wb') as f:
    with http.post(pfsense_backup_url, verify=pfsense_tls_verify, data=backup_params, stream=True) as r:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
