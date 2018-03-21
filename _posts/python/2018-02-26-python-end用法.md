---
layout: article
title: "python用shell的end结束代码块"
categories: python
#excerpt:
tags: [end, python]
image:
#	teaser: /teaser/index.jpeg
date: 2018-02-26T11:04:00+01:00
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
