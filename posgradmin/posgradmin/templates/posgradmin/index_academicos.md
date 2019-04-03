---
title: Tutores acreditados
layout: page
permalink: /tutores/index
---

{% for a in academicos %}| [{{ a }}]({{ a.user.username }}/) | {{ a.show_acreditacion }} |
{% endfor %}
