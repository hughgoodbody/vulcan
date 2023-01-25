import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

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
else:
  anvil.alert('No User Logged In')
