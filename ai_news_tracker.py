#!/usr/bin/env python3
"""
AI News Tracker
Specialized RSS scraper for tracking AI news from TechCrunch, Crunchbase, and other sources
"""

import feedparser
import requests
import json
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
from collections import Counter


class AINewsTracker:
    """Track and filter AI news from multiple RSS feeds"""
    
    # AI-related keywords for filtering
    AI_KEYWORDS = [
        'ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning',
        'neural network', 'gpt', 'llm', 'large language model', 'generative ai',
        'chatbot', 'openai', 'anthropic', 'claude', 'chatgpt', 'gemini',
        'copilot', 'midjourney', 'stable diffusion', 'dall-e', 'deepmind',
        'computer vision', 'natural language processing', 'nlp', 'automation',
        'transformer', 'diffusion model', 'foundation model', 'agi',
        'reinforcement learning', 'supervised learning', 'unsupervised learning',
        'ai model', 'ai startup', 'ai funding', 'ai regulation', 'ai ethics',
        'autonomous', 'robotics ai', 'ai chip', 'gpu', 'nvidia ai', 'ai training'
    ]
    
    def __init__(self, user_agent: str = "AI-News-Tracker/1.0"):
        self.user_agent = user_agent
        self.all_articles = []
        self.ai_articles = []
    
    def fetch_feed(self, feed_url: str) -> Optional[feedparser.FeedParserDict]:
        """Fetch and parse an RSS feed"""
        try:
            headers = {'User-Agent': self.user_agent}
            response = requests.get(feed_url, headers=headers, timeout=15)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            return feed
        except Exception as e:
            print(f"Error fetching {feed_url}: {e}")
            return None
    
    def is_ai_related(self, text: str) -> bool:
        """Check if text contains AI-related keywords"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.AI_KEYWORDS)
    
    def calculate_ai_relevance_score(self, entry: Dict) -> int:
        """Calculate how relevant an article is to AI (0-100)"""
        score = 0
        text_to_check = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
        
        # Count keyword matches
        keyword_matches = sum(1 for keyword in self.AI_KEYWORDS if keyword in text_to_check)
        score += min(keyword_matches * 10, 60)  # Max 60 points for keywords
        
        # Bonus for AI in title
        if self.is_ai_related(entry.get('title', '')):
            score += 20
        
        # Bonus for multiple AI keyword mentions
        if keyword_matches >= 3:
            score += 20
        
        return min(score, 100)
    
    def extract_entry_data(self, entry, feed_name: str, feed_url: str) -> Dict:
        """Extract data from a feed entry"""
        # Get published date
        published_date = 'Unknown'
        if 'published_parsed' in entry and entry.published_parsed:
            published_date = datetime(*entry.published_parsed[:6]).isoformat()
        elif 'updated_parsed' in entry and entry.updated_parsed:
            published_date = datetime(*entry.updated_parsed[:6]).isoformat()
        
        # Extract companies mentioned
        summary_text = entry.get('summary', '') + ' ' + entry.get('title', '')
        companies = self.extract_companies(summary_text)
        
        entry_data = {
            'title': entry.get('title', 'N/A'),
            'link': entry.get('link', 'N/A'),
            'published_date': published_date,
            'author': entry.get('author', 'N/A'),
            'summary': entry.get('summary', entry.get('description', 'N/A')),
            'feed_name': feed_name,
            'feed_url': feed_url,
            'tags': ', '.join([tag.term for tag in entry.get('tags', [])]) if entry.get('tags') else 'N/A',
            'companies_mentioned': ', '.join(companies) if companies else 'N/A'
        }
        
        # Calculate AI relevance
        entry_data['ai_relevance_score'] = self.calculate_ai_relevance_score(entry_data)
        entry_data['is_ai_related'] = entry_data['ai_relevance_score'] >= 30
        
        return entry_data
    
    def extract_companies(self, text: str) -> List[str]:
        """Extract mentioned AI companies from text"""
        ai_companies = [
            'OpenAI', 'Anthropic', 'Google', 'DeepMind', 'Microsoft', 'Meta',
            'Amazon', 'Apple', 'Tesla', 'NVIDIA', 'Stability AI', 'Midjourney',
            'Cohere', 'Hugging Face', 'Scale AI', 'Character.AI', 'Inflection AI',
            'Adept', 'AI21 Labs', 'Jasper', 'Runway', 'Replicate', 'Together AI',
            'Databricks', 'Snowflake', 'C3.ai', 'UiPath', 'Palantir'
        ]
        
        found_companies = []
        for company in ai_companies:
            if re.search(r'\b' + re.escape(company) + r'\b', text, re.IGNORECASE):
                found_companies.append(company)
        
        return found_companies
    
    def scrape_ai_news(self, feed_urls: List[str], days_back: int = 7, 
                       min_relevance_score: int = 30) -> List[Dict]:
        """
        Scrape AI news from multiple feeds
        
        Args:
            feed_urls: List of RSS feed URLs
            days_back: Only get articles from last N days
            min_relevance_score: Minimum AI relevance score (0-100)
        """
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        print(f"🔍 Scanning {len(feed_urls)} RSS feeds for AI news...")
        print(f"📅 Looking for articles from the last {days_back} days")
        print(f"🎯 Minimum relevance score: {min_relevance_score}/100\n")
        
        for feed_url in feed_urls:
            feed = self.fetch_feed(feed_url)
            if not feed:
                continue
            
            feed_name = feed.feed.get('title', 'Unknown Feed')
            print(f"📰 Processing: {feed_name}")
            
            for entry in feed.entries:
                entry_data = self.extract_entry_data(entry, feed_name, feed_url)
                self.all_articles.append(entry_data)
                
                # Filter by date
                if entry_data['published_date'] != 'Unknown':
                    try:
                        pub_date = datetime.fromisoformat(entry_data['published_date'])
                        if pub_date < cutoff_date:
                            continue
                    except:
                        pass
                
                # Filter by AI relevance
                if entry_data['ai_relevance_score'] >= min_relevance_score:
                    self.ai_articles.append(entry_data)
        
        # Sort by relevance score (highest first)
        self.ai_articles.sort(key=lambda x: x['ai_relevance_score'], reverse=True)
        
        print(f"\n✅ Found {len(self.ai_articles)} AI-related articles (out of {len(self.all_articles)} total)")
        return self.ai_articles
    
    def display_summary(self):
        """Display summary of AI news found"""
        if not self.ai_articles:
            print("No AI articles found")
            return
        
        print("\n" + "="*80)
        print("🤖 AI NEWS SUMMARY")
        print("="*80)
        
        # Top articles
        print(f"\n📊 Top 10 AI Articles (by relevance):\n")
        for i, article in enumerate(self.ai_articles[:10], 1):
            print(f"{i}. [{article['ai_relevance_score']}/100] {article['title']}")
            print(f"   📅 {article['published_date'][:10]} | 🏢 {article['feed_name']}")
            print(f"   🔗 {article['link']}")
            if article['companies_mentioned'] != 'N/A':
                print(f"   🏭 Companies: {article['companies_mentioned']}")
            print()
        
        # Statistics
        print("="*80)
        print("📈 STATISTICS")
        print("="*80)
        
        # Company mentions
        all_companies = []
        for article in self.ai_articles:
            if article['companies_mentioned'] != 'N/A':
                all_companies.extend(article['companies_mentioned'].split(', '))
        
        if all_companies:
            company_counts = Counter(all_companies)
            print("\n🏢 Most Mentioned Companies:")
            for company, count in company_counts.most_common(10):
                print(f"   {company}: {count} mentions")
        
        # Feed statistics
        feed_counts = Counter(article['feed_name'] for article in self.ai_articles)
        print("\n📰 Articles by Source:")
        for feed, count in feed_counts.most_common():
            print(f"   {feed}: {count} articles")
        
        print("\n" + "="*80 + "\n")
    
    def export_to_json(self, filename: str = "ai_news.json"):
        """Export AI articles to JSON"""
        data = {
            'generated_at': datetime.now().isoformat(),
            'total_articles': len(self.ai_articles),
            'articles': self.ai_articles
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"📄 Exported {len(self.ai_articles)} articles to {filename}")
    
    def export_to_csv(self, filename: str = "ai_news.csv"):
        """Export AI articles to CSV"""
        if not self.ai_articles:
            print("No articles to export")
            return
        
        keys = self.ai_articles[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.ai_articles)
        
        print(f"📊 Exported {len(self.ai_articles)} articles to {filename}")
    
    def export_html_report(self, filename: str = "ai_news_report.html"):
        """Generate an HTML report of AI news"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI News Report - {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1 {{
            color: #2563eb;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 10px;
        }}
        .article {{
            background: white;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .article h2 {{
            margin-top: 0;
            color: #1f2937;
        }}
        .article a {{
            color: #2563eb;
            text-decoration: none;
        }}
        .article a:hover {{
            text-decoration: underline;
        }}
        .meta {{
            color: #6b7280;
            font-size: 0.9em;
            margin: 10px 0;
        }}
        .score {{
            display: inline-block;
            background: #10b981;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        .companies {{
            background: #eff6ff;
            padding: 8px 12px;
            border-left: 3px solid #2563eb;
            margin: 10px 0;
            font-size: 0.9em;
        }}
        .summary {{
            color: #4b5563;
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <h1>🤖 AI News Report</h1>
    <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p><strong>Total AI Articles:</strong> {len(self.ai_articles)}</p>
    <hr>
"""
        
        for article in self.ai_articles[:50]:  # Top 50 articles
            html += f"""
    <div class="article">
        <h2><a href="{article['link']}" target="_blank">{article['title']}</a></h2>
        <div class="meta">
            <span class="score">Relevance: {article['ai_relevance_score']}/100</span>
            📅 {article['published_date'][:10]} | 
            📰 {article['feed_name']}
            {' | ✍️ ' + article['author'] if article['author'] != 'N/A' else ''}
        </div>
        {f'<div class="companies">🏢 Companies: {article["companies_mentioned"]}</div>' if article['companies_mentioned'] != 'N/A' else ''}
        <div class="summary">{article['summary'][:500]}{'...' if len(article['summary']) > 500 else ''}</div>
    </div>
"""
        
        html += """
</body>
</html>
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"📱 Generated HTML report: {filename}")


def main():
    """Main function to track AI news"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Track AI news from RSS feeds")
    parser.add_argument('-f', '--feeds-file', default='ai_news_feeds.txt',
                       help='File containing RSS feed URLs')
    parser.add_argument('-d', '--days', type=int, default=7,
                       help='Number of days back to search (default: 7)')
    parser.add_argument('-s', '--score', type=int, default=30,
                       help='Minimum AI relevance score 0-100 (default: 30)')
    parser.add_argument('-o', '--output', choices=['json', 'csv', 'html', 'all'],
                       default='all', help='Output format')
    
    args = parser.parse_args()
    
    # Read feed URLs
    try:
        with open(args.feeds_file, 'r') as f:
            feed_urls = [line.strip() for line in f 
                        if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print(f"Error: Feed file '{args.feeds_file}' not found")
        return
    
    if not feed_urls:
        print("No feed URLs found in file")
        return
    
    # Create tracker and scrape
    tracker = AINewsTracker()
    tracker.scrape_ai_news(feed_urls, days_back=args.days, 
                          min_relevance_score=args.score)
    
    # Display results
    tracker.display_summary()
    
    # Export
    if args.output in ['json', 'all']:
        tracker.export_to_json()
    if args.output in ['csv', 'all']:
        tracker.export_to_csv()
    if args.output in ['html', 'all']:
        tracker.export_html_report()


if __name__ == "__main__":
    main()
