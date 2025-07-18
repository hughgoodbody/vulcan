from ._anvil_designer import settingsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import user_data
from ..api_key_alert import api_key_alert

class settings(settingsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.user = user_data.userData['User']
    func = anvil.server.call('onshapeApiKeyCheck', self.user)
    if func == False:
      self.btnOnshapeKey.text = 'Delete API Key'
    else:
      self.btnOnshapeKey.text = 'Add API Key'

    # Any code you write here will run before the form opens.

  def btnOnshapeKey_click(self, **event_args):
    """This method is called when the button is clicked"""
    if self.btnOnshapeKey.text == 'Delete API Key':
      anvil.server.call('onshapeApiKeyRemove', self.user)
      self.btnOnshapeKey.text = 'Add API Key'


    elif self.btnOnshapeKey.text == 'Add API Key':
      apk=api_key_alert()
      result = alert(content=apk, title="Enter API Key", large=True, buttons=[('OK',True),('Cancel',False)])
      if result:
        #print(apk.secretKey,apk.accessKey)      
        anvil.server.call('onshapeApiKeyAdd', self.user, apk.accessKey, apk.secretKey)
        self.btnOnshapeKey.text = 'Delete API Key'   
    pass
