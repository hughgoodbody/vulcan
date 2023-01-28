import anvil.server
userData = {} #created by user_config server module called from index client module
elements = [] #created by CofigurationsPanel client module
configOptions = {} #created by CofigurationsPanel client module
elementType = None #created by CofigurationsPanel client module
configSelectedParams = {} #created by CofigurationsPanel client module
profileOptions = {} #created by dxf_options client module
documentInfo = {} #created by document_info server module called from ConfigurationsPanel - {'Document Id': did, 'Workspace Type': wvm_type, 'Workspace Id': wid, 'Element Id': eid}
configurationString = None
