<%
// Which front-matter keys turn into links under an entry, and what they are called.
// To support a new kind of link, add a line here (and its key to `fields` in the list pages).
const LINKS = [
  ['repo', 'Code'], ['paper', 'Paper'], ['demo', 'Demo'],
  ['slides', 'Slides'], ['pdf', 'PDF'], ['source', 'Source'],
];

// Set `template-params: {tablets: false}` in a list page to hide the topic tablets there.
const P = templateParams || {};
const showTablets = P.tablets !== false;
%>

::: {.list .quarto-listing-default .entries}

<% if (items.length === 0) { %>
```{=html}
<p class="listing-empty">Nothing here yet.</p>
```
<% } %>

<% for (const item of items) { %>

::: {.quarto-post <%= metadataAttrs(item) %>}

::: {.body}

```{=html}
<h3 class="no-anchor listing-title"><a href="<%- item.path %>" class="no-external"><%= item.title %></a></h3>
<% if (item.author) { %><div class="listing-author"><%= [].concat(item.author).join(', ') %></div><% } %>
```

<% if (item.description) { %>
::: {.listing-description}
<%= item.description %>
:::
<% } %>

<% const links = LINKS.filter(([key]) => item[key]); %>
<% if (links.length) { %>
```{=html}
<div class="listing-links">
<% for (const [key, label] of links) { %><a href="<%- item[key] %>" class="no-external"><%= label %></a>
<% } %></div>
```
<% } %>

<% if (showTablets && item.categories && item.categories.length) { %>
```{=html}
<div class="listing-categories">
<% for (const category of item.categories) { %><div class="listing-category" onclick="window.quartoListingCategory('<%= utils.b64encode(category) %>'); return false;"><%= category %></div>
<% } %></div>
```
<% } %>

:::

::: {.metadata}
<% if (item.date) { %>
```{=html}
<div class="listing-date"><%= item.date %></div>
```
<% } %>
:::

:::

<% } %>

:::
