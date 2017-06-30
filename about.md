---
title: About
permalink: /about/
layout: default
contents:
 - top-level: Personal Projects
   links:
    - title: PingARing
      url: https://www.pingaring.com/
    - title: GitHub
      url: https://github.com/PureWeen
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
    - title: Stackoverflow
      url: http://stackoverflow.com/users/953734/shane-neuville
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
      url: http://alphaidaho.org/

---
 
{% for section in page.contents%}
#### [](#header-4){{ section.top-level }}  
    {% for link in section.links %}  
*   <a class="" href="{{ link.url }}" alt="{{ link.title }}">{{ link.title }}</a>
    {% endfor %}
{% endfor %} 
