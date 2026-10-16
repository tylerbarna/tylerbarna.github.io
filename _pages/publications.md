---
layout: page
permalink: /publications/
title: publications
description: Research publications, preprints, and citation impact metrics.
nav: true
nav_order: 1
chart:
  chartjs: true
---

<!-- Bibliometric Overview Card (Google Scholar & NASA ADS / SciX Impact) -->
<div class="card p-4 mb-4" style="background-color: var(--global-card-bg-color); border: 1px solid var(--global-divider-color); border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
  <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 pb-3 mb-3 border-bottom" style="border-color: var(--global-divider-color) !important;">
    <div>
      <h4 class="mb-1" style="font-weight: 700; color: var(--global-text-color);">
        <i class="fa-solid fa-chart-column me-2" style="color: var(--global-theme-color);"></i>
        citation metrics & research impact
      </h4>
      <p class="mb-0 text-muted" style="font-size: 0.9rem;">
        Bibliometric summary synchronized live with NASA ADS / SciX and Google Scholar.
      </p>
    </div>
    <div class="d-flex flex-wrap gap-2">
      <a href="https://scholar.google.com/citations?user={{ site.data.socials.scholar_userid }}" target="_blank" rel="noopener noreferrer" class="btn btn-sm" style="background-color: rgba(66, 133, 244, 0.12); color: #4285f4; border: 1px solid rgba(66, 133, 244, 0.35); font-weight: 600; padding: 0.35rem 0.75rem; border-radius: 6px; font-size: 0.8rem;">
        <i class="fa-brands fa-google-scholar me-1"></i> Google Scholar
      </a>
      <a href="https://scixplorer.org/search/q=orcid%3A{{ site.data.socials.orcid_id }}" target="_blank" rel="noopener noreferrer" class="btn btn-sm" style="background-color: rgba(225, 112, 85, 0.12); color: #e17055; border: 1px solid rgba(225, 112, 85, 0.35); font-weight: 600; padding: 0.35rem 0.75rem; border-radius: 6px; font-size: 0.8rem;">
        <i class="fa-solid fa-satellite-dish me-1"></i> NASA SciX
      </a>
      <a href="https://orcid.org/{{ site.data.socials.orcid_id }}" target="_blank" rel="noopener noreferrer" class="btn btn-sm" style="background-color: rgba(166, 206, 57, 0.15); color: #6a961f; border: 1px solid rgba(166, 206, 57, 0.4); font-weight: 600; padding: 0.35rem 0.75rem; border-radius: 6px; font-size: 0.8rem;">
        <i class="fa-brands fa-orcid me-1"></i> ORCID
      </a>
    </div>
  </div>

  <!-- Key Metrics Row (4 stat blocks) -->
  <div class="row row-cols-2 row-cols-md-4 g-3 mb-4">
    <!-- Citations -->
    <div class="col">
      <div class="p-3 text-center h-100" style="background-color: rgba(59, 130, 246, 0.06); border: 1px solid rgba(59, 130, 246, 0.18); border-radius: 10px;">
        <div class="text-muted small text-uppercase fw-bold" style="font-size: 0.75rem; letter-spacing: 0.5px;">Citations</div>
        <div class="my-1" style="font-size: 1.85rem; font-weight: 800; color: #2563eb; line-height: 1.2;">
          {{ site.data.metrics.total_citations }}
        </div>
        <div class="small text-muted" style="font-size: 0.78rem;">
          <span style="font-weight: 600; color: var(--global-text-color);">{{ site.data.metrics.refereed_citations }}</span> peer-reviewed
        </div>
      </div>
    </div>

    <!-- h-index -->
    <div class="col">
      <div class="p-3 text-center h-100" style="background-color: rgba(16, 185, 129, 0.06); border: 1px solid rgba(16, 185, 129, 0.18); border-radius: 10px;">
        <div class="text-muted small text-uppercase fw-bold" style="font-size: 0.75rem; letter-spacing: 0.5px;">h-index</div>
        <div class="my-1" style="font-size: 1.85rem; font-weight: 800; color: #059669; line-height: 1.2;">
          {{ site.data.metrics.h_index }}
        </div>
        <div class="small text-muted" style="font-size: 0.78rem;">
          g-index: <strong>{{ site.data.metrics.g_index }}</strong> · i10: <strong>{{ site.data.metrics.i10_index }}</strong>
        </div>
      </div>
    </div>

    <!-- Publications -->
    <div class="col">
      <div class="p-3 text-center h-100" style="background-color: rgba(147, 51, 234, 0.06); border: 1px solid rgba(147, 51, 234, 0.18); border-radius: 10px;">
        <div class="text-muted small text-uppercase fw-bold" style="font-size: 0.75rem; letter-spacing: 0.5px;">Publications</div>
        <div class="my-1" style="font-size: 1.85rem; font-weight: 800; color: #7c3aed; line-height: 1.2;">
          23
        </div>
        <div class="small text-muted" style="font-size: 0.78rem;">
          12 peer-reviewed articles
        </div>
      </div>
    </div>

    <!-- Paper Reads / Downloads -->
    <div class="col">
      <div class="p-3 text-center h-100" style="background-color: rgba(245, 158, 11, 0.06); border: 1px solid rgba(245, 158, 11, 0.18); border-radius: 10px;">
        <div class="text-muted small text-uppercase fw-bold" style="font-size: 0.75rem; letter-spacing: 0.5px;">Paper Reads</div>
        <div class="my-1" style="font-size: 1.85rem; font-weight: 800; color: #d97706; line-height: 1.2;">
          4.9k+
        </div>
        <div class="small text-muted" style="font-size: 0.78rem;">
          2,050+ downloads (ADS)
        </div>
      </div>
    </div>
  </div>

  <!-- Interactive Charts Grid (Citations per Year & Publications per Year) -->
  <div class="row row-cols-1 row-cols-md-2 g-4 pt-1">
    
    <!-- Citations by Year Chart -->
    <div class="col">
      <div class="p-3 h-100" style="background-color: var(--global-bg-color); border: 1px solid var(--global-divider-color); border-radius: 10px;">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <h6 class="mb-0" style="font-weight: 700; font-size: 0.95rem; color: var(--global-text-color);">
            <i class="fa-solid fa-chart-line me-1" style="color: #2563eb;"></i> citations per year
          </h6>
          <span class="badge" style="background-color: rgba(59, 130, 246, 0.12); color: #2563eb; font-size: 0.72rem;">
            SciX Verified
          </span>
        </div>
        <div style="position: relative; height: 210px; width: 100%;">
          <canvas id="citationsChart"></canvas>
        </div>
      </div>
    </div>

    <!-- Publications by Year Chart -->
    <div class="col">
      <div class="p-3 h-100" style="background-color: var(--global-bg-color); border: 1px solid var(--global-divider-color); border-radius: 10px;">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <h6 class="mb-0" style="font-weight: 700; font-size: 0.95rem; color: var(--global-text-color);">
            <i class="fa-solid fa-layer-group me-1" style="color: #059669;"></i> publications per year
          </h6>
          <span class="badge" style="background-color: rgba(16, 185, 129, 0.12); color: #059669; font-size: 0.72rem;">
            Refereed vs Other
          </span>
        </div>
        <div style="position: relative; height: 210px; width: 100%;">
          <canvas id="publicationsChart"></canvas>
        </div>
      </div>
    </div>

  </div>
