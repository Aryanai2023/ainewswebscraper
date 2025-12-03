#!/usr/bin/env python3
"""
Startup Ecosystem Tracker
Track startup funding, launches, acquisitions, and ecosystem news
"""

import feedparser
import requests
import json
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
from collections import Counter


class StartupTracker:
    """Track startup ecosystem news with focus on funding, launches, and acquisitions"""
    
    # Startup event types and keywords
    STARTUP_CATEGORIES = {
        'Funding': {
            'keywords': [
                'raises', 'raised', 'funding', 'series a', 'series b', 'series c',
                'series d', 'seed round', 'pre-seed', 'venture capital', 'vc',
                'investment', 'investors', 'valuation', 'million', 'billion',
                'round led by', 'participated', 'invested', 'financing',
                'capital raised', 'oversubscribed', 'closes round'
            ],
            'weight': 1.5  # High priority
        },
        'Acquisition': {
            'keywords': [
                'acquires', 'acquired', 'acquisition', 'buys', 'bought',
                'merger', 'merges', 'deal', 'purchase', 'takeover',
                'exit', 'acquired for', 'acquired by'
            ],
            'weight': 1.4
        },
        'Product Launch': {
            'keywords': [
                'launches', 'launched', 'release', 'released', 'unveils',
                'introduces', 'announces', 'debut', 'new product',
                'rolls out', 'comes out of beta', 'general availability',
                'now available', 'shipping'
            ],
            'weight': 1.2
        },
        'IPO/Public': {
            'keywords': [
                'ipo', 'initial public offering', 'going public',
                'files for ipo', 'public offering', 'nasdaq', 'nyse',
                'direct listing', 'spac', 'public debut'
            ],
            'weight': 1.5
        },
        'Partnership': {
            'keywords': [
                'partnership', 'partners with', 'collaboration',
                'teams up', 'joins forces', 'strategic alliance',
                'works with', 'integration'
            ],
            'weight': 1.0
        },
        'Expansion': {
            'keywords': [
                'expands', 'expansion', 'opens office', 'new market',
                'enters market', 'international', 'launches in',
                'growth', 'scales', 'hiring'
            ],
            'weight': 1.1
        },
        'Pivot': {
            'keywords': [
                'pivot', 'pivots', 'rebrands', 'shifts focus',
                'new direction', 'changes strategy', 'repositions'
            ],
            'weight': 1.2
        },
        'Shutdown': {
            'keywords': [
                'shuts down', 'shutdown', 'closes', 'ceases operations',
                'winds down', 'goes out of business', 'defunct'
            ],
            'weight': 1.3
        }
    }
    
    # Startup stages
    STARTUP_STAGES = {
        'Pre-Seed': ['pre-seed', 'preseed', 'pre seed'],
        'Seed': ['seed round', 'seed funding', 'seed stage'],
        'Series A': ['series a', 'series-a'],
        'Series B': ['series b', 'series-b'],
        'Series C': ['series c', 'series-c'],
        'Series D+': ['series d', 'series e', 'series f', 'late stage'],
        'Growth': ['growth stage', 'growth round', 'growth equity'],
        'IPO': ['ipo', 'going public', 'public offering']
    }
    
    # Technology sectors for startups
    TECH_SECTORS = {
        'AI/ML': ['ai', 'artificial intelligence', 'machine learning', 'deep learning', 
                  'llm', 'generative ai', 'computer vision', 'nlp'],
        'FinTech': ['fintech', 'financial technology', 'payments', 'banking', 
                    'cryptocurrency', 'blockchain', 'defi', 'trading'],
        'HealthTech': ['healthtech', 'digital health', 'telemedicine', 'biotech',
                       'medtech', 'healthcare', 'pharma'],
        'SaaS': ['saas', 'software as a service', 'b2b software', 'enterprise software',
                 'cloud software', 'platform'],
        'E-commerce': ['ecommerce', 'e-commerce', 'online retail', 'marketplace',
                       'd2c', 'direct to consumer'],
        'CleanTech': ['cleantech', 'climate tech', 'renewable energy', 'sustainability',
                      'carbon', 'clean energy'],
        'EdTech': ['edtech', 'education technology', 'online learning', 'e-learning'],
        'PropTech': ['proptech', 'real estate tech', 'property technology'],
        'FoodTech': ['foodtech', 'food delivery', 'restaurant tech', 'agtech'],
        'Transportation': ['mobility', 'transportation', 'automotive', 'ev', 
                          'electric vehicle', 'autonomous'],
        'CyberSecurity': ['cybersecurity', 'security', 'infosec', 'data protection'],
        'DevTools': ['developer tools', 'devops', 'api', 'infrastructure'],
        'MarTech': ['martech', 'marketing technology', 'adtech', 'advertising'],
        'HRTech': ['hrtech', 'human resources', 'recruiting', 'talent'],
        'Gaming': ['gaming', 'game', 'esports', 'metaverse'],
        'Web3': ['web3', 'crypto', 'nft', 'dao', 'decentralized'],
        'Hardware': ['hardware', 'robotics', 'iot', 'consumer electronics'],
        'Consumer': ['consumer', 'consumer app', 'social', 'marketplace']
    }
    
    # Notable VCs and accelerators
    NOTABLE_INVESTORS = [
        'Y Combinator', 'YC', 'Sequoia', 'Andreessen Horowitz', 'a16z',
        'Accel', 'Benchmark', 'Greylock', 'Kleiner Perkins', 'NEA',
        'Lightspeed', 'Index Ventures', 'General Catalyst', 'Founders Fund',
        'Tiger Global', 'SoftBank', 'Insight Partners', 'Thrive Capital',
        'GV', 'Google Ventures', 'Microsoft Ventures', 'Amazon Ventures',
        'Khosla Ventures', 'First Round', 'CRV', 'Battery Ventures',
        '500 Startups', 'Techstars', 'Plug and Play'
    ]
    
    def __init__(self, user_agent: str = "Startup-Tracker/1.0"):
        self.user_agent = user_agent
        self.all_articles = []
        self.startup_articles = []
    
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
    
    def detect_categories(self, text: str) -> List[str]:
        """Detect startup event categories in text"""
        text_lower = text.lower()
        detected = []
        
        for category, info in self.STARTUP_CATEGORIES.items():
            if any(keyword in text_lower for keyword in info['keywords']):
                detected.append(category)
        
        return detected
    
    def detect_stage(self, text: str) -> Optional[str]:
        """Detect startup funding stage"""
        text_lower = text.lower()
        
        for stage, patterns in self.STARTUP_STAGES.items():
            if any(pattern in text_lower for pattern in patterns):
                return stage
        
        return None
    
    def detect_sectors(self, text: str) -> List[str]:
        """Detect technology sectors"""
        text_lower = text.lower()
        detected = []
        
        for sector, keywords in self.TECH_SECTORS.items():
            if any(keyword in text_lower for keyword in keywords):
                detected.append(sector)
        
        return detected
    
    def extract_funding_amount(self, text: str) -> Optional[str]:
        """Extract funding amount from text"""
        # Pattern for $X million/billion
        patterns = [
            r'\$\s*(\d+(?:\.\d+)?)\s*(million|billion|M|B)',
            r'(\d+(?:\.\d+)?)\s*(million|billion)\s*(?:dollars)?',
            r'raised\s*\$\s*(\d+(?:\.\d+)?)\s*(million|billion|M|B)',
            r'funding\s+of\s*\$\s*(\d+(?:\.\d+)?)\s*(million|billion|M|B)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = match.group(1)
                unit = match.group(2).lower()
                if unit in ['b', 'billion']:
                    return f"${amount}B"
                else:
                    return f"${amount}M"
        
        return None
    
    def extract_investors(self, text: str) -> List[str]:
        """Extract mentioned investors"""
        found = []
        for investor in self.NOTABLE_INVESTORS:
            if re.search(r'\b' + re.escape(investor) + r'\b', text, re.IGNORECASE):
                found.append(investor)
        return found
    
    def calculate_relevance_score(self, entry: Dict) -> int:
        """Calculate startup relevance score"""
        score = 0
        text = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
        
        # Category detection with weighting
        categories = self.detect_categories(text)
        for category in categories:
            weight = self.STARTUP_CATEGORIES[category]['weight']
            score += 20 * weight
        
        # Funding amount bonus
        funding_amount = self.extract_funding_amount(text)
        if funding_amount:
            score += 15
            # Extra bonus for large rounds
            if 'B' in funding_amount:
                score += 10
        
        # Notable investor bonus
        investors = self.extract_investors(text)
        if investors:
            score += 10
        
        # Startup-specific keywords in title
        startup_keywords = ['startup', 'founder', 'raises', 'launches', 'acquires']
        if any(kw in entry.get('title', '').lower() for kw in startup_keywords):
            score += 15
        
        # Sector detection
        sectors = self.detect_sectors(text)
        if sectors:
            score += 5 * len(sectors)
        
        return min(score, 100)
    
    def extract_entry_data(self, entry, feed_name: str, feed_url: str) -> Dict:
        """Extract startup data from feed entry"""
        # Get published date
        published_date = 'Unknown'
        if 'published_parsed' in entry and entry.published_parsed:
            published_date = datetime(*entry.published_parsed[:6]).isoformat()
        elif 'updated_parsed' in entry and entry.updated_parsed:
            published_date = datetime(*entry.updated_parsed[:6]).isoformat()
        
        # Extract data
        full_text = entry.get('summary', '') + ' ' + entry.get('title', '')
        categories = self.detect_categories(full_text)
        stage = self.detect_stage(full_text)
        sectors = self.detect_sectors(full_text)
        funding_amount = self.extract_funding_amount(full_text)
        investors = self.extract_investors(full_text)
        
        entry_data = {
            'title': entry.get('title', 'N/A'),
            'link': entry.get('link', 'N/A'),
            'published_date': published_date,
            'author': entry.get('author', 'N/A'),
            'summary': entry.get('summary', entry.get('description', 'N/A')),
            'feed_name': feed_name,
            'feed_url': feed_url,
            
            # Startup-specific fields
            'categories': ', '.join(categories) if categories else 'General',
            'primary_category': categories[0] if categories else 'General',
            'funding_stage': stage if stage else 'N/A',
            'sectors': ', '.join(sectors) if sectors else 'N/A',
            'funding_amount': funding_amount if funding_amount else 'N/A',
            'investors': ', '.join(investors) if investors else 'N/A',
            
            'tags': ', '.join([tag.term for tag in entry.get('tags', [])]) if entry.get('tags') else 'N/A'
        }
        
        # Calculate relevance
        entry_data['relevance_score'] = self.calculate_relevance_score(entry_data)
        entry_data['is_startup_news'] = entry_data['relevance_score'] >= 20
        
        return entry_data
    
    def scrape_startup_news(self, feed_urls: List[str], days_back: int = 7,
                           min_relevance_score: int = 20,
                           category_filter: Optional[str] = None,
                           sector_filter: Optional[str] = None) -> List[Dict]:
        """
        Scrape startup news from multiple feeds
        
        Args:
            feed_urls: List of RSS feed URLs
            days_back: Only get articles from last N days
            min_relevance_score: Minimum relevance score (0-100)
            category_filter: Filter by category (Funding, Acquisition, etc.)
            sector_filter: Filter by sector (AI/ML, FinTech, etc.)
        """
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        print(f"🚀 Scanning {len(feed_urls)} RSS feeds for startup news...")
        print(f"📅 Looking for articles from the last {days_back} days")
        print(f"🎯 Minimum relevance score: {min_relevance_score}/100")
        if category_filter:
            print(f"📂 Category filter: {category_filter}")
        if sector_filter:
            print(f"🏷️  Sector filter: {sector_filter}")
        print()
        
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
                
                # Filter by relevance
                if entry_data['relevance_score'] < min_relevance_score:
                    continue
                
                # Filter by category
                if category_filter:
                    if category_filter.lower() not in entry_data['categories'].lower():
                        continue
                
                # Filter by sector
                if sector_filter:
                    if sector_filter.lower() not in entry_data['sectors'].lower():
                        continue
                
                self.startup_articles.append(entry_data)
        
        # Sort by relevance score
        self.startup_articles.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        print(f"\n✅ Found {len(self.startup_articles)} startup articles (out of {len(self.all_articles)} total)")
        return self.startup_articles
    
    def display_summary(self):
        """Display summary of startup news"""
        if not self.startup_articles:
            print("No startup articles found")
            return
        
        print("\n" + "="*80)
        print("🚀 STARTUP ECOSYSTEM SUMMARY")
        print("="*80)
        
        # Top articles
        print(f"\n📊 Top 15 Startup Stories (by relevance):\n")
        for i, article in enumerate(self.startup_articles[:15], 1):
            # Category emoji
            cat_emoji = {
                'Funding': '💰',
                'Acquisition': '🤝',
                'Product Launch': '🚀',
                'IPO/Public': '📈',
                'Partnership': '🤝',
                'Expansion': '🌍',
                'Pivot': '🔄',
                'Shutdown': '⚠️'
            }.get(article['primary_category'], '📰')
            
            print(f"{i}. {cat_emoji} [{article['relevance_score']}/100] {article['title']}")
            print(f"   📂 {article['primary_category']} | 📅 {article['published_date'][:10]}")
            print(f"   📰 {article['feed_name']}")
            print(f"   🔗 {article['link']}")
            
            if article['funding_amount'] != 'N/A':
                print(f"   💵 Amount: {article['funding_amount']}")
            if article['funding_stage'] != 'N/A':
                print(f"   📊 Stage: {article['funding_stage']}")
            if article['sectors'] != 'N/A':
                print(f"   🏷️  Sectors: {article['sectors']}")
            if article['investors'] != 'N/A':
                print(f"   🏦 Investors: {article['investors']}")
            print()
        
        # Statistics
        print("="*80)
        print("📈 STARTUP ECOSYSTEM STATISTICS")
        print("="*80)
        
        # Category breakdown
        category_counts = Counter()
        for article in self.startup_articles:
            cats = article['categories'].split(', ')
            for cat in cats:
                if cat != 'General':
                    category_counts[cat] += 1
        
        print("\n📂 Articles by Category:")
        for category, count in category_counts.most_common():
            percentage = (count / len(self.startup_articles)) * 100
            emoji = {
                'Funding': '💰',
                'Acquisition': '🤝',
                'Product Launch': '🚀',
                'IPO/Public': '📈',
                'Partnership': '🤝',
                'Expansion': '🌍',
                'Pivot': '🔄',
                'Shutdown': '⚠️'
            }.get(category, '📰')
            print(f"   {emoji} {category}: {count} articles ({percentage:.1f}%)")
        
        # Funding stage breakdown
        stage_counts = Counter(
            article['funding_stage'] for article in self.startup_articles
            if article['funding_stage'] != 'N/A'
        )
        
        if stage_counts:
            print("\n📊 Funding by Stage:")
            for stage, count in stage_counts.most_common():
                print(f"   {stage}: {count} articles")
        
        # Sector breakdown
        sector_counts = Counter()
        for article in self.startup_articles:
            if article['sectors'] != 'N/A':
                sectors = article['sectors'].split(', ')
                for sector in sectors:
                    sector_counts[sector] += 1
        
        if sector_counts:
            print("\n🏷️  Top Sectors:")
            for sector, count in sector_counts.most_common(10):
                percentage = (count / len(self.startup_articles)) * 100
                print(f"   {sector}: {count} articles ({percentage:.1f}%)")
        
        # Investor mentions
        all_investors = []
        for article in self.startup_articles:
            if article['investors'] != 'N/A':
                all_investors.extend(article['investors'].split(', '))
        
        if all_investors:
            investor_counts = Counter(all_investors)
            print("\n🏦 Most Active Investors:")
            for investor, count in investor_counts.most_common(10):
                print(f"   {investor}: {count} mentions")
        
        # Funding amounts
        funding_articles = [a for a in self.startup_articles if a['funding_amount'] != 'N/A']
        if funding_articles:
            print(f"\n💵 Funding Announcements: {len(funding_articles)} articles")
            print("   Top 5 by amount:")
            sorted_funding = sorted(funding_articles, 
                                   key=lambda x: (
                                       float(x['funding_amount'].replace('$', '').replace('B', '').replace('M', '')) * 
                                       (1000 if 'B' in x['funding_amount'] else 1)
                                   ), 
                                   reverse=True)
            for article in sorted_funding[:5]:
                print(f"   💰 {article['funding_amount']}: {article['title'][:60]}...")
        
        # Source statistics
        feed_counts = Counter(article['feed_name'] for article in self.startup_articles)
        print("\n📰 Top Sources:")
        for feed, count in feed_counts.most_common(10):
            print(f"   {feed}: {count} articles")
        
        print("\n" + "="*80 + "\n")
    
    def export_to_json(self, filename: str = "startup_news.json"):
        """Export to JSON"""
        data = {
            'generated_at': datetime.now().isoformat(),
            'total_articles': len(self.startup_articles),
            'categories_tracked': list(self.STARTUP_CATEGORIES.keys()),
            'sectors_tracked': list(self.TECH_SECTORS.keys()),
            'articles': self.startup_articles
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"📄 Exported {len(self.startup_articles)} articles to {filename}")
    
    def export_to_csv(self, filename: str = "startup_news.csv"):
        """Export to CSV"""
        if not self.startup_articles:
            print("No articles to export")
            return
        
        keys = self.startup_articles[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.startup_articles)
        
        print(f"📊 Exported {len(self.startup_articles)} articles to {filename}")
    
    def export_html_report(self, filename: str = "startup_news_report.html"):
        """Generate HTML report"""
        
        # Calculate category distribution
        category_counts = Counter(article['primary_category'] for article in self.startup_articles)
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Startup Ecosystem Report - {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .container {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #667eea;
            font-size: 2.5em;
            margin-top: 0;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .stat-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
        }}
        .stat-box h3 {{
            margin: 0 0 10px 0;
            font-size: 0.9em;
            opacity: 0.9;
        }}
        .stat-box .number {{
            font-size: 2.5em;
            font-weight: bold;
        }}
        .article {{
            background: #f8fafc;
            padding: 25px;
            margin: 20px 0;
            border-radius: 15px;
            border-left: 5px solid #667eea;
        }}
        .article.funding {{
            border-left-color: #10b981;
        }}
        .article.acquisition {{
            border-left-color: #f59e0b;
        }}
        .article.launch {{
            border-left-color: #3b82f6;
        }}
        .article.ipo {{
            border-left-color: #ef4444;
        }}
        .article h2 {{
            margin-top: 0;
            color: #1e293b;
        }}
        .article a {{
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }}
        .article a:hover {{
            text-decoration: underline;
        }}
        .meta {{
            color: #64748b;
            font-size: 0.9em;
            margin: 12px 0;
        }}
        .badge {{
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            margin: 5px 5px 5px 0;
        }}
        .badge.funding {{
            background: #d1fae5;
            color: #065f46;
        }}
        .badge.acquisition {{
            background: #fef3c7;
            color: #92400e;
        }}
        .badge.launch {{
            background: #dbeafe;
            color: #1e40af;
        }}
        .badge.ipo {{
            background: #fee2e2;
            color: #991b1b;
        }}
        .badge.score {{
            background: #667eea;
            color: white;
        }}
        .info-box {{
            background: #f1f5f9;
            padding: 12px 16px;
            border-radius: 10px;
            margin: 12px 0;
            font-size: 0.9em;
        }}
        .summary {{
            color: #475569;
            line-height: 1.7;
            margin-top: 15px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Startup Ecosystem Report</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="stats">
            <div class="stat-box">
                <h3>Total Stories</h3>
                <div class="number">{len(self.startup_articles)}</div>
            </div>
            <div class="stat-box">
                <h3>Funding Rounds</h3>
                <div class="number">{category_counts.get('Funding', 0)}</div>
            </div>
            <div class="stat-box">
                <h3>Acquisitions</h3>
                <div class="number">{category_counts.get('Acquisition', 0)}</div>
            </div>
            <div class="stat-box">
                <h3>Product Launches</h3>
                <div class="number">{category_counts.get('Product Launch', 0)}</div>
            </div>
        </div>
        
        <h2 style="color: #667eea; margin-top: 40px;">📰 Latest Startup News</h2>
"""
        
        for article in self.startup_articles[:50]:
            # Determine article class and emoji
            cat_lower = article['primary_category'].lower().replace('/', '').replace(' ', '')
            article_class = ''
            emoji = '📰'
            
            if 'funding' in cat_lower:
                article_class = 'funding'
                emoji = '💰'
            elif 'acquisition' in cat_lower:
                article_class = 'acquisition'
                emoji = '🤝'
            elif 'launch' in cat_lower:
                article_class = 'launch'
                emoji = '🚀'
            elif 'ipo' in cat_lower or 'public' in cat_lower:
                article_class = 'ipo'
                emoji = '📈'
            
            html += f"""
        <div class="article {article_class}">
            <h2>{emoji} <a href="{article['link']}" target="_blank">{article['title']}</a></h2>
            <div class="meta">
                <span class="badge score">Score: {article['relevance_score']}/100</span>
                <span class="badge {article_class}">{article['primary_category']}</span>
                📅 {article['published_date'][:10]} | 📰 {article['feed_name']}
            </div>
"""
            
            # Add info boxes for funding, stage, sectors, investors
            if article['funding_amount'] != 'N/A' or article['funding_stage'] != 'N/A' or \
               article['sectors'] != 'N/A' or article['investors'] != 'N/A':
                html += '            <div class="info-box">\n'
                
                if article['funding_amount'] != 'N/A':
                    html += f"                💵 <strong>Amount:</strong> {article['funding_amount']}<br>\n"
                if article['funding_stage'] != 'N/A':
                    html += f"                📊 <strong>Stage:</strong> {article['funding_stage']}<br>\n"
                if article['sectors'] != 'N/A':
                    html += f"                🏷️ <strong>Sectors:</strong> {article['sectors']}<br>\n"
                if article['investors'] != 'N/A':
                    html += f"                🏦 <strong>Investors:</strong> {article['investors']}\n"
                
                html += '            </div>\n'
            
            html += f"""            <div class="summary">{article['summary'][:500]}{'...' if len(article['summary']) > 500 else ''}</div>
        </div>
"""
        
        html += """
    </div>
</body>
</html>
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"📱 Generated HTML report: {filename}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Track Startup Ecosystem News")
    parser.add_argument('-f', '--feeds-file', default='startup_feeds.txt',
                       help='File containing RSS feed URLs')
    parser.add_argument('-d', '--days', type=int, default=7,
                       help='Number of days back to search (default: 7)')
    parser.add_argument('-s', '--score', type=int, default=20,
                       help='Minimum relevance score 0-100 (default: 20)')
    parser.add_argument('-c', '--category', 
                       choices=['Funding', 'Acquisition', 'Product Launch', 'IPO/Public', 
                               'Partnership', 'Expansion', 'Pivot', 'Shutdown'],
                       help='Filter by category')
    parser.add_argument('--sector',
                       help='Filter by sector (AI/ML, FinTech, HealthTech, etc.)')
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
    tracker = StartupTracker()
    tracker.scrape_startup_news(feed_urls, days_back=args.days, 
                               min_relevance_score=args.score,
                               category_filter=args.category,
                               sector_filter=args.sector)
    
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
