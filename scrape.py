### Python 3
import lxml.html
import scraperwiki
import html5lib
import pandas as pd
import json
import gspread as gs
from oauth2client.client import SignedJwtAssertionCredentials


### The url
url = 'http://missingmigrants.iom.int/en/latest-global-figures'

### Get the web page in the right format
html = scraperwiki.scrape(url)
tree = lxml.html.fromstring(html)

### Use css inspector / firebugs, etc. to get the css
### we can also use xpath
## we chose css for convience
mytable = tree.cssselect('table.table:nth-child(8)')[0]

### Handy function from the Pandas library to turn the table into DataFrame
pd_tables = pd.read_html(lxml.etree.tostring(mytable, method = 'html'),
                         index_col = 0)[0]

### Check the results
print(pd_tables)


### Upload the data to Google spreadsheets
### Credentials in json format
json_key = json.load(open('google_credential.json'))
scope = ['https://spreadsheets.google.com/feeds']
credentials = SignedJwtAssertionCredentials(json_key['client_email'],
                                            json_key['private_key'].encode(),
                                            scope)
gc = gs.authorize(credentials)

### Turn number to letter for the spreadsheet
def numberToLetters(q):
    q = q - 1
    result = ''
    while q >= 0:
        remain = q % 26
        result = chr(remain+65) + result;
        q = q//26 - 1
return result

### Open the first sheet
workbook = gc.open("missing_migrants")
sheet = workbook.get_worksheet(0)

## prepare the data
columns_name = pd_tables.columns.values.tolist()
columns_name.insert(0, "") ## for the rownames

rows_name = pd_tables.index.tolist()

## row and col index
num_lines, num_columns = pd_tables.shape


## selection of the range that will be updated
## Start at B1
cell_list = sheet.range('A1:'+numberToLetters(len(columns_name))+'1')

## modifying the values in the range
for cell in cell_list:
    cell.value = columns_name[cell.col - 1]
    
## update in batch
sheet.update_cells(cell_list)

### Do the same thing for rownames
## selection of the range that will be updated 
cell_list = sheet.range("A2:A" + str(len(rows_name) + 1))

## modifying the values in the range
for cell in cell_list:
    cell.value = rows_name[cell.row - 2]

## update in batch
sheet.update_cells(cell_list)
    

### Get the rest of the data to populate the sheets
## selection of the range that will be updated
cell_list = sheet.range('B2:'+numberToLetters(num_columns + 1)+str(num_lines + 1))

## modifying the values in the range
for cell in cell_list:
    cell.value = pd_tables.iloc[cell.row-2,cell.col-2]
    
## Update
sheet.update_cells(cell_list)

### Metadata
css_meta1 = "p:nth-child(10)"
css_meta2 = "p:nth-child(11)"

### Caveats
meta1 = tree.cssselect(css_meta1)[0]

### Date
meta2 = tree.cssselect(css_meta2)[0]

### http://docs.hdx.rwlabs.org/providing-metadata-for-your-datasets-on-hdx/
metadata = {'location' : 'World',
            'source'   : 'IOM',
            'date of dataset': lxml.etree.tostring(meta2, method = 'html'),
            'comment' : lxml.etree.tostring(meta1, method = 'html')}
            
