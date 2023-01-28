import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def launch_list_parts(configParams, profileOptions):

  #Encode configuration string


  #Launch background task to list parts
  listPartTask = anvil.server.launch_background_task('list_parts')
  return listPartTask




@anvil.server.background_task
def list_parts():
  # Get thumbnail
  
  #If Part Studio

  #If Assembly
  
    #If Cut List
  
    #If Composite part
  return