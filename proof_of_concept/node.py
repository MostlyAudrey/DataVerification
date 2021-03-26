#/usr/bin/python3
import hashlib

class InnerNode:

	def __init__(self, lc_pk, lc_hash, rc_pk, rc_hash, num_leaf_nodes):
		self.left_child_pk    = lc_pk
		self.left_child_hash  = lc_hash
		self.right_child_pk   = rc_pk
		self.right_child_hash = rc_hash
		self.num_leaf_nodes   = num_leaf_nodes

	def __str__(self):
		return 'lc: ' + str(self.left_child_pk) + ", rc: " + str(self.right_child_pk) + ", #leaves: " + str(self.num_leaf_nodes)

	def GetHash(self):
		return hashlib.sha256(str('{},{},{},{},{}'.format(
			str(self.left_child_pk),
			str(self.left_child_hash),
			str(self.right_child_pk),
			str(self.right_child_hash),
			str(self.num_leaf_nodes)) ).encode()).hexdigest()
		
	def GetNumLeafNodes(self):
		return self.num_leaf_nodes

class LeafNode:
	
	def __init__(self, table, primary_key, data_hash):
		self.table       = table
		self.primary_key = primary_key
		self.data_hash   = data_hash

	def __str__(self):
		return 'table: ' + str(self.table) + ", pk: " + str(self.primary_key) + " \n hash: " + str(self.data_hash)
	
	def GetHash(self):
		return hashlib.sha256(str('{},{},{}'.format(str(self.table), str(self.primary_key), str(self.data_hash))).encode()).hexdigest()
