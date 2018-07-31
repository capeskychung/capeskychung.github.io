---
layout: article
title: "python old school和new school用法"
categories: python
#excerpt:
tags: [old school, new school, python]
image:
    teaser: /teaser/python.jpg
date: 2018-07-30T19:04:00+01:00
---

python2.1(包括2.1)之前的版本只存在旧式类(old school class),python2.2版本之后便出现了新式类new school class。
旧式类生成的时候是没有继承任何类，新式类则继承了object类。python2的类如果没有继承object，那么该类则是旧式类，继承了object则是新式类。python3则不存在旧式类，只有新式类。默认不继承object也是新式类。


##### 简介
{% highlight python %}
class Foo:
    '''old school 不能使用 super 关键字'''
    def __init__(self):
        pass

class Bar(object):
    '''new school 继承自 object 可以使用 super 关键字'''
    def __init__(self):
        pass

# 两者的区别在于是否继承 object，old school 的查找顺序式深度优先，new school 的查找顺序是 C3 算法
{% endhighlight %}


#### 旧式类继承
{% highlight pythob %}
class A():
    def foo1(self):
        print "A"
class B(A):
    def foo2(self):
        pass
class C(A):
    def foo1(self):
        print "C"
class D(B, C):
    pass

d = D()
d.foo1() # 调用的是 A 的 foo1 方法
# result: A
{% endhighlight %}

实际上想调用的是C的foo1方法，而旧式类的继承顺序导致最后的结果不准确。



#### 区别特点
* 新式类都从object继承，旧式类不需要
* 新式类的MRO(method resolution order 基类搜索顺序)算法采用C3算法广度优先搜索，而旧式类的MRO算法是采用深度优先搜索
* 新式类相同父类只执行一次构造函数，旧式类重复执行多次
* python 2.x中默认都是旧式类，只有显示继承了object才是新式类
* python 3.x中默认的都是新式类，旧式类被移除，不必显示继承object
* 新式类对象可以直接通过__class__属性获取自身类型type
* 新式类增加了__slots__内置属性，可以把实例属性的种类锁定到__slots__规定的范围之中。
* 新式类增加了__getattribute__方法



{% highlight python %}
{% endhighlight %}
