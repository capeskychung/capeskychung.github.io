---
layout: article
title: "itertools模块"
categories: python
#excerpt:
tags: [itertools, python]
image:
#	teaser: /teaser/index.jpeg
date: 2018-01-04T11:04:00+01:00
---

> itertools模块在python中处理可迭代的对象很方便。

## itertools模块方法

### itertools.dropwhile
> 参数 predicate, iterable  
> 创建一个迭代器，只要函数predicate(item)为True，就丢弃iterable中的项，如果predicate返回False，就会生成iterable中的项和所有后续项。 

> 等价实现:  
```python
def dropwhile(predicate, iterable):
	iterable = iter(iterable)
	for x in iterable:
		if not predicate(x):
			yield x
			break
	for x in iterable:
		yield x
```


> 使用示例  
```python
from itertools import dropwhile

def should_drop(x):
	print 'test:', x
	return (x < 1)


for i in drpwhile(should_drop, [-1, 0, 1, 2, 3, 4, 1, -2]):
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
```