</div>

<!-- Chart.js CDN & Dynamic Rendering Script -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<script>
  document.addEventListener("DOMContentLoaded", function() {
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    const textColor = isDark ? "#c9d1d9" : "#475569";
    const gridColor = isDark ? "rgba(255, 255, 255, 0.08)" : "rgba(0, 0, 0, 0.06)";

    // Chart 1: Citations by Year
    const citeCtx = document.getElementById("citationsChart");
    if (citeCtx) {
      const citeYears = [{% for item in site.data.metrics.citations_by_year %}"{{ item[0] }}"{% unless forloop.last %},{% endunless %}{% endfor %}];
      const citeCounts = [{% for item in site.data.metrics.citations_by_year %}{{ item[1] }}{% unless forloop.last %},{% endunless %}{% endfor %}];

      new Chart(citeCtx, {
        type: 'bar',
        data: {
          labels: citeYears,
          datasets: [{
            label: 'Citations',
            data: citeCounts,
            backgroundColor: 'rgba(37, 99, 235, 0.82)',
            hoverBackgroundColor: 'rgba(29, 78, 216, 1)',
            borderColor: '#1d4ed8',
            borderWidth: 1,
            borderRadius: 5
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: function(context) {
                  return ` ${context.parsed.y} citations in ${context.label}`;
                }
              }
            }
          },
          scales: {
            x: {
              grid: { display: false },
              ticks: { color: textColor, font: { size: 11, weight: '600' } }
            },
            y: {
              grid: { color: gridColor },
              ticks: { color: textColor, font: { size: 10 }, stepSize: 20 },
              beginAtZero: true
            }
          }
        }
      });
    }

    // Chart 2: Publications by Year (Stacked: Refereed vs Non-refereed)
    const pubCtx = document.getElementById("publicationsChart");
    if (pubCtx) {
      const pubYears = [{% for item in site.data.metrics.publications_by_year %}"{{ item[0] }}"{% unless forloop.last %},{% endunless %}{% endfor %}];
      const pubRefereed = [{% for item in site.data.metrics.publications_by_year %}{{ item[1].refereed }}{% unless forloop.last %},{% endunless %}{% endfor %}];
      const pubNonRef = [{% for item in site.data.metrics.publications_by_year %}{{ item[1].non_refereed }}{% unless forloop.last %},{% endunless %}{% endfor %}];

      new Chart(pubCtx, {
        type: 'bar',
        data: {
          labels: pubYears,
          datasets: [
            {
              label: 'Peer-Reviewed',
              data: pubRefereed,
              backgroundColor: 'rgba(5, 150, 105, 0.85)',
              hoverBackgroundColor: 'rgba(4, 120, 87, 1)',
              borderColor: '#047857',
              borderWidth: 1,
              borderRadius: 4
            },
            {
              label: 'Preprints & Alerts',
              data: pubNonRef,
              backgroundColor: isDark ? 'rgba(148, 163, 184, 0.45)' : 'rgba(148, 163, 184, 0.75)',
              hoverBackgroundColor: 'rgba(100, 116, 139, 0.9)',
              borderColor: '#64748b',
              borderWidth: 1,
              borderRadius: 4
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'top',
              labels: {
                color: textColor,
                boxWidth: 12,
                font: { size: 11, weight: '600' }
              }
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  return ` ${context.dataset.label}: ${context.parsed.y}`;
                }
              }
            }
          },
          scales: {
            x: {
              stacked: true,
              grid: { display: false },
              ticks: { color: textColor, font: { size: 11, weight: '600' } }
            },
            y: {
              stacked: true,
              grid: { color: gridColor },
              ticks: { color: textColor, font: { size: 10 }, stepSize: 1 },
              beginAtZero: true
            }
          }
        }
      });
    }
  });
</script>

<!-- Search and Filter Bar -->
{% include bib_search.liquid %}

<div class="publications">
  {% bibliography %}
</div>
