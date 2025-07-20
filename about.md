---
title: About
permalink: /about/
layout: default
contents:
 - top-level: Personal Projects
   links:
    - title: GitHub
      url: https://github.com/PureWeen
 - top-level: Where you'll find me
   links:
    - title: ReactiveX Slack
      url: https://reactivex.slack.com
 - top-level: Projects I enjoy 
   links:
    - title: ReactiveUI
      url: https://reactiveui.net/
    - title: DynamicData
      url: https://dynamic-data.org/
    - title: Xamarin.Forms
      url: https://www.xamarin.com/forms
 - top-level: Social Profiles
   links:
    - title: Stackoverflow
      url: https://stackoverflow.com/users/953734/shane-neuville
    - title: LinkedIn
      url: https://www.linkedin.com/in/ShaneNeu
    - title: Twitter
      url: https://twitter.com/PureWeen
 - top-level: Additional Life
   links:
    - title: Dancing
      url: https://www.youtube.com/watch?v=_ljgnFxOwb0
    - title: Building wearables with my wife
      url: https://www.youtube.com/watch?v=5v3M1gs21RA
    - title: Alpha Idaho
      url: https://alphaidaho.org/

---
 
{% for section in page.contents%}
#### [](#header-4){{ section.top-level }}  
    {% for link in section.links %}  
*   <a class="" href="{{ link.url }}" alt="{{ link.title }}">{{ link.title }}</a>
    {% endfor %}
{% endfor %}

---

## Open Source Activity

{% if site.data.backup_prs %}
<div class="pr-sections">
  {% if site.data.backup_prs.high_value_prs and site.data.backup_prs.high_value_prs.size > 0 %}
  ### High Value Pull Requests
  <p>Notable PRs with critical labels or significant community engagement:</p>
  <ul class="pr-list">
    {% for pr in site.data.backup_prs.high_value_prs limit:10 %}
    <li>
      <a href="{{ pr.url }}" target="_blank" rel="noopener">{{ pr.title }}</a>
      <span class="pr-meta">
        by {{ pr.user }} • {{ pr.comments }} comments
        {% if pr.labels and pr.labels.size > 0 %}
        • <span class="pr-labels">{{ pr.labels | join: ", " }}</span>
        {% endif %}
      </span>
    </li>
    {% endfor %}
  </ul>
  {% endif %}

  {% if site.data.backup_prs.least_changes_prs and site.data.backup_prs.least_changes_prs.size > 0 %}
  ### Simple Pull Requests
  <p>Focused PRs with minimal file changes:</p>
  <ul class="pr-list">
    {% for pr in site.data.backup_prs.least_changes_prs limit:10 %}
    <li>
      <a href="{{ pr.url }}" target="_blank" rel="noopener">{{ pr.title }}</a>
      <span class="pr-meta">
        by {{ pr.user }} • {{ pr.changed_files }} files changed
        {% if pr.labels and pr.labels.size > 0 %}
        • <span class="pr-labels">{{ pr.labels | join: ", " }}</span>
        {% endif %}
      </span>
    </li>
    {% endfor %}
  </ul>
  {% endif %}

  {% if site.data.backup_prs.generated_at %}
  <p class="pr-updated"><small>Last updated: {{ site.data.backup_prs.generated_at | date: "%B %d, %Y at %H:%M UTC" }}</small></p>
  {% endif %}
</div>
{% else %}
<p><em>PR data not available yet. Check back soon!</em></p>
{% endif %} 
