import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def launch_list_parts(userData, configParams, profileOptions, documentInfo):
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
  listPartTask = anvil.server.launch_background_task('list_parts')
  return configurationString, listPartTask




@anvil.server.background_task
def list_parts():
  # Get thumbnail
  
  #If Part Studio

  #If Assembly
  
    #If Cut List
  
    #If Composite part
  return