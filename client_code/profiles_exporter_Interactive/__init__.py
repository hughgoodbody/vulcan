from ._anvil_designer import profiles_exporter_InteractiveTemplate
from anvil import *
import anvil.server
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class profiles_exporter_Interactive(profiles_exporter_InteractiveTemplate):
  def __init__(self, tableData, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.panel = self.repeating_panel_1
    self.panel.items = tableData  
    self.refresh_data_bindings()
    #print(self.panel.items[0])
    #print(tableData)

    # Any code you write here will run before the form opens.

