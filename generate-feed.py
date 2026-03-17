#!/usr/bin/env python3
"""
Generate podcast RSS feeds from a JSON episode manifest.
Produces two feeds: English and Nepali.
Deploy to GitHub Pages for stable, permanent RSS URLs.
"""
import json
import os
import sys
from datetime import datetime, timezone
from xml.sax.saxutils import escape

MANIFEST_FILE = os.path.join(os.path.dirname(__file__), "episodes.json")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "feeds")

PODCAST_INFO = {
    "en": {
        "title": "Political Science Explained",
        "description": "Deep-dive educational podcast covering political science from ideologies to revolutions. Perfect for students, curious minds, and anyone who wants to understand how the world is governed. New episode daily.",
        "language": "en",
        "author": "Abishek Lakandri",
        "email": "abishek.lakandri69@gmail.com",
        "category": "Education",
        "subcategory": "How To",
        "image": "",
        "website": "",
        "feed_file": "political-science-en.xml"
    },
    "ne": {
        "title": "राजनीतिशास्त्र — Political Science in Nepali",
        "description": "नेपाली भाषामा राजनीतिशास्त्रको विस्तृत व्याख्या। विद्यार्थीहरूको लागि सरल र शैक्षिक पोडकास्ट। हरेक दिन नयाँ एपिसोड।",
        "language": "ne",
        "author": "Abishek Lakandri",
        "email": "abishek.lakandri69@gmail.com",
        "category": "Education",
        "subcategory": "How To",
        "image": "",
        "website": "",
        "feed_file": "political-science-ne.xml"
    }
}

def gdrive_direct_url(file_id):
    """Convert a Google Drive file ID to a direct download URL."""
    return f"https://drive.google.com/uc?export=download&id={file_id}"

def generate_feed(lang, episodes):
    info = PODCAST_INFO[lang]
    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")

    items = []
    for ep in sorted(episodes, key=lambda e: e["day"], reverse=True):
        file_id = ep.get(f"{lang}Id", "")
        if not file_id:
            continue

        url = gdrive_direct_url(file_id)
        title = ep.get("title", f"Episode {ep['day']}")
        day = ep["day"]
        pub_date = ep.get("date", now)
        description = ep.get("description", f"Day {day} of Political Science: {title}")
        duration = ep.get(f"{lang}Duration", "")
        file_size = ep.get(f"{lang}Size", "0")

        items.append(f"""    <item>
      <title>Day {day}: {escape(title)}</title>
      <description>{escape(description)}</description>
      <enclosure url="{escape(url)}" length="{file_size}" type="audio/mpeg"/>
      <guid isPermaLink="false">political-science-{lang}-day-{day:03d}</guid>
      <pubDate>{pub_date}</pubDate>
      <itunes:episode>{day}</itunes:episode>
      <itunes:title>Day {day}: {escape(title)}</itunes:title>
      <itunes:summary>{escape(description)}</itunes:summary>
      <itunes:duration>{duration}</itunes:duration>
      <itunes:explicit>false</itunes:explicit>
    </item>""")

    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
  xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
  xmlns:atom="http://www.w3.org/2005/Atom"
  xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>{escape(info["title"])}</title>
    <description>{escape(info["description"])}</description>
    <language>{info["language"]}</language>
    <link>{info.get("website", "")}</link>
    <lastBuildDate>{now}</lastBuildDate>
    <itunes:author>{escape(info["author"])}</itunes:author>
    <itunes:owner>
      <itunes:name>{escape(info["author"])}</itunes:name>
      <itunes:email>{info["email"]}</itunes:email>
    </itunes:owner>
    <itunes:category text="{info["category"]}">
      <itunes:category text="{info["subcategory"]}"/>
    </itunes:category>
    <itunes:explicit>false</itunes:explicit>
    <itunes:type>episodic</itunes:type>
{chr(10).join(items)}
  </channel>
</rss>"""

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, info["feed_file"])
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(feed)
    print(f"Generated {out_path} ({len(items)} episodes)")

def main():
    if not os.path.exists(MANIFEST_FILE):
        print(f"Error: {MANIFEST_FILE} not found", file=sys.stderr)
        sys.exit(1)

    with open(MANIFEST_FILE) as f:
        episodes = json.load(f)

    generate_feed("en", episodes)
    generate_feed("ne", episodes)

if __name__ == "__main__":
    main()
