from ._anvil_designer import profiles_exporter_Interactive_pdf_printTemplate
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
from .AdditionalsRowTemplate import AdditionalsRowTemplate
from datetime import date

class profiles_exporter_Interactive_pdf_print(profiles_exporter_Interactive_pdf_printTemplate):
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
    self.orderId = self.dataFromTable['Order ID']

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
    self.additionalList = []
    for i in self.dataFromTable:
      if i['Part Number'] is None:
        self.additionalList.append(i['Part Name'])
      else:
        self.additionalList.append(i['Part Number'])

    self.dropAddSelector.items = self.additionalList
    self.dropAddSelector.placeholder = 'Select Part..'






  def btnAddRow_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.additionalParts.append({'Part Number': self.dropAddSelector.selected_value, 'Thickness': self.txtaddThk.text, 'Material': self.txtAddMat.text, 'Quantity': self.txtAddQty.text, 'Additional List': self.additionalList})
    #print(self.additionalParts)
    self.panel2.items = self.additionalParts
    pass

  def btnExecute_click(self, **event_args):
    """This method is called when the button is clicked"""
    #print(self.additionalParts)
    qtyItems = len(self.panel.items)
    for a in self.additionalParts:
      print(f"a part number:  {a['Part Number'], len(self.additionalParts)}")
      for i in range(0, qtyItems):
        b = self.panel.items[i]
        print(f"b part number:  {b['Part Name'], len(self.panel.items)}")
        if a['Part Number'] == b['Part Number'] or a['Part Number'] == b['Part Name']:
          #b['Additional Variations'] = True #Set this in original dictionary so that it will not be tested again
          #Copy element
          copiedElement = b
          #Update element with thickness, material, quantity and additional variation boolean
          copiedElement['Thickness'] = a['Thickness']
          copiedElement['Material'] = a['Material']
          copiedElement['Quantity'] = a['Quantity']
          #Append element to list
          #self.dataFromTable.append(copiedElement)
          self.panel.items.append(copiedElement)


    #Get unique suppliers
    uniqueSuppliers = list(set(d['Supplier'] for d in self.panel.items))
    #print(uniqueSuppliers)

    #For each unique supplier create a list of the components they will process, Dictionary, 'Supplier': ExSupplier, 'Parts': [List of the parts for this supplier]
    outputList = []
    '''FIND DICTIONARY VALUE IN LIST - Position in List'''
    def findInList(lst, key, value):
      xList = []
      for i, dic in enumerate(lst):
        if dic[key] == value:
          xList.append(lst[i])
      return xList

    self.nSup = len(uniqueSuppliers)
    self.x = 1
    self.supplierProcessList = []
    self.idRef = self.dataFromTable[0]['Order ID']
    self.idRefStart = self.dataFromTable[0]['Order ID']
    for s in uniqueSuppliers:
      #print(s)
      #Get unique ID from table
      supplierSpecificParts = findInList(self.panel.items, 'Supplier', s)

      #HERE IS WHERE THE EXPORT NEEDS TO BEGIN, SO IT IS A SEPERATE EXPORT PER SUPPLIER
      #print(f"Exporting for {s}: {len(supplierSpecificParts)} files")
      #print(supplierSpecificParts)
      #Create PDF Summary forms, get the id number here and pass to server as argument, allows individual forms to be made
      anvil.server.call_s('createOutputPdf', supplierSpecificParts, self.idRef, 'FORM_PDF',s)
      self.processTask = anvil.server.call('launchProcessProfiles', supplierSpecificParts, self.idRef, s)
      self.idRef = self.idRef + 1
      #Add task id to list
      self.supplierProcessList.append(self.processTask.get_id())
      if self.nSup == self.x:
      #Start Timer
        self.timer_1.interval = 0.5
        print(self.supplierProcessList)
      else:
        self.x = self.x+1
      #print(f"Output List for {s}: {foundItems}")
      #print(len(foundItems))
    #Create Master PDF Summary
    self.idRef = str(self.idRefStart) + ' - ' + str(self.idRef)
    anvil.server.call_s('createOutputPdf', self.inputList, self.idRef, 'MASTER_PDF', None)

    #Update order id in table
    pass
