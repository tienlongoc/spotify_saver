import requests
import csv
from datetime import date

# TODO: This access token expires in 60 minutes so this is not a helpful way to automate things. To be inproved with some refresh mechanism
access_token = "BQDlOz6hk3PNnFd2R1XWLtV4972DkABAdtJLvGvacXK2BIXiLXqvZRPY4CJGY43m40jhU061Y8bfaVXLLih2bEBbWcXX4UUXNqnS8wNOoYTUDnFWGHeY7NHvMO0tAB7yF8gjRigcsG9Ia5tl4xs5BIk69XRX7u2WLDXMjsC6rf56QA"
token_type = "bearer"
base_url = "https://api.spotify.com/v1/me/tracks"
limit = "50"

today = date.today().isoformat()
output_csv = "saves/oscar_spotify_backup_" + today + ".csv"

def retrieve_details_list(offset):
    # Return 50 tracks #offset, ... , #(offset + 49) from my liked songs list
    params = {
        "access_token": access_token,
        "token_type": token_type,
        "offset": str(offset),
        "limit": limit
    }
    res = requests.get(base_url, params=params)
    items = res.json()["items"]

    if not items:
        # We have reached the end of our search
        return False

    details_list = []

    for item in items:
        artists = ""
        for artist in item["track"]["artists"]:
            artists += artist["name"] + ";"
        if artists:
            artists = artists[:-1]
        track_name = item["track"]["name"]
        external_url = item["track"]["external_urls"]["spotify"]
        spotify_uri = item["track"]["uri"]
        details_list.append((track_name, artists, external_url, spotify_uri))
    return details_list

if __name__ == "__main__":
    with open(output_csv, "w", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        header = ["track_name", "artists", "external_url", "spotify_uri"]
        writer.writerow(header)
        offset = 0
        details_list_batch = retrieve_details_list(offset)
        while details_list_batch:
            writer.writerows(details_list_batch)
            offset += 50
            details_list_batch = retrieve_details_list(offset)
