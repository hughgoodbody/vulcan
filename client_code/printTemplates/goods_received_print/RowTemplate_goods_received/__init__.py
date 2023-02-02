from ._anvil_designer import RowTemplate_goods_receivedTemplate
from anvil import *
import anvil.server
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .... import user_data
import base64


class RowTemplate_goods_received(RowTemplate_goods_receivedTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.


    #Set Part Number or Name
    self.lnkUrl.url = self.item['Part URL']
    if self.item['Part Number'] is None:
      self.lnkUrl.text = self.item['Part Name']
    else:
      self.lnkUrl.text = self.item['Part Number']

    #Set thumbnail image from the 'thumbnail' field - decode from base64
    #print(self.item['Thumbnail'])
    self.imgdata = base64.b64decode(self.item['Part Thumbnail'])
    mymedia = anvil.BlobMedia('image/png', self.imgdata)
    self.image_1.source = mymedia

