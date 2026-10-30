# willluft.com

Personal site for Will Luft: static HTML and CSS built on [Graffiti](https://graffiti-ui.com/) (`@drop-in/graffiti` 4.30.0, vendored in `site/css/graffiti.css`). No JavaScript and no build step.

```
site/
  index.html          /
  about/index.html    /about/
  leather/index.html  /leather/
  404.html            served by GitHub Pages for unknown paths
  css/graffiti.css    the library (don't edit; replace it to upgrade)
  css/site.css        site styles and overrides
  assets/             headshot and leather photos
```

## Preview locally

```bash
python -m http.server 8000 -d site
```

Then open http://localhost:8000. (`404.html` uses root-absolute paths, so preview it at http://localhost:8000/404.html.)

## Deploy

Pushing to `main` runs `.github/workflows/pages.yml`, which publishes `site/` to GitHub Pages. See [DEPLOY.md](DEPLOY.md) for the one-time Pages and DNS setup.
