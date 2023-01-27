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
  from .geometryFunctions import findExportFaces
  from .Onshape_api.onshape import Onshape

  ak = userData['Encoded Access Key']
  sk = userData['Encoded Secret Key']
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
  url = '/api/v5/documnets/d/%s/%s/%s/elements' % (did, wvm_type, wid, eid) 
  method = 'GET'  
  payload = {}  
  params = {}
  elements = onshape.request(method, url, query=params, body=payload)
  elements = json.loads(elements.content)

  #Get pasted element type
  #Find element id in list of elements and then get elementType

  elementType = ''
  

  #Get element configurations
  url = '/api/v5/elements/d/%s/w/%s/e/%s/configuration' % (did, wid, eid)
  method = 'GET'  
  payload = {}
  params = {}
  config = onshape.request(method, url, query=params, body=payload)
  config = json.loads(config.content)
  return elements, elementType, config