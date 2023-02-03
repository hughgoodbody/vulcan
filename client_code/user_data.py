import anvil.server
userData = {} #created by user_config server module called from index client module
'''COntains the following:
   "User":None,
   "Users Suppliers":[],  All supplier information
   "Access Key":None,
   "Secret Key":None,
   "Order ID":None,
   "Order Prefix":None,
   "Order Reference":None
}'''
elements = [] #created by CofigurationsPanel client module
configOptions = {} #created by CofigurationsPanel client module
elementType = None #created by CofigurationsPanel client module
configSelectedParams = {} #created by CofigurationsPanel client module
profileOptions = {} #created by dxf_options client module
documentInfo = {} #created by document_info server module called from ConfigurationsPanel - {'URL: url, 'Document Id': did, 'Workspace Type': wvm_type, 'Workspace Id': wid, 'Element Id': eid}
configurationString = None
materialLibrary = []
namingConvention = {'Delimiter':'_',
                    'field0':'Part Number',
                    'field1': 'Thickness',
                    'field2': 'Material',
                    'field3': 'Quantity',
                    'field4': 'Operations',
                    'field5': 'Process'}  

'''
foundPartsInformation = {'Parent Document Name': api_bom['bomSource']['document']['name'], 
                           'Parent Element Name': api_bom['bomSource']['element']['name'], 
                           'Parent Document ID': did, 'Parent Element ID': eid, 
                           'Parent Configuration': configurationString,
                           'Parent WVM ID': wid, 
                           'Parent WVM Type': wvm_type, 
                           'Parent URL': masterUrl, 
                           'Parent Thumbnail': imageStr,
                           'Order ID': userData['Order ID'],
                           'Order Prefix': userData['Order Prefix'],
                           'Order Reference': userData['Order Reference'],
                           'Customer Reference': profileOptions['Reference'],
                           'Supplier': profileOptions['Supplier'],
                           'Process': None,                           
                           'Delete': None,
                           'Drill template': None,
                           'Material': None,
                           'Operations': [],
                           'Thickness': None,
                           'Undersize Holes': profileOptions['Hole Options'],
                           'Etch Part Number': profileOptions['Etch Part Number'],
                           'Bend Line Marks': profileOptions['Bend Line Marks'],
                           'Contact Sheet': profileOptions['Contact Sheet'],
                           'CSV File': profileOptions['CSV File'],
                           'Max Thickness': profileOptions['Max Thickness'],
                           'Multiplier': profileOptions['Multiplier'],
                           'Remove': False,
                           'Quantity': 0,
                           'Variation': False,
                           'Additional Qty': 0,
                           'Hole Data': None,
                           'DXF Name': None,
                          'Document ID': i['itemSource']['documentId'],
                          'Element ID': i['itemSource']['elementId'],
                          'Created Version Id': None,
                          'WVM ID': i['itemSource']['wvmId'],
                          'WVM Type': i['itemSource']['wvmType'],
                          'Part ID': i['itemSource']['partId'],
                          'Part Name': i['headerIdToValue'][headerDict['Name']],
                          'Part Number': i['headerIdToValue'][headerDict['Part number']],
                          'Part URL': i['itemSource']['viewHref'],
                          'Part Thumbnail': None,
                          'Composite Part ID': None,
                          'Part of Cut List': False,
                          'Cut List Qty': 0,
                          'Document Name': None,
                          'Element Name': None,
                          'Configuration': i['itemSource']['fullConfiguration'],
                          'Sheet Metal': False,
                          'Flat Pattern ID': i['itemSource']['flatId'],
                          'Material': assignedMaterial,
                          'BOM Qty': i['headerIdToValue'][headerDict['Quantity']]}
'''