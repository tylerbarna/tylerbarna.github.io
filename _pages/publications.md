---
layout: page
permalink: /publications/
title: publications
description: Refereed papers, preprints, and conference contributions, kept in sync with NASA ADS.
nav: true
nav_order: 1
chart:
  chartjs: true
---

{% assign m = site.data.metrics %}
{% capture ads_url %}https://ui.adsabs.harvard.edu/search/q=orcid%3A{{ site.data.socials.orcid_id }}&sort=date%20desc{% endcapture %}

<section class="pub-summary" aria-label="Publication summary">
  <dl class="pub-stats">
    <div><dt>refereed papers</dt><dd>{{ m.papers_refereed }}</dd></div>
    <div><dt>as first author</dt><dd>{{ m.papers_refereed_first_author }}</dd></div>
    <div><dt>citations</dt><dd>{{ m.total_citations }}</dd></div>
    <div><dt>h-index</dt><dd>{{ m.h_index }}</dd></div>
  </dl>

{% if m.citations_by_year %}

  <figure class="pub-chart">
    <div class="pub-chart-canvas">
      <canvas id="citations-chart" role="img"
        aria-label="Citations per year: {% for y in m.citations_by_year %}{{ y[0] }}: {{ y[1] }}{% unless forloop.last %}, {% endunless %}{% endfor %}"
        data-years="{% for y in m.citations_by_year %}{{ y[0] }}{% unless forloop.last %},{% endunless %}{% endfor %}"
        data-counts="{% for y in m.citations_by_year %}{{ y[1] }}{% unless forloop.last %},{% endunless %}{% endfor %}"></canvas>
    </div>
    <figcaption>citations per year</figcaption>
  </figure>
  {% endif %}

  <p class="pub-source">
    Citation counts from <a href="{{ ads_url }}">NASA ADS</a>{% if m.updated %}, updated {{ m.updated | date: "%-d %B %Y" }}{% endif %}.
    Also on <a href="https://scholar.google.com/citations?user={{ site.data.socials.scholar_userid }}">Google Scholar</a>
    and <a href="https://orcid.org/{{ site.data.socials.orcid_id }}">ORCID</a>.
  </p>
</section>

{% include bib_search.liquid %}

<div class="publications">
  <section class="pub-section" id="refereed">
    <h2 class="pub-section-title">refereed articles</h2>
    {% bibliography --query @*[pubtype=refereed] %}
  </section>

  <section class="pub-section" id="preprints">
    <h2 class="pub-section-title">preprints</h2>
    {% bibliography --query @*[pubtype=preprint] %}
  </section>

  <section class="pub-section" id="other">
    <h2 class="pub-section-title">conference abstracts, reports, software &amp; data</h2>
    {% bibliography --query @*[pubtype!=refereed,pubtype!=preprint] %}
  </section>
</div>

<script>
  document.addEventListener("DOMContentLoaded", () => {
    const canvas = document.getElementById("citations-chart");
    if (!canvas || typeof Chart === "undefined") return;
    const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    const chart = new Chart(canvas, {
      type: "bar",
      data: {
        labels: canvas.dataset.years.split(","),
        datasets: [{ data: canvas.dataset.counts.split(",").map(Number), borderRadius: 2, maxBarThickness: 28 }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        plugins: { legend: { display: false }, tooltip: { displayColors: false, callbacks: { label: (c) => `${c.parsed.y} citations` } } },
        scales: {
          x: { grid: { display: false }, border: { display: false } },
          y: { beginAtZero: true, border: { display: false }, ticks: { maxTicksLimit: 4 } },
        },
      },
    });
    const applyTheme = () => {
      const text = css("--global-text-color-light");
      chart.data.datasets[0].backgroundColor = css("--global-theme-color");
      chart.options.scales.x.ticks.color = text;
      chart.options.scales.y.ticks.color = text;
      chart.options.scales.y.grid.color = css("--global-divider-color");
      chart.update();
    };
    applyTheme();
    // Re-colour when the reader toggles light / dark mode.
    new MutationObserver(applyTheme).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  });
</script>
