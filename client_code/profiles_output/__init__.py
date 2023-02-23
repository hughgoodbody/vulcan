from ._anvil_designer import profiles_outputTemplate
from anvil import *
import anvil.server
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .downloadTemplate import downloadTemplate
from .. import user_data

class profiles_output(profiles_outputTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    self.files = app_tables.files.search(owner=user_data.userData['User'], type='PROFILES')
  
    #self.downloads = downloadTemplate()
    #self.repeating_panel_1 = self.downloads
    self.repeating_panel_1.items = self.files

    self.pdfMaster = app_tables.files.get(owner=user_data.userData['User'], type='MASTER')
    self.lnkPdfMaster.text = self.pdfMaster['file'].name + ' Summary'
    self.lnkPdfMaster.url = self.pdfMaster['file']

    # Any code you write here will run before the form opens.



