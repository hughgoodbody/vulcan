import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def launch_list_parts(userData, configParams, profileOptions, documentInfo, elementType):
  from urllib.parse import urlparse  
  import json
  import requests
  import math
  from pprint import pprint  
  #from .geometryFunctions import findExportFaces
  from .onshape_api.onshape import Onshape
  ak = userData['Access Key']
  sk = userData['Secret Key']
  onshape = Onshape('https://cad.onshape.com', ak, sk, logging=False)  

  #Encode configuration string
  did = documentInfo['Document Id']
  eid = documentInfo['Element Id']
  url = '/api/v5/elements/d/%s/e/%s/configurationencodings' % (did, eid)
  method = 'POST'  
  payload = {"parameters": configParams}
  params = {}
  configEncode = onshape.request(method, url, query=params, body=payload)
  configEncode = json.loads(configEncode.content)
  configurationString = configEncode['queryParam'].replace('configuration=','') #remove configuration= from the string, as this is added in the query 

  #Launch background task to list parts
  if elementType == 'ASSEMBLY':
   listPartTask = anvil.server.launch_background_task('list_parts_assembly', userData, documentInfo, configurationString, profileOptions)
   return configurationString, listPartTask
  elif elementType == 'PARTSTUDIO':  
    listPartTask = anvil.server.launch_background_task('list_parts_partstudio', userData, documentInfo, configurationString, profileOptions)




