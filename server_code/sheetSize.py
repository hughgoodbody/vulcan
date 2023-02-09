sheetSize = {'Page': 'A3',
             'Width': 390,
             'Height': 277,
             'Border': 5,
             'Horizontal Boxes': 4,
             'Vertical Boxes': 4,
             'Title Text': 6,
             'Spacing': 3,
             'Box Width': 119.33,
             'Box Height': 81.33,
             'Left Pad': 11,
             'Bottom Pad': 5,
}

def sheetParameters():
  sheetInfo = {'Page': 'A3',
             'Width': 358,
             'Height': 244,
             'Border': 5,
             'Horizontal Boxes': 3,
             'Vertical Boxes': 3,
             'Title Text': 6,
             'Spacing': 3,
             'Box Width': None,
             'Box Height': None,
             'Left Pad': 11,
             'Bottom Pad': 5,
             'imageStartPoint': None,
              'supplierStartPoint': None,
              'idStartPoint': None,
              'refStartPoint': None,
              }
  
  sheetInfo['Box Width'] = sheetInfo['Width'] / sheetInfo['Horizontal Boxes']
  sheetInfo['Box Height'] = sheetInfo['Height'] / sheetInfo['Vertical Boxes']  
  sheetInfo['imageStartPoint'] = (sheetInfo['Border']+sheetInfo['Spacing'], sheetInfo['Border']+sheetInfo['Bottom Pad']+(2*sheetInfo['Title Text'])+(2*sheetInfo['Spacing']))
  sheetInfo['supplierStartPoint'] = (sheetInfo['Border']+sheetInfo['Spacing'] + sheetInfo['Left Pad'], sheetInfo['Border']+sheetInfo['Bottom Pad']+(sheetInfo['Spacing'])+(sheetInfo['Title Text']))
  sheetInfo['idStartPoint'] = (sheetInfo['Border']+sheetInfo['Spacing'] + sheetInfo['Left Pad'], sheetInfo['Border']+sheetInfo['Bottom Pad'])
  sheetInfo['refStartPoint'] = (sheetInfo['Border']+sheetInfo['Spacing'] + sheetInfo['Left Pad'] + (sheetInfo['Width']/2), sheetInfo['Border']+sheetInfo['Bottom Pad'])
  return sheetInfo

