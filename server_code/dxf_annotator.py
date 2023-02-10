#### CHOOSE COLOURS ####
'''
The colors are assigned as follows: 1 Red, 2 Yellow, 3 Green, 4 Cyan, 5 Blue, 6 Magenta, 7 White/Black.
'''
#https://gohtx.com/acadcolors.php
etch_colour = 3
annotations_colour = 150
no_cut_colour = 1
tapping_colour = 6
drill_colour = 5


def annotateDxf(userData, folder, inputData, prefix, orderId, supplier):
  import os
  import pyparsing
  import ezdxf
  import datetime
  import csv
  import sys
  from pathlib import Path
  from ezdxf import bbox
  import shutil
  import tempfile
  from . import bin_pack
  from .bin_pack import binPack
  from .functions import detailTapping
  from .functions import dimensionPrincipal
  from .functions import dimensionBoundingBox
  from .functions import findInList
  from ezdxf.addons import Importer
  from . import functions
  import math
  from . import user_data
  import anvil.server
  from anvil.tables import app_tables
  import matplotlib.pyplot as plt
  from ezdxf import recover
  from ezdxf.addons.drawing import RenderContext, Frontend
  from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
  from ezdxf.addons.drawing import matplotlib
  from . import sheetSize
  import numpy as np

  xTappingDict = {}
  #List to generate CSV from
  ipLasercsvList = [["NAME", "MATERIAL", "GRADE", "THICKNESS", "GRAIN", "OVERRIDE EXISTING", "QUANTITY", "NOTES", "DWG NOT FOR MANUFACTURE"]]
  othercsvList = [["NAME", "MATERIAL", "THICKNESS", "GRAIN", "OVERRIDE EXISTING", "QUANTITY", "NOTES", "DWG NOT FOR MANUFACTURE"]]

  #List for bin packing
  binPackList = []
  
  #Constants for csv file for IP laser
  csvGrain = "N"
  csvOverride = 1
  csvDwgnfm = None

  
  #For loop to iterate through files in directory
 
  path = Path(folder)
  searchfiles = path.glob('*.dxf')
  for dxfFile in searchfiles:
    textWidth = 0
    fileName = str(os.path.basename(dxfFile))    #Remove path
    #print(f"Processing {fileName}")
 
    #Get input data for the selected file, find out if part number is in fileName
    for partInfo in inputData:
      renameOps = []
      if partInfo['Part Number'] not in fileName:
        continue
  
      if 'dxf' in fileName:
        fileNameNoSuffix = fileName.strip('.dxf')
    
      if 'DXF' in fileName:
        fileNameNoSuffix = fileName.strip('DXF')  
    
      #Create a list of entries to add to drawing, this will then give the multiplier for spacing and positioning of the text
      dictInfo = {}
      drawingNotes = []
      dictInfo['File Name'] = fileName
      dictInfo['PartNumber'] = fileNameNoSuffix
      dictInfo['Thickness'] = partInfo['Thickness']      
      dictInfo['Material'] = partInfo['Material']
      dictInfo['Operations'] = partInfo['Operations']
      dictInfo['Process'] = partInfo['Process']
      dictInfo['Supplier'] = partInfo['Supplier']
      dictInfo['Qty'] = partInfo['Quantity']
        
      if partInfo['Etch Part Number'] == True:
        dictInfo['PARTDATA18'] = fileNameNoSuffix
        if 'ETCHING REQUIRED' not in drawingNotes:
          drawingNotes.append('ETCHING REQUIRED')
      else: 
        dictInfo['PARTDATA18'] = ''

      #Create readable notes of operations for drawings
      if 'B' in dictInfo['Operations']:
        drawingNotes.append('BENDING REQUIRED')
      if 'T' in dictInfo['Operations']:
        drawingNotes.append('TAPPING REQUIRED')
      if 'D' in dictInfo['Operations']:
        drawingNotes.append('DRILLING REQUIRED')
      if 'CSK' in dictInfo['Operations']:
        drawingNotes.append('COUNTERSINKING REQUIRED')  
    
      if 'LAS' in dictInfo['Process']:  
        dictInfo['ProcessOnDrawing'] = "LASER"
      elif 'WJ' in dictInfo['Process']:  
        dictInfo['ProcessOnDrawing'] = "WATERJET"
      elif 'PLA' in dictInfo['Process']:  
        dictInfo['ProcessOnDrawing'] = "PLASMA"
      elif 'OXY' in dictInfo['Process']:  
        dictInfo['ProcessOnDrawing'] = "OXY-FUEL"
      elif 'SAW' in dictInfo['Process']:  
        dictInfo['ProcessOnDrawing'] = "SAW"
      elif 'MAN' in dictInfo['Process']:  
        dictInfo['ProcessOnDrawing'] = "MANUAL"  
      else:
        dictInfo['ProcessOnDrawing'] = "" 
        
      
      dictInfo['Notes'] = drawingNotes
      PARTDATA6 = dictInfo['Operations']  
      
    '''------------------------------------------------------------CARRY OUT DXF FILE EXAMINATIONS AND ALTERATIONS--------------------------------------------------------------------------------------------'''
    #### READ DXF FILE ####
    dwg = ezdxf.readfile(dxfFile)
    #print(dwg)
    msp = dwg.modelspace()
    #Delete existing text entities if they exist
    myquery = msp.query('TEXT')
    #print(myquery)
    try:
      for entity in myquery:
        msp.delete_entity(entity)
      assert len(msp.query('TEXT')) == 0
    except:  
      pass
  
    #### CREATE NEW LAYERS ####
    try:
        dwg.layers.add(name='Hole_Drilling', color = drill_colour)
        dwg.layers.add(name='Etch', color = etch_colour)
        dwg.layers.add(name='Annotations', color = annotations_colour)
        dwg.layers.add(name='Dont_Cut', color = no_cut_colour)
        dwg.layers.add(name='Hole_Tapping', color = tapping_colour)
        dwg.layers.add(name='Profile', color = 0)          
    except:
        pass
    try: 
        dwg.layers.add(name='Dimensions', color = no_cut_colour) #Seperate try here as likely someones dxf already has a Dimensions layer, dont want to throw exception with other layers
    except:
        pass

    #Put all entities onto Profile layer
    for entity in msp:
      entity.dxf.layer = "Profile"
    #### GET DRAWING LIMITS ####  
    extMin = dwg.header['$EXTMIN']
    extMax = dwg.header['$EXTMAX']
    
    #Position the text box 10mm below the bounding box and the scaled text height
    #If statement required here to differentiate between SWorks and Onshape DXF's. If EXTMAX and EXTMIN are 1e+20, then use
    #LIMMAX and LIMMIN - because Onshape currently uses fulle extents in $EXTMIN and $EXTMAX
    #Could amend to Tuple size here, as Onshape has a 2 touple, Solidworks a 3 Tuple
    if extMin[0] == 1e+20 and extMin[1] == 1e+20:
        minLimit = dwg.header['$LIMMIN']
        maxLimit = dwg.header['$LIMMAX']
        text_point = dwg.header['$LIMMIN']
        boundingBox = bbox.extents(msp)
        minLimit = boundingBox.extmin
        maxLimit = boundingBox.extmax
        text_point = boundingBox.extmin  
    else:
        minLimit = dwg.header['$EXTMIN']
        maxLimit = dwg.header['$EXTMAX']
        text_point = dwg.header['$EXTMIN']
        boundingBox = bbox.extents(msp)
  
    text_x = text_point[0]
    text_y = text_point[1] - 10 - (((maxLimit[1]) - (minLimit[1])) * 0.025)
        
    #Get bounding box of part
    partBoundingBox = bbox.extents(msp)  #Make sure to add on the space the text takes up
    #Get scale factor to fit the image into half of the grid box
    imageWidth = partBoundingBox.extmax[0] - partBoundingBox.extmin[0]
    imageHeight = partBoundingBox.extmax[1] - partBoundingBox.extmin[1]
    gridBoxWidth = (sheetSize.sheetSize['Width'] - (2 * sheetSize.sheetSize['Border'])) / (sheetSize.sheetSize['Horizontal Boxes'])
    gridBoxHeight = (sheetSize.sheetSize['Height'] - (2 * sheetSize.sheetSize['Border']) - 20) / (sheetSize.sheetSize['Vertical Boxes']) # 20 here is the sheet title at the foot
    
    if imageHeight > gridBoxHeight/2:
      imageScaleFactor = (gridBoxHeight/2) / imageHeight    
    elif imageWidth > gridBoxWidth:
      imageScaleFactor = gridBoxWidth / imageWidth    
    else:
      imageScaleFactor = 1
      
    dictInfo['Bounding Box'] = partBoundingBox
      
    #Set text height
    def set_text_height():
      idealFontHeight = 2.6
      idealFontSpace = 1.3
      text_height = idealFontHeight * (1/imageScaleFactor)
      text_spacing = idealFontSpace * (1/imageScaleFactor)
      return(text_height, text_spacing)    
    
    #Set text properties
    def set_text_props(xtextLayer, xText):
      text_height, text_spacing = set_text_height()    
      xText.dxf.height = text_height
      xText.dxf.layer = xtextLayer
      return (text_height)
      
    #Define function for applying annotations
    def applyAnnotations():
      i = 1 #Multiplier for row spacing
      #This first section is to allow for the dimension text size
      text_height, text_spacing = set_text_height()
      initial_spacing = (text_height + (text_spacing * 3))
      
      text = msp.add_text(f"PART NUMBER: {dictInfo['PartNumber']}").set_placement((text_x, text_y - initial_spacing))
      text_height = set_text_props('Annotations', text)
      spacing = ((text_height + text_spacing) * i) + initial_spacing
      i = i + 1
      text = msp.add_text(f"MATERIAL: {dictInfo['Material']}").set_placement((text_x, text_y - spacing))
      text_height = set_text_props('Annotations', text)
      spacing = ((text_height + text_spacing) * i) + initial_spacing
      i = i + 1
      text = msp.add_text(f"THICKNESS: {dictInfo['Thickness']}").set_placement((text_x, text_y - spacing))
      text_height = set_text_props('Annotations', text)
      spacing = ((text_height + text_spacing) * i) + initial_spacing
      i = i + 1
      text = msp.add_text(f"QTY: {dictInfo['Qty']}").set_placement((text_x, text_y - spacing))
      text_height = set_text_props('Annotations', text)
      spacing = ((text_height + text_spacing) * i) + initial_spacing
      i = i + 1
      text = msp.add_text(f"OPERATIONS: {dictInfo['Operations']}").set_placement((text_x, text_y - spacing))
      text_height = set_text_props('Annotations', text)
      spacing = ((text_height + text_spacing) * i) + initial_spacing
      i = i + 1
      text = msp.add_text(f"PARTDATA6: {dictInfo['Operations']}").set_placement((text_x, text_y - spacing))
      text_height = set_text_props('Annotations', text)
      spacing = ((text_height + text_spacing) * i) + initial_spacing
      i = i + 1
      text = msp.add_text(f"PARTDATA18: {dictInfo['PARTDATA18']}").set_placement((text_x, text_y - spacing))
      text_height = set_text_props('Annotations', text)
      spacing = ((text_height + text_spacing) * i) + initial_spacing
      i = i + 1
      text = msp.add_text(f"NOTES: {dictInfo['Notes']}").set_placement((text_x, text_y - spacing))
      text_height = set_text_props('Annotations', text)
      spacing = ((text_height + text_spacing) * i) + initial_spacing
      i = i + 1
      text = msp.add_text(f"PROCESS: {dictInfo['Process']}").set_placement((text_x, text_y - spacing))
      text_height = set_text_props('Annotations', text)
      spacing = ((text_height + text_spacing) * i) + initial_spacing
      i = i + 1
      
      #Get the length of the longest string in the dictionary, this is added to the longest note heading (PART NUMBER) this is passed into the bin packer for correct spacing    
      tempDict = {'Operations': dictInfo['Operations'], 'Part Number': dictInfo['PartNumber']}
      strLength = len('PART NUMBER: ') + len(max(tempDict.values(), key=len))    
      textWidth = strLength * text_height
      return textWidth
      
      
      
    #### GET BEND LINES ####   
    if partInfo['Sheet Metal'] == True: 
      try:
        bendLines = msp.query('LINE[(layer=="SHEETMETAL_BEND_LINES_DOWN" | layer=="SHEETMETAL_BEND_LINES_UP")]')
        blEtchLength = 12
        for bl in bendLines:
          #Change bend line colour to no-cut and turn layer off
          bl.dxf.color = no_cut_colour
          dwg.layers.get('SHEETMETAL_BEND_LINES_DOWN').off()
          dwg.layers.get('SHEETMETAL_BEND_LINES_UP').off()
          if bendLineMarks == True:
            lenBendLine = math.sqrt(((bl.dxf.end[0] - bl.dxf.start[0])**2) + ((bl.dxf.end[1] - bl.dxf.start[1])**2))
            startEnd = ((bl.dxf.start[0] + (((bl.dxf.end[0] - bl.dxf.start[0])/lenBendLine) * blEtchLength)), (bl.dxf.start[1] + (((bl.dxf.end[1] - bl.dxf.start[1])/lenBendLine) * blEtchLength)))  
            endEnd = ((bl.dxf.end[0] - (((bl.dxf.end[0] - bl.dxf.start[0])/lenBendLine) * blEtchLength)), (bl.dxf.end[1] - (((bl.dxf.end[1] - bl.dxf.start[1])/lenBendLine) * blEtchLength)))          
            msp.add_line((bl.dxf.start), (startEnd), dxfattribs={'layer': 'Etch'})
            msp.add_line((bl.dxf.end), (endEnd), dxfattribs={'layer': 'Etch'})
      except:
          anvil.alert('No compatible sheet metal layer')
  
  
      
    #### GET THE HOLES ####
    lstHolesOnDrawing = []  
    for e in msp:
      if e.dxftype() == 'CIRCLE':
          #Create a temp diameter variable and see if exists in list
          holeDiameter = round((e.dxf.radius * 2),1)
          ## FIND CENTRE OF CIRCLE ##
          holeCentre = e.dxf.center
          #print("Centre Point: ", cent)
          #print("CIRCLE radius: %s\n" % e.dxf.radius)
          holeXcoordinate = holeCentre[0]         
          holeYcoordinate = holeCentre[1]
          lstHolesOnDrawing.append({'Circle': e, 'X-Coordinate': holeXcoordinate, 'Y-Coordinate': holeYcoordinate, 'Diameter': holeDiameter})  #Create a list of the hole entities
          #detailTapping(e, msp)
    #print(f'Circle Coordinates: {lstHolesOnDrawing}')    
          
    #Workout hole ratio based on material thickness
    #Less than 20mm ratio is 60%
    #20mm is 70%    
    #25mm or greater is 90%    
    if int(dictInfo['Thickness']) >= 25:
      ratio = 0.9
    elif int(dictInfo['Thickness']) >= 20:
      ratio = 0.7
    else:
      ratio = 0.6    
    
      
    #UNDERSIZE HOLES
    #Ignore Ratio
    if partInfo['Undersize Holes'] == 'Ignore':
      ratio = 0.01  
    #Drill the holes - still need etch marks though
    if partInfo['Undersize Holes'] == 'Drill':
      for holeEntity in lstHolesOnDrawing:
        if round((holeEntity.dxf.radius*2),1) <= ratio * int(dictInfo['Thickness']):
          cent = holeEntity.dxf.center
          x1 = cent[0] - 5
          x2 = cent[0] + 5
          y1 = cent[1] - 5
          y2 = cent[1] + 5
          ## DRAW ETCH LINES ##
          msp.add_line((x1, cent[1]), (x2, cent[1]), dxfattribs={'layer': 'Etch'})
          msp.add_line((cent[0], y1), (cent[0], y2), dxfattribs={'layer': 'Etch'})
          holeEntity.dxf.layer = 'Hole_Drilling'                   #Move hole circle to drilling layer
          holeEntity.dxf.color = drill_colour
          dictInfo['Operations'].append('D')
    #Etch the holes
    if partInfo['Undersize Holes'] == 'Etch':
      if 'ETCHING REQUIRED' not in drawingNotes:
        drawingNotes.append('ETCHING REQUIRED')
      for holeEntity in lstHolesOnDrawing:
        if round((holeEntity.dxf.radius*2),1) <= ratio * int(dictInfo['Thickness']):
          cent = holeEntity.dxf.center
          x1 = cent[0] - 5
          x2 = cent[0] + 5
          y1 = cent[1] - 5
          y2 = cent[1] + 5
          ## DRAW ETCH LINES ##
          msp.add_line((x1, cent[1]), (x2, cent[1]), dxfattribs={'layer': 'Etch'})
          msp.add_line((cent[0], y1), (cent[0], y2), dxfattribs={'layer': 'Etch'})
          holeEntity.dxf.layer = 'Dont_Cut'                   #Move hole circle to No Cut layer
          holeEntity.dxf.color = no_cut_colour
          if 'E' not in dictInfo['Operations']:
            dictInfo['Operations'].append('E')

    '''      
    #Rename the operations field to account for the drilling and etchin of undersize holes
    operationsField = user_data.namingConvention['field4']         
    delimiter = user_data.namingConvention['Delimiter']
    parseName = fileNameNoSuffix.split(delimiter)
    print(parseName)
    if parseName[4] == '':
      newName = parseName[0]+parseName[1]+parseName[2]+parseName[3]+parseName[5]
    else: 
      newName = parseName[0]+parseName[1]+parseName[2]+parseName[3]+parseName[4]
    #Update the dictionary with the new filename  
    dictInfo['File Name'] = newName
    '''
    #APPLY THE ANNOTATIONS TO THE DRAWING **************************************************************************************
    #dimensionPrincipal(msp)
    #Get text height for dimension
    text_height, text_spacing = set_text_height()
    #dimensionBoundingBox(msp, partBoundingBox, text_height)
    textWidth = applyAnnotations()
    finalBoundingBox = bbox.extents(msp)
    
    
    #Square up the bounding box to avoid rotations in the contact sheet
    rotScale = 2
    squareBoxMax = [0,0]
    squareBoxMax[0] = finalBoundingBox.extmax[0] 
    squareBoxMax[1] = finalBoundingBox.extmax[1] 
    fbbLength = finalBoundingBox.extmax[0] - finalBoundingBox.extmin[0]
    fbbHeight = finalBoundingBox.extmax[1] - finalBoundingBox.extmin[1]
    
    #X value larger
    if abs(finalBoundingBox.extmax[0]) > abs(finalBoundingBox.extmax[1]):
      #Check if negative
      if finalBoundingBox.extmax[1] < 0:
        squareBoxMax[1] = -finalBoundingBox.extmax[0]
      else:
         squareBoxMax[1] = finalBoundingBox.extmax[0]
    #Y value larger
    if abs(finalBoundingBox.extmax[1]) > abs(finalBoundingBox.extmax[0]):
      #Check if negative
      if finalBoundingBox.extmax[0] < 0:
        squareBoxMax[0] = -finalBoundingBox.extmax[1]
      else:
         squareBoxMax[0] = finalBoundingBox.extmax[1]    
        
         
    
    
    #Save changes to the drawing
    dwg.save()    
    #os.rename(fileName, dictInfo['File Name'] + '.dxf')
    
    #print(f"Bounding box: {finalBoundingBox}")
    binPackList.append({"File": fileName, "Bounding Box": [squareBoxMax, finalBoundingBox.extmin], "Pre Text Box": partBoundingBox, 'Scale Factor': imageScaleFactor, 'Text Height': text_height})
    #print(f"Bin Pack List: {binPackList}")
    
  
  
    #Generate csv list for ipLaser
    #Generate IP Laser materials and grades  
    if "AL" in dictInfo['Material'] or "5251" in dictInfo['Material']:
        ipLasercsvMaterial = "Aluminium"
        ipLasercsvGrade = 5251
    elif "316" in dictInfo['Material']:
        ipLasercsvMaterial = "Stainless Steel"
        ippLasercsvGrade = 316
    elif "304" in dictInfo['Material']:
        ipLasercsvMaterial = "Stainless Steel"
        ipLasercsvGrade = 304
    else:
        ipLasercsvMaterial = "Mild Steel"
        if int(dictInfo['Thickness']) <= 3:
            ipLasercsvGrade = "CR4"
        else:
            ipLasercsvGrade = "HR"
  
  
    ipLasercsvList.append([dictInfo['File Name'], ipLasercsvMaterial, ipLasercsvGrade, dictInfo['Thickness'], csvGrain, csvOverride, dictInfo['Qty'], dictInfo['Notes'], csvDwgnfm])  
    othercsvList.append([dictInfo['PartNumber'], dictInfo['Material'], dictInfo['Thickness'], csvGrain, csvOverride, dictInfo['Qty'], dictInfo['Notes'], csvDwgnfm])
  
  #Get reference number from data table to build csv and zip file name
  
  #If no reference is entered by the user
  reference = inputData[0]['Customer Reference']
  
  numberRef = inputData[0]['Order Prefix'] + str(inputData[0]['Order ID'])  
  if len(reference) == 0:
    csvFilename = numberRef + '_DATA' + ".csv"  
    ipLasercsvFilename = numberRef + "_IPLASER" + '_' + supplier + ".csv"  
  else:
    csvFilename = numberRef + '_' + reference + ".csv"  
    ipLasercsvFilename = numberRef + '_' + reference + "_IPLASER" + '_' + supplier + ".csv"   
  
  
  #Write CSV file
  if inputData[0]['CSV File'] == True:
    with open(os.path.join(folder, csvFilename), 'w', newline='') as file:
      writer = csv.writer(file)
      writer.writerows(othercsvList)
  
    with open(os.path.join(folder, ipLasercsvFilename), 'w', newline='') as file:
      writer = csv.writer(file)
      writer.writerows(ipLasercsvList)
  

  
    
  
  #Create bin packed contact sheet
  #print(os.listdir(folder))    
  if inputData[0]['Contact Sheet'] == True: 
    if reference is not '':
      contactSheetName = numberRef + '_' + reference + '_CONTACT SHEET' + '_' + supplier + ".dxf" 
    else:
      contactSheetName = numberRef + '_CONTACT SHEET' + '_' + supplier + ".dxf" 
    #print(f"Text Width = {textWidth}")
    packed, sheetWidth = binPack(binPackList, folder, contactSheetName, False, textWidth)   #Pass in name to save to, boolean save, textWidth comes from return value when annotations are applied 
    #print(f"Packed Items: {packed}")
    #print(f"Sheet Width: {sheetWidth}")
    
    
    #----------------------Create contact sheet-----------------------------
    #print(file.name)
    sheetSize = sheetSize.sheetParameters()      
    maxSheetImages = sheetSize['Horizontal Boxes'] * sheetSize['Vertical Boxes']
    chunkId = 1
    #Break binpack list into chunks that fit on a page
    # How many elements each list should have
    n = maxSheetImages      
    # using list comprehension
    pageChunks = [binPackList[i:i + n] for i in range(0, len(binPackList), n)]
    #print(pageChunks)
    #Create the points for the grid
    x = np.linspace(sheetSize['imageStartPoint'][0], sheetSize['Width'], sheetSize['Horizontal Boxes'] + 1)
    y = np.linspace(sheetSize['imageStartPoint'][1], sheetSize['Height'], sheetSize['Horizontal Boxes'] + 1)
    # The meshgrid function returns
    # two 2-dimensional arrays
    x_1, y_1 = np.meshgrid(x, y)
    print(f'x_1 = {x_1}')
    print(f'y_1 = {y_1}')

    for c in range(0,len(pageChunks)-1): 
      print(f'Len Page Chunks {len(pageChunks)}')
      tdoc = ezdxf.new()
      msp = tdoc.modelspace()
      #Create contact sheet layers
      tdoc.layers.add(name='Dimensions', color = no_cut_colour)
      tdoc.layers.add(name='Hole_Drilling', color = drill_colour)
      tdoc.layers.add(name='Etch', color = etch_colour)
      tdoc.layers.add(name='Annotations', color = annotations_colour)
      tdoc.layers.add(name='Dont_Cut', color = no_cut_colour)
      tdoc.layers.add(name='Hole_Tapping', color = tapping_colour)
      tdoc.layers.add(name='Border')
      tdoc.layers.add(name='Profile')
      
      xc = 0
      yc = 0
      searchfiles = path.glob('*.dxf')
      #print(searchfiles)
      #for eachFile in searchfiles: 
      os.chdir(folder)
      positionGrid = sheetSize['imageStartPoint']
      
      for p in range(0,len(pageChunks[c])-1):
        print(f'Len Page Chunks C {len(pageChunks[c])}')
        # Create a block 
        #blockName = str(os.path.basename(eachFile))    #Remove path      
        blockName = pageChunks[c][p]['File']
        
        
        #Source document
        #sdoc = ezdxf.readfile(eachFile)
        sdoc = ezdxf.readfile(blockName)      
        targetBlock = tdoc.blocks.new(name='blk'+blockName)
        #Import source modelspace into block 
        importer = Importer(sdoc, tdoc)
        # query all source entities
        ents = sdoc.modelspace().query('*')      
        # import source entities into target block
        importer.import_entities(ents, targetBlock)
        #importer.import_modelspace(targetBlock)
        #Get the insert coordinates from the bin packing
        index = findInList(packed, 'File Name', blockName)
        xc = packed[index]['Position'][0]
        yc = packed[index]['Position'][1]
        #xpos = xc - (item['Bounding Box'][1][0])
        #ypos = yc - (item['Bounding Box'][1][1])
        print(pageChunks[c][p]['Bounding Box'][1][0] * pageChunks[c][p]['Scale Factor'])
        #print(pageChunks[c][p]['Scale Factor'])
        print(f'x-Pos {x_1[0]}')
        xpos = x_1[0][p] - (((pageChunks[c][p]['Bounding Box'][1][0])) * pageChunks[c][p]['Scale Factor'])
        ypos = y_1[0][p] - (((pageChunks[c][p]['Bounding Box'][1][1])) * pageChunks[c][p]['Scale Factor'])
        #Dimensions are added to the block rather than the original file, makes it cleaner for the supplier to deal with
        #as the information is only relevant on the contact sheet
        dimensionBoundingBox(targetBlock, pageChunks[c][p]['Pre Text Box'], pageChunks[c][p]['Text Height'])
        msp.add_blockref('blk'+blockName, (xpos,ypos), dxfattribs={
          'xscale': pageChunks[c][p]['Scale Factor'],
          'yscale': pageChunks[c][p]['Scale Factor'],
          })
        positionGrid = (positionGrid[0], positionGrid[1] + sheetSize['Box Height'])
        #xc = xc + 300
        #yc = yc + 0 
      #'''
      #Add border
      #Get template     
      templateRow = app_tables.drawingtemplates.get(size='A3', owner=userData['User'])
      template = templateRow['template']
      templateName = 'A3Template'
      mediaObject = anvil.BlobMedia('.dxf', template.get_bytes(), name=templateName)  
      with open(os.path.join(folder, templateName), 'wb+') as destFile:      
        destFile.write(mediaObject.get_bytes()) 
      #Source document
      sdoc = ezdxf.readfile(templateName) 
      targetBlock = tdoc.blocks.new(name='blk'+templateName)
      #Import source modelspace into block 
      importer = Importer(sdoc, tdoc)
      ents = sdoc.modelspace().query('*')      
      # import source entities into target block
      importer.import_entities(ents, targetBlock)      
      msp.add_blockref('blk'+templateName,(0,0), dxfattribs={
          'color': 0,
      })
      #'''
      importer.finalize()
      #Add reference detail to the contact sheet
      titleTextHeight = sheetSize['Title Text']     
      supplierText = msp.add_text(f"SUPPLIER: {supplier}").set_placement(sheetSize['supplierStartPoint'])
      supplierText.dxf.height = titleTextHeight
      supplierText.dxf.layer = 'Annotations'
      previousText = ('Supplier: ' + supplier)
      if reference is not '':
        refText = msp.add_text(f"ORDER ID: {numberRef + '_' + reference}").set_placement(sheetSize['idStartPoint'])  
      else:
        refText = msp.add_text(f"ORDER ID: {numberRef}").set_placement(sheetSize['idStartPoint']) 
        
      refText.dxf.height = titleTextHeight
      refText.dxf.layer = 'Annotations'    
      tdoc.saveas(contactSheetName+str(chunkId))
  
      #Save contact sheet as PDF
      doc, auditor = recover.readfile(contactSheetName+str(chunkId))
      if not auditor.has_errors:
          fileNameNoSuffix = contactSheetName+str(chunkId).strip('.dxf')
          msp = doc.modelspace()
          #msp_properties.set_colors("#eaeaeaff")
          matplotlib.qsave(doc.modelspace(), fileNameNoSuffix+str(chunkId) + '.pdf', bg='#FFFFFF00', size_inches=(16.5,11.7))
      chunkId = chunkId + 1  

    
    os.chdir('/tmp')   
  pass