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

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "feeds")

# All podcast shows — each has its own manifest file and RSS feeds
SHOWS = {
    "political-science": {
        "manifest": "episodes.json",
        "feeds": {
            "en": {
                "title": "Political Science Explained",
                "description": "Deep-dive educational podcast covering political science from ideologies to revolutions. Perfect for students, curious minds, and anyone who wants to understand how the world is governed. New episode daily.",
                "language": "en",
                "author": "Abishek Lakandri",
                "email": "abishek.lakandri69@gmail.com",
                "category": "Education",
                "subcategory": "How To",
                "feed_file": "political-science-en.xml",
                "ep_key": "day"
            },
            "ne": {
                "title": "राजनीतिशास्त्र — Political Science in Nepali",
                "description": "नेपाली भाषामा राजनीतिशास्त्रको विस्तृत व्याख्या। विद्यार्थीहरूको लागि सरल र शैक्षिक पोडकास्ट। हरेक दिन नयाँ एपिसोड।",
                "language": "ne",
                "author": "Abishek Lakandri",
                "email": "abishek.lakandri69@gmail.com",
                "category": "Education",
                "subcategory": "How To",
                "feed_file": "political-science-ne.xml",
                "ep_key": "day"
            }
        }
    },
    "professor-jiang": {
        "manifest": "jiang-episodes.json",
        "feeds": {
            "en": {
                "title": "Professor Jiang Deep Dive — Predictive History",
                "description": "Deep-dive analysis and fact-checking of Professor Jiang Xueqin's viral Predictive History series. Each episode expands on one of Jiang's 131 lectures with additional research, cross-references, and cinematic storytelling. Covering Secret History, Civilization, Game Theory, Geo-Strategy, and Great Books.",
                "language": "en",
                "author": "Abishek Lakandri",
                "email": "abishek.lakandri69@gmail.com",
                "category": "History",
                "subcategory": "Documentary",
                "feed_file": "professor-jiang-en.xml",
                "ep_key": "episode"
            },
            "ne": {
                "title": "प्रोफेसर जियांग — गहन विश्लेषण | Predictive History in Nepali",
                "description": "प्रोफेसर जियांग शुएचिनको भाइरल Predictive History शृङ्खलाको गहन विश्लेषण र तथ्य-जाँच। नेपाली भाषामा ऐतिहासिक र भू-राजनीतिक विषयहरूको विस्तृत अध्ययन।",
                "language": "ne",
                "author": "Abishek Lakandri",
                "email": "abishek.lakandri69@gmail.com",
                "category": "History",
                "subcategory": "Documentary",
                "feed_file": "professor-jiang-ne.xml",
                "ep_key": "episode"
            }
        }
    }
}

def gdrive_direct_url(file_id):
    """Convert a Google Drive file ID to a direct download URL."""
    return f"https://drive.google.com/uc?export=download&id={file_id}"

def generate_feed(show_id, lang, info, episodes):
    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    ep_key = info.get("ep_key", "day")

    items = []
    for ep in sorted(episodes, key=lambda e: e.get(ep_key, 0), reverse=True):
        file_id = ep.get(f"{lang}Id", "")
        if not file_id:
            continue

        url = gdrive_direct_url(file_id)
        title = ep.get("title", f"Episode {ep.get(ep_key, '?')}")
        ep_num = ep.get(ep_key, 0)
        pub_date = ep.get("date", now)
        description = ep.get("description", f"Episode {ep_num}: {title}")
        duration = ep.get(f"{lang}Duration", "")
        file_size = ep.get(f"{lang}Size", "0")

        items.append(f"""    <item>
      <title>{escape(title)}</title>
      <description>{escape(description)}</description>
      <enclosure url="{escape(url)}" length="{file_size}" type="audio/mpeg"/>
      <guid isPermaLink="false">{show_id}-{lang}-ep-{ep_num:03d}</guid>
      <pubDate>{pub_date}</pubDate>
      <itunes:episode>{ep_num}</itunes:episode>
      <itunes:title>{escape(title)}</itunes:title>
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
    <link></link>
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
    script_dir = os.path.dirname(os.path.abspath(__file__))

    for show_id, show in SHOWS.items():
        manifest_path = os.path.join(script_dir, show["manifest"])
        if not os.path.exists(manifest_path):
            print(f"Skipping {show_id}: {show['manifest']} not found")
            continue

        with open(manifest_path) as f:
            episodes = json.load(f)

        for lang, info in show["feeds"].items():
            generate_feed(show_id, lang, info, episodes)

if __name__ == "__main__":
    main()
