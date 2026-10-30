# willluft.com

Personal site for Will Luft: static HTML and CSS built on [Graffiti](https://graffiti-ui.com/) (`@drop-in/graffiti` 4.30.0, vendored in `site/css/graffiti.css`). No JavaScript. The only build step swaps the leather gallery for the latest Instagram posts at deploy time (see below).

```
site/
  index.html          /
  about/index.html    /about/
  leather/index.html  /leather/
  404.html            served by GitHub Pages for unknown paths
  css/graffiti.css    the library (don't edit; replace it to upgrade)
  css/site.css        site styles and overrides
  assets/             headshot and leather photos
scripts/
  fetch_instagram.py  fills the leather gallery from Instagram at deploy time
```

## Preview locally

```bash
python -m http.server 8000 -d site
```

Then open http://localhost:8000. (`404.html` uses root-absolute paths, so preview it at http://localhost:8000/404.html.)

## Deploy

Pushing to `main` (and a daily schedule) runs `.github/workflows/pages.yml`, which publishes `site/` to GitHub Pages. See [DEPLOY.md](DEPLOY.md) for the one-time Pages and DNS setup.

## Instagram gallery

On every deploy, `scripts/fetch_instagram.py` replaces the photos between the `<!-- instagram:start -->` and `<!-- instagram:end -->` markers in `site/leather/index.html` with the latest 24 posts from [@willmadeleather](https://www.instagram.com/willmadeleather/). It downloads the photos into the deployed copy only, so nothing gets committed. Instagram's image URLs expire, which is why the photos aren't hotlinked. The daily run picks up new posts.

The photos in the repo are the fallback. They deploy whenever no token is set or the fetch fails. A failure still deploys the site, but the run turns red so GitHub emails you.

It uses Instagram's official API, which needs a one-time setup:

1. **Make the account professional.** In the Instagram app go to Settings → Account type and tools → Switch to professional account. Creator or Business both work. It's free and doesn't need a Facebook Page.
2. **Create a Meta app** at https://developers.facebook.com/apps: Create app, pick the "Manage messaging & content on Instagram" use case, and skip the business portfolio. It can stay unpublished, since only your own account uses it.
   - Then go to Use cases → Customize → API setup with Unified login. Meta requires a business portfolio here, so connect one or create a free one. Business verification isn't needed: choose "Verify later".
   - App roles → Roles → Add People → Instagram Tester → @willmadeleather. Accept the invite in Instagram under Settings → Apps and websites → Tester invites.
3. **Generate a token.** Go to Use cases → Customize → API setup with Unified login → 2. Generate access tokens → Add account. Log in as @willmadeleather and copy the token.
   - This page issues a Facebook Login token (it starts with `EAA`). The script sends those to graph.facebook.com using the account's Instagram user ID, which is set as `IG_USER_ID` in the workflow.
   - To see when it expires, paste it into Meta's [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/). The workflow can only refresh Instagram Login tokens (starting with `IG`), so step 5 doesn't renew this one.
4. **Add it to the repo:** willluftdotcom → Settings → Secrets and variables → Actions → New secret `IG_ACCESS_TOKEN`.
5. **Let the workflow keep it fresh.** Create a fine-grained personal access token limited to `wdluft/willluftdotcom` with **Secrets: Read and write**. Save it as the repo secret `IG_SECRET_WRITER`. Each run then refreshes the Instagram token and saves the new one. Without this secret you'd have to repeat step 3 every 60 days.
6. Run **Deploy to GitHub Pages** from the Actions tab and check that the leather page shows your posts.

GitHub pauses scheduled workflows on public repos after 60 days without a commit. It emails you first. Re-enable the workflow from the Actions tab before the Instagram token runs out.

To test locally, run `IG_ACCESS_TOKEN=... python scripts/fetch_instagram.py`. It rewrites `site/leather/index.html` and adds `site/assets/instagram/`, so discard both afterwards (`git checkout site/leather/index.html`).
