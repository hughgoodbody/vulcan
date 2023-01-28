from ._anvil_designer import mainTemplate
from anvil import *
import anvil.server
import stripe.checkout
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
from .. import user_data
from ..profiles_start import profiles_start




class main(mainTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

    while not anvil.users.login_with_form(allow_remembered=True, remember_by_default=True, show_signup_option=True):
      pass
    #Get the current user data which will be required throughout the use of the app, saves repeated calls to tables
    currentUserConfig = anvil.server.call('userConfig')
    currentUser = currentUserConfig['User']
    #print(currentUserConfig)
    #print(currentUserConfig['Users Suppliers'][0]['supplierName'])
    user_data.userData = currentUserConfig 
    


  def lnkSettings_click(self, **event_args):
    """This method is called when the link is clicked"""
    open_form('settings')
    pass

  def btnProfileExporter_click(self, **event_args):
    """This method is called when the button is clicked"""
    #self.column_application.clear()
    #self.profileExporter = profiles_start() #THIS IS WHAT NEEDS TO BE DONE IN ORDER TO GET CHILD VALUES OUT OF FORM
    #self.column_application.add_component(self.profileExporter)
    open_form('profiles_start')
    pass










