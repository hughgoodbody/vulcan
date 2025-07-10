import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import os

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#

def createOutputPdf(userData, inputList, prefix, orderId, orderIdStart, heading, type, supplier, reference, f):
  import anvil.pdf
  from anvil.pdf import PDFRenderer
  if reference is not None or reference != '':
    #Make reference name file safe  
    keepcharacters = ('.','_', '-','%','(', ')')
    reference = "".join(c for c in reference if c.isalnum() or c in keepcharacters).rstrip()
    fileName =str(prefix) + str(orderId) + '_' + supplier + '_' + 'SUMMARY'
  else:
    fileName =str(prefix) + str(orderId) + '_' + supplier + '_' + 'SUMMARY'
  pdf = PDFRenderer(page_size='A4', landscape=True, scale=0.5, filename=fileName + '.pdf').render_form('printTemplates.profiles_exporter_Interactive_pdf_print', inputList, prefix, orderId, heading, supplier)
  with open(os.path.join(f, fileName + '.pdf'), 'wb+') as destFile:      
      destFile.write(pdf.get_bytes()) 
  #app_tables.files.add_row(file=pdf, type=type, owner=userData['User'], supplier=supplier)
  return pdf
  

def createMasterPdf(userData, inputList, prefix, orderId, orderIdStart, heading, type, supplier, reference):
  import anvil.pdf
  from anvil.pdf import PDFRenderer
  if reference is not None or reference != '':
    #Make reference name file safe  
    keepcharacters = ('.','_', '-','%','(', ')')
    reference = "".join(c for c in reference if c.isalnum() or c in keepcharacters).rstrip()
    fileName =str(prefix) + str(orderId) + '_MASTER'
  else:
    fileName =str(prefix) + str(orderId) + '_MASTER'    
  pdf = PDFRenderer(page_size='A4', landscape=True, scale=0.5, filename=fileName + '.pdf').render_form('printTemplates.profiles_exporter_Interactive_pdf_print', inputList, prefix, orderId, heading, supplier)
  app_tables.files.add_row(file=pdf, type=type, owner=userData['User'], supplier='MASTER')
  return pdf
   

  

def goodsReceivedPdf(userData, inputList, prefix, orderId, orderIdStart, heading, type, supplier, reference, f):
  import anvil.pdf
  from anvil.pdf import PDFRenderer
  if reference is not None or reference != '':
    fileName =str(prefix) + str(orderId) + '_' + supplier + '_' + 'RECEIVED'
  else:
    fileName =str(prefix) + str(orderId) + '_' + supplier + '_' + 'RECEIVED'
  pdf = PDFRenderer(page_size='A4', landscape=False, scale=0.5, filename=fileName + '.pdf').render_form('printTemplates.goods_received_print', inputList, prefix, orderId, heading, supplier)
  with open(os.path.join(f, fileName + '.pdf'), 'wb+') as destFile:      
    destFile.write(pdf.get_bytes()) 
  #app_tables.files.add_row(file=pdf, type=type, owner=userData['User'], supplier=supplier)
  return pdf
  

@anvil.server.callable
def launchProcessProfiles(userData, prefix, orderId, orderIdStart, supplier):
  #Process profiles for each supplier
  profilesTask = anvil.server.launch_background_task('processProfiles', userData, prefix, orderId, orderIdStart, supplier)
  taskId = profilesTask.get_id()
  #Create master PDF
  return profilesTask



