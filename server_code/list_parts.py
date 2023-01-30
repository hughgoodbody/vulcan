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
  allParts = []
  partsAndFacesToTest = []
  import time
  start_time = time.time()
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
  assemblyInfo = {'Assembly Url': masterUrl, 'Assembly Thumbnail': imageStr, 'Assembly Name': assemblyName, 'Profile Options': profileOptions} 

  foundPartsInformation = {'Parent Document Name': api_bom['bomSource']['document']['name'], 
                           'Parent Element Name': api_bom['bomSource']['element']['name'], 
                           'Parent Document ID': did, 'Parent Element ID': eid, 
                           'Parent Configuration': configurationString,
                           'Parent WVM ID': wid, 
                           'Parent WVM Type': wvm_type, 
                           'Parent URL': masterUrl, 
                           'Parent Thumbnail': imageStr,
                           'Order ID': userData['Order ID'],
                           'Order Prefix': userData['Order Prefix'],
                           'Order Reference': userData['Order Reference'],
                           'Customer Reference': profileOptions['Reference'],
                           'Supplier': profileOptions['Supplier'],
                           'Process': None,
                           'Additional': None,
                           'Delete': None,
                           'Drill template': None,
                           'Material': None,
                           'Operations': None,
                           'Thickness': None,
                           'Undersize Holes': profileOptions['Hole Options'],
                           'Etch Part Number': profileOptions['Etch Part Number'],
                           'Bend Line Marks': profileOptions['Bend Line Marks'],
                           'Contact Sheet': profileOptions['Contact Sheet'],
                           'CSV File': profileOptions['CSV File'],
                           'Max thickness': profileOptions['Max Thickness'],
                           'Multiplier': profileOptions['Multiplier'],}


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
    #Add element for a flat pattern id
    i['itemSource'].update({'flatId':None})
    
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
            api_bom['rows'][index]['itemSource']['flatId'] = flatId        
 
    #Get material
    if i['headerIdToValue'][headerDict['Material']] != None:
      assignedMaterial = i['headerIdToValue'][headerDict['Material']]['displayName']     
    else:
      assignedMaterial = None

    foundPartsInformation.update({'Document ID': i['itemSource']['documentId'],
                                  'Element ID': i['itemSource']['elementId'],
                                  'Created Version Id': None,
                                  'WVM ID': i['itemSource']['wvmId'],
                                  'WVM Type': i['itemSource']['wvmType'],
                                  'Part ID': i['itemSource']['partId'],
                                  'Part Name': i['headerIdToValue'][headerDict['Name']],
                                  'Part Number': i['headerIdToValue'][headerDict['Part number']],
                                  'Part Thumbnail': None,
                                  'Composite Part ID': None,
                                  'Part of Cut List': False,
                                  'Cut List Qty': 0,
                                  'Document Name': None,
                                  'Element Name': None,
                                  'Configuration': i['itemSource']['fullConfiguration'],
                                  'Sheet Metal': False,
                                  'Flat Pattern ID': i['itemSource']['flatId'],
                                  'Material': assignedMaterial,
                                  'BOM Qty': i['headerIdToValue'][headerDict['Quantity']]})  
    if foundPartsInformation['Flat Pattern ID'] != None:
      foundPartsInformation['Sheet Metal'] = True
    allParts.append(foundPartsInformation)
    
    #Get Bodies
    for part in allParts:      
        did = part['Document ID']
        wvm_type = part['WVM Type']
        wv = part['WVM ID']
        eid = part['Element ID']
        #If sheet metal, get body details of the flat part ID
        if part['Sheet Metal'] == True:
          pid = part['Flat Pattern ID'] 
        else:
          pid = part['Part ID'] 
        url = '/api/parts/d/%s/%s/%s/e/%s/partid/%s/bodydetails' % (docid, wvm_type, wv, eid, pid)
        method = 'GET'  
        payload = {}
        params = {'configuration': part['Configuration']}
        #print(part['Part Name'])
        body_details = onshape.request(method, url, query=params, body=payload)
        body_details = json.loads(body_details.content)
        if len(body_details['bodies']) == 1: #Then we have only one body, therefore add the face and edge details to the dictionary
          part['Faces'] = body_details['bodies'][0]['faces']
          part['Edges'] = body_details['bodies'][0]['edges']
          partsAndFacesToTest.append(part)
        else: #we have a composite part which is either a simple composite or a cut list
          #Run featurescript code to determine if this is a cutlist
          did = part['Document ID']
          wvm_type = part['WVM Type']
          wv = part['WVM ID']
          eid = part['Element ID']
          pid = part['Part ID']
          url = '/api/partstudios/d/%s/%s/%s/e/%s/featurescript' % (did, wvm_type, wv, eid)
          method = 'POST'
          payload = {
            'script': """function(context is Context, queries is map){
                    // Define the function's action
          //Create output list
          var framesOutput = [];
          var frameInfo = {};
          var frameAtt = getFrameProfileAttributes(context, queries.id);
          var cutListAtt = getCutlistAttributes(context, queries.id);
          var bodyId = evaluateQuery(context, queries.id);
          //If a cutlist loop to get body id etc
          if (size(cutListAtt)!=0)
          {
          var currentTable = cutListAtt[0].table;
          for (var row in currentTable.rows)
          {
            frameInfo = {"Item": row.columnIdToCell.Item, "BodyId": row.entities.subqueries[0].transientId, "Description": row.columnIdToCell.Description, "Qty": row.columnIdToCell.Qty, "CutListBodyId" : (bodyId[0].transientId)};
            //println(frameInfo);
            framesOutput = append(framesOutput, frameInfo);
          }
          }
          return framesOutput;
          }
          """,
            'queries': [{ "key" : "id", "value" : [ pid ] }]
                    }
          params = {}
          resp = onshape.request(method, url, query=params, body=payload)
          resp = json.loads(resp.content)   
          print(resp)
          

          
          #CASE 1 - Composite part Cut List
          if len(resp['result']['message']['value']) != 0:   #Then we have a cut list
            for cutListPart in resp['result']['message']['value']:
              cutListPartInformation = part.copy()
              cutListPartInformation['Composite Part ID'] = cutListPartInformation['Part ID'] #The part ID found earlier is actually the composite ID, so assign this now
              cutListPartInformation['Part ID'] = cutListPart['message']['value'][0]['message']['value']['message']['value']
              cutListPartInformation['Cut List Qty'] = int(cutListPart['message']['value'][3]['message']['value']['message']['value'])
              cutListPartInformation['Part of Cut List'] = True
              if cutListPartInformation['Composite Part ID'] != cutListPartInformation['Part ID']: #this means that the composite is not added to the list                
                #Now get the faces and edges from body details by looking for the cutlistpart body id
                tempId = None #temp id so we don't get multiples of same body
                for body in body_details['bodies']:
                  if cutListPartInformation['Part ID'] == body['id'] and tempId != body['id']:
                    tempId = cutListPartInformation['Part ID']
                    cutListPartInformation['Faces'] = body['faces']
                    cutListPartInformation['Edges'] = body['edges']
                    partsAndFacesToTest.append(cutListPartInformation)
          else: #No cut list, just a composite part          
            for childPart in body_details['bodies']:
              childPartInformation = part.copy()
              childPartInformation['Composite Part ID'] = childPartInformation['Part ID'] #The part ID found earlier is actually the composite ID, so assign this now
              childPartInformation['Part ID'] = childPart['id']            
              if childPartInformation['Composite Part ID'] != childPartInformation['Part ID']: #this means that the composite is not added to the list              
                childPartInformation['Faces'] = childPart['faces']
                childPartInformation['Edges'] = childPart['edges']
                partsAndFacesToTest.append(childPartInformation)
          
  print(partsAndFacesToTest)  
  print ("My program took", time.time() - start_time, "to run")
  

  
  #If Part Studio

  #If Assembly
  
    #If Cut List
  

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