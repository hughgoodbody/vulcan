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

#### CHOOSE COLOURS ####
'''
The colors are assigned as follows: 1 Red, 2 Yellow, 3 Green, 4 Cyan, 5 Blue, 6 Magenta, 7 White/Black.
'''
etch_colour = 3
annotations_colour = 4
no_cut_colour = 1
tapping_colour = 6
drill_colour = 5

@anvil.server.callable
def annotateDxf(userData, folder, inputData, orderId, tappedHoles, supplier, supplierData):
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
  pass