@anvil.server.background_task
def processProfiles(userData, prefix, orderId, orderIdStart, supplier):
  import urllib.parse
  from urllib.parse import urlparse
  from urllib.parse import parse_qsl
  from urllib.parse import urlencode
  import urllib.request
  import json
  import requests
  import math
  from pprint import pprint
  import os.path  
  import anvil.media
  import shutil
  from tempfile import TemporaryDirectory
  from .onshape_api.onshape import Onshape
  from . import user_data
  from . import dxf_annotator

  
  inputDataRow = app_tables.transfertable.get(owner=userData['User'], type='supplierParts')
  inputData = inputDataRow['data']
  ak = userData['Access Key']
  sk = userData['Secret Key']
  onshape = Onshape('https://cad.onshape.com', ak, sk, logging=False) 
  requireTapping = []
  reference = inputData[0]['Customer Reference'] 
  numberRef = prefix + str(orderId)

  with TemporaryDirectory(dir = '/tmp') as f:
    for part in inputData:
      if part['Remove'] == True:
        continue
      did = part['Document ID']
      wvm_type = part['WVM Type']
      wid = part['WVM ID']
      eid = part['Element ID']
      faceId = part['Face Info']['Face']
      configId = part['Configuration']
      url = '/api/v5/documents/d/%s/%s/%s/e/%s/export' % (did, wvm_type, wid, eid)
      #print(part['Face Info']['ViewMatrix'])
      viewString = str(part['Face Info']['ViewMatrix'])
      viewString = viewString.strip('[')
      viewString = viewString.strip(']')
      payload = {
          'format': 'DXF',
          'view': viewString, #Convert the list into a string
          'destinationName': 'Export Flatpattern via API',
          'version': '2007',
          'flatten': True,
          'includeBendCenterlines': True,
          'includeSketches': False,
          'sheetMetalFlat': True,
          'triggerAutoDownload': True,
          'storeInDocument': False,
          'configuration': configId,
          'cloudStorageAccountId': '',
          'cloudObjectId':"",
          'partIds': faceId      #THIS IS  A FACEID NOT A PARTID!!!!!!
      }
      method = 'POST'
      params = {}
      resp = onshape.request(method, url, query=params, body=payload)
      dxfUrl = resp.json()['href'] #For use with no client
      query = urlparse(dxfUrl).query
      query = parse_qsl(query)
      path = urlparse(dxfUrl).path

      if part['Process'] == 'Laser':
        process = 'LAS'
      elif part['Process'] == 'Waterjet': 
        process = 'WJ'
      elif part['Process'] == 'Plasma': 
        process = 'PLA'
      elif part['Process'] == 'Oxy Fuel': 
        process = 'OXY'
      elif part['Process'] == 'Saw': 
        process = 'SAW'  
      elif part['Process'] == 'Manual': 
        process = 'MAN'    


      #Make material name file safe  
      keepcharacters = ('.','_', '-','%','(', ')')
      print(f"Part Material 100725: {part['Material']}")
      material = "".join(c for c in part['Material'] if c.isalnum() or c in keepcharacters).rstrip()
      print(f"Part Material Name Cleaned Up 100725: {part['Material']}")
      part['Material'] = material

      delimiter = user_data.namingConvention['Delimiter']
      #part['Operations2'] = ''.join(filter(None, [part['Bend Operation'] , part['Tap Operation'] , part['Drill Operation'] , part['Etch Operation']]))
      #part['Operations'] = ''.join(part['Operations'])
      print(f"Operations Required: {part['Operations']}")
      if part['Operations'] == '' or part['Operations'] == None:
        #Create dxf name  
        #dxfName = part['Part Number'] + '_' + str(part['Thickness']) + 'mm' + '_' + material + '_' + str(part['Quantity']) + '_' + process + '.dxf'
        dxfName = (part[user_data.namingConvention['field0']] + delimiter + str(part[user_data.namingConvention['field1']]) + 'mm' + delimiter + part[user_data.namingConvention['field2']] + delimiter + str(part[user_data.namingConvention['field3']])
        + '.dxf')
      else:  
        #Create dxf name  
        #dxfName = part['Part Number'] + '_' + str(part['Thickness']) + 'mm' + '_' + material + '_' + str(part['Quantity']) + '_' + operations + '_' + process + '.dxf'  
        dxfName = (part[user_data.namingConvention['field0']] + delimiter + str(part[user_data.namingConvention['field1']]) + 'mm' + delimiter + part[user_data.namingConvention['field2']] + delimiter + str(part[user_data.namingConvention['field3']]) 
        + delimiter + part[user_data.namingConvention['field4']] + '.dxf')
        
      #Add dxf filename to part information
      part['DXF Name'] = dxfName
      
      #Save file to temp directory
      method = 'GET'
      payload = {}
      params = query     
      resp = onshape.request(method, path, query=params, body=payload)
      open(os.path.join(f, dxfName), 'wb').write(resp.content)
      #Create list of the files which require hole tapping    
      #if part['Hole Data'] is not None:
        #requireTapping.append({'File Name':dxfName, 'Hole Data': part['Hole Data']})

      

      #Save the STEP file of a sheet metal part---------------------------------------------------STEP FILE OF FOLDED------------------------------------------------------

      #Get DRAWING of sheet metal folded part and save as PDF to folder---------------------------------------------------DRAWING FILE OF FOLDED------------------------------------------------------

    # Annotate the DXF files 
    dxf_annotator.annotateDxf(userData, f, inputData, prefix, orderId, supplier) #Set all arguments to None, when using to annotate just files not exported with Vulcan

    #Create PDF summary files for supplier
    createOutputPdf(userData, inputData, prefix, orderId, None, supplier, 'FORM_PDF', supplier, reference, f)
    goodsReceivedPdf(userData, inputData, prefix, orderId, None, 'Goods Received', 'GOODSRECEIVED_PDF', supplier, reference, f)
    
    

    #Get the supplier specific summary pdf from table and save to tempfolder, so that can be saved into the zip
    #Save Form PDF to the directory so is included in the zip file

    #Save Form PDF to the directory so is included in the zip file

          
    os.chdir('/tmp') #Change directory out of f so we can zip it up  
    zippedFile = shutil.make_archive(numberRef + '_PROFILES_' + supplier, 'zip', f) 
    mediaZipped = anvil.media.from_file(zippedFile,'zip')
    app_tables.files.add_row(file=mediaZipped, type='PROFILES', owner=userData['User'], supplier=supplier)  
    #Get master list data and create pdf
    masterDataRow = app_tables.transfertable.get(owner=userData['User'], type='facesList', suppliername='MASTER')
    masterData = masterDataRow['data']
    createMasterPdf(userData, masterData, prefix, orderId, orderIdStart, 'Order Summary', 'MASTER', supplier, reference)
  
  pass
