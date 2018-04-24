---
layout: article
title: "红黑树"
categories: algorithm
# excerpt:
tags: [R-B Tree, algorithm]
image:
    teaser: /teaser/shell.jpg
date: 2018-04-08T18:04:00+01:00
---

二叉搜索树可以快速定位一个给定关键字的数据项，可以快速插入和删除数据。二叉树存在一个问题，如果插入的数据是正序或者逆序的数据，二叉搜索树的执行会变慢，因为有序的二叉树是非平衡的，此时的二叉树类似与链表。
红黑树,基于二叉搜索树，二叉搜索树可以快速地找到一个给定的关键字的数据项，并且可以快速地插入和删除数据项。以较快的时间O(logN)来搜索一棵树，需要保证树总是平衡的，树种的每个节点在它左边的后代数目和在它右边的后代数据应该大致相等。红黑树就是一棵平衡树，对要插入的数据项，插入过程要检查是否破坏树的特征，是则程序需要纠正，改变树的结构，从而保持树的平衡。

####  特征与规则

* 所有节点都有颜色
* 在插入和删除的过程中，要遵循保持这些颜色的不同排列的规则。   

红黑树的主要规则：
1. 每个节点不是红色就是黑色；
2. 根节点总是黑色的；
3. 如果节点是红色的，则它的子节点必须是黑色的（反之不一定）；
4. 从根节点到叶节点或空子节点的每条路径，必须包含相同数目的黑色节点（相同的黑色高度）


在红黑树中插入的节点都是红色的，因为插入一个红色节点比插入一个黑色节点违背红黑原则的可能性更小。原因是：插入黑色节点总会改变黑色高度（规则4），但是插入红色节点只有一半的概率违背规则3.规则3比规则4更容易修正。

#### 修正平衡性
红黑树主要通过三种方式平衡，改变节点颜色、左旋和右旋。     


1. 变色  

改变节点颜色因为违背了规则3.假设现在节点E，然后插入节点A和S，节点A在左子节点，S在右子节点，目前是平衡的。如果此时插入一个节点，就出现了不平衡，因为红色节点的子节点必须为褐色，但是新差的节点是红色的，所以此时必须改变节点颜色。将根的两个子节点从红色变为黑色，将父节点从黑色变为红色。

2. 左旋
通常左旋操作用于将一个向右倾斜的红色链接选座为向左链接。
左旋示意图：对节点x进行左旋 
{% highlight c %}

     p                       p 
     /                       / 
    x                       y 
   / \                     / \ 
  lx  y      ----->       x  ry 
     / \                 / \ 
    ly ry               lx ly  
{% endhighlight %}


  左旋做了三件事：   
  1. 将y的左子节点赋给x的右子节点,并将x赋给y左子节点的父节点(y左子节点非空时)    
  2. 将x的父节点p(非空时)赋给y的父节点，同时更新p的子节点为y(左或右)    
  3. 将y的左子节点设为x，将x的父节点设为y   

3. 右旋

右旋示意图：对节点y进行右旋 
{% highlight c %}
         p                   p 
        /                   / 
       y                   x 
      / \                 / \ 
     x  ry   ----->      lx  y 
    / \                     / \ 
  lx  rx                   rx ry 

{% endhighlight %}
  右旋做了三件事： 
  1. 将x的右子节点赋给y的左子节点,并将y赋给x右子节点的父节点(x右子节点非空时)   
  2. 将y的父节点p(非空时)赋给x的父节点，同时更新p的子节点为x(左或右)    
  3. 将x的右子节点设为y，将y的父节点设为x   


#### 红黑树操作


红黑树节点
{% highlight python %}

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
		if not isinstance(other, RBNode):
			raise TypeError, "cann't cmp other type" + str(type(other))
		if other.key == self.key:
			return True
		return False

	def __lt__(self, other):
		if not isinstance(other, RBNode):
			raise TypeError, "cann't cmp other type"
		if other.key > self.key:
			return True
		return False

	def __gt__(self, other):
		if not isinstance(other, RBNode):
			raise TypeError, "cann't cmp other type"
		if other.key < self.key:
			return True
		return False
{% endhighlight %}


红黑树插入  
红黑树的插入与二叉搜索树的实现一致，主要的是在于最后的insertFixUp操作。插入数据后会导致树不平衡，insertFixUp要根据情况，决定何时变色，左旋，右旋。
第一次插入的时候，原树为空，只会违背规则2（根节点必须为黑色），只需要将根节点的颜色改为黑色即可。