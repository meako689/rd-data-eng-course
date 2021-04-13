import os
import json
import requests
from datetime import (timedelta, datetime)


config = json.load(open('config.json', 'r'))


def authorize():
    auth_token = requests.post(url=f"{config['base_url']}{config['auth_url']}",
                               json=config['auth_credentials']
                               )
    auth_header = {'Authorization': f"JWT {auth_token.json()['access_token']}"}
    return auth_header


def get_data(day, auth_header):
    response = requests.get(f"{config['base_url']}{config['data_url']}",
                            json={'date': day},
                            headers=auth_header)
    return response


def main():
    today = datetime.now().date()
    days = [(today - timedelta(days=step)).strftime('%Y-%m-%d')
            for step in range(config['days_to_load'])]

    if not os.path.exists('data'):
        os.mkdir('data')
    auth_header = authorize()

    print("Writing data")
    for day in days:
        response = get_data(day, auth_header)
        if response.status_code == 503:
            auth_header = authorize()
            response = get_data(day, auth_header)
        data = response.json()

        dirname = f"data/out-of-stock-{day}"
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        with open(f"{dirname}/data.json", 'w') as datafile:
            json.dump(data, datafile)
        print(f"date: {day}")
    print("done")


if __name__ == '__main__':
    main()
