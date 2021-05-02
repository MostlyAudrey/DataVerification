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
try:
	conn = psycopg2.connect(
		host=host,
		database=dbname,
		user=user,
		password=pswd
	)
except:
	fail("Error connecting to database")

db_cursor = conn.cursor()


primary_key_columns = {}
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


def loadChildren(root_node_pk, is_leaf):
	if root_node_pk is None or root_node_pk == "None": return
	if not is_leaf:
		query = f"SELECT inner_node_id, left_child, left_child_hash, right_child, right_child_hash, are_children_leaves FROM verification.tb_inner_node WHERE inner_node_id = {root_node_pk}"
		db_cursor.execute(query)
		node_id, lc, lc_hash, rc, rc_hash, children_are_leaves = db_cursor.fetchall()[0]
		if rc == "None": rc, rc_hash = None, None
		if root_node_pk in InnerNodes: return
		InnerNodes[root_node_pk] = InnerNode(node_id, lc, lc_hash, rc, rc_hash, children_are_leaves)
		loadChildren(lc, children_are_leaves )
		if rc != "None":
			loadChildren(rc, children_are_leaves)
	else:
		query = f"SELECT leaf_node_id, table_name, primary_key_value, data_hash FROM verification.tb_leaf_node WHERE leaf_node_id = {root_node_pk}"
		db_cursor.execute(query)
		leaf_node_id, table, primary_key, data_hash = db_cursor.fetchall()[0]
		LeafNodes[root_node_pk] = LeafNode(leaf_node_id, table, primary_key, data_hash)

def verifyChildren(root_node_pk):
	if root_node_pk is None or root_node_pk == "None": return True
	root = InnerNodes[root_node_pk]
	if not root.children_are_leaves:
		lc = InnerNodes[root.left_child_pk]	
		if lc.GetHash(db_cursor) != root.left_child_hash: 
			fail(f"Left node stucture was corrupted at node:\n{lc}")
			return False
		if root.right_child_pk != "None" and root.right_child_pk is not None:
			rc = InnerNodes[root.right_child_pk]
			if rc.GetHash(db_cursor) != root.right_child_hash: 
				fail(f"Right node stucture was corrupted at node:\n{rc}")
				return False

		return verifyChildren(root.left_child_pk) and verifyChildren(root.right_child_pk)
	else:
		lc, rc = LeafNodes[root.left_child_pk], None
		if lc.GetHash(db_cursor) != root.left_child_hash: 
			fail(f"found leaf_node was altered:\n{lc} ")
			return False

		if root.right_child_pk is not None:
			rc = LeafNodes[root.right_child_pk]
			if rc.GetHash(db_cursor) != root.right_child_hash:
				fail(f"found leaf_node was altered:\n{rc} ")
				return False
		return verifyTupleData(lc) and verifyTupleData(rc)

def getTablePKName(relation_id):
    global primary_key_columns
    db_cursor.execute(f"SELECT sub_table AS table, primary_key FROM verification.tb_relation_sub_table WHERE relation = {relation_id};")
    results = db_cursor.fetchall()
    for row in results:
    	primary_key_columns[row[0]] = row[1]

def verifyTupleData(leaf_node):
	if leaf_node is None: return True

	tuple_data = None
	pk_name = primary_key_columns[leaf_node.table]
	query = f"SELECT * FROM {leaf_node.table} WHERE {pk_name} = {leaf_node.primary_key}"
	db_cursor.execute(query)
	tuple_data = db_cursor.fetchall()[0]
	return True

def fail(msg="The data could not be verified, data may have been tampered with"):
	print(f"{bcolors.FAIL} "+msg+f" {bcolors.ENDC}")
	conn.close()
	exit()


@click.command()
@click.option('-r', '--relation_id', required=True, prompt='Relation ID', help='The relation you are trying to verify')
@click.option('-p', '--pk_id', required=True, prompt='Order ID', help='The pk of the relation you are trying to verify')
@click.option('-h', '--root_hash', required=True,  prompt='The data verification key provided when you created the order', help='This is the hash of the root of the data verification data structure')
def main(pk_id, relation_id, root_hash):
	getTablePKName(relation_id)

	root_node_pk = None

	# 1. find the root of the verification structure associated with this order
	try:
		query = f"SELECT rin.root_inner_node FROM verification.tb_relation_inner_node rin WHERE rin.relation_id = {relation_id} AND rin.primary_key_value = {pk_id} ORDER BY rin.relation_map_id DESC"
		db_cursor.execute(query)
		root_node_pk = db_cursor.fetchall()[0][0]
	except:
		fail("Unable to find order, make sure you have stamped this order")
	
	if root_node_pk is None:
		fail("No matching verification data structure found")

	# 2. Recursively load all Inner and Leaf Nodes into memory
	loadChildren(root_node_pk, False)

	# 3. Verify the root node matches the provided hash
	if root_hash != InnerNodes[root_node_pk].GetHash(db_cursor):
		fail("Root hashes do not match, data may have been tampered with")
		
	# 4. Recursively verify the contents of all of the nodes
	if not verifyChildren(root_node_pk):
		fail()

	print(f"{bcolors.OKGREEN} The data has been verified, the order has not been tampered with")
	conn.close()


if __name__ == '__main__':
    main()