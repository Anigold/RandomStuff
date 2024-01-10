'''
This is a script to extract order data from the Craftable order PDFs.

It takes the PDF file, converts it to a hardcoded HTML page, and then parses
the HTML to pull out the table data.

Because the order sheets are templated, the spacing of the HTML tables are the same
from page to page and we can use this fact to ensure that each respective table
is parsed in the exact same manner.

The main runtime of this file looks for all possible files in a folder, but
this can be easily modulated to a file-by-file basis.
'''
import pprint
from PyPDF2 import PdfReader
from os import listdir, remove
from os.path import isfile, join
from bs4 import BeautifulSoup
from openpyxl import load_workbook, Workbook
from io import StringIO
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from vendor_bots.VendorBot import VendorBot

'''
Parses HTML for table with supplied column data.

Args:
	html: the to-be-parsed HTML
	column_data: dictionary mapping column header to the distinguishing HTML element attributes

Returns:
	output_data: dictionary mapping column names to row data
'''
def extract_table_column_data(html: str, column_data: dict) -> dict:

	output_data = {}
	soup 		= BeautifulSoup(html, 'html.parser')

	for key in column_data:

		column_info = [div.extract() for div in soup.select(f'[style*="{column_data[key]["styles"]}"]')]

		if key not in output_data: output_data[key] = column_info

	return output_data

'''
Writes file data to supplied string buffer as hardcoded HTML.

Args:
	path: path to file
	string_buffer: to-be-written-to string buffer

Returns:
	None
'''
def convert_to_html(path: str, string_buffer: StringIO) -> None:
	with open(path, 'rb') as pdf_file:
		extract_text_to_fp(pdf_file, string_buffer, laparams=LAParams(), output_type='html', codec=None)
	return

'''
Pulls out order information from the Craftable HTML data.

Args:
	column_info: dictionary mapping columns names to row data

Returns:
	Dictionary mapping SKU to ordering quantity
'''
def retrieve_item_ordering_information(column_info: dict) -> dict:

	skus 	   = []
	quantities = []
	for sku in column_info['item_skus']:
		
		sku_spans = sku.find_all('span')
		sku 	  = ''
		
		for sku_span in sku_spans:
			if 'SKU: ' in sku_span.text: sku = sku_span.text.replace('SKU: ', '').strip().replace('\n', '')

		if sku: skus.append(sku)

	for quantity in column_info['item_quantities']:
		if quantity.text.strip().isnumeric(): quantities.append(quantity.text.strip())

	return {skus[i]: quantities[i] for i in range(len(skus))}

'''
Get all file-type objects found in specified path.

Args:
	path: path to the folder

Returns:
	List of file references
'''
def get_files(path: str) -> list:
	return [file for file in listdir(path) if isfile(join(path, file))]

def craftable_pdf_to_excel(path: str, vendor: VendorBot):
	order_sheets = get_files(f'{path}')
	
	for order_sheet in order_sheets:

		output = StringIO()
		
		# Extract PDF text to string builder
		convert_to_html(join(path, order_sheet), output)

		# Convert PDF text to HTML page
		with open(f'{path}temp{order_sheet.split(".")[0]}.html', 'w') as html_file:
			html_file.write(output.getvalue())

		# Parse HTML page
		with open(f'{path}temp{order_sheet.split(".")[0]}.html') as fp:
			column_info = extract_table_column_data(fp, {'item_skus': {'styles': 'left:52px'}, 'item_quantities': {'styles': 'left:352px'}})
			
		items = retrieve_item_ordering_information(column_info)

		workbook = vendor.format_for_file_upload(items, f'{path}{order_sheet.split(".")[0]}')
		
		

		remove(join(path, f'temp{order_sheet.split(".")[0]}.html'))
