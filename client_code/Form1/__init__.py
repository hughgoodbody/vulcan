from ._anvil_designer import Form1Template
from anvil import *
import stripe.checkout
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users


class Form1(Form1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

    while not anvil.users.login_with_form(allow_remembered=True, remember_by_default=True, show_signup_option=True):
      pass
    from .. import user_config  
    print(user_config.currentUserConfig)
    print(user_config.currentUserConfig['Users Suppliers'][0]['supplierName'])