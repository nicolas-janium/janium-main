import lastpass
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from google.cloud import secretmanager
import google.auth
from google.oauth2 import service_account
from dotenv import load_dotenv
import os
load_dotenv()

# vault = lastpass.Vault.open_remote('nic@janium.io', 'Janium113112')

# fullname = 'Ryan Harris'
# fullname = "".join(fullname.split()).lower()
# client = fullname

# return_list = []
# for i in vault.accounts:
#     name = i.name.decode('utf-8')
#     try:
#         site, fullname = tuple(name.split("-"))
#         if fratio := fuzz.ratio(fullname.lower(), client) > 90:
#             print(fratio)
#             return_list.append(
#                 {'fullname': fullname, 'id': i.id.decode('utf-8'), 'site': site}
#             )
#     except ValueError as verr:
#         print("Vault item has no '-' in name field")

# if len(return_list) > 0:
#     print(return_list)
# else:
#     print("Return list is empty. No matches in lastpass vault for given client name")

def retrieve_lpass_master():
    client = secretmanager.SecretManagerServiceClient(credentials="/home/nicolas/gcp/key.json")
    secret_name = "janium-lastpass-masterpass"
    project_id = "janium0-0"
    request = {"name": f"projects/{project_id}/secrets/{secret_name}/versions/latest"}
    response = client.access_secret_version(request)
    return response.payload.data.decode('UTF-8')

def main(request):
    request_json = request.get_json()

    if request_json and 'client_fullname' in request_json:
        client_fullname = request_json['client_fullname']
    else:
        return "Payload is missing client_fullname value"
    
    client_fullname = "".join(client_fullname.split()).lower()

    lpass_secret = retrieve_lpass_master()
    vault = lastpass.Vault.open_remote('nic@janium.io', lpass_secret)

    vault = lastpass.Vault.

if __name__ == '__main__':
    # print(retrieve_lpass_master())
    # credentials = service_account.Credentials.from_service_account_file('/home/nicolas/gcp/key.json')
    # print(credentials)
    credentials, project = google.auth.default()
    print(credentials, project)