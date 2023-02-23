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
from .AdditionalsRowTemplate import AdditionalsRowTemplate
from datetime import date
import time

class profiles_exporter_Interactive(profiles_exporter_InteractiveTemplate):
  def __init__(self, **properties):
    self.additionalParts = []
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    #Get face data from table
    self.row = app_tables.transfertable.get(owner=user_data.userData['User'], type='facesList', suppliername='MASTER')
    self.materialRow = app_tables.transfertable.get(owner=user_data.userData['User'], type='materials')
    self.dataFromTable = self.row['data']   
    self.materialsList = self.materialRow['data']
    user_data.materialLibrary = self.materialsList
    self.panel = self.repeating_panel_1
    
    self.panel.items = self.dataFromTable
    #print(self.panel.items)
    self.panel2 = self.repeating_panel_2
    self.orderId = self.dataFromTable[0]['Order ID']

    for j in self.panel.items:
      print(j['Operations'])

    

    #Set thumbnail image from the 'thumbnail' field - decode from base64
    self.imgdata = base64.b64decode(self.panel.items[0]['Parent Thumbnail'])    
    mymedia = anvil.BlobMedia('image/png', self.imgdata)
    self.imgAssemblyImage.source = mymedia

    #Parent Name and Link
    self.lnkAssemblyLink.url = self.panel.items[0]['Parent URL']
    self.lnkAssemblyLink.text = self.panel.items[0]['Parent Document Name'] + ' / ' + self.panel.items[0]['Parent Element Name']
    self.lblIdRef.text = self.panel.items[0]['Order Prefix'] + str(self.panel.items[0]['Order ID'])
    self.txtReference.text = self.panel.items[0]['Customer Reference']
    
    

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
    
    self.dropAddSelector.items = [('Select Part...', None)] + self.additionalList 
    
    
    


    

  def btnAddRow_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.additionalParts.append({'Part Number': self.dropAddSelector.selected_value, 'Thickness': self.txtaddThk.text, 'Material': self.txtAddMat.text, 'Quantity': self.txtAddQty.text, 'Additional List': self.additionalList})
    #print(self.additionalParts)
    self.panel2.items = self.additionalParts   
    pass

  def btnExecute_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.taskList = []
    
    #print(self.additionalParts)
    self.processNotification = Notification("Creating profile DXF's... PLease Wait", timeout=None)
    self.processNotification.show()
    


        
        
        
    
    
    
    qtyItems = len(self.panel.items)
    for a in self.additionalParts:
      #print(f"a part number:  {a['Part Number'], len(self.additionalParts)}")      
      for i in range(0, qtyItems):
        b = self.panel.items[i]
        #print(f"b part number:  {b['Part Name'], len(self.panel.items)}")
        if a['Part Number'] == b['Part Number'] or a['Part Number'] == b['Part Name']:
          #b['Additional Variations'] = True #Set this in original dictionary so that it will not be tested again
          #Copy element
          copiedElement = b.copy()
          #Update element with thickness, material, quantity and additional variation boolean
          copiedElement['Thickness'] = a['Thickness']
          copiedElement['Material'] = a['Material']
          copiedElement['Quantity'] = a['Quantity']    
          copiedElement['Drill Template'] = False
          copiedElement['Remove'] = False
          copiedElement['Additional Qty'] = 0
          copiedElement['Variation'] = True
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
    self.prefixRef = self.dataFromTable[0]['Order Prefix']
    self.idRefStart = self.dataFromTable[0]['Order ID']
    #Update the table with user input data - MASTER LIST
    self.row.update(data=self.panel.items)
    
    for s in uniqueSuppliers:  
      #print(s)
      #Get unique ID from table
      supplierSpecificParts = findInList(self.panel.items, 'Supplier', s)   
      
      #HERE IS WHERE THE EXPORT NEEDS TO BEGIN, SO IT IS A SEPERATE EXPORT PER SUPPLIER
      #print(f"Exporting for {s}: {len(supplierSpecificParts)} files")
      #print(supplierSpecificParts) 
      #Create PDF Summary forms, get the id number here and pass to server as argument, allows individual forms to be made
      #Write supplier specific parts to table
      #Update master parts table
      #run background tasks on the above
      #create pdf's in the background tasks
      #anvil.server.call_s('createOutputPdf', user_data.userData, supplierSpecificParts, self.prefixRef, self.idRef, None, s, 'FORM_PDF',s)      
      start_time = time.time()
      app_tables.transfertable.add_row(data=supplierSpecificParts, type='supplierParts',owner=user_data.userData['User'], suppliername=s)
      self.processTask = anvil.server.call('launchProcessProfiles', user_data.userData, self.prefixRef, self.idRef, self.idRefStart, s)
      self.taskList.append(self.processTask)
      print(f"Launch process profiles call duration{(time.time() - start_time)}")
      #Create goods received form
      #anvil.server.call_s('goodsReceivedPdf', user_data.userData, supplierSpecificParts, self.prefixRef, self.idRef, None, 'Goods Received', 'GOODSRECEIVED_PDF', s)
      self.idRef = self.idRef + 1
      #Add task id to list
      #self.supplierProcessList.append(self.processTask.get_id())
      if self.nSup == self.x:
        #Start Timer
        self.timer_1.interval = 0.5
        #print(self.supplierProcessList)
      else:  
        self.x = self.x+1
      #print(f"Output List for {s}: {foundItems}") 
      #print(len(foundItems))
    #Create Master PDF Summary - Only if more than one supplier
    if self.nSup > 1:   
      #print('Printing a Master List')  
      self.idRef = self.idRef - 1
      #anvil.server.call_s('createOutputPdf', user_data.userData, self.panel.items, self.prefixRef, self.idRef, self.idRefStart, 'Order Summary', 'MASTER_PDF', None)  
       
    
    #update order id in table
    # Fetch a row.      
    numberRow = app_tables.numbers.get(owner=user_data.userData['User'])
    # Update method 1
    numberRow.update(RefNumber=self.idRef)
    # Update method 2
    #row['name']="fred" 

  def txtReference_change(self, **event_args):
    """This method is called when the text is changed"""
    user_data.profileOptions['Customer Reference'] = self.txtReference.text
    #self.dataFromTable[0]['Customer Reference'] = self.txtReference.text
    pass



  def dropAddSelector_change(self, **event_args):
    """This method is called when an item is selected"""
    if self.dropAddSelector.selected_value is not None:
      #use the list index of the panel2 (additional items list) this will be the same index as in the main list, but can be found from either part name or part number
      listIndex = self.additionalList.index(self.dropAddSelector.selected_value)      
      self.txtAddMat.text = self.panel.items[listIndex]['Material']
      self.txtAddQty.text = self.panel.items[listIndex]['Quantity']
      self.txtaddThk.text = self.panel.items[listIndex]['Thickness']  
   
    pass

  def timer_1_tick(self, **event_args):
    """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
    for task in self.taskList:
      if task.is_completed():
        self.taskList.remove(task)
      if len(self.taskList) == 0:
        self.processNotification.hide()
        open_form('profiles_output')

      
    pass










      
     

    