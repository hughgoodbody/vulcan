from ._anvil_designer import api_key_alertTemplate
from anvil import *

class api_key_alert(api_key_alertTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    #https://anvil.works/forum/t/custom-alert-window-output/15726
  def txtSecretKey_change(self, sender, **event_args):
    """This method is called when the text in this text box is edited"""
    self.secretKey = sender.text  
    pass

  def txtAccessKey_change(self, sender, **event_args):
    """This method is called when the text in this text box is edited"""
    self.accessKey = sender.text
    pass
