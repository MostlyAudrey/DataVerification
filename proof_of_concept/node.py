#/usr/bin/python3

class InnerNode:

	def __init__(self, left_child, hash_lc, right_child, hash_rc):
		self.left_child = left_child
		self.right_child = right_child

	def __str__(self):
		return 'lc: ' + str(self.left_child) + ", rc: " + str(self.right_child)

class LeafNode:
	
	def __init__(self, table, primary_key, data_hash):
		self.table       = table
		self.primary_key = primary_key
		self.data_hash   = data_hash

	def __str__(self):
		return 'table: ' + str(self.table) + ", pk: " + str(self.primary_key) + " \n hash: " + str(self.data_hash)
