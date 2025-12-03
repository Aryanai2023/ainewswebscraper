#!/usr/bin/env python3
"""
Enhanced AI News Tracker with Source Credibility Weighting
Prioritizes accredited news sources and adjusts relevance scores accordingly
"""

import feedparser
import requests
import json
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
from collections import Counter


class EnhancedAINewsTracker:
    """Enhanced AI News tracker with source credibility scoring"""
    
    # SOURCE CREDIBILITY TIERS
    # Higher tier = more credible/authoritative source
    SOURCE_TIERS = {
        # TIER 1: Premier Academic & Research (Multiplier: 1.5x)
        'MIT Technology Review': {'tier': 1, 'multiplier': 1.5, 'type': 'Academic'},
        'Nature': {'tier': 1, 'multiplier': 1.5, 'type': 'Academic'},
        'Science Magazine': {'tier': 1, 'multiplier': 1.5, 'type': 'Academic'},
        'Stanford HAI': {'tier': 1, 'multiplier': 1.5, 'type': 'Academic'},
        'Berkeley AI Research': {'tier': 1, 'multiplier': 1.5, 'type': 'Academic'},
        
        # TIER 2: Company Research Blogs (Multiplier: 1.4x)
        'OpenAI Blog': {'tier': 2, 'multiplier': 1.4, 'type': 'Primary Source'},
        'DeepMind Blog': {'tier': 2, 'multiplier': 1.4, 'type': 'Primary Source'},
        'Anthropic News': {'tier': 2, 'multiplier': 1.4, 'type': 'Primary Source'},
        'Google AI Blog': {'tier': 2, 'multiplier': 1.4, 'type': 'Primary Source'},
        'Meta AI': {'tier': 2, 'multiplier': 1.4, 'type': 'Primary Source'},
        'Microsoft Research': {'tier': 2, 'multiplier': 1.4, 'type': 'Primary Source'},
        
        # TIER 3: Established Tech Journalism (Multiplier: 1.3x)
        'The Verge': {'tier': 3, 'multiplier': 1.3, 'type': 'Tech Journalism'},
        'Ars Technica': {'tier': 3, 'multiplier': 1.3, 'type': 'Tech Journalism'},
        'Wired': {'tier': 3, 'multiplier': 1.3, 'type': 'Tech Journalism'},
        'IEEE Spectrum': {'tier': 3, 'multiplier': 1.3, 'type': 'Tech Journalism'},
        
        # TIER 4: Major Business/Tech News (Multiplier: 1.2x)
        'TechCrunch': {'tier': 4, 'multiplier': 1.2, 'type': 'Business News'},
        'VentureBeat': {'tier': 4, 'multiplier': 1.2, 'type': 'Business News'},
        'Reuters Technology': {'tier': 4, 'multiplier': 1.2, 'type': 'Business News'},
        'Bloomberg Technology': {'tier': 4, 'multiplier': 1.2, 'type': 'Business News'},
        'Wall Street Journal Tech': {'tier': 4, 'multiplier': 1.2, 'type': 'Business News'},
        'Financial Times Tech': {'tier': 4, 'multiplier': 1.2, 'type': 'Business News'},
        
        # TIER 5: General Tech News (Multiplier: 1.0x)
        'Hacker News': {'tier': 5, 'multiplier': 1.0, 'type': 'Aggregator'},
        'AI News': {'tier': 5, 'multiplier': 1.0, 'type': 'General'},
        'Machine Learning Mastery': {'tier': 5, 'multiplier': 1.0, 'type': 'Educational'},
        'Towards Data Science': {'tier': 5, 'multiplier': 1.0, 'type': 'Community'},
    }
    
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
    
    def __init__(self, user_agent: str = "Enhanced-AI-News-Tracker/1.0"):
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
            print(f"⚠️  Error fetching {feed_url}: {e}")
            return None
    
    def get_source_info(self, feed_name: str) -> Dict:
        """Get source credibility information"""
        for source, info in self.SOURCE_TIERS.items():
            if source.lower() in feed_name.lower():
                return {
                    'tier': info['tier'],
                    'multiplier': info['multiplier'],
                    'type': info['type'],
                    'credibility': 'High' if info['tier'] <= 2 else 'Medium' if info['tier'] <= 4 else 'Standard'
                }
        
        # Default for unknown sources
        return {
            'tier': 6,
            'multiplier': 0.9,
            'type': 'Unknown',
            'credibility': 'Standard'
        }
    
    def is_ai_related(self, text: str) -> bool:
        """Check if text contains AI-related keywords"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.AI_KEYWORDS)
    
    def calculate_base_ai_score(self, entry: Dict) -> int:
        """Calculate base AI relevance score before source weighting"""
        score = 0
        text_to_check = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
        
        # Count keyword matches
        keyword_matches = sum(1 for keyword in self.AI_KEYWORDS if keyword in text_to_check)
        score += min(keyword_matches * 8, 50)  # Max 50 points for keywords
        
        # Bonus for AI in title
        if self.is_ai_related(entry.get('title', '')):
            score += 15
        
        # Bonus for multiple AI keyword mentions
        if keyword_matches >= 3:
            score += 15
        
        # Bonus for breakthrough/significant keywords
        impact_keywords = ['breakthrough', 'announces', 'launches', 'releases', 
                          'first', 'new', 'raises', 'funding', 'acquisition']
        if any(kw in text_to_check for kw in impact_keywords):
            score += 10
        
        return min(score, 100)
    
    def calculate_weighted_score(self, base_score: int, source_multiplier: float) -> int:
        """Apply source credibility weighting to base score"""
        weighted = base_score * source_multiplier
        return min(int(weighted), 100)
    
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
    
    def extract_entry_data(self, entry, feed_name: str, feed_url: str) -> Dict:
        """Extract data from a feed entry with credibility weighting"""
        # Get published date
        published_date = 'Unknown'
        if 'published_parsed' in entry and entry.published_parsed:
            published_date = datetime(*entry.published_parsed[:6]).isoformat()
        elif 'updated_parsed' in entry and entry.updated_parsed:
            published_date = datetime(*entry.updated_parsed[:6]).isoformat()
        
        # Extract companies mentioned
        summary_text = entry.get('summary', '') + ' ' + entry.get('title', '')
        companies = self.extract_companies(summary_text)
        
        # Get source credibility info
        source_info = self.get_source_info(feed_name)
        
        # Calculate base score
        base_score = self.calculate_base_ai_score({
            'title': entry.get('title', ''),
            'summary': entry.get('summary', '')
        })
        
        # Apply source weighting
        final_score = self.calculate_weighted_score(base_score, source_info['multiplier'])
        
        entry_data = {
            'title': entry.get('title', 'N/A'),
            'link': entry.get('link', 'N/A'),
            'published_date': published_date,
            'author': entry.get('author', 'N/A'),
            'summary': entry.get('summary', entry.get('description', 'N/A')),
            'feed_name': feed_name,
            'feed_url': feed_url,
            'tags': ', '.join([tag.term for tag in entry.get('tags', [])]) if entry.get('tags') else 'N/A',
            'companies_mentioned': ', '.join(companies) if companies else 'N/A',
            
            # Source credibility fields
            'source_tier': source_info['tier'],
            'source_type': source_info['type'],
            'source_credibility': source_info['credibility'],
            'source_multiplier': source_info['multiplier'],
            
            # Scoring fields
            'base_score': base_score,
            'final_score': final_score,
            'is_ai_related': final_score >= 30
        }
        
        return entry_data
    
    def scrape_ai_news(self, feed_urls: List[str], days_back: int = 7,
                      min_final_score: int = 30, tier_filter: Optional[int] = None) -> List[Dict]:
        """
        Scrape AI news from multiple feeds with credibility weighting
        
        Args:
            feed_urls: List of RSS feed URLs
            days_back: Only get articles from last N days
            min_final_score: Minimum final score (after weighting)
            tier_filter: Only include sources from tier X or better (1-6)
        """
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        print(f"🤖 Scanning {len(feed_urls)} RSS feeds for AI news...")
        print(f"📅 Looking for articles from the last {days_back} days")
        print(f"🎯 Minimum final score: {min_final_score}/100")
        if tier_filter:
            print(f"🏆 Source tier filter: Tier {tier_filter} or better")
        print()
        
        for feed_url in feed_urls:
            feed = self.fetch_feed(feed_url)
            if not feed:
                continue
            
            feed_name = feed.feed.get('title', 'Unknown Feed')
            source_info = self.get_source_info(feed_name)
            
            # Apply tier filter
            if tier_filter and source_info['tier'] > tier_filter:
                print(f"⏭️  Skipping: {feed_name} (Tier {source_info['tier']})")
                continue
            
            print(f"📰 Processing: {feed_name} [Tier {source_info['tier']}, {source_info['credibility']}]")
            
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
                
                # Filter by final score
                if entry_data['final_score'] >= min_final_score:
                    self.ai_articles.append(entry_data)
        
        # Sort by final score (highest first)
        self.ai_articles.sort(key=lambda x: x['final_score'], reverse=True)
        
        print(f"\n✅ Found {len(self.ai_articles)} AI-related articles (out of {len(self.all_articles)} total)")
        return self.ai_articles
    
    def display_summary(self):
        """Display summary with source credibility analysis"""
        if not self.ai_articles:
            print("No AI articles found")
            return
        
        print("\n" + "="*80)
        print("🤖 AI NEWS SUMMARY (Source-Weighted)")
        print("="*80)
        
        # Top articles
        print(f"\n📊 Top 10 AI Articles (by credibility-weighted score):\n")
        for i, article in enumerate(self.ai_articles[:10], 1):
            tier_emoji = "🏆" if article['source_tier'] <= 2 else "⭐" if article['source_tier'] <= 4 else "📄"
            print(f"{i}. {tier_emoji} [{article['final_score']}/100] {article['title']}")
            print(f"   📰 {article['feed_name']} | Tier {article['source_tier']} ({article['source_credibility']})")
            print(f"   📅 {article['published_date'][:10]}")
            print(f"   🔗 {article['link']}")
            print(f"   📈 Base: {article['base_score']} → Final: {article['final_score']} (×{article['source_multiplier']})")
            if article['companies_mentioned'] != 'N/A':
                print(f"   🏢 {article['companies_mentioned']}")
            print()
        
        # Statistics
        print("="*80)
        print("📈 STATISTICS")
        print("="*80)
        
        # Source tier breakdown
        tier_counts = Counter(article['source_tier'] for article in self.ai_articles)
        print("\n🏆 Articles by Source Tier:")
        tier_names = {
            1: "Premier Academic/Research",
            2: "Company Research Blogs",
            3: "Established Tech Journalism",
            4: "Major Business/Tech News",
            5: "General Tech News",
            6: "Unknown/Other"
        }
        for tier in sorted(tier_counts.keys()):
            count = tier_counts[tier]
            percentage = (count / len(self.ai_articles)) * 100
            print(f"   Tier {tier} ({tier_names.get(tier, 'Other')}): {count} articles ({percentage:.1f}%)")
        
        # Credibility distribution
        cred_counts = Counter(article['source_credibility'] for article in self.ai_articles)
        print("\n🎖️  Articles by Credibility:")
        for cred, count in cred_counts.most_common():
            percentage = (count / len(self.ai_articles)) * 100
            print(f"   {cred}: {count} articles ({percentage:.1f}%)")
        
        # Source type breakdown
        type_counts = Counter(article['source_type'] for article in self.ai_articles)
        print("\n📰 Articles by Source Type:")
        for stype, count in type_counts.most_common():
            percentage = (count / len(self.ai_articles)) * 100
            print(f"   {stype}: {count} articles ({percentage:.1f}%)")
        
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
        
        # Top sources
        feed_counts = Counter(article['feed_name'] for article in self.ai_articles)
        print("\n📰 Top Sources:")
        for feed, count in feed_counts.most_common(10):
            source_info = self.get_source_info(feed)
            print(f"   {feed}: {count} articles [Tier {source_info['tier']}]")
        
        print("\n" + "="*80 + "\n")
    
    def export_to_json(self, filename: str = "ai_news_credibility_weighted.json"):
        """Export with source credibility data"""
        data = {
            'generated_at': datetime.now().isoformat(),
            'total_articles': len(self.ai_articles),
            'source_tiers_used': self.SOURCE_TIERS,
            'articles': self.ai_articles
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"📄 Exported {len(self.ai_articles)} articles to {filename}")
    
    def export_to_csv(self, filename: str = "ai_news_credibility_weighted.csv"):
        """Export to CSV with credibility fields"""
        if not self.ai_articles:
            print("No articles to export")
            return
        
        keys = self.ai_articles[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.ai_articles)
        
        print(f"📊 Exported {len(self.ai_articles)} articles to {filename}")
    
    def export_html_report(self, filename: str = "ai_news_credibility_report.html"):
        """Generate enhanced HTML report with credibility indicators"""
        
        # Calculate tier distribution for visualization
        tier_counts = Counter(article['source_tier'] for article in self.ai_articles)
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI News Report (Credibility-Weighted) - {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1 {{
            color: #2563eb;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 10px;
        }}
        .tier-badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            margin-left: 8px;
        }}
        .tier-1 {{ background: #fbbf24; color: #000; }}
        .tier-2 {{ background: #c0c0c0; color: #000; }}
        .tier-3 {{ background: #cd7f32; color: #fff; }}
        .tier-4 {{ background: #60a5fa; color: #000; }}
        .tier-5 {{ background: #94a3b8; color: #000; }}
        .article {{
            background: white;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 5px solid #2563eb;
        }}
        .article.high-credibility {{
            border-left-color: #10b981;
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
        .score-breakdown {{
            background: #eff6ff;
            padding: 8px 12px;
            border-left: 3px solid #2563eb;
            margin: 10px 0;
            font-size: 0.85em;
        }}
        .companies {{
            background: #fef3c7;
            padding: 8px 12px;
            border-left: 3px solid #f59e0b;
            margin: 10px 0;
            font-size: 0.9em;
        }}
        .summary {{
            color: #4b5563;
            line-height: 1.6;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-box {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-box h3 {{
            margin: 0 0 10px 0;
            color: #2563eb;
            font-size: 0.9em;
        }}
        .stat-box .number {{
            font-size: 2em;
            font-weight: bold;
            color: #1f2937;
        }}
    </style>
</head>
<body>
    <h1>🤖 AI News Report (Credibility-Weighted)</h1>
    <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="stats">
        <div class="stat-box">
            <h3>Total Articles</h3>
            <div class="number">{len(self.ai_articles)}</div>
        </div>
        <div class="stat-box">
            <h3>High Credibility</h3>
            <div class="number">{sum(1 for a in self.ai_articles if a['source_tier'] <= 2)}</div>
        </div>
        <div class="stat-box">
            <h3>Avg Final Score</h3>
            <div class="number">{int(sum(a['final_score'] for a in self.ai_articles) / len(self.ai_articles))}</div>
        </div>
    </div>
    
    <h2>📊 Source Tier Distribution</h2>
    <p>
        <span class="tier-badge tier-1">Tier 1 (Premier): {tier_counts.get(1, 0)}</span>
        <span class="tier-badge tier-2">Tier 2 (Company): {tier_counts.get(2, 0)}</span>
        <span class="tier-badge tier-3">Tier 3 (Tech Journalism): {tier_counts.get(3, 0)}</span>
        <span class="tier-badge tier-4">Tier 4 (Business News): {tier_counts.get(4, 0)}</span>
        <span class="tier-badge tier-5">Tier 5 (General): {tier_counts.get(5, 0)}</span>
    </p>
    <hr>
"""
        
        for article in self.ai_articles[:50]:
            tier_class = f"tier-{article['source_tier']}"
            high_cred = " high-credibility" if article['source_tier'] <= 2 else ""
            tier_emoji = "🏆" if article['source_tier'] <= 2 else "⭐" if article['source_tier'] <= 4 else "📄"
            
            html += f"""
    <div class="article{high_cred}">
        <h2>{tier_emoji} <a href="{article['link']}" target="_blank">{article['title']}</a></h2>
        <div class="meta">
            <span class="score">Final Score: {article['final_score']}/100</span>
            <span class="tier-badge {tier_class}">Tier {article['source_tier']}: {article['source_credibility']}</span>
            <br>
            📰 {article['feed_name']} ({article['source_type']}) | 
            📅 {article['published_date'][:10]}
            {' | ✍️ ' + article['author'] if article['author'] != 'N/A' else ''}
        </div>
        <div class="score-breakdown">
            📈 Base Score: {article['base_score']} → Final Score: {article['final_score']} (×{article['source_multiplier']} multiplier)
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
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced AI News Tracker with Source Credibility")
    parser.add_argument('-f', '--feeds-file', default='ai_news_feeds_enhanced.txt',
                       help='File containing RSS feed URLs')
    parser.add_argument('-d', '--days', type=int, default=7,
                       help='Number of days back to search (default: 7)')
    parser.add_argument('-s', '--score', type=int, default=30,
                       help='Minimum final score 0-100 (default: 30)')
    parser.add_argument('-t', '--tier', type=int, choices=[1,2,3,4,5,6],
                       help='Only include sources from this tier or better')
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
        print("No feed URLs found")
        return
    
    # Create tracker and scrape
    tracker = EnhancedAINewsTracker()
    tracker.scrape_ai_news(feed_urls, days_back=args.days, 
                          min_final_score=args.score, tier_filter=args.tier)
    
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
