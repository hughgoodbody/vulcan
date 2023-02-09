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
  sheetSize = {'Page': 'A3',
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
}
  
sheetSize['Box Width'] = sheetSize['Width'] / sheetSize['Horizontal Boxes']
sheetSize['Box Height'] = sheetSize['Height'] / sheetSize['Vertical Boxes']

ImageStartPoint = (sheetSize['Border']+sheetSize['Spacing'], sheetSize['Border']+sheetSize['Bottom Pad']+(2*sheetSize['Title Text'])+(2*sheetSize['Spacing']))
supplierStartPoint = (sheetSize['Border']+sheetSize['Spacing'] + sheetSize['Left Pad'], sheetSize['Border']+sheetSize['Bottom Pad']+(sheetSize['Spacing'])+(sheetSize['Title Text']))
idStartPoint = (sheetSize['Border']+sheetSize['Spacing'] + sheetSize['Left Pad'], sheetSize['Border']+sheetSize['Bottom Pad'])
refStartPoint = (sheetSize['Border']+sheetSize['Spacing'] + sheetSize['Left Pad'] + (sheetSize['Width']/2), sheetSize['Border']+sheetSize['Bottom Pad'])

