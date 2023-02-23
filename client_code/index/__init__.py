from ._anvil_designer import indexTemplate
from anvil import *
import anvil.server
import anvil.users
from .. import user_data

class index(indexTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    if user_data.userData is False:
      open_form('main')    


  def btnSignIn_click(self, **event_args):
    """This method is called when the button is clicked"""
    while not anvil.users.login_with_form(allow_remembered=True, remember_by_default=True, show_signup_option=True):
      pass
    #Get the current user data which will be required throughout the use of the app, saves repeated calls to tables
    currentUserConfig = anvil.server.call('userConfig')
    currentUser = currentUserConfig['User']
    user_data.userData = currentUserConfig   
    open_form('main') 
    pass

  def link_1_click(self, **event_args):
    """This method is called when the link is clicked"""
    open_form('settings')
    pass




