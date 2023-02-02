import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server



@anvil.server.callable
def launchGetMaterials(userData):
  materialTask = getMaterialLibrary(userData)
  return


@anvil.server.background_task
def getMaterialLibrary(userData):
  from urllib.parse import urlparse  
  import json
  import requests
  from pprint import pprint 
  from .onshape_api.onshape import Onshape
  ak = userData['Access Key']
  sk = userData['Secret Key']
  onshape = Onshape('https://cad.onshape.com', ak, sk, logging=False)  

  try:
    #Get id's from url passed in
    docUrl = userData['User']['materialLibraryUrl']
    docUrl = urlparse(docUrl).path
    docUrl = docUrl.split('/')
      
    did = docUrl[2]
    wvm_type = docUrl[3]
    wid = docUrl[4]
    eid = docUrl[6]
  
    if wvm_type == 'v' or wvm_type == 'm':
      raise Exception("Material library currently doesn't work with versions, please change URL to point to Workspace") 
  
    #Get materials    
    url = '/api/v5/materials/libraries/d/%s/%s/%s/e/%s' % (did, wvm_type, wid, eid) 
    method = 'GET'  
    payload = {}  
    params = {}
    materials = onshape.request(method, url, query=params, body=payload)
    materials = json.loads(materials.content)
    materials = materials['materials']
    #Create a new list of material names
    matNames=['']
    for m in materials:
      matNames.append(m['displayName'])
      
  except:
    raise Exception("Invalid Material Library URL, Please amend...") 


  #Clear out existing files from the table
  usersFiles = app_tables.transfertable.search(owner=userData['User'], type='materials')
  for row in usersFiles:
    row.delete()
  app_tables.transfertable.add_row(data=matNames, type='materials',owner=userData['User'])
  