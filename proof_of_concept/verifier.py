#/usr/bin/python3

import hashlib
import click
import linecache

from node import LeafNode, InnerNode

InnerNodeFile = "../Mock_DB/InnerNodes.csv"
LeafNodeFile = "../Mock_DB/LeafNodes.csv"
CitiesFile = "../Mock_DB/Cities.csv"
ClientsFile = "../Mock_DB/Clients.csv"
LineItemsFile = "../Mock_DB/LineItems.csv"
OrdersFile = "../Mock_DB/Orders.csv"
ProductsFile = "../Mock_DB/Products.csv"
InnerNodes = {}
LeafNodes = {}

def tformat(tuple):
	return [int(x) if x.isdigit() else True if x == 'True' else False if x == 'False' else x for x in tuple]

def loadChildren(root_node_pk, is_leaf):
	if root_node_pk is None or root_node_pk == "None": return
	if not is_leaf:
		lc, lc_hash, rc, rc_hash, num_leaves, children_are_leaves = tformat(tuple(linecache.getline(InnerNodeFile, root_node_pk + 2).strip().split(',')))
		if rc == "None": rc, rc_hash = None, None
		if root_node_pk in InnerNodes: return
		InnerNodes[root_node_pk] = InnerNode(lc, lc_hash, rc, rc_hash, num_leaves, children_are_leaves)
		# print('{}:{}'.format(root_node_pk, InnerNodes[root_node_pk]))
		loadChildren(lc, children_are_leaves )
		if rc != "None":
			loadChildren(rc, children_are_leaves)
	else:
		table, primary_key, data_hash = tformat(tuple(linecache.getline(LeafNodeFile, root_node_pk + 2).strip().split(',')))
		LeafNodes[root_node_pk] = LeafNode(table, primary_key, data_hash)

def verifyChildren(root_node_pk):
	if root_node_pk is None or root_node_pk == "None": return True
	root = InnerNodes[root_node_pk]
	if not root.children_are_leaves:
		lc = InnerNodes[root.left_child_pk]	
		# print('LC: {}: {}'.format(root.left_child_pk, lc))
		# print( '{}: {}'.format( lc.GetHash(), root.left_child_hash))
		if lc.GetHash() != root.left_child_hash: return False
		if root.right_child_pk != "None" and root.right_child_pk is not None:
			rc = InnerNodes[root.right_child_pk]
			# print('RC: {}: {}'.format(root.right_child_pk, rc))
			# print( '{}: {}'.format( rc.GetHash(), root.right_child_hash))
			if rc.GetHash() != root.right_child_hash: return False

		return verifyChildren(root.left_child_pk) and verifyChildren(root.right_child_pk)
	else:
		lc, rc = LeafNodes[root.left_child_pk], None
		# print('LC: {}: {}'.format(root.left_child_pk, lc))
		# print( '{}: {}'.format( lc.GetHash(), root.left_child_hash))
		if lc.GetHash() != root.left_child_hash: return False



		if root.right_child_pk is not None:
			rc = LeafNodes[root.right_child_pk]
			# print('RC: {}: {}'.format(root.right_child_pk, rc))
			# print( '{}: {}'.format( rc.GetHash(), root.right_child_hash))
			if rc.GetHash() != root.right_child_hash: return False

		return verifyTupleData(lc) and verifyTupleData(rc)

def getTableFile(table_name):
    switcher = {
        "tb_order": OrdersFile,
        "tb_city": CitiesFile,
        "tb_product": ProductsFile,
        "tb_lineitem": LineItemsFile,
        "tb_client": ClientsFile
    }
    return switcher.get(table_name, None)

def verifyTupleData(leaf_node):
	if leaf_node is None: return True
	tableFile, tuple_data = getTableFile(leaf_node.table), None
	with open(tableFile, 'r') as file: 
		file.readline()
		for line in file.readlines():
			tup = tformat(tuple(line.strip().split(',')))
			if tup[0] == leaf_node.primary_key:
				tuple_data = tup
				break
	return hashlib.sha256(str(tuple_data).encode()).hexdigest() == leaf_node.data_hash


def fail(msg="The data could not be verified, data may have been tampered with"):
	print(msg)
	exit()


@click.command()
@click.option('-o', '--order_id', required=True, prompt='Order ID', help='The pk of the order you are trying to verify')
@click.option('-r', '--root_hash', required=True,  prompt='The data verification key provided when you created the order', help='This is the hash of the root of the data verification data structure')
def main(order_id, root_hash):

	root_node_pk = None

	# 1. find the root of the verification structure associated with this order
	with open("../Mock_DB/order_root_node.csv") as order_root_node:
		order_root_node.readline()
		for line in order_root_node.readlines():
			tmp_order, tmp_root_node_pk = tuple(line.strip().split(','))
			if tmp_order == order_id:
				root_node_pk = int(tmp_root_node_pk)
				break

	if root_node_pk is None:
		print("No matching verification data structure found")
		exit()

	# 2. Recursively load all Inner and Leaf Nodes into memory
	loadChildren(root_node_pk, False)

	# 3. Verify the root node matches the provided hash
	
	if root_hash != InnerNodes[root_node_pk].GetHash():
		fail("Root hashes do not match, data may have been tampered with")
		
	# 4. Recursively verify the contents of all of the nodes

	if not verifyChildren(root_node_pk):
		fail()

	print("The data has been verified, the order has not been tampered with")


if __name__ == '__main__':
    main()