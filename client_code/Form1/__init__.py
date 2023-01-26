import time
start_time = time.time()
from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import stripe.checkout
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
from .. import user_data



class Form1(Form1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

    while not anvil.users.login_with_form(allow_remembered=True, remember_by_default=True, show_signup_option=True):
      pass
    #Get the current user data which will be required throughout the use of the app, saves repeated calls to tables
    currentUserConfig = anvil.server.call('userConfig')
    currentUser = currentUserConfig['User']
    print(currentUserConfig)
    print(currentUserConfig['Users Suppliers'][0]['supplierName'])
    user_data.userData = currentUserConfig
    open_form('Form2')
    print ("My program took", time.time() - start_time, "to run")