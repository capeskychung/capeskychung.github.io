---
layout: article
title: "python descriptor用法"
categories: python
#excerpt:
tags: [descriptor, python]
image:
    teaser: /teaser/python.jpg
date: 2018-03-29T19:04:00+01:00
---

初学python的时候，以为python的代码块结束以缩进来控制即可。随着深入学习，发现了python可以支持跟shell一样以end来结束代码

{% highlight python %}
__builtins__.end = None

def test(a):
	if a > 0:
		print 'a > 0'
	else:
		print 'a <= 0'
	end
end

if __name__ == '__main__':
	test(1)

{% endhighlight %}
