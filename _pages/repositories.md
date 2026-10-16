---
layout: page
permalink: /repositories/
title: repositories
description: Open-source scientific software, alert broker pipelines, and data tools for multi-messenger astronomy.
nav: true
nav_order: 3
---

<!-- GitHub Profile Summary Card -->
<div class="card p-4 mb-4" style="background-color: var(--global-card-bg-color); border: 1px solid var(--global-divider-color); border-radius: 10px;">
  <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3">
    <div>
      <h4 class="mb-1" style="font-weight: 700; color: var(--global-text-color);">
        <i class="fa-brands fa-github me-2" style="color: var(--global-theme-color);"></i>
        Tyler Barna on GitHub
      </h4>
      <p class="mb-2 text-muted" style="font-size: 0.92rem;">
        {{ site.data.repositories.profile.summary }}
      </p>
      <div class="d-flex flex-wrap align-items-center pt-2" style="gap: 0.6rem; row-gap: 0.65rem;">
        <span class="badge" style="background-color: rgba(234, 179, 8, 0.12); color: #b45309; border: 1px solid rgba(234, 179, 8, 0.35); font-weight: 600; font-size: 0.8rem; padding: 0.38rem 0.65rem;">
          <i class="fa-solid fa-star me-1" style="color: #eab308;"></i> {{ site.data.repositories.profile.combined_stars }} Combined Stars (NASA GCN, NMMA & SkyPortal)
        </span>
        <span class="badge" style="background-color: rgba(142, 68, 173, 0.12); color: #8e44ad; border: 1px solid rgba(142, 68, 173, 0.35); font-weight: 600; font-size: 0.8rem; padding: 0.38rem 0.65rem;">
          <i class="fa-solid fa-code-pull-request me-1"></i> {{ site.data.repositories.profile.merged_prs }} Merged PRs
        </span>
        <span class="badge" style="background-color: rgba(39, 174, 96, 0.12); color: #27ae60; border: 1px solid rgba(39, 174, 96, 0.35); font-weight: 600; font-size: 0.8rem; padding: 0.38rem 0.65rem;">
          <i class="fa-solid fa-code-commit me-1"></i> {{ site.data.repositories.profile.contributions }} Annual Contributions
        </span>
        <a href="https://pypi.org/project/nmma/" target="_blank" rel="noopener noreferrer" style="display: inline-flex; align-items: center; text-decoration: none;" title="nmma on PyPI">
          <img src="https://img.shields.io/pypi/dm/nmma?style=flat&color=3498db&label=nmma%20PyPI" alt="nmma PyPI downloads" style="height: 24px; border-radius: 4px;" loading="lazy">
        </a>
      </div>
    </div>
    <div class="flex-shrink-0">
      <a href="{{ site.data.repositories.profile.url }}" target="_blank" rel="noopener noreferrer" class="btn btn-sm" style="background-color: var(--global-theme-color); color: #ffffff; font-weight: 600; padding: 0.45rem 0.95rem; border-radius: 6px;">
        <i class="fa-brands fa-github me-1"></i> View Profile
      </a>
    </div>
  </div>
</div>

