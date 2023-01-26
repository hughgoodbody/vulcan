import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import anvil.secrets


@anvil.server.callable
def userConfig():
  currentUserConfig = {
   "User":None,
   "Users Suppliers":[],
   "Encoded Access Key":None,
   "Encoded Secret Key":None,
   "Order ID":None,
   "Order Prefix":None,
   "Order Reference":None
}
  currentUser = anvil.users.get_user()
  if currentUser is not None:
    currentUserConfig['User'] = currentUser
    currentUserConfig['Encoded Access Key'] = currentUser['onshape_access_key_encoded']
    currentUserConfig['Encoded Secret Key'] = currentUser['onshape_secret_key_encoded']
    currentUserConfig['Order ID'] = app_tables.numbers.client_readable().get(owner=currentUser)['RefNumber']
    currentUserConfig['Order Prefix'] = app_tables.numbers.client_readable().get(owner=currentUser)['RefPrefix']
    currentUserConfig['Users Suppliers'] = app_tables.suppliers.client_readable().search(owner=[currentUser])
    return currentUserConfig
  else:
    return None

@anvil.server.callable
def onshapeApiKeyCheck(user):  
  if user['onshape_access_key_encrypted'] == None or user['onshape_secret_key_encrypted'] == None:
    #print('TRUE')
    return True
  else:
    #print('FALSE')
    return False

@anvil.server.callable
def onshapeApiKeyRemove(user):
  user.update(onshape_access_key_encrypted=None, onshape_secret_key_encrypted=None)
  return

@anvil.server.callable
def onshapeApiKeyAdd(user, access, secret):
  encryptedAccess = anvil.secrets.encrypt_with_key('vc_onshape_encryption_key',access)
  encryptedSecret = anvil.secrets.encrypt_with_key('vc_onshape_encryption_key', secret)
  user.update(onshape_access_key_encrypted=encryptedAccess, onshape_secret_key_encrypted=encryptedSecret)
  return