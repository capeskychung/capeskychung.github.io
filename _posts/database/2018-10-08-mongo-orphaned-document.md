---
layout: article
title: "mongo孤儿数据"
categories: database
#excerpt:
tags: [orphaned document, mongo]
image:
    teaser: /teaser/regex.jpg
date: 2018-10-07T20:20:00+01:00
---

主要介绍什么是孤儿数据，以及孤儿数据的产生，另外还有为什么孤儿数据会被查询到，并对查询的结果产生影响。


#### 官方定义
Mongodb官方文档中，关于orphaned document的描述：
 
> In a sharded cluster, orphaned documents are those documents on a shard that also exist in chunks on other shards as a result of failed migrations or incomplete migration cleanup due to abnormal shutdown. Delete orphaned documents using cleanupOrphaned to reclaim disk space and reduce.

孤儿文档是指在sharded cluster集群下，同时存在不同shard上的document。在mongodb sharded cluster集群中，分布在不同shard的数据自己是正交，一个文档只能出现在一个shard中。docuemnt宇shard的映射关系维护在config server中。在mongo发生迁移的过程中，mongod进程shutdown，导致迁移过程失败或者部分完成。


#### 产生原因








> 参考: https://www.cnblogs.com/xybaby/p/7131776.html?utm_source=itdadao&utm_medium=referral
