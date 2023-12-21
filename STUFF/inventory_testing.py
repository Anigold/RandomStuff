import pandas as pd
import numpy as np

data_file_location = 'C:/Users/Will/Desktop/Andrew/BreadInventory.xlsx'
df = pd.read_excel(data_file_location)

def graph_product_ordering(product_info: None) -> None:
	pass

def run():
	items = {}
	for i in range(2, len(df.index)-1):

		average_order_size 	= 0
		number_of_orders 	= 0
		item_name 			= df.iloc[i, 0]

		if item_name not in items:
			items[item_name] = {
				"orders": [],
				"average_order_size": 0,
			}
		# Orders
		for j in range(13, len(df.columns)-1, 6):

			order_value = df.iloc[i, j]
			if not (np.isnan(order_value)) and order_value > 0:
				average_order_size += order_value
			
			number_of_orders += 1

		

		print(average_order_size / number_of_orders)



if __name__ == '__main__':
	run()
	