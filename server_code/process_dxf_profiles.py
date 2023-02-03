import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

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
@anvil.server.callable
def createOutputPdf(userData, inputList, prefix, orderId, orderIdStart, heading, type, supplier):
  import anvil.pdf
  from anvil.pdf import PDFRenderer
  if orderIdStart == None:
    newId = prefix + str(orderId)
    fileName = newId
  else:
    newId = prefix + str(orderIdStart) + '-' + prefix + str(orderId)
    fileName = newId
  if supplier is not None:
    fileName =newId + '-' + supplier
  pdf = PDFRenderer(page_size='A4', landscape=True, scale=0.5, filename=fileName + '.pdf').render_form('printTemplates.profiles_exporter_Interactive_pdf_print', inputList, prefix, orderId, heading, supplier)
  app_tables.files.add_row(file=pdf, type=type, owner=userData['User'], supplier=supplier)
  return pdf
  pass

  
@anvil.server.callable
def goodsReceivedPdf(userData, inputList, prefix, orderId, orderIdStart, heading, type, supplier):
  import anvil.pdf
  from anvil.pdf import PDFRenderer
  if orderIdStart == None:
    newId = prefix + str(orderId)
    fileName = newId
    fileName =newId + '-' + supplier + '-' + 'RECEIVED'
  else:
    newId = prefix + str(orderIdStart) + '-' + prefix + str(orderId)
    fileName =newId + '-' + supplier + '-' + 'RECEIVED'
  pdf = PDFRenderer(page_size='A4', landscape=False, scale=0.5, filename=fileName + '.pdf').render_form('printTemplates.goods_received_print', inputList, prefix, orderId, heading, supplier)
  app_tables.files.add_row(file=pdf, type=type, owner=userData['User'], supplier=supplier)
  return pdf
  pass

@anvil.server.callable
def launchProcessProfiles(userData, inputData, prefix, orderId, supplier):
  profilesTask = anvil.server.launch_background_task('processProfiles', userData, inputData, prefix, orderId, supplier)
  return profilesTask
  pass


@anvil.server.background_task
def processProfiles(userData, inputData, prefix, orderId, supplier):
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


  ak = userData['Access Key']
  sk = userData['Secret Key']
  onshape = Onshape('https://cad.onshape.com', ak, sk, logging=False) 
  requireTapping = []

  with TemporaryDirectory(dir = '/tmp') as f:
    for part in inputData:
      did = part['Document ID']
      wvm_type = part['WVM Type']
      wid = part['WVM ID']
      eid = part['Element ID']
      faceId = part['Face Info']['Face']
      configId = part['Configuration']
      url = '/api/documents/d/%s/%s/%s/e/%s/export' % (did, wvm_type, wid, eid)
      viewString = str(part['Face Info']['ViewMatrix'])
      viewString = viewString.strip('[')
      viewString = viewString.strip(']')
      payload = {
          'format': 'DXF',
          'view': viewString, #Convert the list into a string
          'destinationName': 'Export Flatpattern via API',
          'version': '2007',
          'flatten': True,
          'includeBendCenterlines': False,
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
      material = "".join(c for c in part['Material'] if c.isalnum() or c in keepcharacters).rstrip()
      part['Material'] = material
      delimiter = user_data.namingConvention['Delimiter']
      
      if part['Operations'] == '' or part['Operations'] == None:
        #Create dxf name  
        #dxfName = part['Part Number'] + '_' + str(part['Thickness']) + 'mm' + '_' + material + '_' + str(part['Quantity']) + '_' + process + '.dxf'
        dxfName = (part[user_data.namingConvention['field0']] + delimiter + str(part[user_data.namingConvention['field1']]) + 'mm' + delimiter + part[user_data.namingConvention['field2']] + delimiter + str(part[user_data.namingConvention['field3']])
        + delimiter + part[user_data.namingConvention['field5']] + '.dxf')
      else:  
        #Create dxf name  
        #dxfName = part['Part Number'] + '_' + str(part['Thickness']) + 'mm' + '_' + material + '_' + str(part['Quantity']) + '_' + operations + '_' + process + '.dxf'  
        dxfName = (part[user_data.namingConvention['field0']] + delimiter + str(part[user_data.namingConvention['field1']]) + 'mm' + delimiter + part[user_data.namingConvention['field2']] + delimiter + str(part[user_data.namingConvention['field3']]) 
        + delimiter + part[user_data.namingConvention['field4']] + delimiter + part[user_data.namingConvention['field5']] + '.dxf')
        
      #Add dxf filename to part information
      part['DXF Name'] = dxfName
      
      #Save file to temp directory
      method = 'GET'
      payload = {}
      params = query     
      resp = onshape.request(method, path, query=params, body=payload)
      open(os.path.join(f, dxfName), 'wb').write(resp.content)
      #Create list of the files which require hole tapping    
      if part['Hole Data'] is not None:
        requireTapping.append({'File Name':dxfName, 'Hole Data': part['Hole Data']})

      

      #Save the STEP file of a sheet metal part---------------------------------------------------STEP FILE OF FOLDED------------------------------------------------------

      #Get DRAWING of sheet metal folded part and save as PDF to folder---------------------------------------------------DRAWING FILE OF FOLDED------------------------------------------------------

    # Annotate the DXF files 

    #annotateDxf(userData, f, inputData, prefix, orderId, supplier, requireTapping, inputList) #Set all arguments to None, when using to annotate just files not exported with Vulcan
    makeRef = prefix + str(orderId)

    #Get the supplier specific summary pdf from table and save to tempfolder, so that can be saved into the zip
    
    zippedFile = shutil.make_archive(makeRef + '_PROFILES_' + supplier, 'zip', f) 
    mediaZipped = anvil.media.from_file(zippedFile,'zip')
    app_tables.files.add_row(file=mediaZipped, type='PROFILES', owner=userData['User'], supplier=supplier)  
  
  pass