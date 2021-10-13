import requests
import base64
import json
from datetime import datetime,timedelta


class TokenManager():
  def __init__(self):
        self.client_id = "40de8e28b092413e9414d20fcb4f0bad"
        self.client_secret = "b0a75ec4fa2e4bddb7a888787545669f"
        self.mix = self.client_id + ":" + self.client_secret
        self.authorization_token = base64.b64encode(self.mix.encode("ascii")).decode("ascii")

  def get_token(self):
    try:
      with open('token') as infile:
        token = json.load(infile)
      if datetime.strptime(token["expiry"],"%Y-%m-%d:%H:%M:%S") > datetime.now():
        print("TOKEN VALID")
        return token["token"]
    except:
      pass

    status,token = self.request_new_token()
    if status:
      print("NEW TOKEN")
      return token

  def request_new_token(self):
    headers = {
        'Authorization': f'Basic {self.authorization_token}',
    }

    data = {
      'grant_type': 'client_credentials'
    }

    token = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data).json()
    expiry = datetime.now() + timedelta(seconds=token["expires_in"])
    dict = {"token":token["access_token"],"expiry":expiry.strftime("%Y-%m-%d:%H:%M:%S")}
    with open('token', 'w') as outfile:
      json.dump(dict, outfile)

    return (True,token["access_token"])