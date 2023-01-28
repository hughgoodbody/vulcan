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
   listPartTask = anvil.server.launch_background_task('list_parts_assembly', userData, documentInfo, configurationString)
   return configurationString, listPartTask
  elif elementType == 'PARTSTUDIO':  
    listPartTask = anvil.server.launch_background_task('list_parts_partstudio', userData, documentInfo, configurationString)




@anvil.server.background_task
def list_parts_assembly(userData, documentInfo, configurationString):
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