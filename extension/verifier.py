#/usr/bin/python3

import hashlib
import click
import linecache
import psycopg2

from node import LeafNode, InnerNode

host="localhost"
dbname="DataVerification"
user="postgres"
pswd="evan8989" #put password here
ini = "dbname=" + dbname + " user=" + user + " password=" + pswd
conn = psycopg2.connect(
	host=host,
	database=dbname,
	user=user,
	password=pswd)
cur = conn.cursor()

InnerNodeFile = "../Mock_DB/InnerNodes.csv"
LeafNodeFile = "../Mock_DB/LeafNodes.csv"
InnerNodes = {}
LeafNodes = {}

class bcolors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def tformat(tuple):
	return [int(x) if x.isdigit() else True if x == 'True' else False if x == 'False' else x for x in tuple]

def loadChildren(root_node_pk, is_leaf):
	if root_node_pk is None or root_node_pk == "None": return
	if not is_leaf:
		query = f"SELECT left_child, left_child_hash, right_child, right_child_hash, are_children_leaves FROM verification.tb_inner_node WHERE inner_node_id = {root_node_pk}"
		cur.execute(query)
		lc, lc_hash, rc, rc_hash, children_are_leaves = cur.fetchall()[0]
		num_leaves = 2
		if rc == "None": rc, rc_hash, num_leaves = None, None, 1
		if root_node_pk in InnerNodes: return
		InnerNodes[root_node_pk] = InnerNode(lc, lc_hash, rc, rc_hash, num_leaves, children_are_leaves)
		loadChildren(lc, children_are_leaves )
		if rc != "None":
			loadChildren(rc, children_are_leaves)
	else:
		query = f"SELECT table_name, primary_key_value, data_hash FROM verification.tb_leaf_node WHERE leaf_node_id = {root_node_pk}"
		cur.execute(query)
		table, primary_key, data_hash = cur.fetchall()[0]
		LeafNodes[root_node_pk] = LeafNode(table, primary_key, data_hash)

def verifyChildren(root_node_pk):
	if root_node_pk is None or root_node_pk == "None": return True
	root = InnerNodes[root_node_pk]
	if not root.children_are_leaves:
		lc = InnerNodes[root.left_child_pk]	
		if lc.GetHash() != root.left_child_hash: return False
		if root.right_child_pk != "None" and root.right_child_pk is not None:
			rc = InnerNodes[root.right_child_pk]
			if rc.GetHash() != root.right_child_hash: return False

		return verifyChildren(root.left_child_pk) and verifyChildren(root.right_child_pk)
	else:
		lc, rc = LeafNodes[root.left_child_pk], None
		if lc.GetHash() != root.left_child_hash: return False



		if root.right_child_pk is not None:
			rc = LeafNodes[root.right_child_pk]
			if rc.GetHash() != root.right_child_hash: return False
		return verifyTupleData(lc) and verifyTupleData(rc)

def getTablePKName(table_name):
    switcher = {
        "tb_order": "order_id",
        "tb_city": "city_id",
        "tb_product": "product_id",
        "tb_line_item": "line_item_id",
        "tb_client": "client_id"
    }
    return switcher.get(table_name, None)

def verifyTupleData(leaf_node):
	if leaf_node is None: return True

	tuple_data = None
	try:
		pk_name = leaf_node.table.replace("tb_", "") + "_id"
		query = f"SELECT * FROM {leaf_node.table} WHERE {pk_name} = {leaf_node.primary_key}"
		cur.execute(query)
		tuple_data = cur.fetchall()[0]
		conn.commit()
	except:
	    conn.close()
	    print("No matching primary key in table")
	    exit()

	return True

def fail(msg="The data could not be verified, data may have been tampered with"):
	print(f"{bcolors.FAIL} "+msg+f" {bcolors.ENDC}")
	exit()


@click.command()
@click.option('-p', '--pk_id', required=True, prompt='Order ID', help='The pk of the relation you are trying to verify')
@click.option('-r', '--relation_id', required=True, prompt='Relation ID', help='The relation you are trying to verify')
@click.option('-h', '--root_hash', required=True,  prompt='The data verification key provided when you created the order', help='This is the hash of the root of the data verification data structure')
def main(pk_id, relation_id, root_hash):

	root_node_pk = None


	try:
		# 1. find the root of the verification structure associated with this order
		query = f"SELECT rin.root_inner_node FROM verification.tb_relation_inner_node rin WHERE rin.relation_id = {relation_id} AND rin.primary_key_value = {pk_id}"
		cur.execute(query)
		tmp_root_node_pk = cur.fetchall()[0][0]
		root_node_pk = tmp_root_node_pk
		conn.commit()
	except:
		conn.close()
		print("No matching primary key in table")
		exit()

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

	print(f"{bcolors.OKGREEN} The data has been verified, the order has not been tampered with")


if __name__ == '__main__':
    main()

conn.close()