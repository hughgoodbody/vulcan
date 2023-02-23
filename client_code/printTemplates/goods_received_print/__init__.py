from ._anvil_designer import goods_received_printTemplate
from anvil import *
import anvil.server
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import base64
from ... import user_data
from .RowTemplate_goods_received import RowTemplate_goods_received

from datetime import date

class goods_received_print(goods_received_printTemplate):
  def __init__(self, inputList, prefix, orderId, heading, supplier, **properties):
    self.additionalParts = []
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    #Data from input List
    self.panel = self.repeating_panel_1
    self.panel.items = inputList


    #Set thumbnail image from the 'thumbnail' field - decode from base64
    self.imgdata = base64.b64decode(self.panel.items[0]['Parent Thumbnail'])
    mymedia = anvil.BlobMedia('image/png', self.imgdata)
    self.imgAssemblyImage.source = mymedia

    #Parent Name and Link
    self.lnkAssemblyLink.url = self.panel.items[0]['Parent URL']
    self.lnkAssemblyLink.text = self.panel.items[0]['Parent Document Name'] + ' / ' + self.panel.items[0]['Parent Element Name']
    self.lblIdRef.text = prefix + str(orderId)
    self.txtReference.text = self.panel.items[0]['Order Reference']
    self.lblHeading.text = heading + ' - ' + supplier


    #Get date
    today = date.today()
    # dd/mm/YY
    self.lblDate.text = today.strftime("%d/%m/%Y")
