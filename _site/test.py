# -*- coding: utf-8 -*-


RED = True
BLACK = False


class RBNode(object):
	def __init__(self, key, color):
		self.color = color  # 默认为黑色
		self.left = None
		self.right = None
		self.parent = None
		self.key = key

	def getKey(self):
		return self.key

	def __str__(self):
		color = "R" if self.color == RED else "B"
		return "" + str(self.key) + " " + color

	def __cmp__(self, other):
		if self.__eq__(other):
			return 0
		elif self.__lt__(other):
			return -1
		elif self.__gt__(other):
			return 1

	def __eq__(self, other):
		print type(other)
		if not isinstance(other, RBNode):
			raise TypeError, "cann't cmp other type" + str(type(other))
		if other.key == self.key:
			return True
		return False

	def __lt__(self, other):
		if not isinstance(other, RBNode):
			raise TypeError, "cann't cmp other type"
		if other.key < self.key:
			return True
		return False

	def __gt__(self, other):
		if not isinstance(other, RBNode):
			raise TypeError, "cann't cmp other type"
		if other.key > self.key:
			return True
		return False


class RedBlackTree(object):

	def __init__(self):
		self.root = None

	def isRed(self, node):	
		return True if node and node.color == RED else False

	def isBlack(self, node):
		return not self.isRed(node)
	
	def setBlack(self, node):
		if node:
			node.color = BLACK

	def setRed(self, node):
		if node:
			node.color = RED

	def parentOf(self, node):
		return node.parent if node else None

	def setParent(self, node, parent):
		if node:
			node.parent = parent

	def colorOf(self, node):
		return node.color if node else BLACK

	def setColor(self, node, color):
		if node:
			node.color = color

	def preOrder(self):
		# 前序遍历
		self.realPreOrder(self.root)

	def realPreOrder(self, node):
		if node:
			print node
			self.realPreOrder(node.left)
			self.realPreOrder(node.right)

	def inOrder(self):
		# 中序遍历
		self.realInOrder(self.root)

	def realInOrder(self, node):
		if node:
			self.realInOrder(node.left)
			print node
			self.realInOrder(node.right)

	def postOrder(self):
		# 后序遍历
		self.realPostOrder(self.root)

	def realPostOrder(self, node):
		if node:
			self.realPostOrder(node.left)
			self.realPostOrder(node.right)
			print node

	def sreach(self, key):
		return self.realSearch(self.root, key)

	def realSearch(self, node, key):
		while node:
			if key > node.key:
				node = node.right
			elif key < node.key:
				node = node.left
			else:
				return node

	def searchIter(self, node, key):
		if node:
			return node
		if key > node.key:
			return self.searchIter(node.right, key)
		elif key < node.key:
			return self.searchIter(node.left, key)
		else:
			return node

	def minValue(self):
		node = self.minNode(self.root)
		if node:
			return node.key

	def minNode(self, node):
		if node is None:
			return None
		while(node.left):
			node = node.left
		return node

	def maxValue(self):
		node = self.maxNode(self.root)
		if node:
			return node.key

	def maxNode(self, node):
		if node is None:
			return None
		while node.left:
			node = node.left
		return node

	def successor(self, node):
		""" 查找节点node的后继节点， 大于节点node的最小节点. """
		if node.right:
			return self,minNode(node.right)
		# 如果没有右子节点，会出现以下两种情况
		# 1. node是其父节点的左子节点，则node的后继节点是它的父节点
		# 2. node是父节点的右子节点，则先查找node的父节点p，然后对p再次进行条件判断
		p = node.parent
		while p and node == p.right:
			node = p
			p = node.parent
		return p

	def predecessor(self, node):
		""" 查找节点node的前驱节点，即小于节点node的最大节点. """
		if node.left:
			return self.maxNode(node)
		# 如果node没有左子节点，会出现以下两种情况
		# 1. node是父节点的右子节点,则node的前驱节点是它的父节点
		# 2. node是父节点的左子节点，则先查找node的父节点p,然后对p再次进行判断
		p = node.parent
		while p and node == p.left:
			node = p
			p = node.parent
		return p



	def leftRotate(self, x):
		y = x.right
		x.right = y.left
		if y.left:
			y.left.parent = x
		y.parent = x.parent
		if x.parent is None:
			self.root = y  # 如果x的父节点为空，则将y设为父节点
		else:
			if x == x.parent.left:
				x.parent.left = y
			else:
				x.parent.right = y

		y.left = x
		x.parent = y


	def rightRotate(self, y):
		x = y.left
		y.left = x.right
		if x.right:
			x.right.parent = y

		x.parent = y.parent
		if y.parent is None:
			self.root = x
		else:
			if y == y.parent.right:
				y.parent.right = x
			else:
				y.parent.left = x

		x.right = y
		y.parent = x

	def insert(self, key):
		node = RBNode(key, RED)
		if node:
			self.realInsert(node)

	def realInsert(self, node):
		current = None
		x = self.root

		while x:
			current = x
			if node > x:
				x = x.right
			else:
				x = x.left
		node.parent = current

		if current:
			if node > current:
				current.right = node
			else:
				current.left = node
		else:
			self.root = node


		self.insertFixUp(node)

	def insertFixUp(self, node):
		parent = gparent = None
		parent = node.parent
		while parent and self.isRed(parent):
			gparent = parent.parent
			if parent == gparent.left:
				uncle = gparent.right
				if uncle is None:
					continue
				if uncle and self.isRed(uncle):
					self.setBlack(parent)
					self.setBlack(uncle)
					self.setRed(gparent)
					node = gparent
				elif node == parent.right:
					self.leftRotate(parent)
					tmp = parent
					parent = node
					node = tmp
				else:
					self.setBlack(parent)
					self.setRed(gparent)
					self.rightRotate(gparent)
			else:
				uncle = gparent.left
				if uncle and self.isRed(uncle):
					self.setBlack(parent)
					self.setBlack(uncle)
					self.setRed(gparent)
					node = gparent
				elif node == parent.left:
					self.rightRotate(node)
					tmp = parent
					parent = node
					node = tmp
				else:
					self.setBlack(parent)
					self.setRed(gparent)
					self.leftRotate(node)
			parent = node.parent
		self.root.color = BLACK

	def remove(self, key):
		node = self.search(self.root, key)
		if node:
			self.realRemove(node)

	def realRemove(self, node):
		child = parent = None
		color = False

		if node.left and node.right:
			replace = node
			# 寻找后继节点
			replace = replace.right
			while replace.left:
				replace = replace.left

			# 处理后继节点和被删除节点的父节点之间的关系
			if node.parent:
				# 要删的节点不是根节点
				if node == node.parent.left:
					node.parent.left = replace
				else:
					node.parent.right = replace
			else:
				self.root = replace

			# 处理后继节点的子节点和被删除节点的子节点之间的关系
			child = replace.right
			parent = self.parentOf(replace)
			color = replace.color

			if parent == node:
				parent = replace
			else:
				if child:
					self.setParent(child, parent)
				parent.left = child
				replace.right = node.right
				self.setParent(node.right, replace)
			replace.parent = node.parent
			replace.color = node.color

	def clear(self):
		self.destroy(self.root)
		self.root = None

	def destroy(self, node):
		if node is None:
			return
		if node.left:
			self.destroy(node.left)
		if node.right:
			self.destroy(node.right)
		node = None

	def print1(self):
		if self.root:
			self.printNode(self.root, self.root.key, 0)

	def printNode(self, node, key, direction):
		if not node:
			return
		if direction == 0:
			print "%2d(B) is root\n", node.key
		else:
			print "%2d{%s} is %2d's %6s child \n", node.key, \
				"R" if self.isRed(node) else "B", \
				key, "right" if direction == 1 else "left"
		self.printNode(node.left, node.left.key, -1)
		self.printNode(node.right, node.right.key, 1)




a = [10, 40, 30, 60, 90, 70, 20, 50, 8]

i = ilen = len(a)
tree = RedBlackTree()

print "----原始数据----"
print a

for v in a:
	tree.insert(v)

print '---前序遍历----'
tree.preOrder()




