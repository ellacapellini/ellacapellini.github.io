# ellacapellini.github.io

The willow entrance (`index.html`) and, behind it, Research, Courses, Resources and CV. Built with
[Quarto](https://quarto.org): every page is a small text file, and the lists write themselves.

## Adding things

Every kind of entry works the same way: **one file in the right folder, a few lines at the top,
then write below them.** Nothing needs registering. The lists, dates, tablets and search pick it up.

The quickest way, from a terminal in this folder:

```
python3 new.py research "Title of the project"
python3 new.py courses  "Bayesian Statistics"
python3 new.py videos   "A lecture worth watching"     # also: books, papers (these go to resources/)
```

It creates the file with today's date in place. Open it and edit. (Without the script: copy the
`_template.qmd` in the same folder, rename it, and replace `__TITLE__` and `__DATE__`.)
You can also do it entirely on github.com: *Add file → Create new file*, type the path
(for example `research/my-project.qmd`), paste the template, commit.

| Where | What goes at the top of the file |
|---|---|
| `research/` | `title`, `date`, `description` (the abstract), `categories`, and any of `repo`, `paper`, `demo`, `slides`, `pdf` |
| `courses/` | `title`, `date`, `description`, optional `repo` or `pdf`. Notes go in the body. |
| `resources/` | `title`, `date`, `description`, `categories` (`Video`, `Book` or `Paper`; the templates set it), `author`, and `source` or `paper` for the link |

The date is only used for sorting and for the label on the left. Each `repo`, `paper`, ... you add
becomes a link under the abstract, on the list and on the entry's own page. Topic tags come from
`categories`; every distinct tag gets a filter on the Research and Resources pages.

Useful to know:

- **The Greek-letter scramble** on a title (when hovering) only happens for entries with `greek: true`
  at the top: today the Homer and Linear B projects. Add it to anything else about Ancient Greek.
- **Hide something without deleting it:** add `draft: true` to its top lines.
- **Maths:** `$p(\theta \mid y)$` inline, `$$ ... $$` on its own line.
- **Images:** put the image next to the file and write `![caption](figure.png)`.
- **A course with several pages:** make a folder, e.g. `courses/pai/`, with an `index.qmd`
  (the course, which appears in the list) and one file per lecture next to it.

### The blog

There is no blog on the site for now. It is parked in the folder `_blog` (folders starting with `_`
are not published), with its list page, a template and an example post that shows maths, code and
callouts. To bring it back: rename `_blog` to `blog`, add `- text: Blog` and `href: blog/index.qmd`
to the menu in `_quarto.yml`, and a `{ label: 'Blog', href: 'blog/' }` line to `sections` in `index.html`.

### The CV

Edit `cv/index.qmd`. Each entry is a date line, then a line starting with `:` for the details.
The PDF version is `cv/Ella-Capellini-CV.pdf`; replace the file to update it (keep the name).

## Preview on your computer

Install Quarto from <https://quarto.org/docs/get-started/>, then in this folder:

```
quarto preview
```

The page reloads as you save. Drafts are visible in the preview.

## Publishing

One time:

1. On GitHub create a **public** repository named exactly `ellacapellini.github.io`.
2. Upload these files to it:
   ```
   git init -b main
   git add .
   git commit -m "First version of the site"
   git remote add origin https://github.com/ellacapellini/ellacapellini.github.io.git
   git push -u origin main
   ```
3. In the repository, go to *Settings → Pages* and set *Source* to **GitHub Actions**.

From then on, every push to `main` rebuilds and publishes the site in a couple of minutes
(progress is in the *Actions* tab). The site appears at <https://ellacapellini.github.io>.

Later, for your own domain: *Settings → Pages → Custom domain*.

## The entrance

`index.html` is your own file and Quarto copies it as it is. Everything you would want to change is in
the `CONFIG` block near the top of its script:

- `eyebrow` (the small line above your name), `lede` (the sentence under your name, shown at once) and `phrases`
  (typed out one after another underneath; the last one stays).
- `tree`: `false` (as shipped) shows only the leaves, hanging from the top edge; `true` brings back the
  trunk and limbs they hang from.
- `links`: the four icons. The CV icon and the CV tablet open the PDF in `cv/Ella-Capellini-CV.pdf`;
  **to update your CV, replace that file** (keep the name). An empty `href` hides an icon.
- `sections`: the tablets, and the branches that grow out of them. If you rename or add a section,
  change the link there and in the menu in `_quarto.yml`.

The light/dark switch (top right) remembers the visitor's choice and shares it with the other pages.
On the first visit the tree fades in on a gust of wind; later visits skip that.

The typeface is `--font` at the top of the styles in `index.html` (and the `<link>` above it).

## Changing how it looks

- **Colours and fonts:** the top of `styles/light.scss` and `styles/dark.scss` (the colours come
  from the entrance; the font is also set in `assets/head.html`). Shared layout rules: `styles/shared.scss`.
- **Menu and footer:** `_quarto.yml`. To add an email link to the footer, add
  `- icon: envelope` with `href: mailto:you@example.com` next to the GitHub one.
- **How an entry looks in the lists:** `_templates/entries.ejs.md`.
  A new kind of link (say `poster:`) is one line in the `LINKS` table at the top; also add it to
  `fields` in the list pages and to `_partials/title-block.html`.
- **The scramble on titles:** `assets/shuffle.html`.
- **Maths:** uses KaTeX. If you ever need an unusual LaTeX package, set `html-math-method: mathjax` in `_quarto.yml`.
- **Quarto version:** pinned in `.github/workflows/publish.yml`. Raise it when you update Quarto locally.
