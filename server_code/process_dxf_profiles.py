import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#
@anvil.server.callable
def createOutputPdf(userData, inputList, prefix, orderId, type, supplier):
  import anvil.pdf
  from anvil.pdf import PDFRenderer
  pdf = PDFRenderer(page_size='A4', landscape=True, scale=0.5, filename=(prefix + str(orderId)) + '.pdf').render_form('printTemplates.profiles_exporter_Interactive_pdf_print', inputList, prefix, orderId)
  app_tables.files.add_row(file=pdf, type=type, owner=userData['User'], supplier=supplier)
  return pdf
  pass


@anvil.server.callable
def launchProcessProfiles(userData, inputData, prefix, refId, supplier):
  pass


@anvil.server.background_task
def processProfiles(userData, inputData, prefix, refId, supplier):
  #update order id in table
  # Fetch a row.
  row = app_tables.numbers.get(owner=userData['User'])
  # Update method 1
  row.update(RefNumber=(refId+1))  
  # Update method 2
  #row['name']="fred"  
  pass