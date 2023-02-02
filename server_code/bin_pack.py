import anvil.server
from typing import List
import ezdxf
from ezdxf import colors
from ezdxf.addons import binpacking as bp
import os

SMALL_ENVELOPE = ("small-envelope", 420, 295,1, 0)
LARGE_ENVELOPE = ("large-envelope", 1180, 917, 1, 0)
THREE_M_SHEET = ("three-meter-sheet", 3000, 2142, 0)
SMALL_TEST = ("test-sheet", 500, 200, 0)

A_THREE = ("A3", 420, (420/1.4), 0)
A_ZERO = ("A3", 1189, (1189/1.4), 0)
ONE_METER = ("1m", 1000, (1000/1.4), 0)
TWO_METER = ("2m", 2000, (2000/1.4), 0)
THREE_METER = ("3m", 3000, (3000/1.4), 0)
FOUR_METER = ("4m", 4000, (4000/1.4), 0)
FIVE_METER = ("5m", 5000, (5000/1.4), 0)
SIX_METER = ("6m", 6000, (6000/1.4), 0)

binList = [A_THREE, A_ZERO, ONE_METER, TWO_METER, THREE_METER, FOUR_METER, FIVE_METER, SIX_METER]
#binList = [ONE_METER]


#Height calculated from notes text height at 10mm
notes_height = (10*10)+2+(9*5)
#Width Padding
widthPad = 20

def binPack(xLstItems, saveLoc, xsaveAsName, xSave, textWidth):   #Pass in notes height here from calling function
  
  packedList = []    #List of the bin packed item with position
  for testBin in binList:
    ALL_BINS = [testBin]
    def build_packer():
        packer = bp.FlatPacker()
        for item in xLstItems:
          #print(item)
          #print(item['Bounding Box'])
          #.add_item(item['File'], abs(item['Bounding Box'][0][0] - item['Bounding Box'][1][0]) + widthPad, abs(item['Bounding Box'][0][1] - item['Bounding Box'][1][1] + notes_height), 0)
          #Width and height are swapped around in order to get the boxes oriented correctly
          #Get largest of bounding box width or text width
          if (abs(item['Bounding Box'][0][0] - item['Bounding Box'][1][0])) > textWidth:
            boxWidth = (abs(item['Bounding Box'][0][0] - item['Bounding Box'][1][0]))
          else:
            boxWidth = textWidth
          packer.add_item(item['File'], abs(item['Bounding Box'][0][1] - item['Bounding Box'][1][1]) + notes_height, boxWidth + widthPad, 0)
          #bp.RotationType.HWD
          bp.RotationType.WDH
          bp.Axis.WIDTH
        return packer
    
    
    def make_doc():
        doc = ezdxf.new()
        doc.layers.add("FRAME", color=colors.YELLOW)
        doc.layers.add("ITEMS")
        doc.layers.add("TEXT")
        return doc
    
    
  
    bins: List[bp.Bin] = []
    for box in ALL_BINS:
        packer = build_packer()
        packer.add_bin(*box)
        packer.pack(bp.PickStrategy.BIGGER_FIRST)
        bins.extend(packer.bins)
      
    
      
        
  
      
    doc = make_doc()
    bp.export_dxf(doc.modelspace(), bins, offset=(20, 20, 0))
    #print(packer.bins)
    #print(packer.bins[0])
    #print(packer.bins[0].items)
    if len(packer.bins[0].items) < len(xLstItems):
      continue
    elif len(packer.bins[0].items) == len(xLstItems): 
      break

  sheetWidth = packer.bins[0].width  
  for b in packer.bins:  
      #print("FITTED ITEMS:")
      for item in b.items:
            #print(f"Packed item: {item.payload} --- {item.position}")
            packedList.append({"File Name": item.payload, "Position": item.position})
       
  
  if xSave == True:
    doc.saveas(xsaveAsName)
  return packedList, sheetWidth







