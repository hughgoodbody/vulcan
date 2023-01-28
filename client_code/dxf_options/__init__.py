from ._anvil_designer import dxf_optionsTemplate
from anvil import *
import anvil.server
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class dxf_options(dxf_optionsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

    self.dropSupplier.items = [(r['supplierName']) for r in app_tables.suppliers.search()]
    self.txtThickness.text = 25
    self.txtMultiplier.text = 1


