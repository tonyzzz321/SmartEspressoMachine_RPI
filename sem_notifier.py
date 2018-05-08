import json, requests, logging
from oauth2client.service_account import ServiceAccountCredentials

from sem_constants import FCM_SERVICE_ACCOUNT_PRIV_KEY, FCM_API_LINK, FCM_IID_LINK
from server_key import FCM_SERVER_KEY

class Notifier():
   
   def __init__(self, token_path):
      self.logger = logging.getLogger(__name__)
      self.token_path = token_path
      self.token_list = None
      self.__load_token()

   def msg(self, text, level='info'):
      if hasattr(self.logger, level):
         getattr(self.logger, level)(text)

   def __load_token(self):
      self.msg('Attempting to load FCM token database from %s' % self.token_path, 'debug')
      try:
         with open(self.token_path, 'r', encoding='utf-8') as db:
            self.token_list = json.loads(db.read())
         self.msg('FCM token database loaded', 'debug')
      except:
         self.msg('FCM token database does not exist, creating new database', 'debug')
         self.token_list = []
         self.msg('FCM token database created', 'debug')

   def __save_token(self):
      self.msg('Attempting to write FCM token database to %s' % self.token_path, 'debug')
      with open(self.token_path, 'w', encoding='utf-8') as db:
         db.write(json.dumps(self.token_list, indent=3, sort_keys=True, ensure_ascii=False))
      self.msg('FCM token database written to file sucessfully', 'debug')

   def new_token(self, token):
      self.msg('Attempting to add FCM token to database: %s' % token, 'debug')
      self.msg('Checking if FCM token is valid', 'debug')
      header = {'Authorization': 'key=%s' % FCM_SERVER_KEY}
      r = requests.get(FCM_IID_LINK+token, headers=header)
      if r.status_code != 200:
         self.msg('Adding FCM token to database failed: token is not valid', 'debug')
         return 'ERROR: token is not valid'

      self.token_list.append(token)
      self.__save_token()
      self.msg('FCM token added to database', 'debug')
      return 'SUCCESS'

   def clear_token(self):
      self.msg('Attempting to clear FCM token database', 'debug')
      self.token_list = []
      self.__save_token()
      self.msg('FCM token database cleared', 'debug')
      return 'SUCCESS'

   def delete_token(self, token):
      self.msg('Attempting to delete FCM token from database: %s' % token, 'debug')
      if token in self.token_list:
         self.token_list.remove(token)
         self.msg('FCM token deleted from database', 'debug')
         return 'SUCCESS'
      else:
         self.msg('Deleting FCM token from database failed: token is not in database', 'debug')
         return 'ERROR: token not in database'

   def send(self, title, message):
      self.msg('Attempting to send push notification to all registered devices: title=%s, message=%s' % (title, message), 'debug')
      headers = {
         'Authorization': 'Bearer ' + self.__get_access_token('https://www.googleapis.com/auth/firebase.messaging'),
         'Content-Type': 'application/json',
      }
      failed_token_list = []
      all_successful = True
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
            failed_token_list.append(token)
            all_successful = False
            self.msg('Failed sending to device FCM token %s with HTTP error code %s' % (token,str(r.status_code)), 'debug')
         else:
            self.msg('Succeeded sending to device FCM token %s' % token, 'debug')

      if all_successful:
         self.msg('Successfully sending push notication to all registered devices', 'debug')
         return 'SUCCESS'
      else:
         self.msg('Push notication failed to send to some devices, check log for more details', 'debug')
         return 'WARNING: Push notication failed to send to some devices, check log for more details'

   def __get_access_token(self, scopes):
      """Retrieve a valid access token that can be used to authorize requests.

      :return: Access token.
      """
      self.msg('Retrieving access token from Google FCM to authorize push notication requests', 'debug')
      credentials = ServiceAccountCredentials.from_json_keyfile_name(FCM_SERVICE_ACCOUNT_PRIV_KEY, scopes)
      access_token_info = credentials.get_access_token()
      result = access_token_info.access_token
      self.msg('Access token retrieved')
      return result
         