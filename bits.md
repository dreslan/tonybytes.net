---
layout: page
title: Bits
permalink: /bits/
---

Small pieces of information I find useful — a term, a quote, a fleeting thought.

<div class="bit-filters">
  <button class="bit-filter active" data-filter="all">All</button>
  <button class="bit-filter" data-filter="term">Terms</button>
  <button class="bit-filter" data-filter="quote">Quotes</button>
  <button class="bit-filter" data-filter="thought">Thoughts</button>
</div>

<div class="bit-list">
{% assign sorted_bits = site.bits | sort: "date" | reverse %}
{% for bit in sorted_bits %}
  <a href="{{ bit.url | relative_url }}" class="bit-card" data-type="{{ bit.type }}">
    <div class="bit-card-header">
      <span class="bit-type-badge bit-type-{{ bit.type }}">{{ bit.type }}</span>
      <span class="bit-card-date">{{ bit.date | date: "%b %d, %Y" }}</span>
    </div>
    <span class="bit-card-title">{{ bit.title }}</span>
    {% if bit.source %}<span class="bit-card-source">{{ bit.source }}</span>{% endif %}
    <div class="bit-card-body">{{ bit.content | markdownify | strip_html | strip | truncate: 200 }}</div>
  </a>
{% endfor %}
</div>

<script>
(function() {
  var buttons = document.querySelectorAll('.bit-filter');
  var cards = document.querySelectorAll('.bit-card');

  buttons.forEach(function(btn) {
    btn.addEventListener('click', function() {
      buttons.forEach(function(b) { b.classList.remove('active'); });
      btn.classList.add('active');
      var filter = btn.getAttribute('data-filter');

      cards.forEach(function(card) {
        if (filter === 'all') {
          card.style.display = '';
        } else {
          card.style.display = card.getAttribute('data-type') === filter ? '' : 'none';
        }
      });
    });
  });
})();
</script>
