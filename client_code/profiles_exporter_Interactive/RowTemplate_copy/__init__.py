from ._anvil_designer import RowTemplate_copyTemplate
from anvil import *
import anvil.server
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ... import user_data
import base64


class RowTemplate_copy(RowTemplate_copyTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    if self.item['Cut List Qty'] != 0:
      self.item['Quantity'] = self.item['BOM Qty'] * self.item['Cut List Qty']
    else:  
      self.item['Quantity'] = self.item['BOM Qty']

   
