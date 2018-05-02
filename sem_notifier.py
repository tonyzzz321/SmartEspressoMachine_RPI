import json, requests
from oauth2client.service_account import ServiceAccountCredentials

from sem_constants import FCM_SERVICE_ACCOUNT_PRIV_KEY, FCM_API_LINK

class Notifier():
   
   def __init__(self, token_path):
      self.token_path = token_path
      self.token_list = None
      self.__load_token()

   def __load_token(self):
      try:
         with open(self.token_path, 'r', encoding='utf-8') as db:
            self.token_list = json.loads(db.read())
      except:
         self.token_list = []

   def __save_token(self):
      with open(self.token_path, 'w', encoding='utf-8') as db:
         db.write(json.dumps(self.token_list, indent=3, sort_keys=True, ensure_ascii=False))

   def new_token(self, token):
      self.token_list.append(token)
      self.__save_token()
      return 'SUCCESS'

   def clear_token(self, token):
      self.token_list = []
      self.__save_token()
      return 'SUCCESS'

   def delete_token(self, token):
      if token in self.token_list:
         self.token_list.remove(token)
         return 'SUCCESS'
      else:
         return 'ERROR: token not in database'

   def send(self, title, message):

      headers = {
         'Authorization': 'Bearer ' + self.__get_access_token('https://www.googleapis.com/auth/firebase.messaging'),
         'Content-Type': 'application/json',
      }

      for token in self.token_list:
         data = {
            "message": {
               "token" : token,
               "notification" : {
                  "body" : message,
                  "title" : title,
               }
            }
         }
         r = requests.post(FCM_API_LINK, data=json.dumps(data), headers=headers)
         if r.status_code != 200:
            print(r.status_code, r.reason, r.text)
            return 'ERROR'

      return 'SUCCESS'

   def __get_access_token(self, scopes):
      """Retrieve a valid access token that can be used to authorize requests.

      :return: Access token.
      """
      credentials = ServiceAccountCredentials.from_json_keyfile_name(FCM_SERVICE_ACCOUNT_PRIV_KEY, scopes)
      access_token_info = credentials.get_access_token()
      return access_token_info.access_token
         