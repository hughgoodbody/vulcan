from ._anvil_designer import AdditionalsRowTemplate_printTemplate
from anvil import *
import anvil.server
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class AdditionalsRowTemplate_print(AdditionalsRowTemplate_printTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.drop_down_1.items = self.item['Additional List']
    self.drop_down_1.selected_value = self.item['Part Number']
