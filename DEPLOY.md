# Deploying willluft.com on GitHub Pages

The site is the static folder `site/`. `.github/workflows/pages.yml` publishes it on every push to `main`. There is no build step and no npm.

## Current state (checked 2026-10-30)

| Item | Value now | Change it to |
|---|---|---|
| Registrar / DNS host | Namecheap (nameservers `dns1/dns2.registrar-servers.com`) | No change. Edit the records in Namecheap. |
| `willluft.com` A | `104.198.14.52` (Netlify) | The four GitHub Pages A records (step 4) |
| `www.willluft.com` CNAME | `upbeat-williams-799f87.netlify.com` | `wdluft.github.io` |
| MX / TXT / CAA | None found | No change (add only the verification TXT) |
| Canonical host | Apex (`www` redirects to `willluft.com`) | Same. GitHub redirects `www` to the apex automatically. |
| Repo Pages source | Probably the old `gh-pages` branch (**unconfirmed**: the API needs auth) | **GitHub Actions** |

## Checklist

Do steps 1–4 before changing the A/CNAME records in step 5. GitHub warns that pointing DNS at Pages before the domain is claimed opens a takeover risk.

1. **Repo → Settings → Pages → Build and deployment → Source: GitHub Actions.** *(you)*
   - This stops publishing the stale `gh-pages` branch. Nothing live depends on it: willluft.com still points at Netlify.
2. **Merge this branch to `main` and push.**
   - Confirm the "Deploy to GitHub Pages" run in the Actions tab is green.
   - Confirm https://wdluft.github.io/willluft-2024/ shows the new site. Its pages use relative links, so they work under the repo path. Only the 404 page needs the domain root.
3. **Verify the domain on your account.** *(you, recommended)*
   - GitHub profile → Settings → Pages → Add a domain → `willluft.com`.
   - GitHub shows a TXT record. In Namecheap → Advanced DNS add host `_github-pages-challenge-wdluft` with the value GitHub shows.
   - Click Verify; it can take up to 24h.
   - **Keep this TXT record permanently.**
4. **Repo → Settings → Pages → Custom domain: `willluft.com` → Save.** *(you)*
   - The workflow deploy needs no `CNAME` file; this setting is the source of truth.
5. **Namecheap → Domain List → willluft.com → Advanced DNS.** *(you)*
   - *(Optional, a day ahead)* Lower the TTL on the `@` and `www` records to shorten the switchover.
   - **Delete** the A record `@ → 104.198.14.52`.
   - **Add** four A records for host `@`:
     - `185.199.108.153`
     - `185.199.109.153`
     - `185.199.110.153`
     - `185.199.111.153`
   - *(Optional, IPv6)* Add four AAAA records for host `@`:
     - `2606:50c0:8000::153`
     - `2606:50c0:8001::153`
     - `2606:50c0:8002::153`
     - `2606:50c0:8003::153`
   - **Edit** CNAME `www` → `wdluft.github.io.` (no repo name).
   - Leave no other A, ALIAS, CNAME, URL Redirect or parking records for `@`/`www`. Leftover records can block the HTTPS certificate.
   - **Unconfirmed:** subdomains I couldn't enumerate. Look over the full record list while you're there.
6. **Wait for DNS and the certificate.**
   - Each can take up to 24h.
   - When the Pages settings show the DNS check passing, tick **Enforce HTTPS**.
   - If the certificate is stuck for more than a day, remove the custom domain and re-add it.
   - Do the cutover at a quiet time. The current site sends HSTS (1 year), so returning visitors get a certificate error until GitHub's certificate is issued.
7. **Retire Netlify.** *(you)*
   - In the Netlify dashboard, remove `willluft.com` / `www.willluft.com` from whichever site holds them, then delete or stop that site.
   - **Unconfirmed which Netlify site that is.** The `www` CNAME points at `upbeat-williams-799f87`, but that site serves an old Gatsby build, so the domain is probably attached to a different site. The dashboard will show it.
8. **Optional cleanup.**
   - Delete the stale `gh-pages` branch: `git push origin --delete gh-pages`. It holds 2024 Parcel build output and isn't used once the source is GitHub Actions.

## Check after cutover

- `https://willluft.com/`, `/about/`, `/leather/` load; `/about` redirects to `/about/`.
- `https://www.willluft.com/` and `http://willluft.com/` redirect to `https://willluft.com/`.
- `https://willluft.com/does-not-exist` shows the custom 404 page.
- `nslookup willluft.com` returns only the 185.199.108–111.153 addresses, plus the `2606:50c0:800x::153` ones if you added the AAAA records.

## Things to decide

- **`wdluft/willluft-2026` also exists.** "Personal website, remade in 2026" is live at `wdluft.github.io/willluft-2026/` with no custom domain. Only one repo can hold `willluft.com`. This guide assumes `willluft-2024` does. If you'd rather point the domain at the 2026 repo, do step 4 there instead.
