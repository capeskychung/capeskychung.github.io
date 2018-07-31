---
layout: article
title: "itertools模块"
categories: python
#excerpt:
tags: [itertools, python]
image:
    teaser: /teaser/itertools.jpg
date: 2018-01-04T11:04:00+01:00
---

itertools模块在python中处理可迭代的对象很方便。

####  itertools模块方法

##### itertools.dropwhile
参数 predicate, iterable  
创建一个迭代器，只要函数predicate(item)为True，就丢弃iterable中的项，如果predicate返回False，就会生成iterable中的项和所有后续项。 

等价实现:  
{% highlight python %}
def dropwhile(predicate, iterable):
	iterable = iter(iterable)
	for x in iterable:
		if not predicate(x):
			yield x
			break
	for x in iterable:
		yield x
{% endhighlight %}


使用示例  
{% highlight python %}
from itertools import dropwhile

def should_drop(x):
	print 'test:', x
	return (x < 1)


for i in dropwhile(should_drop, [-1, 0, 1, 2, 3, 4, 1, -2]):
	print 'yield', i

Test: -1  
Test: 0  
Test: 1  
Yield: 1  
Yield: 2  
Yield: 3  
yield: 4  
yield: 1  
yield: -2  

{% endhighlight %}


##### takewhile
创建一个迭代器，生成iterable中predicate(item)为True的项，只要predicate计算为False，迭代就会立即停止。
即：从序列的头开始，直到执行函数func失败。

{% highlight python %}
def takewhile(predicate, iterable):
	for x in iterable:
		if predicate(x):
			yield x
		else:
			break
{% endhighlight %}

使用
{% highlight python %}
from itertools import *

def should_take(x):
	print 'Testing:', x
	return (x < 2)

for i in takewhile(should_take, [-1, 0, 1, 2, 3, 4, 1, -2]):
	print 'Yielding:', i


Testing: -1
Yielding: -1
Testing: 0
Yielding: 0
Testing: 1
Yielding: 1
Testing: 2
{% endhighlight %}




