---
layout: page
title: Books
permalink: /books/
---

<div class="book-filters">
  <button class="book-filter active" data-filter="all">All</button>
  <button class="book-filter" data-filter="now-reading">Now Reading</button>
  <button class="book-filter" data-filter="read">Read</button>
  <button class="book-filter" data-filter="reading-list">Reading List</button>
  <button class="book-filter" data-filter="reviewed">Reviewed</button>
</div>

{% assign now_reading = site.reviews | where: "status", "now-reading" %}
{% if now_reading.size > 0 %}
<h3 class="archive-year now-reading-heading">Now Reading</h3>
<div class="book-shelf">
  {% for book in now_reading limit:5 %}
  <a href="{{ book.url | relative_url }}" class="book-card" data-status="now-reading">
    {% if book.cover %}<img src="{{ book.cover | relative_url }}" alt="" class="book-card-cover">{% else %}<div class="book-card-cover book-card-no-cover">{{ book.title | truncate: 30 }}</div>{% endif %}
    <div class="book-card-info">
      <span class="book-card-title">{{ book.title }}</span>
      <span class="book-card-author">{{ book.author }}</span>
      {% if book.description %}<p class="book-card-desc">{{ book.description | truncate: 120 }}</p>{% endif %}
    </div>
  </a>
  {% endfor %}
</div>
{% endif %}

{% assign read_books = site.reviews | where: "status", "read" %}
{% assign reviews_by_year = read_books | group_by_exp: "review", "review.date_read | date: '%Y'" | sort: "name" | reverse %}
{% for year in reviews_by_year %}
<h3 class="archive-year">{{ year.name }}</h3>
<div class="book-shelf">
  {% for review in year.items %}
  {% assign body = review.content | strip %}
  <a href="{{ review.url | relative_url }}" class="book-card" data-status="read" {% if body != "" %}data-reviewed{% endif %}>
    {% if review.cover %}<img src="{{ review.cover | relative_url }}" alt="" class="book-card-cover">{% else %}<div class="book-card-cover book-card-no-cover">{{ review.title | truncate: 30 }}</div>{% endif %}
    <div class="book-card-info">
      <span class="book-card-title">{{ review.title }}</span>
      <span class="book-card-author">{{ review.author }} {% if review.rating > 0 %}· {% assign full = review.rating | round %}{% for i in (1..5) %}{% if i <= full %}★{% else %}☆{% endif %}{% endfor %}{% endif %}</span>
      {% if body != "" %}<span class="review-badge">reviewed</span>{% endif %}
      {% if review.description %}<p class="book-card-desc">{{ review.description | truncate: 120 }}</p>{% endif %}
    </div>
  </a>
  {% endfor %}
</div>
{% endfor %}

<h3 class="archive-year reading-list-heading">Reading List</h3>
<div class="book-shelf">
{% assign want_to_read = site.reviews | where: "status", "reading-list" %}
{% for book in want_to_read %}
  <a href="{{ book.url | relative_url }}" class="book-card" data-status="reading-list">
    {% if book.cover %}<img src="{{ book.cover | relative_url }}" alt="" class="book-card-cover">{% else %}<div class="book-card-cover book-card-no-cover">{{ book.title | truncate: 30 }}</div>{% endif %}
    <div class="book-card-info">
      <span class="book-card-title">{{ book.title }}</span>
      <span class="book-card-author">{{ book.author }}</span>
      {% if book.description %}<p class="book-card-desc">{{ book.description | truncate: 120 }}</p>{% endif %}
    </div>
  </a>
{% endfor %}
</div>

<script>
(function() {
  var buttons = document.querySelectorAll('.book-filter');
  var cards = document.querySelectorAll('.book-card');
  var shelves = document.querySelectorAll('.book-shelf');

  buttons.forEach(function(btn) {
    btn.addEventListener('click', function() {
      buttons.forEach(function(b) { b.classList.remove('active'); });
      btn.classList.add('active');
      var filter = btn.getAttribute('data-filter');

      cards.forEach(function(card) {
        if (filter === 'all') {
          card.style.display = '';
        } else if (filter === 'reviewed') {
          card.style.display = card.hasAttribute('data-reviewed') ? '' : 'none';
        } else if (filter === 'now-reading') {
          card.style.display = card.getAttribute('data-status') === 'now-reading' ? '' : 'none';
        } else {
          card.style.display = card.getAttribute('data-status') === filter ? '' : 'none';
        }
      });

      shelves.forEach(function(shelf) {
        var visible = shelf.querySelectorAll('.book-card:not([style*="display: none"])');
        shelf.style.display = visible.length ? '' : 'none';
        var heading = shelf.previousElementSibling;
        if (heading && heading.classList.contains('archive-year')) {
          heading.style.display = visible.length ? '' : 'none';
        }
      });
    });
  });
})();
</script>
