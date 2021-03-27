#/usr/bin/python3

import hashlib
from node import LeafNode, InnerNode


Cities = []
Clients = []
Orders = []
LineItems = []
Products = []
InnerNodes = []
LeafNodes = []

def CreateLeafNodes(order_id):
	order = Orders[order_id - 1]
	client = Clients[order[1] - 1]
	city = Cities[client[4] - 1]
	line_items = [item for item in LineItems if item[1] == order_id]
	product_ids = [item[2] for item in line_items]
	products = [p for p in Products if p[0] in product_ids]

	leaf_data = [order, client, city] + line_items + products

	leaf_nodes = []
	for data in leaf_data:
		# print(data)
		table = ""
		if data in Cities:
			table = 'tb_city'
		elif data in Clients:
			table = 'tb_client'
		elif data in Orders:
			table = 'tb_order'
		elif data in LineItems:
			table = 'tb_lineitem'
		elif data in Products:
			table = 'tb_product'
		node = LeafNode(table, data[0], hashlib.sha256(str(data).encode()).hexdigest())
		leaf_nodes.append(len(LeafNodes))
		LeafNodes.append(node)
	return leaf_nodes

def CreateTree(child_nodes, are_leaves):

	if len(child_nodes) == 1:
		return len(InnerNodes) - 1

	parent_nodes = []
	i = 0
	while i < len(child_nodes):
		lchild = child_nodes[i]
		rchild = None
		if (i + 1) < len(child_nodes):
			rchild = child_nodes[i + 1]

		left_child_hash, right_child_hash, num_leaf_nodes = None, None, 1

		if are_leaves:
			left_child_hash = LeafNodes[lchild].GetHash()
			if rchild is not None:
				num_leaf_nodes = 2
				right_child_hash = LeafNodes[rchild].GetHash()
		else:
			num_leaf_nodes = InnerNodes[lchild].GetNumLeafNodes()
			left_child_hash = InnerNodes[lchild].GetHash()

			if rchild is not None:
				num_leaf_nodes += InnerNodes[rchild].GetNumLeafNodes() 
				right_child_hash = InnerNodes[rchild].GetHash()

		pnode = InnerNode(lchild, left_child_hash, rchild, right_child_hash, num_leaf_nodes, are_leaves)
		parent_nodes.append(len(InnerNodes))
		InnerNodes.append(pnode)
		i += 2

	return CreateTree(parent_nodes, False)


def CheckTreeIndex(root, tree_index, tuple):
	return

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

trees = {}

for order in Orders:
	leaf_nodes = CreateLeafNodes(order[0])
	trees[order[0]] = CreateTree(leaf_nodes, True)


with open("../Mock_DB/InnerNodes.csv", 'w') as inner_nodes_file:
	inner_nodes_file.write('left_child_pk, left_child_hash, right_child_pk, right_child_hash, num_leaf_nodes\n')
	for node in InnerNodes:
		inner_nodes_file.write('{},{},{},{},{},{}\n'.format(node.left_child_pk, node.left_child_hash, node.right_child_pk, node.right_child_hash, node.num_leaf_nodes,node.children_are_leaves))

with open("../Mock_DB/LeafNodes.csv", 'w') as leaf_nodes_file:
	leaf_nodes_file.write('table, primary_key_value, data hash\n')
	for node in LeafNodes:
		leaf_nodes_file.write('{},{},{}\n'.format(node.table, node.primary_key, node.data_hash))

with open("../Mock_DB/order_root_node.csv", 'w') as order_root_node:
	order_root_node.write('order_id, root_node\n')
	for order_id in trees:
		order_root_node.write('{},{}\n'.format(order_id, trees[order_id]))
		print ('{}, Hash = {}'.format(order_id, InnerNodes[trees[order_id]].GetHash()))