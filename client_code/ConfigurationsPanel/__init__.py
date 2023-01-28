from ._anvil_designer import ConfigurationsPanelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import ConfigurationTemplates
from .. import user_data


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
    self.url = self.parent.parent.txtUrl.text #Get url which is in a parent form
    self.btnGetConfigs.visible = False    
    self.elements, self.elementType, self.configOptions, self.documentInfo = anvil.server.call('get_elements_configurations', user_data.userData, self.url) #From document_info module
      
    #Store information in user_data module, for access from other forms
    user_data.elements = self.elements
    user_data.configOptions = self.configOptions
    user_data.elementType = self.elementType
    user_data.documentInfo = self.documentInfo
    if len((self.configOptions['configurationParameters'])) != 0:
      for i in self.configOptions['configurationParameters']:      
        #If a list
        #print(i)
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
          self.pnlValues.add_component(self.quantity)
          self.quantity.txtValue.text = i['message']['rangeAndDefault']['message']['minValue']
          self.quantity.lblValue.text = i['message']['parameterName']
          self.quantity.lblMin.text = ('Min: ' + str(i['message']['rangeAndDefault']['message']['minValue']) + ' ( ' + i['message']['rangeAndDefault']['message']['units'] + ' ) ')
          self.quantity.lblMax.text = ('Max: ' + str(i['message']['rangeAndDefault']['message']['maxValue']) + ' ( ' + i['message']['rangeAndDefault']['message']['units'] + ' ) ')
          self.quantity.lblUnits.text = i['message']['rangeAndDefault']['message']['units']
          self.quantity.lblMin.align = 'right'
          
          
      
        #If boolean
        elif i['typeName'] == 'BTMConfigurationParameterBoolean':
          #create a checkbox
          #pprint(i['message']['parameterName'] + '  Checkbox')
          self.booleanBox = ConfigurationTemplates.BooleanItemTemplate()
          self.pnlCheck.add_component(self.booleanBox)
          self.booleanBox.lblBoolean.text = i['message']['parameterName']
          

      #For the list items, we need to get the
          
    else:
      #No configurations
      self.ncLabel = ConfigurationTemplates.NoConfigsTemplate()
      self.panelConfigPanel.add_component(self.ncLabel)
      self.ncLabel.lblNoConfigs.text = 'No configurations'        

    self.parent.parent.btnExecute.visible = True #Show execute button on parent form
    pass

  def configurating(self, **event_args):
    """This method is called when the button is clicked"""
    configParams = []
    self.listComps = self.panelConfigPanel.get_components() #get list components from list panel
    self.valueComps = self.pnlValues.get_components() #get value components from value panel
    self.checkComps = self.pnlCheck.get_components() #get check components from check panel

    def get_configuration_parameter_values(componentObjects):
      for c in componentObjects:
        #Get the components in the panel to find whether it is a drop down, text or boolean, then get info accordingly
        #c.get_components()
        #print((c.column_panel_1.get_components()))
        for d in c.grid_panel_1.get_components():
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
      return configParams       

    listParams = get_configuration_parameter_values(self.listComps)  
    valueParams = get_configuration_parameter_values(self.valueComps) 
    checkParams = get_configuration_parameter_values(self.checkComps) 
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1FOR SOME REASON listParams contains valueParams and checkParams without appending them !!!!!!!!!!!
    #Store in user_data module 
    #print(listParams)      
    #print(valueParams)
    #print(checkParams)
    user_data.configSelectedParams = listParams
    #print(user_data.configSelectedParams)






