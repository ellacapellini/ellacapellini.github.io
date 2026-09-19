# ellacapellini.github.io

The willow entrance (`index.html`) and, behind it, Research, Notes, Blog and CV. Built with
[Quarto](https://quarto.org): every page is a small text file, and the lists write themselves.

## Adding things

Every kind of entry works the same way: **one file in the right folder, a few lines at the top,
then write below them.** Nothing needs registering. The lists, dates, tablets and search pick it up.

The quickest way, from a terminal in this folder:

```
python3 new.py research "Title of the project"
python3 new.py blog     "Title of the post"
python3 new.py courses  "Bayesian Statistics"     # also: videos, books, papers
```

It creates the file with today's date in place. Open it and edit. (Without the script: copy the
`_template.qmd` in the same folder, rename it, and replace `__TITLE__` and `__DATE__`.)
You can also do it entirely on github.com: *Add file → Create new file*, type the path
(for example `research/my-project.qmd`), paste the template, commit.

| Where | What goes at the top of the file |
|---|---|
| `research/` | `title`, `date`, `description` (the abstract), `categories`, and any of `repo`, `paper`, `demo`, `slides`, `pdf` |
| `notes/courses/` | `title`, `date`, `description`, optional `repo` or `pdf`. Notes go in the body. |
| `notes/videos/` | `title`, `date`, `author` (speaker), `description`, `source` (link to the video) |
| `notes/books/` | `title`, `date`, `author`, `description` |
| `notes/papers/` | `title`, `date`, `author` (paper authors), `description`, `paper` (link) |
| `blog/` | `title`, `date`, `description`, `categories` |

The date is only used for sorting and for the label on the left. Each `repo`, `paper`, ... you add
becomes a link under the abstract, on the list and on the entry's own page. Topic tags come from
`categories`; every distinct tag gets a filter on the Research and Notes pages.

Useful to know:

- **Hide something without deleting it:** add `draft: true` to its top lines.
- **Maths:** `$p(\theta \mid y)$` inline, `$$ ... $$` on its own line.
- **Images:** put the image next to the file and write `![caption](figure.png)`.
- **A course with several pages:** make a folder, e.g. `notes/courses/pai/`, with an `index.qmd`
  (the course, which appears in the list) and one file per lecture next to it.
- **Example of everything you can write:** `blog/example-post.qmd`. It is a draft, so it never goes live.
  Delete it when you like.

### The CV

Edit `cv/index.qmd`. Each entry is a date line, then a line starting with `:` for the details.
To add a PDF, put it in `cv/` and uncomment the download link at the top.

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

`index.html` is your own file and Quarto copies it as it is. Its tablets point to `research/`,
`notes/`, `notes/courses/`, `notes/videos/`, `notes/books/`, `notes/papers/`, `blog/` and `cv/`.
If you rename or add a section, change the link there and in the menu in `_quarto.yml`.

## Changing how it looks

- **Colours and fonts:** the top of `styles/light.scss` and `styles/dark.scss`. The values come
  from the entrance. The shared layout rules are in `styles/shared.scss`.
- **Menu and footer:** `_quarto.yml`. To add an email link to the footer, add
  `- icon: envelope` with `href: mailto:you@example.com` next to the GitHub one.
- **How an entry looks in the lists:** `_templates/entries.ejs.md`.
  A new kind of link (say `poster:`) is one line in the `LINKS` table at the top; also add it to
  `fields` in the list pages and to `_partials/title-block.html`.
- **The scramble on titles:** `assets/shuffle.html`.
- **Maths:** uses KaTeX. If you ever need an unusual LaTeX package, set `html-math-method: mathjax` in `_quarto.yml`.
- **Quarto version:** pinned in `.github/workflows/publish.yml`. Raise it when you update Quarto locally.
