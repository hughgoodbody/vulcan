from ._anvil_designer import ConfigurationsPanelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import ConfigurationTemplates


class ConfigurationsPanel(ConfigurationsPanelTemplate):
  outputStr = None  
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.configStr =  None
    
    #self.url = url #Make passed in url variable accessible from other functions

    # Any code you write here will run before the form opens.
  def btnGetConfigs_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.n = Notification("Getting Model Configurations.....Please Wait", timeout=None)
    self.n.show()
    self.url = self.parent.parent.txtUrl.text #Get url which is in a parent form
    #Delete existing config row
    anvil.server.call_s('deletFilesFromTable', app_tables.transfertable, 'CONFIGLIST', True)
    #Call server function to get configurations - returns a list    
    self.configResult = anvil.server.call_s('launchGetConfigurations', self.url)  
    #Start timer
    self.timer_1.interval = 0.5  #Start timer for progresss bars etc
    self.btnGetConfigs.visible = False    
    pass

  def timer_1_tick(self, **event_args):
    """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
    if self.configResult.is_completed() == True:
      
      
      configData = anvil.server.call_s('getObject', 'CONFIGLIST')      
      #Stop timer
      self.timer_1.interval = 0
      configData = configData['object']
      #print(len((configData['configurationParameters'])))
      #print(configData['configurationParameters'])
      #If there are configurations
      if len((configData['configurationParameters'])) != 0:
        for i in configData['configurationParameters']:      
          #If a list
          if i['typeName'] == 'BTMConfigurationParameterEnum':
            configParamEnumOptions = []
            #create list of tuples of options for dropdown box
            for j in i['message']['options']:
              optionsTuple = (j['message']['optionName'], j['message']['option'])
              configParamEnumOptions.append(optionsTuple)#add tuple to list
            self.dropDown = ConfigurationTemplates.ListItemTemplate()
            self.panelConfigPanel.add_component(self.dropDown)
            self.dropDown.lblList.text = i['message']['parameterName']
            self.dropDown.lblParamId.text = i['message']['parameterId'] #Hidden label with parameter ID
            self.dropDown.dropConfigOptions.items = configParamEnumOptions
            
            
            
          #If quantity
          elif i['typeName'] == 'BTMConfigurationParameterQuantity':
          #create a text box to enter a number between range indicated
            #pprint(i['message']['parameterName'] + '  Enter Value')
            self.quantity = ConfigurationTemplates.ValueItemTemplate()
            self.panelConfigPanel.add_component(self.quantity)
            self.quantity.txtValue.text = i['message']['rangeAndDefault']['message']['minValue']
            self.quantity.lblValue.text = i['message']['parameterName']
            self.quantity.lblMin.text = ('Min: ' + str(i['message']['rangeAndDefault']['message']['minValue']) + ' ( ' + i['message']['rangeAndDefault']['message']['units'] + ' ) ')
            self.quantity.lblMax.text = ('Max: ' + str(i['message']['rangeAndDefault']['message']['maxValue']) + ' ( ' + i['message']['rangeAndDefault']['message']['units'] + ' ) ')
            self.quantity.lblUnits.text = i['message']['rangeAndDefault']['message']['units']
            self.quantity.lblMin.align = 'right'
            outputTuple = (3, 4)
            
        
          #If boolean
          elif i['typeName'] == 'BTMConfigurationParameterBoolean':
            #create a checkbox
            #pprint(i['message']['parameterName'] + '  Checkbox')
            self.booleanBox = ConfigurationTemplates.BooleanItemTemplate()
            self.panelConfigPanel.add_component(self.booleanBox)
            self.booleanBox.lblBoolean.text = i['message']['parameterName']
            outputTuple = ('A', 'B')

      #For the list items, we need to get the
          
      else:
        #No configurations
        self.ncLabel = ConfigurationTemplates.NoConfigsTemplate()
        self.panelConfigPanel.add_component(self.ncLabel)
        self.ncLabel.lblNoConfigs.text = 'No configurations'        
      self.n.hide() # Hide notification
      self.parent.parent.btnExecute.visible = True #Show execute button on parent form
    pass

  def encodeConfigurations_onClick(self, **event_args):
    """This method is called when the button is clicked"""
    configParams = []
    self.majorComps = self.panelConfigPanel.get_components()
    for c in self.majorComps:
      #Get the components in the panel to find whether it is a drop down, text or boolean, then get info accordingly
      #c.get_components()
      #print((c.column_panel_1.get_components()))
      for d in c.column_panel_1.get_components():
        #print(d)
        if type(d) is anvil.DropDown:
          #Then we have a drop down box, therefore create tuple from id label and selection
          outputTuple = (c.lblParamId.text, c.dropConfigOptions.selected_value)
          outputDict = {"parameterId": c.lblParamId.text, "parameterValue": c.dropConfigOptions.selected_value}
          #print(outputTuple)
          configParams.append(outputDict)

        elif type(d) is anvil.TextBox: 
          #print(d)
          outputTuple = (c.lblValue.text, c.txtValue.text)
          outputDict = {"parameterId": c.lblValue.text, "parameterValue": (str(c.txtValue.text)+'*'+c.lblUnits.text)}
          #print(outputTuple)
          configParams.append(outputDict)

        elif type(d) is anvil.CheckBox: 
          outputTuple = (c.lblBoolean.text, c.chkBoolean.checked)
          outputDict = {"parameterId": c.lblBoolean.text, "parameterValue": c.chkBoolean.checked}
          #print(outputTuple)
          configParams.append(outputDict)

    #print(configParams)  
    self.encodeResult = anvil.server.call('launchEncodeConfigurations', self.url, configParams)
    #Start encode timer
    self.encode_timer.interval = 0.5 
    pass

  def encode_timer_tick(self, **event_args):
    """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
    if self.encodeResult.is_completed() == True:
        #Stop timer
        self.encode_timer.interval = 0
        self.outputStr = anvil.server.call_s('getConfigString')                      
    pass





