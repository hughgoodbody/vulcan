1. Create a goods received form
2. Shims etc, remove operations

4. Supplier bed size
5. Supplier material for filename

7. Create version

9. Update table
10. Processes in suppliers as a list rather than linked table 
11. Clear data table at start of background task also
12 Create new list of just hole tapping data and filename when doing the export

14. DXF lineweight,  change version to 2000 or newer   
15. Operations in pdf instead of warnings
safe filename
https://stackoverflow.com/questions/7406102/create-sane-safe-filename-from-any-unsafe-string

Two titles for printed PDF's
Supplier Summary: Lasershape Order Id: 783
Order Summary: 783-786
  
BUGS:
Thumbnail view matrix

Materials API call:
https://cad.onshape.com/api/materials/libraries/d/81e33fccf396569c09b88d8f/w/71306831da3af0636d92f2ed/e/2335880ba0008e0ed01e8a07
Standard Material Library Doc: https://cad.onshape.com/documents/2718281828459eacfeeda11f/w/97628b48cc974c2681faacfc/e/6bbab304a1f64e7d640a2d7d

if a version, skip the featurescript code api call, and get the parts from the constituentBodyIds, invert the list first as usually listed in the last entry
https://www.w3schools.com/python/ref_list_reverse.asp

DataGrid Borders: https://anvil.works/forum/t/data-grid-visible-internal-borders/6122
Get key for value
d = {'key1': 'aaa', 'key2': 'aaa', 'key3': 'bbb'}
keys = [k for k, v in d.items() if v == 'bbb']
