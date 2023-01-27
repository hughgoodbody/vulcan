from ._anvil_designer import profiles_startTemplate
from anvil import *
import anvil.server
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import user_data

class profiles_start(profiles_startTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    

  def btnGetConfigs_click(self, **event_args):
    """This method is called when the button is clicked"""   
    self.txtUrl.text = 'https://cad.onshape.com/documents/0740e62af91b4a69c5cb92f8/w/101c03aa7b9ecdde77d140ca/e/bc096209b90c889565acc50a'
    self.elements, self.elementType, self.configOptions = anvil.server.call('get_elements_configurations', user_data.userData, self.txtUrl.text) #From document_info module
    pass

