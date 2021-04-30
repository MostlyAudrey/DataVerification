#/usr/bin/python3

from random import *
import psycopg2

Cities = []
Clients = []
Orders = []
LineItems = []
Products = []

def Generate_Orders(num_orders_to_generate, order_date):
	print("Creating Items\n")

	num_cities = len(Cities)
	num_products = len(Products)

	orders = []
	items = []
	for n in range(num_orders_to_generate):
		client = Clients[randint(0, num_cities-1)]
		order_id = Orders[-1][0] + 1
		order = [order_id, client[0], order_date]
		Orders.append(order)
		orders.append(order)

		print("Order" + str(order))
		print("--------LineItems--------")

		for i in range(randint(1,15)):
			litem = [LineItems[-1][0] + 1, order_id, Products[randint(0, num_products-1)][0], randint(1,20), round(random() * 2.5 * 10,2)]
			LineItems.append(litem)
			items.append(litem)  

			print(litem)
		print()


	with open("../Mock_DB/Orders.csv", 'a') as orders_file:
		for o in orders:
			o_str = ""
			for x in o:
				o_str = o_str + str(x) + ','
			orders_file.write(o_str.strip(',') + "\n")

	with open("../Mock_DB/LineItems.csv", 'a') as line_items_file: 
		for i in items:
			item_str = ""
			for x in i:
				item_str = item_str + str(x) + ','
			line_items_file.write(item_str.strip(',') + "\n")

def tformat(tuple):
	return [int(x) if x.isdigit() else x for x in tuple]


with open("../Mock_DB/Cities.csv", 'r') as cities_file:
	cities_file.readline()
	for line in cities_file.readlines():
		tup = tformat(tuple(line.strip().split(',')))
		Cities.append(tup)

with open("../Mock_DB/Clients.csv", 'r') as clients_file:
	clients_file.readline()
	for line in clients_file.readlines():
		tup = tformat(tuple(line.strip().split(',')))
		Clients.append(tup)

with open("../Mock_DB/Orders.csv", 'r') as orders_file:
	orders_file.readline()
	for line in orders_file.readlines():
		tup = tformat(tuple(line.strip().split(',')))
		Orders.append(tup)

with open("../Mock_DB/LineItems.csv", 'r') as line_items_file: 
	line_items_file.readline()
	for line in line_items_file.readlines():
		tup = tformat(tuple(line.strip().split(',')))
		LineItems.append(tup)

with open("../Mock_DB/Products.csv", 'r') as products_file:
	products_file.readline()
	for line in products_file.readlines():
		tup = tformat(tuple(line.strip().split(',')))
		Products.append(tup)


with open("../Mock_DB/Orders.csv", 'a') as orders_file:
	orders_file.write("\n")

with open("../Mock_DB/LineItems.csv", 'a') as line_items_file: 
	line_items_file.write("\n")

Generate_Orders(3, "1/1/2021")

Generate_Orders(2, "3/7/2021")

Generate_Orders(3, "3/24/2021")

Generate_Orders(4, "4/10/2021")