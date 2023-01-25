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
currentUserConfig['User'] = currentUser