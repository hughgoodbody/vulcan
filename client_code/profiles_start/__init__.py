from ._anvil_designer import profiles_startTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import user_data
from ..ConfigurationsPanel import ConfigurationsPanel
from ..dxf_options import dxf_options
from ..profiles_exporter_Interactive import profiles_exporter_Interactive

class profiles_start(profiles_startTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    #Clear table
    anvil.server.call('clear_files_table', user_data.userData['User'])
    #Put configurations form into config panel   
    self.btnExecute.visible = False #Hide execute button
    self.configs = ConfigurationsPanel() #THIS IS WHAT NEEDS TO BE DONE IN ORDER TO GET CHILD VALUES OUT OF FORM
    self.pnlConfigPanel.add_component(self.configs)

    #Create DXF Options panel
    self.dxfOptions = dxf_options() #THIS IS WHAT NEEDS TO BE DONE IN ORDER TO GET CHILD VALUES OUT OF FORM
    self.pnlDxfOptions.add_component(self.dxfOptions)
    self.profileOptions = {'Hole Options':'', 'Etch Part Number':'', 'Bend Line Marks':'', 'Contact Sheet':'', 'CSV File':'', 'Supplier':'', 'Max Thickness':'', 'Reference':'', 'Multiplier':''}
    self.dxfOptions.items = self.profileOptions

  def btnExecute_click(self, **event_args):
    """This method is called when the button is clicked"""
    listPartTask = anvil.server.call('launch_list_parts')
    pass

    



