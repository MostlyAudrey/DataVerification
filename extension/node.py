#/usr/bin/python3
import hashlib

class InnerNode:

	def __init__(self, node_id, lc_pk, lc_hash, rc_pk, rc_hash, children_are_leaves):
		self.id 				 = node_id
		self.left_child_pk       = lc_pk
		self.left_child_hash     = lc_hash
		self.right_child_pk      = rc_pk
		self.right_child_hash    = rc_hash
		self.children_are_leaves = children_are_leaves

	def __str__(self):
		return 'id: ' + str(self.id) + ', lc: ' + str(self.left_child_pk) + ", rc: " + str(self.right_child_pk) + ", #leaves: " + str(self.children_are_leaves)

	def GetHash(self, db_cursor):
		bytestring = str('{}{}{}{}{}{}'.format(
			str(self.id),
			str(self.left_child_pk),
			str(self.left_child_hash),
			str(self.right_child_pk) if self.right_child_pk else '',
			str(self.right_child_hash) if self.right_child_pk else '',
			"true" if self.children_are_leaves else "false" )).encode()

		query = f"SELECT substring(sha256::VARCHAR,3,64) FROM sha256('\\x{bytestring.hex()}');"
		db_cursor.execute(query)
		results = db_cursor.fetchone()
		return results[0]
		
	def GetNumLeafNodes(self):
		return self.num_leaf_nodes

class LeafNode:
	
	def __init__(self, node_id, table, primary_key, data_hash):
		self.id	         = node_id
		self.table       = table
		self.primary_key = primary_key
		self.data_hash   = data_hash

	def __str__(self):
		return 'table: ' + str(self.table) + ", pk: " + str(self.primary_key) + " \n hash: " + str(self.data_hash)
	
	def GetHash(self, db_cursor):
		bytestring = str('{}{}{}{}'.format(str(self.id), str(self.table), str(self.primary_key), str(self.data_hash))).encode()
		query = f"SELECT substring(sha256::VARCHAR,3,64) FROM sha256('\\x{bytestring.hex()}');"
		db_cursor.execute(query)
		results = db_cursor.fetchone()
		return results[0]
