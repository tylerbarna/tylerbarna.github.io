---
layout: page
permalink: /repositories/
title: software
description: Research code I have written or contribute to.
nav: true
nav_order: 3
---

{% assign lang_colors = "TypeScript:#3178c6,Python:#3572a5,Jupyter Notebook:#da5b0b,Rust:#dea584,JavaScript:#f1e05a" | split: "," %}

<p class="repo-intro">Everything else is on <a href="{{ site.data.repositories.profile.url }}">GitHub</a>.</p>

<ul class="repo-list">
  {% for project in site.data.repositories.projects %}
    {% assign color = "" %}
    {% for pair in lang_colors %}
      {% assign kv = pair | split: ":" %}
      {% if kv[0] == project.language %}{% assign color = kv[1] %}{% endif %}
    {% endfor %}
    <li class="repo">
      <div class="repo-head">
        <h3><a href="https://github.com/{{ project.repo }}">{{ project.name }}</a></h3>
        <span class="repo-role">{{ project.role }}</span>
      </div>
      <p class="repo-desc">{{ project.description }}</p>
      <p class="repo-meta">
        {% if project.language %}<span class="repo-lang" style="--lang-color: {{ color }}">{{ project.language }}</span>{% endif %}
        {% if project.stars > 0 %}<span><i class="fa-regular fa-star" aria-hidden="true"></i> {{ project.stars }}<span class="sr-only"> stars</span></span>{% endif %}
        {% if project.website %}<a href="{{ project.website }}">{{ project.website | remove: "https://" }}</a>{% endif %}
        {% if project.paper %}<a href="{{ project.paper }}">paper</a>{% endif %}
        <a href="https://github.com/{{ project.repo }}">{{ project.repo }}</a>
      </p>
    </li>
  {% endfor %}
</ul>