@anvil.server.background_task
def list_parts_assembly(userData, documentInfo, configurationString, profileOptions):
  from urllib.parse import urlparse  
  import json
  import requests
  import math
  from pprint import pprint  
  #from .geometryFunctions import findExportFaces
  from .onshape_api.onshape import Onshape
  ak = userData['Access Key']
  sk = userData['Secret Key']
  onshape = Onshape('https://cad.onshape.com', ak, sk, logging=False)  

  #Construct master URL for form link
  masterUrl = documentInfo['URL'] + '?configuration=' + configurationString
  
  # Get thumbnail
  did = documentInfo['Document Id']
  wvm_type = documentInfo['Workspace Type']
  wid = documentInfo['Workspace Id']
  eid = documentInfo['Element Id']
  url = '/api/v5/assemblies/d/%s/%s/%s/e/%s/shadedviews' % (did, wvm_type, wid, eid) 
  method = 'GET'  
  payload = {}
  viewMatrix='0.612,0.612,0,0,-0.354,0.354,0.707,0,0.707,-0.707,0.707,0' #approximate isometric view, from: https://cad.onshape.com/glassworks/explorer/#/PartStudio
  params = {'viewMatrix':viewMatrix, 'outputHeight':900, 'outputWidth':900, 'pixelSize':0, 'edges':'show', 'useAntiAliasing':False, 'configuration':configurationString}
  #imageStr = client.api_client.request(method, url=base + url, query_params=params, headers=headers, body=payload, _preload_content=False)
  #imageStr = json.loads(imageStr.data)
  imageStr = onshape.request(method, url, query=params, body=payload)  
  imageStr = json.loads(imageStr.content)
  imageStr = imageStr['images'][0]

  url = '/api/v5/assemblies/d/%s/%s/%s/e/%s/bom' % (did, wvm_type, wid, eid)
  method = 'GET'  
  payload = {}
  params = {'indented':False, 'multiLevel':False, 'generateIfAbsent':True, 'configuration':configurationString}
  #api_bom = client.api_client.request(method, url=base + url, query_params=params, headers=headers, body=payload, _preload_content=False)
  #api_bom = json.loads(api_bom.data)
  api_bom = onshape.request(method, url, query=params, body=payload)
  api_bom = json.loads(api_bom.content)
  #pprint(api_bom)

  #Get assembly name and put into dictionary
  assemblyName = api_bom['bomSource']['element']['name']
  documentName = api_bom['bomSource']['document']['name']
  assemblyName = documentName + ' < ' + assemblyName + ' > '
  assemblyInfo = {'Assembly Url': assemblyUrl, 'Assembly Thumbnail': imageStr, 'Assembly Name': assemblyName, 'Profile Options': profileOptions} 

  foundPartsInformation = {'Parent Document Name': api_bom['bomSource']['document']['name'], 
                           'Parent Element Name': api_bom['bomSource']['element']['name'], 
                           'Parent Document ID': did, 'Parent Element ID': eid, 
                           'Parent Configuration': configurationString,
                           'Parent WVM ID': wid, 
                           'Parent WVM Type': wvm_type, 
                           'Parent URL': assemblyUrl, 
                           'Parent Thumbnail': imageStr,
                           'Order ID': None,
                           'Order Prefix': None,
                           'Order Reference': None,
                           'Customer Reference': None,
                           'Supplier': None,
                           'Process': None,
                           'Additional': None,
                           'Delete': None,
                           'Drill template': None,
                           'Material': None,
                           'Operations': None,
                           'Thickness': None,
                           'Undersize Holes': None,
                           'Etch Part Number': None,
                           'Bend Line Marks': None,
                           'Contact Sheet': None,
                           'CSV File': None,
                           'Max thickness': None,
                           'Multiplier': None,}
  
  #Create new headers id dictionary for v5 API
  headerDict = {}
  for h in api_bom['headers']:
    headerDict.update({h['name']: h['id']})
    #pprint(headerList)
  
  #Remove items excluded from laser Search
  api_bom['rows'][:] = [x for x in api_bom['rows'] if x['headerIdToValue'].get(headerDict['Exclude From Laser Search']) == False]
  api_bom['rows'][:] = [x for x in api_bom['rows'] if x['headerIdToValue'].get(headerDict['Exclude from BOM']) == False]
  api_bom['rows'][:] = [x for x in api_bom['rows'] if x['itemSource'].get('isStandardContent') == False]
  #pprint(api_bom['rows'])

  #Go through BOM and get all parts in each discrete document, place each discrete document id in a list for comparison
  docsList = []
  docsDict = {}
  anvil.server.task_state['message'] = 'Analysing Part Geometry'
  for i in api_bom['rows']:
    docid = i['itemSource']['documentId']
    wvm_type = i['itemSource']['wvmType']
    wv = i['itemSource']['wvmId']
    configId = i['itemSource']['fullConfiguration']
    partId = i['itemSource']['partId']
    elementId = i['itemSource']['elementId']
    #Get the parts for each element in the bom
    url = '/api/parts/d/%s/%s/%s' % (docid, wvm_type, wv)
    params = {'elementId':elementId,'includeFlatParts': True, 'configuration':configId}
    method = 'GET'  
    payload = {} 
    api_parts = []
    #api_parts = client.api_client.request(method, url=base + url, query_params=params, headers=headers, body=payload, _preload_content=False)
    #api_parts = json.loads(api_parts.data)
    api_parts = onshape.request(method, url, query=params, body=payload)
    api_parts = json.loads(api_parts.content)

    #If the part has a flat pattern, add a flatId field to the BOM with the flat pattern body ID
    for j in range(0,len(api_parts)):
      if api_parts[j]['isFlattenedBody'] == True:
        flatId = api_parts[j]['partId']
        foldedId = api_parts[j]['unflattenedPartId']
        #print(f'Folded Id:{foldedId}')
        #print(api_bom['bomTable']['items'])
        index = next((i for i, d in enumerate(api_bom['rows']) if d['itemSource']['partId'] == foldedId), None)
        #print(index)
        if index != None:
            #print(api_bom['rows'][index])
            api_bom['rows'][index]['itemSource'].update({'flatId':flatId})


  #Go through amended BOM and get bodies
  for i in api_bom['rows']:
    docid = i['itemSource']['documentId']
    wvm_type = i['itemSource']['wvmType']
    wv = i['itemSource']['wvmId']
    eid = i['itemSource']['elementId']
    configId = i['itemSource']['fullConfiguration']
  
    #Get material
    if i['headerIdToValue'][headerDict['Material']] != None:
      assignedMaterial = i['headerIdToValue'][headerDict['Material']]['displayName']     
    else:
      assignedMaterial = None

    foundPartsInformation.update({'Document ID': docid,
                                  'Element ID': eid,
                                  'Created Version Id': None,
                                  'WVM ID': wv,
                                  'WVM Type': wvm_type,
                                  'Part ID': None,
                                  'Part Name': None,
                                  'Document Name': None,
                                  'Element Name': None,
                                  'Configuration': configId,
                                  'Sheet Metal': None,
                                  'Flat Pattern ID': i['itemSource']['flatId']})  


  
  #If Part Studio

  #If Assembly
  
    #If Cut List
  
    #If Composite part
  return

@anvil.server.background_task
def list_parts_partstudio(userData, documentInfo, configurationString):
  from urllib.parse import urlparse  
  import json
  import requests
  import math
  from pprint import pprint  
  #from .geometryFunctions import findExportFaces
  from .onshape_api.onshape import Onshape
  ak = userData['Access Key']
  sk = userData['Secret Key']
  onshape = Onshape('https://cad.onshape.com', ak, sk, logging=False)  

  #Construct master URL for form link
  masterUrl = url + '?configuration=' + configurationString
  
  # Get thumbnail
  did = documentInfo['Document Id']
  wvm_type = documentInfo['Workspace Type']
  wid = documentInfo['Workspace Id']
  eid = documentInfo['Element Id']
  url = None