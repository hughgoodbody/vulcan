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
from ..ConfigurationsPanel import ConfigurationsPanel


class profiles_start(profiles_startTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    #Check for API key
    if user_data.userData['Access Key'] is None or user_data.userData['Secret Key'] is None:
      alert('Please create API key in Settings')
      return
    #Clear tables
    anvil.server.call('clear_all_tables', user_data.userData['User'])
    #Put configurations form into config panel   
    self.btnExecute.visible = False #Hide execute button
    self.configs = ConfigurationsPanel() #THIS IS WHAT NEEDS TO BE DONE IN ORDER TO GET CHILD VALUES OUT OF FORM
    self.pnlConfigPanel.add_component(self.configs, full_width_row=True)

    #Create DXF Options panel
    self.dxfOptions = dxf_options() #THIS IS WHAT NEEDS TO BE DONE IN ORDER TO GET CHILD VALUES OUT OF FORM
    self.pnlDxfOptions.add_component(self.dxfOptions)
    self.profileOptions = {'Hole Options':None, 'Etch Part Number':None, 'Bend Line Marks':None, 'Contact Sheet':None, 'CSV File':None, 'Supplier':None, 'Max Thickness':None, 'Reference':None, 'Multiplier':None}
    self.dxfOptions.items = self.profileOptions
    user_data.profileOptions = self.profileOptions
    

  def btnExecute_click(self, **event_args):
    """This method is called when the button is clicked"""
    if user_data.elementType == 'PARTSTUDIO':
      c = confirm("You have selected a Part Studio to process, Do you wish to continue?")
      if c == False or c == None:
        return
    else: 
      self.profileOptions['Hole Options'] = self.dxfOptions.radRatio.get_group_value()
      self.profileOptions['Etch Part Number'] = self.dxfOptions.chkEtchPart.checked
      self.profileOptions['Bend Line Marks'] = self.dxfOptions.chkEtchBend.checked
      self.profileOptions['Contact Sheet'] = self.dxfOptions.chkContactSheet.checked
      self.profileOptions['CSV File'] = self.dxfOptions.chkCsvFile.checked
      self.profileOptions['Supplier'] = self.dxfOptions.dropSupplier.selected_value
      self.profileOptions['Max Thickness'] = self.dxfOptions.txtThickness.text
      self.profileOptions['Reference'] = self.dxfOptions.txtRef.text
      self.profileOptions['Multiplier'] = self.dxfOptions.txtMultiplier.text
      user_data.profileOptions = self.profileOptions
      #print(self.profileOptions)

      #Encode configurations and then lauch task to get parts
      self.configStr = ConfigurationsPanel.configurating(self.configs)  
      configurationString, searchPartsTask = anvil.server.call('launch_list_parts', user_data.userData, user_data.configSelectedParams, user_data.profileOptions, user_data.documentInfo)
      user_data.configurationString = configurationString
      #print(user_data.configurationString)
    pass

    



