from ._anvil_designer import RowTemplateTemplate
from anvil import *
import anvil.server
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ... import user_data

class RowTemplate(RowTemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

    #Create supplier drop down box 
    supplier = self.item['Supplier']      
    #self.dropSupplier.items = [(r['supplierName']) for r in app_tables.suppliers.search()]
    self.dropSupplier.items = user_data.userData['Users Suppliers']
    
    if self.item['Supplier'] != None or self.item['Supplier'] != '':
      supplier = self.item['Supplier']
      self.dropSupplier.selected_value = supplier
    else:
      supplier = self.dropSupplier.selected_value




