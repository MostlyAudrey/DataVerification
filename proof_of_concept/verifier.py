#/usr/bin/python3

import hashlib
import click
import linecache

from node import LeafNode, InnerNode

InnerNodeFile = "Mock_DB/InnerNodes.csv"
LeafNodeFile = "Mock_DB/LeafNodes.csv"
InnerNodes = {}
LeafNodes = {}

def tformat(tuple):
	return [int(x) if x.isdigit() else x for x in tuple]

def loadChildren(root_node_pk, is_leaf):
	if root_node_pk is None or root_node_pk == "None": return
	if not is_leaf:
		lc, lc_hash, rc, rc_hash, num_leaves = tformat(tuple(linecache.getline(InnerNodeFile, root_node_pk + 2).strip().split(',')))
		if rc == "None": rc, rc_hash = None, None
		if root_node_pk in InnerNodes: return
		InnerNodes[root_node_pk] = InnerNode(lc, lc_hash, rc, rc_hash, num_leaves)
		# print('{}:{}'.format(root_node_pk, InnerNodes[root_node_pk]))
		loadChildren(lc, int(num_leaves) == 2)
		if rc != "None":
			loadChildren(rc, int(num_leaves) <= 2)
	else:
		table, primary_key, data_hash = tformat(tuple(linecache.getline(LeafNodeFile, root_node_pk + 2).strip().split(',')))
		LeafNodes[root_node_pk] = LeafNode(table, primary_key, data_hash)

def verifyChildren(root_node_pk):
	if root_node_pk is None or root_node_pk == "None": return True
	root = InnerNodes[root_node_pk]
	# print("Verifying node{}".format(root_node_pk))
	if (root.num_leaf_nodes > 2):
		lc = InnerNodes[root.left_child_pk]	
		# print('LC: {}: {}'.format(root.left_child_pk, lc))
		# print( '{}: {}'.format( lc.GetHash(), root.left_child_hash))
		if lc.GetHash() != root.left_child_hash: return False

		if root.right_child_pk != "None":
			rc = InnerNodes[root.right_child_pk]
			# print('RC: {}: {}'.format(root.right_child_pk, rc))
			# print( '{}: {}'.format( rc.GetHash(), root.right_child_hash))
			if rc.GetHash() != root.right_child_hash: return False

		return verifyChildren(root.left_child_pk) and verifyChildren(root.right_child_pk)
	else:
		lc = LeafNodes[root.left_child_pk]	
		# print('LC: {}: {}'.format(root.left_child_pk, lc))
		# print( '{}: {}'.format( lc.GetHash(), root.left_child_hash))
		if lc.GetHash() != root.left_child_hash: 
			if root.num_leaf_nodes == 1:
				lc_i = InnerNodes[root.left_child_pk]
				if lc_i.GetHash() != root.left_child_hash: return False
				return verifyChildren(root.left_child_pk)
			else: return False

		if root.right_child_pk is not None:
			rc = LeafNodes[root.right_child_pk]
			# print('RC: {}: {}'.format(root.right_child_pk, rc))
			# print( '{}: {}'.format( rc.GetHash(), root.right_child_hash))
			if rc.GetHash() != root.right_child_hash: return False
	return True




def verifyTupleData(node):
	print("HIOKS")


def fail(msg="The data could not be verified, data may have been tampered with"):
	print(msg)
	exit()


@click.command()
@click.option('-o', '--order_id', required=True, prompt='Order ID', help='The pk of the order you are trying to verify')
@click.option('-r', '--root_hash', required=True,  prompt='The data verification key provided when you created the order', help='This is the hash of the root of the data verification data structure')
def main(order_id, root_hash):

	root_node_pk = None

	# 1. find the root of the verification structure associated with this order
	with open("Mock_DB/order_root_node.csv") as order_root_node:
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
		

	# 4. Recursively verify the contents of all of the Inner Nodes

	if not verifyChildren(root_node_pk):
		fail()


	# 5. Load and verify the tuple data in each leaf node

	# for node in LeafNodes:
	# 	if not verifyTupleData(node): 
	# 		fail()
	


	print("The data has been verified, the order has not been tampered with")


if __name__ == '__main__':
    main()