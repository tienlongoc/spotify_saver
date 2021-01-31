import requests
import csv
from datetime import datetime
from flask import Flask, request, send_from_directory

# Spotify API endpoints
AUTHORIZATION_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
TRACKS_URL = "https://api.spotify.com/v1/me/tracks"

# Local endpoint details
ENDPOINT_PORT = "5000"

# Client information  of my registered application
CLIENT_ID = "61ea0a206c6a46d0b48dd1113ddeb46e"
CLIENT_HASH_CODE = "NjFlYTBhMjA2YzZhNDZkMGI0OGRkMTExM2RkZWI0NmU6MTU5MjE2MjRiOTI4NGIwMTliYjFhOWM2MTU2ODMxNGI="

# Local server details
UPLOAD_DIRECTORY = "saves/"

def prepare_temporary_access_endpoint(endpoint_uri):
    # Create temporary access endpoint to receive the redirect request once the user gives access permission to Spotify.
    # Read the access token from the request and generate the spotify saver file accordingly.
    app = Flask(__name__)
    @app.route("/", methods=["GET"])
    def endpoint():
        code = request.args.get("code")
        access_token = exchange_code_for_access_token(code, endpoint_uri)
        spotify_saver_file = "spotify_saver_" + datetime.now().isoformat() + ".csv" 
        generate_spotify_saver_file(UPLOAD_DIRECTORY + spotify_saver_file, access_token)
        return send_from_directory(UPLOAD_DIRECTORY, spotify_saver_file, as_attachment=True)

    app.run(host='0.0.0.0', port=ENDPOINT_PORT)

def exchange_code_for_access_token(code, endpoint_uri):
    # Post to the Spotify "token" endpoint with our temporary code to obtain an access token for subsequent use.
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": endpoint_uri
    }
    headers = {
        "Authorization": "Basic " + CLIENT_HASH_CODE
    }
    res = requests.post(TOKEN_URL, data=data, headers=headers)
    return res.json()["access_token"]

def contruct_endpoint_uri():
    # Use a 3rd party service to get the server's external IP.
   return "http://" + requests.get("https://api.ipify.org").text + ":" + ENDPOINT_PORT 

def print_request_url(base_url, params):
    # A helper function that prints the full API request text given the base URL and param dictionaty.
    if not params:
        print(base_url)
    else:
        url = base_url + "?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        print(url[:-1])

def generate_authorization_request(endpoint):
    # Given my application's client_id & endpoint generated just now, generate a Spotify authorization request in the form of a URL.
    # The user will click the URL to prompt Spotify to generate an access token specific to the user's Spotify account.
    # Once Spotify has generated the token, the URL will be redirected to the temporary access endpoint we have spun up.
    # Our endpoint will extract the application access token from the redirect request and start off subsequent processing.
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": endpoint,
        "scope": "user-library-read",
        "expires_in": "3600"
    }
    print("Please go to the following link and give our application read-access to your Spotify app.")
    print_request_url(AUTHORIZATION_URL, params)

def retrieve_details_list(access_token, offset):
    # Return 50 tracks #offset, ... , #(offset + 49) from my liked songs list
    params = {
        "access_token": access_token,
        "token_type": "Bearer",
        "offset": str(offset),
        "limit": "50"
    }
    res = requests.get(TRACKS_URL, params=params)
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

def generate_spotify_saver_file(output_csv, access_token):
    with open(output_csv, "w", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        header = ["track_name", "artists", "external_url", "spotify_uri"]
        writer.writerow(header)
        offset = 0
        details_list_batch = retrieve_details_list(access_token, offset)
        while details_list_batch:
            writer.writerows(details_list_batch)
            offset += 50
            details_list_batch = retrieve_details_list(access_token, offset)
    

if __name__ == "__main__":
    local_endpoint_uri = contruct_endpoint_uri()
    generate_authorization_request(local_endpoint_uri)
    prepare_temporary_access_endpoint(local_endpoint_uri)
