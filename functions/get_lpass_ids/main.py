import lastpass
from fuzzywuzzy import fuzz
from google.cloud import secretmanager
import google.auth


def get_lpass_master():
    creds, project = google.auth.default()
    client = secretmanager.SecretManagerServiceClient(credentials=creds)
    secret_name = "janium-lastpass-masterpass"
    project_id = "janium0-0"
    request = {"name": f"projects/{project_id}/secrets/{secret_name}/versions/latest"}
    response = client.access_secret_version(request)
    return response.payload.data.decode('UTF-8')

def main(request):
    request_json = request.get_json()
    if request_json and 'client_fullname' in request_json:
        client_fullname = request_json['client_fullname']
        client_fullname = "".join(client_fullname.split()).lower()
    else:
        return {
            'ids': None,
            'Error': 'Payload is missing client_fullname value'
        }

    lpass_secret = get_lpass_master()
    try:
        vault = lastpass.Vault.open_remote('nic@janium.io', lpass_secret)
    except lastpass.exceptions.LastPassUnknownError:
        return {
            'ids': None,
            'Error': 'Device or location not verified. Email sent to nic@janium.io. Verify device or location then request again.'
        }

    return_list = []
    for i in vault.accounts:
        item_name = i.name.decode('utf-8')
        try:
            # site, fullname = tuple(item_name.split("-"))
            split_item = item_name.split("-")
            fullname = split_item[-1]
            if fuzz.ratio(fullname.lower(), client_fullname) > 90:
                return_list.append(
                    {'fullname': fullname, 'id': i.id.decode('utf-8'), 'site': item_name}
                )
        except ValueError:
            pass

    if len(return_list) > 0:
        return {
            'ids': return_list,
            'Error': None
        }
    return {
        'ids': None,
        'Error': 'No matches in lastpass vault for given client name'
    }
