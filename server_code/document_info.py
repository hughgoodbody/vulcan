import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def get_elements_configurations(userData, url):
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

  #Get id's from url passed in
  docUrl = url
  docUrl = urlparse(docUrl).path
  docUrl = docUrl.split('/')
    
  did = docUrl[2]
  wvm_type = docUrl[3]
  wid = docUrl[4]
  eid = docUrl[6]

  #Get elements in document
  url = '/api/v5/documents/d/%s/%s/%s/elements' % (did, wvm_type, wid) 
  method = 'GET'  
  payload = {}  
  params = {}
  elements = onshape.request(method, url, query=params, body=payload)
  elements = json.loads(elements.content)


  #Get pasted element type
  #Find element id in list of elements and then get elementType
  for elem in elements:
    if eid == elem['id']:
      elementType = elem['elementType']
  

  #Get element configurations
  url = '/api/v1/elements/d/%s/w/%s/e/%s/configuration' % (did, wid, eid)
  method = 'GET'  
  payload = {}
  params = {}
  configOptions = onshape.request(method, url, query=params, body=payload)
  configOptions = json.loads(configOptions.content)
  return elements, elementType, configOptions

@anvil.server.callable
def encodeConfigurations(userData, url, configParams):
  encodeString = ''
  return encodeString