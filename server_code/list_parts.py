import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def launch_list_parts(user_data, profileOptions):
  if user_data.elementType == 'PARTSTUDIO':
    anvil.alert('You have selected a Part Studio to process, Do you wish to continue?')
    #Encode configuration string
    user_data.configSelectedParams

    #Launch background task to list parts
    listPartTask = anvil.server.launch_background_task('launch_list_parts')
  return listPartTask








@anvil.server.background_task
def list_parts():
  # Get thumbnail
  
  #If Part Studio

  #If Assembly
  
    #If Cut List
  
    #If Composite part
  return