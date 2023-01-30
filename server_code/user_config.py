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
   "Access Key":None,
   "Secret Key":None,
   "Order ID":None,
   "Order Prefix":None,
   "Order Reference":None
}
  currentUser = anvil.users.get_user()
  if currentUser is not None:
    currentUserConfig['User'] = currentUser
    currentUserConfig['Access Key'] = anvil.secrets.decrypt_with_key('vc_onshape_encryption_key', currentUser['onshape_access_key_encrypted'])
    currentUserConfig['Secret Key'] = anvil.secrets.decrypt_with_key('vc_onshape_encryption_key', currentUser['onshape_secret_key_encrypted'])
    currentUserConfig['Order ID'] = app_tables.numbers.get(owner=currentUser)['RefNumber']
    currentUserConfig['Order Prefix'] = app_tables.numbers.get(owner=currentUser)['RefPrefix']
    currentUserConfig['Users Suppliers'] = app_tables.suppliers.search(owner=[currentUser])
    #currentUserConfig['Users Suppliers'] = [r['supplierName'] for r in app_tables.suppliers.search(owner=[currentUser])]
    
    #Clear out existing files from the table
    usersFiles = app_tables.files.search(owner=currentUser)
    for row in usersFiles:
      row.delete()
    #Clear out existing temporary data from the table
    tempData = app_tables.transfertable.search(owner=currentUser)
    for row in tempData:
      row.delete()
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

@anvil.server.callable
def clear_files_table(currentUser):
  usersFiles = app_tables.files.search(owner=currentUser)
  for row in usersFiles:
    row.delete()

@anvil.server.callable
def clear_transfer_table(currentUser):
  usersFiles = app_tables.files.search(owner=currentUser)
  for row in usersFiles:
    row.delete()  

@anvil.server.callable
def clear_all_tables(currentUser):
  usersFiles = app_tables.files.search(owner=currentUser)
  for row in usersFiles:
    row.delete() 
  usersFiles = app_tables.transfertable.search(owner=currentUser)
  for row in usersFiles:
    row.delete()   
