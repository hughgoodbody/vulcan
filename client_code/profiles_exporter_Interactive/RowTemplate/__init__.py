from ._anvil_designer import RowTemplateTemplate
from anvil import *
import anvil.server
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ... import user_data
import base64


class RowTemplate(RowTemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    if self.item['Cut List Qty'] != 0:
      self.item['Quantity'] = self.item['BOM Qty'] * self.item['Cut List Qty']
    else:  
      self.item['Quantity'] = self.item['BOM Qty']

    #Set thumbnail image from the 'thumbnail' field - decode from base64
    #print(self.item['Thumbnail'])
    self.imgdata = base64.b64decode(self.item['Part Thumbnail'])    
    mymedia = anvil.BlobMedia('image/png', self.imgdata)
    self.image_1.source = mymedia 

    #Set Material and row colour
    self.txtMaterial.text = self.item['Material']
    if self.txtMaterial.text == '':      
      self.background = 'theme:Material Warning'
      #self.item['Warnings'] = 'No material'
      self.lblWarnings.text = 'No material'

    #Create supplier drop down box 
    supplier = self.item['Supplier']      
    #self.dropSupplier.items = [(r['supplierName']) for r in app_tables.suppliers.search()]
    #self.dropSupplier.items = user_data.userData['Users Suppliers']
    self.dropSupplier.items = [(r['supplierName']) for r in user_data.userData['Users Suppliers']]

    #Create process drop down box based on chosen supplier
    processList = [(p['process']) for p in user_data.userData['Users Suppliers']['Supplier']]
    self.dropProcess.items = processList
    self.dropProcess.selected_value = processList[0]   
    self.item['Process'] = self.dropProcess.selected_value
    
    if self.item['Supplier'] != None or self.item['Supplier'] != '':
      supplier = self.item['Supplier']
      self.dropSupplier.selected_value = supplier
    else:
      supplier = self.dropSupplier.selected_value

    #Set hole options override drop down
    self.dropHoles.items = ['Ignore', 'Etch', 'Drill']  
    self.item['Undersize Holes'] = self.dropHoles.selected_value
    #Set drill template option
    self.chkDrillTemplate.align = 'center'
    self.item['Drill Template'] = self.chkDrillTemplate.checked  




