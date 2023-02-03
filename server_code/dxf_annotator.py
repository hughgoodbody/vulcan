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
from . import BinPacker
from .BinPacker import binPack
from .functions import detailTapping
from .functions import dimensionPrincipal
from .functions import dimensionBoundingBox
from .functions import findInList
from ezdxf.addons import Importer
from . import functions
import math
from . import user_data

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

  if inputData != False:#Information extracted from information passed in from dictionaries
    

  
  #For loop to iterate through files in directory
  #print(f'START Directory Contents: {os.listdir(f.name)}') 
  path = Path(folder)
  searchfiles = path.glob('*.dxf')
  pass