#/usr/bin/python3

import hashlib
from node import LeafNode, InnerNode

merkle_tree_inner_node_file = open("mock_db/innernode.csv")
merkle_tree_leaf_node_file = open("mock_db/leafnode.csv")