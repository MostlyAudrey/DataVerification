#/usr/bin/python3

import hashlib
from node import LeafNode, InnerNode


Cities = [
( 1, 'Baltimore', 'MD', 'US' ),
( 2, 'Atlanta',   'GA', 'US' ),
( 3, 'Dallas',    'TX', 'US' ),
( 4, 'Demoins',   'IO', 'US' ),
( 5, 'Paris',     'P',  'FR')
]

Clients = [
( 1, 'Joy Arulraj',             35, '1 North Ave',              2, ' 30332'),
( 2, 'Bob Waters',              86, '123 Marietta St.',         4, ' 30341'),
( 3, 'Bill Leahy',              69, 'A nice beach somewhere',   3, ' 30312'),
( 4, 'Kishore Ramachandrian',   41, '2 Clough Lane',            2, ' 12423'),
]

Orders = [
( 1, 1, '2021-02-10' ),
( 2, 1, '2021-02-13' ),
( 3, 2, '2021-02-18' ),
( 4, 4, '2021-02-19' ),
( 5, 1, '2021-02-29' ),
( 6, 3, '2021-03-08' ),
( 7, 2, '2021-03-12' ),
]

LineItems = [
( 1,  1, 1,   15, 33.00 ),
( 2,  1, 12,  2,  5.00  ),
( 3,  1, 101, 20, 3.75  ),
( 4,  2, 1,   15, 33.00 ),
( 5,  2, 12,  2,  5.00  ),
( 6,  2, 101, 20, 3.75  ),
( 7,  2, 1,   15, 33.00 ),
( 8,  3, 12,  2,  5.00  ),
( 9,  3, 101, 20, 3.75  ),
( 10, 4, 1,   15, 33.00 ),
( 11, 5, 12,  2,  5.00  ),
( 12, 5, 101, 20, 3.75  ),
( 13, 5, 1,   15, 33.00 ),
( 14, 5, 12,  2,  5.00  ),
( 15, 6, 101, 20, 3.75  ),
( 16, 6, 1,   15, 33.00 ),
( 17, 6, 12,  2,  5.00  ),
( 18, 7, 101, 20, 3.75  ),
]

Products = [
( 1,   'Garden Hose',         'Plant inc.'       ),
( 2,   'Garden Hose',         'Plant inc.'       ),
( 12,  'Strawberry Poptarts', 'Kellogs'          ),
( 13,  'BlueBerry Poptarts',  'Kellogs'          ),
( 14,  'Strawberry Poptarts', 'Kellogs'          ),
( 15,  'Strawberry Poptarts', 'Kellogs'          ),
( 16,  'Strawberry Poptarts', 'Kellogs'          ),
( 17,  'Strawberry Poptarts', 'Kellogs'          ),
( 18,  'Strawberry Poptarts', 'Kellogs'          ),
( 19,  'Strawberry Poptarts', 'Kellogs'          ),
( 101, 'Honey Nut Cherios',   'General Mills'    ),
( 102, 'Honey Nut Cherios',   'General Mills'    ),
( 103, 'Honey Nut Cherios',   'General Mills'    ),
( 104, 'Honey Nut Cherios',   'General Mills'    ),
( 105, 'Honey Nut Cherios',   'General Mills'    ),
( 106, 'Honey Nut Cherios',   'General Mills'    ),
( 107, 'Honey Nut Cherios',   'General Mills'    ),
]



# def CreateOrder(order_id, line_item_ids):

#     client_id = Orders[order_id - 1][1]

#     client_node = node.LeafNode('tb_client', client_id, hashlib.sha256( str(Clients[client_id]).encode() ) )
#     order_node  = node.LeafNode('tb_order',  order_id,  hashlib.sha256( str(Orders[order_id]).encode() ) )
#     print(client_node)
#     print(order_node)

# CreateOrder(1, [1,2,3])

def CreateOrder(order_id):
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

    	node = LeafNode(table, data[0], hashlib.sha256(str(data).encode()))
    	leaf_nodes.append(node)
    	# print(node)
    return leaf_nodes

treeNodes = []
root_node = None
def CreateTree(leaf_nodes):
	global treeNodes, root_node

	if len(leaf_nodes) == 1:
		root_node = leaf_nodes[0]
		treeNodes.append(root_node)
		return

	parent_nodes = []
	i = 0
	while i < len(leaf_nodes):
		lchild = leaf_nodes[i]
		rchild = None
		if (i + 1) < len(leaf_nodes):
			rchild = leaf_nodes[i + 1]

		num_leaf_nodes = 0
		if isinstance(lchild, LeafNode):
			if (rchild is not None):
				num_leaf_nodes = 2 
			else:
				num_leaf_nodes = 1
		else:
			if (rchild is not None):
				num_leaf_nodes = lchild.GetNumLeafNodes() + rchild.GetNumLeafNodes() 
			else:
				num_leaf_nodes = lchild.GetNumLeafNodes()
		pnode = InnerNode(lchild, hashlib.sha256(str(lchild).encode()), rchild, hashlib.sha256(str(rchild).encode()), num_leaf_nodes)
		print(pnode)
		parent_nodes.append(pnode)
		i += 2

	treeNodes += parent_nodes
	CreateTree(parent_nodes)


def CheckTreeIndex(root, tree_index, tuple):
	return

trees = {}
for order in Orders:
	leaf_nodes = CreateOrder(order[0])
	print(leaf_nodes)
	CreateTree(leaf_nodes)
	trees[order[0]] = root_node

print(trees)
