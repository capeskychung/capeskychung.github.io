---
layout: archive
title: "Latest Posts"
---

<div class="tiles">
{% for post in site.categories.algorithm %}
	{% include post-grid.html %}
{% endfor %}
</div><!-- /.tiles -->
