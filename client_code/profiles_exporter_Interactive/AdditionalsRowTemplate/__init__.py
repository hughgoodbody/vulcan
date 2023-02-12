from ._anvil_designer import AdditionalsRowTemplateTemplate
from anvil import *
import anvil.server
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class AdditionalsRowTemplate(AdditionalsRowTemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.drop_down_1.items = self.item['Additional List']
    self.drop_down_1.selected_value = self.item['Part Number']

  def drop_down_1_change(self, **event_args):
    """This method is called when an item is selected"""
    listIndex = self.drop_down_1.items.index(self.drop_down_1.selected_value)
    print(listIndex)
    #self.text_box_1.text = get_open_form().self.panel.items[listIndex]['Material']
    pass

    
    
    
