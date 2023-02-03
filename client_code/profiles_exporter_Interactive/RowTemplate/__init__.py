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


    #Set Part Number or Name
    self.lnkUrl.url = self.item['Part URL']
    if self.item['Part Number'] is None:
      self.lnkUrl.text = self.item['Part Name']
    else:  
      self.lnkUrl.text = self.item['Part Number']

    #Set thumbnail image from the 'thumbnail' field - decode from base64
    #print(self.item['Thumbnail'])
    self.imgdata = base64.b64decode(self.item['Part Thumbnail'])    
    mymedia = anvil.BlobMedia('image/png', self.imgdata)
    self.image_1.source = mymedia 

    #Set Material and row colour
    self.dropMaterial.items = user_data.materialLibrary 
    self.dropMaterial.selected_value = self.item['Material']
    #self.txtMaterial.text = self.item['Material']
    if self.dropMaterial.selected_value == '' or self.dropMaterial.selected_value == None:      
      self.background = 'theme:Material Warning'
      #self.item['Warnings'] = 'No material'
      self.lblWarnings.text = 'No material'
      self.lblWarnings.icon = 'fa:exclamation-triangle'



    #Create supplier drop down box 
    supplier = self.item['Supplier']      
    #self.dropSupplier.items = [(r['supplierName']) for r in app_tables.suppliers.search()]
    #self.dropSupplier.items = user_data.userData['Users Suppliers']
    self.dropSupplier.items = [(r['supplierName']) for r in user_data.userData['Users Suppliers']]
    if self.item['Supplier'] != None or self.item['Supplier'] != '':
      supplier = self.item['Supplier']
      self.dropSupplier.selected_value = supplier
    else:
      supplier = self.dropSupplier.selected_value

    #Create the process list
    processList = []
    for i in user_data.userData['Users Suppliers']:
      if i['supplierName'] == supplier:
        for j in i['process']:
          #print(j[0][1])
          processList.append(j[0][1])
    self.dropProcess.items = processList
    self.dropProcess.selected_value = self.dropProcess.items[0]  
    self.item['Process'] = self.dropProcess.selected_value
    


    #Set hole options override drop down
    self.dropHoles.items = ['Ignore', 'Etch', 'Drill']  
    self.item['Undersize Holes'] = self.dropHoles.selected_value
    #Set drill template option
    self.chkDrillTemplate.align = 'center'
    self.item['Drill Template'] = self.chkDrillTemplate.checked  

    #Set drill template option
    self.chkDrillTemplate.align = 'center'
    self.item['Drill Template'] = self.chkDrillTemplate.checked


  def dropSupplier_change(self, **event_args):
    """This method is called when an item is selected"""
    supplier = self.dropSupplier.selected_value
    #Create the process list
    processList = []
    for i in user_data.userData['Users Suppliers']:
      if i['supplierName'] == supplier:
        for j in i['process']:
          #print(j[0][1])
          processList.append(j[0][1])
    self.dropProcess.items = processList
    self.dropProcess.selected_value = self.dropProcess.items[0]  
    self.item['Process'] = self.dropProcess.selected_value    
    #Set row colours
    if self.dropProcess.selected_value == 'Waterjet' and self.dropMaterial.selected_value == '':
      self.background = 'theme:Material Warning'
      self.lblWarnings.text = 'No material'
      self.lblWarnings.icon = 'fa:exclamation-triangle'
    else:      
      if self.dropMaterial.selected_value == '':   
        #print(self.txtMaterial.text)
        self.background = 'theme:Material Warning'
        #self.item['Warnings'] = 'No material'
        self.lblWarnings.text = 'No material'
        self.lblWarnings.icon = 'fa:exclamation-triangle'
      
      elif self.dropProcess.selected_value == 'Waterjet':
        self.background = 'theme:Waterjet'
        self.lblWarnings.text = None
      else:
        self.background = 'theme:Default'
        self.lblWarnings.text = None

    pass

  def dropProcess_change(self, **event_args):
    """This method is called when an item is selected"""
    self.item['Process'] = self.dropProcess.selected_value
    #Set row colours
    if self.dropProcess.selected_value == 'Waterjet' and self.dropMaterial.selected_value == '':
      self.background = 'theme:Material Warning' 
      self.lblWarnings.text = 'No material'
      self.lblWarnings.icon = 'fa:exclamation-triangle'
    else:      
      if self.dropMaterial.selected_value == None:   
        #print(self.txtMaterial.text)
        self.background = 'theme:Material Warning'
        #self.item['Warnings'] = 'No material'
        self.lblWarnings.text = 'No material'
        self.lblWarnings.icon = 'fa:exclamation-triangle'
      
      elif self.dropProcess.selected_value == 'Waterjet':
        self.background = 'theme:Waterjet' 
        self.lblWarnings.text = None
      else:
        self.background = 'theme:Default'
        self.lblWarnings.text = None

  def txtMaterial_change(self, **event_args):
    """This method is called when the TextBox loses focus"""
    #print(self.txtMaterial.select())
    #Set row colours
    if self.dropProcess.selected_value == 'Waterjet' and self.dropMaterial.selected_value == '':
      self.background = 'theme:Material Warning'
      self.lblWarnings.text = 'No material'
      self.lblWarnings.icon = 'fa:exclamation-triangle'
    else:      
      if self.dropMaterial.selected_value == '':   
        #print(self.txtMaterial.text)
        self.background = 'theme:Material Warning'
        #self.item['Warnings'] = 'No material' 
        self.lblWarnings.text = 'No material'
        self.lblWarnings.icon = 'fa:exclamation-triangle'
      
      elif self.dropProcess.selected_value == 'Waterjet':
        self.background = 'theme:Waterjet' 
        self.lblWarnings.text = None
        self.lblWarnings.icon = None
      else:
        self.background = 'theme:Default' 
        self.lblWarnings.text = None
        self.lblWarnings.icon = None
      pass    

  def chkDrillTemplate_change(self, **event_args):
    """This method is called when this checkbox is checked or unchecked"""
    pass

  #Add additional quantity to Quantity in item
  def txtQtyAdd_change(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    self.item['Quantity'] = self.item['Quantity'] + self.txtQtyAdd.text
    pass

  def dropHoles_change(self, **event_args):

    pass