<!-- Curated Scientific Software & Repositories Grid -->
<div class="row row-cols-1 row-cols-md-2 g-4 my-2">
  {% for project in site.data.repositories.projects %}
  <div class="col">
    <div class="card h-100 p-3" style="background-color: var(--global-card-bg-color); border: 1px solid var(--global-divider-color); border-radius: 10px; display: flex; flex-direction: column; justify-content: space-between; transition: transform 0.18s ease, box-shadow 0.18s ease;">
      
      <!-- Top info -->
      <div>
        <div class="d-flex justify-content-between align-items-start mb-2">
          <h5 class="card-title mb-0" style="font-weight: 700; font-size: 1.05rem;">
            <a href="{{ project.url }}" target="_blank" rel="noopener noreferrer" style="color: var(--global-text-color); text-decoration: none;">
              {{ project.name }}
            </a>
          </h5>
        </div>

        <!-- Role badge and language dot -->
        <div class="d-flex align-items-center flex-wrap gap-2 mb-2" style="font-size: 0.8rem;">
          <span class="badge" style="background-color: rgba(59, 130, 246, 0.12); color: #2563eb; border: 1px solid rgba(59, 130, 246, 0.3); font-weight: 600; border-radius: 4px; padding: 0.2rem 0.5rem;">
            {{ project.role }}
          </span>
          <span class="d-inline-flex align-items-center text-muted" style="gap: 5px;">
            <span style="width: 9px; height: 9px; border-radius: 50%; background-color: {{ project.language_color }}; display: inline-block;"></span>
            {{ project.language }}
          </span>
        </div>

        <!-- Description -->
        <p class="card-text text-muted mb-3" style="font-size: 0.88rem; line-height: 1.45;">
          {{ project.description }}
        </p>

        <!-- Topic Tags -->
        <div class="d-flex flex-wrap gap-1 mb-3">
          {% for tag in project.tags %}
          <span style="font-size: 0.72rem; padding: 2px 8px; border-radius: 9999px; background-color: rgba(100, 116, 139, 0.12); color: var(--global-text-color); border: 1px solid var(--global-divider-color); font-weight: 500;">
            #{{ tag }}
          </span>
          {% endfor %}
        </div>
      </div>

      <!-- Bottom action buttons & live stats -->
      <div class="pt-2 border-top" style="border-color: var(--global-divider-color) !important;">
        <div class="d-flex justify-content-between align-items-center flex-wrap gap-2">
          
          <!-- Live GitHub badges (only shown when count > 0) -->
          <div class="d-flex align-items-center gap-1 flex-wrap">
            {% if project.stars and project.stars > 0 %}
            <a href="{{ project.url }}/stargazers" target="_blank" rel="noopener noreferrer" title="{{ project.stars }} stars on GitHub">
              <img src="https://img.shields.io/github/stars/{{ project.repo }}?style=flat&logo=github&color=333333&labelColor=1a1a1a" alt="Stars" style="height: 20px; border-radius: 4px;" loading="lazy" onerror="this.parentElement.style.display='none';">
            </a>
            {% endif %}
            {% if project.forks and project.forks > 0 %}
            <a href="{{ project.url }}/network/members" target="_blank" rel="noopener noreferrer" title="{{ project.forks }} forks on GitHub">
              <img src="https://img.shields.io/github/forks/{{ project.repo }}?style=flat&color=444444&labelColor=1a1a1a" alt="Forks" style="height: 20px; border-radius: 4px;" loading="lazy" onerror="this.parentElement.style.display='none';">
            </a>
            {% endif %}
          </div>

          <!-- Direct links -->
          <div class="d-flex align-items-center gap-2">
            {% if project.website %}
            <a href="{{ project.website }}" target="_blank" rel="noopener noreferrer" class="btn btn-sm" style="font-size: 0.73rem; font-weight: 600; padding: 0.22rem 0.55rem; background-color: rgba(41, 128, 185, 0.12); color: #2980b9; border: 1px solid rgba(41, 128, 185, 0.35); border-radius: 6px;">
              <i class="fa-solid fa-arrow-up-right-from-square me-1"></i> Live Site
            </a>
            {% endif %}

            {% if project.paper_url %}
            <a href="{{ project.paper_url }}" target="_blank" rel="noopener noreferrer" class="btn btn-sm" style="font-size: 0.73rem; font-weight: 600; padding: 0.22rem 0.55rem; background-color: rgba(142, 68, 173, 0.12); color: #8e44ad; border: 1px solid rgba(142, 68, 173, 0.35); border-radius: 6px;">
              <i class="fa-solid fa-book-open me-1"></i> Paper
            </a>
            {% endif %}

            <a href="{{ project.url }}" target="_blank" rel="noopener noreferrer" class="btn btn-sm" style="font-size: 0.73rem; font-weight: 600; padding: 0.22rem 0.55rem; background-color: rgba(39, 174, 96, 0.12); color: #27ae60; border: 1px solid rgba(39, 174, 96, 0.35); border-radius: 6px;">
              <i class="fa-brands fa-github me-1"></i> Code
            </a>
          </div>

        </div>
      </div>

    </div>
  </div>
  {% endfor %}
</div>
