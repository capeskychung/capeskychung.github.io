---
layout: article
title: "nginx负载均衡"
categories: linux
#excerpt:
tags: [nginx, balance, linux]
image:
    teaser: /teaser/nginx.jpg
date: 2018-03-25T22:00:00+01:00
---
nginx的负载均衡功能很早之前就听说了，一直没有部署使用该功能。在项目中分析程序打印的日志，根据相似度将日志归类。由于相似度的计算对精度要求不高，只是简单的分类，这个是后话（后续的博客会更新相似度计算的方法）。分析出结果之后要以一个比较直观的方式显示给程序看，所以考虑到数据可视化，就使用百度的框架echats来显示。后续觉得echats有点多余，直接以网页的显示，表格来显示具体的日志出现的次数。

考虑到目前开发对效率要求很高，需要快速搭建一个http服务器，用其他的语言可能并没有那么快，而且目前主要使用的诗python，所以以python作为开发语言。python的web目前用的比较多的框架有flask、bottle、django等。flask和bottle是轻量级的，使用非常方便。这里快速的选择了bottle，比较适合做一些工具网站之类的。  

由于bottle框架自带wsgi是单进程单线程运行模式（bottle默认运行在内置的wsgireg服务器上，单线程的http服务器在开发的时候特别有用，但是性能比较低，随着服务器负载不断增加，会出现性能瓶颈，一次只能响应一个请求）。为了提高程序的性能，首先需要启用多线程，在程序中使用gevent（大多数服务器的线程池都限制了线程池中线程的数量，避免创建和切换线程的代价。尽管和进程的fork比起来，线程还是很便宜，但是为每一个请求创建一个线程的代价就比较高了。）gevent添加了greenlet的支持，greenlet和传统的线程类似，但其创建只需要消耗很少的资源，基于gevent的服务器可以生成成千上万的greenlet，为每个练剑分配一个greenlet无性能压力。阻塞greenlet，也不会影响到服务器接受新的请求，同时处理的连接数理论上是没有限制的）。只需要在run中加上server=gevent即可。


{% highlight python %}
import gevent
from gevent import monkey
monkey.patch_all()

run(host='0.0.0.0', port=8080, server='gevent')
{% endhighlight %}

使用了多线程模式之后，但是线程都在一个进程中运行，所以需要多开进程来提升并发能力，在启动http服务器的时候，端口应该是灵活的，通过变量来传递，最好可以从配置文件中读取。
{% highlight python %}
# app_log.py

import sys
from gevent import monkey
monkey.patch_all()

try:
	portnum = int(sys.argv[1])
except Exception:
	print 'port is error'
	sys.exit(1)

if portnum <= 1024:
	print 'port num should be greater than 1024'
	sys.exit(1)

run(host='0.0.0.0', port=portnum, server='gevent')
{% endhighlight %}

执行方式: python app_log 8811

#### shell启动
可以通过shell脚本来控制多进程http服务器的启动和关闭.
{% highlight shell %}
#!/bin/bash

port_list=(8811 8812 8813)  # 设置三个端口也即是启动三个http进程
pro_path='~/logWeb/app_log.py'
RETVAL=0
start() {
	for i inn ${port_list[*]}
	do
		p=`/usr/sbin/lsof -i :${i} | wc -l`
		if [ ${p} -ge 2 ]
		then
			action "app_log ${i} already exists" /bin/false
		else
			/usr/bin/python ${pro_path} ${i} &>> ${log_path}
		RETVAL=$?
			if [ ${RETVAL} == 0 ]
			then
				action "app_log ${i} start ..." /bin/true
			else
				action "app_log ${i} start ..." /bin/false
			fi
		fi
	done
return $RETVAL
}
stop() {
	for i in ${port_list[*]}
	do
		pidfile="/var/run/app_log_${i}.pid"
		if [ -f ${pidfile} ]
		then
			pid=`cat ${pidfile}`
			kill -9 ${pid}
			RETVAL=%?
			if [ ${RETVAL} == 0 ]
			then
				action "app_log ${i} stop ..." /bin/true
			else
				action "app_log ${i} stop ..." /bin/false
			fi
			rm -f ${pidfile}
		else
			action "app_log ${i} Has stopped !" /bin/false
		fi
	done 
}

case "$1" in
	start)
		start
		;;
	stop)
		stop
		;;
	status)
		status -p ${pidfile} 'app_log'
		RETVAL=$?
		;;
	restart)
		stop
		sleep 2
		start
		;;
	condrestart|try-restart)
		if status -p ${pidfile} 'app_log' >&dev/null; then
			stop
			start
		fi
		;;
	force-reload|reload)
		reload
		;;
	*)
		echo $"Usage: $prog {start|stop|restart|condrestart|try-restart|force-reload|reload|status|fullstatus|gracefull|help|configtest}" 
		RETVAL=2
esac
exit $RETVAL
{% endhighlight %}



#### nginx 代理负载  
用nginx代理负载，nginx的配置如下
{% highlight conf %}
upstream app_log {
	server 127.0.0.1:8811 weight=4 max_fails=2 fail_timeout=30s;
	server 127.0.0.1:8812 weight=4 max_fails=2 fail_timeout=30s;
	server 127.0.0.1:8813 weight=4 max_fails=2 fail_timeout=30s;
}

server {
	listen 8001;
	server_name localhost;
	location /
	{
		proxy_pass http://app_log;
		proxy_set_header Host $host;
		proxy_set_header X-Forwarded-For $remote_addr;
		proxy_cache_key $host$url$is_args$args;
	}
	access_log off;
}
{% endhighlight %}
启动nginx之后，访问8001端口时，nginx就会负载均衡到每个端口，实现多进程，提升并发处理能力。

