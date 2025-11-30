# 🤖 AI News Tracker - Quick Start Guide

Track the latest AI news from TechCrunch, VentureBeat, and other top tech sources!

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install feedparser requests
```

### 2. Run the Tracker
```bash
# Track AI news from the last 7 days
python ai_news_tracker.py

# Track from the last 3 days
python ai_news_tracker.py -d 3

# Only show highly relevant AI articles (score >= 50)
python ai_news_tracker.py -s 50

# Export to specific format
python ai_news_tracker.py -o html
```

## 📋 What You Get

### 1. **Console Summary**
- Top 10 most relevant AI articles
- Company mentions (OpenAI, Anthropic, Google, etc.)
- Statistics by source

### 2. **JSON Export** (`ai_news.json`)
```json
{
  "generated_at": "2024-11-30T12:00:00",
  "total_articles": 45,
  "articles": [
    {
      "title": "OpenAI Announces GPT-5",
      "link": "https://...",
      "published_date": "2024-11-30",
      "ai_relevance_score": 95,
      "companies_mentioned": "OpenAI, Microsoft",
      "summary": "..."
    }
  ]
}
```

### 3. **CSV Export** (`ai_news.csv`)
Spreadsheet format - open in Excel/Google Sheets

### 4. **HTML Report** (`ai_news_report.html`)
Beautiful formatted report you can open in your browser

## 🎯 Features

### Smart AI Detection
- **Relevance scoring (0-100)**: Articles scored based on AI keyword density
- **Keyword matching**: Detects AI, ML, LLMs, GPT, ChatGPT, etc.
- **Company tracking**: Automatically extracts mentions of AI companies

### Tracked Sources
- **TechCrunch** - AI category + main feed filtered
- **VentureBeat** - AI news
- **MIT Technology Review** - AI articles  
- **The Verge** - AI coverage
- **Ars Technica** - Tech Lab
- **AI News** - Dedicated AI publications
- **Hacker News** - Filtered for AI
- **Company blogs**: OpenAI, DeepMind, Anthropic

### AI Companies Tracked
OpenAI, Anthropic, Google, DeepMind, Microsoft, Meta, Amazon, Apple, Tesla, NVIDIA, Stability AI, Midjourney, Cohere, Hugging Face, Scale AI, Character.AI, and 15+ more

## 📊 Command Line Options

```bash
-f, --feeds-file    Feed URLs file (default: ai_news_feeds.txt)
-d, --days         Days back to search (default: 7)
-s, --score        Min relevance score 0-100 (default: 30)
-o, --output       Output format: json, csv, html, all (default: all)
```

## 🔧 Customization

### Add Your Own Feeds
Edit `ai_news_feeds.txt` and add any RSS feed URL:
```
https://your-favorite-blog.com/feed/
```

### Adjust Relevance Threshold
- **Score 0-30**: Mentions AI tangentially
- **Score 30-60**: AI is discussed but not main topic
- **Score 60-100**: Highly AI-focused content

## 💡 Use Cases

### Daily AI News Digest
```bash
# Run every morning
python ai_news_tracker.py -d 1 -o html
```
Opens `ai_news_report.html` for your daily AI news

### Weekly Research
```bash
# Comprehensive weekly scan
python ai_news_tracker.py -d 7 -s 40 -o all
```

### Track Specific Companies
Edit the code to add your companies of interest to the `ai_companies` list

### Integration with Other Tools
```python
from ai_news_tracker import AINewsTracker

tracker = AINewsTracker()
feed_urls = ['https://techcrunch.com/category/artificial-intelligence/feed/']
articles = tracker.scrape_ai_news(feed_urls, days_back=3)

# Process articles
for article in articles:
    if article['ai_relevance_score'] >= 80:
        print(f"High priority: {article['title']}")
```

## 🌟 Example Output

```
🔍 Scanning 17 RSS feeds for AI news...
📅 Looking for articles from the last 7 days
🎯 Minimum relevance score: 30/100

📰 Processing: TechCrunch
📰 Processing: VentureBeat AI
📰 Processing: MIT Technology Review
...

✅ Found 73 AI-related articles (out of 421 total)

================================================================================
🤖 AI NEWS SUMMARY
================================================================================

📊 Top 10 AI Articles (by relevance):

1. [95/100] OpenAI announces GPT-5 with breakthrough capabilities
   📅 2024-11-29 | 🏢 TechCrunch
   🔗 https://techcrunch.com/...
   🏭 Companies: OpenAI, Microsoft

2. [92/100] Anthropic raises $2B Series D at $18B valuation
   📅 2024-11-28 | 🏢 VentureBeat AI
   🔗 https://venturebeat.com/...
   🏭 Companies: Anthropic, Google

...

================================================================================
📈 STATISTICS
================================================================================

🏢 Most Mentioned Companies:
   OpenAI: 23 mentions
   Google: 18 mentions
   Anthropic: 12 mentions
   Microsoft: 11 mentions
   NVIDIA: 9 mentions

📰 Articles by Source:
   TechCrunch: 28 articles
   VentureBeat AI: 19 articles
   MIT Technology Review: 12 articles
   The Verge: 8 articles
   ...

================================================================================
```

## 🎨 HTML Report Preview

The HTML report includes:
- ✅ Clean, readable design
- ✅ Clickable article links
- ✅ Color-coded relevance scores
- ✅ Company highlights
- ✅ Mobile-friendly layout

## 📝 Notes

- **Network required**: Needs internet to fetch RSS feeds
- **Rate limiting**: Some feeds may limit requests
- **Feed availability**: Some feeds may change or become unavailable
- **Relevance scoring**: Algorithm-based, may need tuning for your needs

## 🆘 Troubleshooting

**No articles found?**
- Lower the relevance score: `-s 20`
- Increase days back: `-d 14`
- Check if feeds are accessible

**Too many irrelevant articles?**
- Raise the relevance score: `-s 50`
- Edit AI keywords in the code

**Feed errors?**
- Some feeds may be temporarily down
- Check the feed URL in your browser

## 🔄 Automation

### Daily cron job (Linux/Mac)
```bash
# Add to crontab
0 9 * * * cd /path/to/tracker && python ai_news_tracker.py -d 1 -o html
```

### Windows Task Scheduler
Create a task to run `ai_news_tracker.py` daily

---

**Pro Tip**: Start with default settings, then adjust `-d` and `-s` parameters based on how many articles you want!
