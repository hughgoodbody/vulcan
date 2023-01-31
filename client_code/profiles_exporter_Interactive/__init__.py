from ._anvil_designer import profiles_exporter_InteractiveTemplate
from anvil import *
import anvil.server
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import base64
from .. import user_data
from .RowTemplate import RowTemplate
from datetime import date

class profiles_exporter_Interactive(profiles_exporter_InteractiveTemplate):
  def __init__(self, **properties):
    self.additionalParts = []
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    #Get face data from table
    row = app_tables.transfertable.get(owner=user_data.userData['User'])
    self.dataFromTable = row['data']    
    self.panel = self.repeating_panel_1
    self.panel.items = self.dataFromTable
    self.panel2 = self.repeating_panel_2

    #Set thumbnail image from the 'thumbnail' field - decode from base64
    self.imgdata = base64.b64decode(self.panel.items[0]['Parent Thumbnail'])    
    mymedia = anvil.BlobMedia('image/png', self.imgdata)
    self.imgAssemblyImage.source = mymedia

    #Parent Name and Link
    self.lnkAssemblyLink.url = self.panel.items[0]['Parent URL']
    self.lnkAssemblyLink.text = self.panel.items[0]['Parent Document Name'] + ' / ' + self.panel.items[0]['Parent Element Name']
    self.lblIdRef.text = self.panel.items[0]['Order ID']
    self.txtReference.text = self.panel.items[0]['Order Reference']
    

    #Get date 
    today = date.today()    
    # dd/mm/YY
    self.lblDate.text = today.strftime("%d/%m/%Y")

    #Check here if there is no part number
    additionalList = []
    for i in self.dataFromTable:  
      if i['Part Number'] is None:
        additionalList.append(i['Part Name'])
      else:
        additionalList.append(i['Part Number'])
    
    self.dropAddSelector.items = additionalList 
    self.dropAddSelector.selected_value = ''
    
    

    

  def btnAddRow_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.additionalParts.append({'Part Number': self.dropAddSelector.selected_value, 'Thickness': self.txtaddThk.text, 'Material': self.txtAddMat.text, 'Quantity': self.txtAddQty.text})
    print(self.additionalParts)
    self.panel2.items = self.additionalParts
    pass




      
     

    