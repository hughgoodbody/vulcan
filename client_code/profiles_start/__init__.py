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
    self.elements, self.elementType, self.configOptions = anvil.server.call('get_elements_configurations', user_data.userData, self.txtUrl.text) #From document_info module
    print(self.elementType)
    pass

