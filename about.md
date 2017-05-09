---
title: About
permalink: /about/
layout: default
contents:
 - top-level: Personal Projects
   links:
    - title: PingARing
      url: https://www.pingaring.com/
 - top-level: Where you'll find me
   links:
    - title: ReactiveX Slack
      url: https://reactivex.slack.com
 - top-level: Projects I enjoy 
   links:
    - title: ReactiveUI
      url: http://reactiveui.net/
    - title: DynamicData
      url: https://dynamic-data.org/
    - title: Xamarin.Forms
      url: https://www.xamarin.com/forms
 - top-level: Social Profiles
   links:
    - title: GitHub
      url: https://github.com/PureWeen
    - title: Stackoverflow
      url: http://stackoverflow.com/users/953734/shane-neuville
    - title: LinkedIn
      url: https://www.linkedin.com/in/shane-neuville-3907884/
    - title: Twitter
      url: https://twitter.com/PureWeen
---
 
{% for section in page.contents%}
#### [](#header-4){{ section.top-level }}  
    {% for link in section.links %}  
*   <a class="" href="{{ link.url }}" alt="{{ link.title }}">{{ link.title }}</a>
    {% endfor %}
{% endfor %} 