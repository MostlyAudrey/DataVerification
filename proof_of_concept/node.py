#/usr/bin/python3

class InnerNode:

	def __init__(self, left_child, hash_lc, right_child, hash_rc, num_leaf_nodes):
		self.left_child = left_child
		self.right_child = right_child
		self.num_leaf_nodes = num_leaf_nodes

	def __str__(self):
		return 'lc: ' + str(self.left_child) + ", rc: " + str(self.right_child) + ", #leaves: " + str(self.num_leaf_nodes)

	def GetNumLeafNodes(self):
		return self.num_leaf_nodes

class LeafNode:
	
	def __init__(self, table, primary_key, data_hash):
		self.table       = table
		self.primary_key = primary_key
		self.data_hash   = data_hash

	def __str__(self):
		return 'table: ' + str(self.table) + ", pk: " + str(self.primary_key) + " \n hash: " + str(self.data_hash)
