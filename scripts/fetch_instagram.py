#!/usr/bin/env python3
"""Fill the leather gallery with the latest @willmadeleather Instagram posts.

Runs in the Pages workflow before upload, so the downloaded photos and the
rewritten page exist only in the deployed copy of site/, never in git.
Uses the official Instagram API (Instagram Login) and needs a long-lived
token in IG_ACCESS_TOKEN. Without one it leaves the committed gallery as is.

Instagram's media URLs are signed and expire, so the photos are downloaded
and served from this site instead of hotlinked.

Standard library only: no pip install on the runner.
"""

import html
import json
import os
import re
import struct
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://graph.instagram.com/me/media"
FIELDS = ("id,caption,media_type,media_url,thumbnail_url,permalink,"
          "children{media_type,media_url,thumbnail_url}")
SITE = Path(__file__).resolve().parent.parent / "site"
PAGE = SITE / "leather" / "index.html"
PHOTOS = SITE / "assets" / "instagram"
MARKERS = re.compile(r"(<!-- instagram:start -->\n)(.*?)(\s*<!-- instagram:end -->)", re.S)
EAGER = 3  # first row loads eagerly, matching the hand-written gallery


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "willluft.com gallery"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def fetch_posts(token, limit):
    url = API + "?" + urllib.parse.urlencode(
        {"fields": FIELDS, "limit": min(limit, 50), "access_token": token})
    posts = []
    while url and len(posts) < limit:
        try:
            page = json.loads(get(url))
        except urllib.error.HTTPError as err:
            # The body says why (expired token, missing permission, ...).
            sys.exit(f"Instagram API error {err.code}: {err.read().decode(errors='replace')}")
        posts += page.get("data", [])
        url = page.get("paging", {}).get("next")
    return posts[:limit]


def image_url(post):
    """The still image to show for a post: carousels use their first item."""
    item = post
    if post["media_type"] == "CAROUSEL_ALBUM":
        children = post.get("children", {}).get("data", [])
        if not children:
            return None
        item = children[0]
    if item["media_type"] == "VIDEO":
        return item.get("thumbnail_url")  # absent for some videos
    return item.get("media_url")


def jpeg_size(data):
    """(width, height) from a JPEG's SOF header, or None."""
    if data[:2] != b"\xff\xd8":
        return None
    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            return None
        marker = data[i + 1]
        length = struct.unpack(">H", data[i + 2:i + 4])[0]
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            height, width = struct.unpack(">HH", data[i + 5:i + 9])
            return width, height
        i += 2 + length
    return None


def alt_text(caption):
    """First line of the caption, without hashtags. The API exposes no alt text."""
    line = (caption or "").strip().split("\n")[0]
    line = re.sub(r"#\w+", "", line).strip(" .-·")
    if len(line) > 150:
        line = line[:147].rsplit(" ", 1)[0] + "…"
    return line or "Leather project posted on Instagram."


def gallery_item(post, filename, size, index):
    attrs = f'src="../assets/instagram/{filename}"'
    if size:
        attrs += f' width="{size[0]}" height="{size[1]}"'
    if index >= EAGER:
        attrs += ' loading="lazy"'
    attrs += f' decoding="async" alt="{html.escape(alt_text(post.get("caption")))}"'
    href = html.escape(post["permalink"])
    return f'      <li><a href="{href}"><img {attrs}></a></li>'


def main():
    token = os.environ.get("IG_ACCESS_TOKEN", "").strip()
    if not token:
        print("IG_ACCESS_TOKEN is not set: keeping the committed gallery.")
        return 0
    limit = int(os.environ.get("IG_MAX_POSTS", "24"))

    page = PAGE.read_text(encoding="utf-8")
    if not MARKERS.search(page):
        sys.exit(f"{PAGE} has no <!-- instagram:start/end --> markers")

    PHOTOS.mkdir(parents=True, exist_ok=True)
    items = []
    for post in fetch_posts(token, limit):
        url = image_url(post)
        if not url:
            continue
        data = get(url)
        filename = f'{post["id"]}.jpg'
        (PHOTOS / filename).write_bytes(data)
        items.append(gallery_item(post, filename, jpeg_size(data), len(items)))

    if not items:
        sys.exit("Instagram returned no usable posts: keeping the committed gallery.")

    # Rewrite only after every download succeeded, so a failure mid-way
    # leaves the committed gallery intact.
    page = MARKERS.sub(lambda m: m[1] + "\n".join(items) + m[3], page, count=1)
    PAGE.write_text(page, encoding="utf-8")
    print(f"Gallery now shows {len(items)} Instagram posts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
