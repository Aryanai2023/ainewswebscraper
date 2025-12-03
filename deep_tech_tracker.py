#!/usr/bin/env python3
"""
Deep Tech Sector Tracker
Track innovations across quantum computing, biotech, space tech, robotics, and more
"""

import feedparser
import requests
import json
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
from collections import Counter


class DeepTechTracker:
    """Track deep technology innovations across multiple sectors"""
    
    # Deep tech sectors and their keywords
    SECTORS = {
        'Quantum Computing': [
            'quantum', 'qubit', 'quantum computing', 'quantum algorithm',
            'quantum supremacy', 'quantum advantage', 'superconducting',
            'quantum entanglement', 'quantum gate', 'quantum processor',
            'topological qubit', 'quantum error correction', 'quantum annealing'
        ],
        'Biotechnology': [
            'biotech', 'crispr', 'gene editing', 'gene therapy', 'synthetic biology',
            'mrna', 'protein', 'genome', 'genetic', 'biopharmaceutical',
            'cell therapy', 'immunotherapy', 'antibody', 'vaccine',
            'drug discovery', 'bioengineering', 'metabolic engineering'
        ],
        'Space Technology': [
            'space', 'satellite', 'rocket', 'orbital', 'spacecraft', 'astronaut',
            'launch', 'spacex', 'nasa', 'blue origin', 'rocket lab',
            'starship', 'falcon', 'reusable rocket', 'space station',
            'mars', 'lunar', 'asteroid mining', 'space debris'
        ],
        'Robotics': [
            'robot', 'robotics', 'autonomous', 'manipulation', 'gripper',
            'humanoid', 'industrial robot', 'collaborative robot', 'cobot',
            'robot arm', 'wheeled robot', 'legged robot', 'drone robot',
            'robotic surgery', 'warehouse automation', 'robot vision'
        ],
        'Advanced Materials': [
            'nanomaterial', 'graphene', 'metamaterial', 'carbon nanotube',
            '2d material', 'superconductor', 'smart material',
            'advanced composite', 'aerogel', 'quantum dot',
            'perovskite', 'photonic crystal', 'nanoparticle'
        ],
        'Clean Energy': [
            'solar', 'wind energy', 'fusion', 'nuclear', 'battery',
            'energy storage', 'hydrogen fuel', 'geothermal', 'tidal energy',
            'grid scale', 'renewable', 'cleantech', 'carbon capture',
            'energy efficiency', 'power generation', 'solar cell',
            'lithium ion', 'solid state battery'
        ],
        'Semiconductors': [
            'semiconductor', 'chip', 'processor', 'transistor', 'wafer',
            'fabrication', 'lithography', 'euv', 'asml', 'tsmc',
            'foundry', '3nm', '5nm', '7nm', 'chiplet', 'packaging',
            'gallium nitride', 'silicon carbide', 'risc-v'
        ],
        'Neurotechnology': [
            'brain computer interface', 'bci', 'neural interface',
            'neurotech', 'brain implant', 'neural recording',
            'neuralink', 'neuroprosthetic', 'brain stimulation',
            'optogenetics', 'neural engineering', 'neuromorphic'
        ],
        'Photonics': [
            'photonics', 'laser', 'optical', 'fiber optic', 'lidar',
            'photonic chip', 'quantum optics', 'optical computing',
            'photonic integrated circuit', 'holography', 'optoelectronics'
        ],
        '3D Printing': [
            '3d print', 'additive manufacturing', 'metal printing',
            'bioprinting', 'powder bed fusion', 'stereolithography',
            'direct metal laser sintering', 'material jetting'
        ],
        'Agricultural Technology': [
            'agtech', 'precision agriculture', 'vertical farming',
            'agricultural drone', 'crop monitoring', 'soil sensor',
            'agricultural robot', 'smart farming', 'aquaculture',
            'food tech', 'alternative protein', 'cellular agriculture'
        ],
        'Fusion Energy': [
            'fusion', 'tokamak', 'stellarator', 'inertial confinement',
            'iter', 'fusion reactor', 'plasma', 'magnetic confinement',
            'fusion energy', 'nuclear fusion'
        ]
    }
    
    # Deep tech companies and organizations
    DEEP_TECH_ORGS = [
        # Quantum
        'IBM Quantum', 'Google Quantum AI', 'IonQ', 'Rigetti', 'D-Wave',
        'PsiQuantum', 'Atom Computing', 'QuEra', 'Pasqal', 'Xanadu',
        # Biotech
        'Moderna', 'CRISPR Therapeutics', 'Editas', 'Intellia', 'Ginkgo Bioworks',
        'Zymergen', 'Synthego', 'Mammoth Biosciences', 'Beam Therapeutics',
        # Space
        'SpaceX', 'Blue Origin', 'Rocket Lab', 'Relativity Space', 'Astra',
        'Virgin Galactic', 'Axiom Space', 'Planet Labs', 'Spire Global',
        # Robotics
        'Boston Dynamics', 'Figure AI', 'Agility Robotics', 'ANYbotics',
        'Sanctuary AI', 'Miso Robotics', 'Covariant', 'Intrinsic',
        # Energy
        'Commonwealth Fusion', 'TAE Technologies', 'Helion Energy',
        'QuantumScape', 'Solid Power', 'Form Energy', 'Energy Vault',
        # Semiconductors
        'TSMC', 'ASML', 'Applied Materials', 'Cerebras', 'Graphcore',
        'SambaNova', 'Groq', 'Tenstorrent',
        # Other
        'Neuralink', 'Synchron', 'Kernel', 'Paradromics',
        'Desktop Metal', 'Carbon', 'Formlabs', 'Velo3D'
    ]
    
    def __init__(self, user_agent: str = "DeepTech-Tracker/1.0"):
        self.user_agent = user_agent
        self.all_articles = []
        self.deep_tech_articles = []
    
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
    
    def detect_sectors(self, text: str) -> List[str]:
        """Detect which deep tech sectors are mentioned in text"""
        text_lower = text.lower()
        detected_sectors = []
        
        for sector, keywords in self.SECTORS.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_sectors.append(sector)
        
        return detected_sectors
    
    def calculate_relevance_score(self, entry: Dict) -> int:
        """Calculate deep tech relevance score (0-100)"""
        score = 0
        text = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
        
        # Count sector matches
        detected_sectors = self.detect_sectors(text)
        score += len(detected_sectors) * 15  # 15 points per sector
        
        # Bonus for multiple sectors (interdisciplinary)
        if len(detected_sectors) >= 2:
            score += 20
        
        # Bonus for sector keywords in title
        title_lower = entry.get('title', '').lower()
        for sector, keywords in self.SECTORS.items():
            if any(keyword in title_lower for keyword in keywords):
                score += 10
                break
        
        # Bonus for funding/breakthrough keywords
        high_impact_keywords = [
            'breakthrough', 'first', 'novel', 'raises', 'funding',
            'series a', 'series b', 'milestone', 'achievement',
            'record', 'demonstration', 'prototype', 'commercial'
        ]
        if any(keyword in text for keyword in high_impact_keywords):
            score += 15
        
        return min(score, 100)
    
    def extract_organizations(self, text: str) -> List[str]:
        """Extract mentioned deep tech organizations"""
        found_orgs = []
        for org in self.DEEP_TECH_ORGS:
            if re.search(r'\b' + re.escape(org) + r'\b', text, re.IGNORECASE):
                found_orgs.append(org)
        return found_orgs
    
    def categorize_funding_stage(self, text: str) -> Optional[str]:
        """Detect funding stage if mentioned"""
        text_lower = text.lower()
        
        funding_stages = {
            'Seed': ['seed round', 'seed funding', 'pre-seed'],
            'Series A': ['series a', 'series-a'],
            'Series B': ['series b', 'series-b'],
            'Series C': ['series c', 'series-c'],
            'Series D+': ['series d', 'series e', 'series f'],
            'IPO': ['ipo', 'initial public offering', 'going public'],
            'Acquisition': ['acquired', 'acquisition', 'acquires'],
            'Grant': ['grant', 'awarded', 'government funding']
        }
        
        for stage, patterns in funding_stages.items():
            if any(pattern in text_lower for pattern in patterns):
                return stage
        
        return None
    
    def extract_entry_data(self, entry, feed_name: str, feed_url: str) -> Dict:
        """Extract data from a feed entry"""
        # Get published date
        published_date = 'Unknown'
        if 'published_parsed' in entry and entry.published_parsed:
            published_date = datetime(*entry.published_parsed[:6]).isoformat()
        elif 'updated_parsed' in entry and entry.updated_parsed:
            published_date = datetime(*entry.updated_parsed[:6]).isoformat()
        
        # Extract data
        summary_text = entry.get('summary', '') + ' ' + entry.get('title', '')
        sectors = self.detect_sectors(summary_text)
        organizations = self.extract_organizations(summary_text)
        funding_stage = self.categorize_funding_stage(summary_text)
        
        entry_data = {
            'title': entry.get('title', 'N/A'),
            'link': entry.get('link', 'N/A'),
            'published_date': published_date,
            'author': entry.get('author', 'N/A'),
            'summary': entry.get('summary', entry.get('description', 'N/A')),
            'feed_name': feed_name,
            'feed_url': feed_url,
            'sectors': ', '.join(sectors) if sectors else 'General',
            'primary_sector': sectors[0] if sectors else 'General',
            'organizations': ', '.join(organizations) if organizations else 'N/A',
            'funding_stage': funding_stage if funding_stage else 'N/A',
            'tags': ', '.join([tag.term for tag in entry.get('tags', [])]) if entry.get('tags') else 'N/A'
        }
        
        # Calculate relevance
        entry_data['relevance_score'] = self.calculate_relevance_score(entry_data)
        entry_data['is_deep_tech'] = entry_data['relevance_score'] >= 20
        
        return entry_data
    
    def scrape_deep_tech(self, feed_urls: List[str], days_back: int = 7,
                        min_relevance_score: int = 20) -> List[Dict]:
        """Scrape deep tech news from multiple feeds"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        print(f"🔬 Scanning {len(feed_urls)} RSS feeds for Deep Tech news...")
        print(f"📅 Looking for articles from the last {days_back} days")
        print(f"🎯 Minimum relevance score: {min_relevance_score}/100\n")
        
        for feed_url in feed_urls:
            feed = self.fetch_feed(feed_url)
            if not feed:
                continue
            
            feed_name = feed.feed.get('title', 'Unknown Feed')
            print(f"📡 Processing: {feed_name}")
            
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
                if entry_data['relevance_score'] >= min_relevance_score:
                    self.deep_tech_articles.append(entry_data)
        
        # Sort by relevance score
        self.deep_tech_articles.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        print(f"\n✅ Found {len(self.deep_tech_articles)} deep tech articles (out of {len(self.all_articles)} total)")
        return self.deep_tech_articles
    
    def display_summary(self):
        """Display summary of deep tech news"""
        if not self.deep_tech_articles:
            print("No deep tech articles found")
            return
        
        print("\n" + "="*80)
        print("🔬 DEEP TECH NEWS SUMMARY")
        print("="*80)
        
        # Top articles
        print(f"\n📊 Top 15 Deep Tech Articles (by relevance):\n")
        for i, article in enumerate(self.deep_tech_articles[:15], 1):
            print(f"{i}. [{article['relevance_score']}/100] {article['title']}")
            print(f"   📅 {article['published_date'][:10]} | 📰 {article['feed_name']}")
            print(f"   🔗 {article['link']}")
            print(f"   🏷️  Sectors: {article['sectors']}")
            if article['organizations'] != 'N/A':
                print(f"   🏢 Organizations: {article['organizations']}")
            if article['funding_stage'] != 'N/A':
                print(f"   💰 {article['funding_stage']}")
            print()
        
        # Statistics
        print("="*80)
        print("📈 DEEP TECH STATISTICS")
        print("="*80)
        
        # Sector breakdown
        sector_counts = Counter()
        for article in self.deep_tech_articles:
            sectors = article['sectors'].split(', ')
            for sector in sectors:
                if sector != 'General':
                    sector_counts[sector] += 1
        
        print("\n🏷️  Articles by Sector:")
        for sector, count in sector_counts.most_common():
            percentage = (count / len(self.deep_tech_articles)) * 100
            print(f"   {sector}: {count} articles ({percentage:.1f}%)")
        
        # Organization mentions
        all_orgs = []
        for article in self.deep_tech_articles:
            if article['organizations'] != 'N/A':
                all_orgs.extend(article['organizations'].split(', '))
        
        if all_orgs:
            org_counts = Counter(all_orgs)
            print("\n🏢 Most Mentioned Organizations:")
            for org, count in org_counts.most_common(15):
                print(f"   {org}: {count} mentions")
        
        # Funding activity
        funding_counts = Counter(
            article['funding_stage'] for article in self.deep_tech_articles
            if article['funding_stage'] != 'N/A'
        )
        
        if funding_counts:
            print("\n💰 Funding Activity:")
            for stage, count in funding_counts.most_common():
                print(f"   {stage}: {count} articles")
        
        # Source statistics
        feed_counts = Counter(article['feed_name'] for article in self.deep_tech_articles)
        print("\n📰 Articles by Source:")
        for feed, count in feed_counts.most_common(10):
            print(f"   {feed}: {count} articles")
        
        print("\n" + "="*80 + "\n")
    
    def export_to_json(self, filename: str = "deep_tech_news.json"):
        """Export to JSON"""
        data = {
            'generated_at': datetime.now().isoformat(),
            'total_articles': len(self.deep_tech_articles),
            'sectors_tracked': list(self.SECTORS.keys()),
            'articles': self.deep_tech_articles
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"📄 Exported {len(self.deep_tech_articles)} articles to {filename}")
    
    def export_to_csv(self, filename: str = "deep_tech_news.csv"):
        """Export to CSV"""
        if not self.deep_tech_articles:
            print("No articles to export")
            return
        
        keys = self.deep_tech_articles[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.deep_tech_articles)
        
        print(f"📊 Exported {len(self.deep_tech_articles)} articles to {filename}")
    
    def export_html_report(self, filename: str = "deep_tech_report.html"):
        """Generate HTML report"""
        
        # Calculate sector distribution for chart
        sector_counts = Counter()
        for article in self.deep_tech_articles:
            sectors = article['sectors'].split(', ')
            for sector in sectors:
                if sector != 'General':
                    sector_counts[sector] += 1
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Deep Tech Report - {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: #0f172a;
            color: #e2e8f0;
        }}
        h1 {{
            color: #38bdf8;
            border-bottom: 3px solid #38bdf8;
            padding-bottom: 15px;
            font-size: 2.5em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .stat-card {{
            background: #1e293b;
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #38bdf8;
        }}
        .stat-card h3 {{
            margin: 0 0 10px 0;
            color: #38bdf8;
            font-size: 0.9em;
            text-transform: uppercase;
        }}
        .stat-card .number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #fff;
        }}
        .article {{
            background: #1e293b;
            padding: 25px;
            margin: 20px 0;
            border-radius: 12px;
            border-left: 5px solid #38bdf8;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        .article h2 {{
            margin-top: 0;
            color: #fff;
            font-size: 1.4em;
        }}
        .article a {{
            color: #38bdf8;
            text-decoration: none;
        }}
        .article a:hover {{
            text-decoration: underline;
        }}
        .meta {{
            color: #94a3b8;
            font-size: 0.9em;
            margin: 12px 0;
        }}
        .score {{
            display: inline-block;
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        .sector-tags {{
            margin: 12px 0;
        }}
        .sector-tag {{
            display: inline-block;
            background: #334155;
            color: #38bdf8;
            padding: 5px 12px;
            border-radius: 15px;
            margin: 3px 5px 3px 0;
            font-size: 0.85em;
            border: 1px solid #38bdf8;
        }}
        .org-box {{
            background: #0f172a;
            padding: 10px 15px;
            border-left: 3px solid #f59e0b;
            margin: 12px 0;
            font-size: 0.9em;
            border-radius: 5px;
        }}
        .funding-badge {{
            background: #f59e0b;
            color: #000;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        .summary {{
            color: #cbd5e1;
            line-height: 1.7;
            margin-top: 15px;
        }}
        .sector-list {{
            columns: 2;
            margin: 20px 0;
        }}
        .sector-item {{
            break-inside: avoid;
            padding: 8px;
            margin: 5px 0;
            background: #334155;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <h1>🔬 Deep Tech Innovation Report</h1>
    
    <div class="stats-grid">
        <div class="stat-card">
            <h3>Total Articles</h3>
            <div class="number">{len(self.deep_tech_articles)}</div>
        </div>
        <div class="stat-card">
            <h3>Sectors Covered</h3>
            <div class="number">{len(sector_counts)}</div>
        </div>
        <div class="stat-card">
            <h3>Generated</h3>
            <div class="number" style="font-size: 1.2em;">{datetime.now().strftime('%b %d')}</div>
        </div>
    </div>
    
    <h2 style="color: #38bdf8; margin-top: 40px;">📊 Sector Distribution</h2>
    <div class="sector-list">
"""
        
        for sector, count in sector_counts.most_common():
            percentage = (count / len(self.deep_tech_articles)) * 100
            html += f'        <div class="sector-item">🏷️ {sector}: {count} ({percentage:.1f}%)</div>\n'
        
        html += """    </div>
    
    <h2 style="color: #38bdf8; margin-top: 40px;">📰 Latest Deep Tech News</h2>
"""
        
        for article in self.deep_tech_articles[:50]:
            sectors_html = ''.join([f'<span class="sector-tag">{s}</span>' 
                                   for s in article['sectors'].split(', ')])
            
            org_html = ''
            if article['organizations'] != 'N/A':
                org_html = f'<div class="org-box">🏢 {article["organizations"]}</div>'
            
            funding_html = ''
            if article['funding_stage'] != 'N/A':
                funding_html = f' <span class="funding-badge">💰 {article["funding_stage"]}</span>'
            
            html += f"""
    <div class="article">
        <h2><a href="{article['link']}" target="_blank">{article['title']}</a></h2>
        <div class="meta">
            <span class="score">Score: {article['relevance_score']}/100</span>
            📅 {article['published_date'][:10]} | 
            📰 {article['feed_name']}
            {' | ✍️ ' + article['author'] if article['author'] != 'N/A' else ''}
            {funding_html}
        </div>
        <div class="sector-tags">
            {sectors_html}
        </div>
        {org_html}
        <div class="summary">{article['summary'][:600]}{'...' if len(article['summary']) > 600 else ''}</div>
    </div>
"""
        
        html += """
    <footer style="margin-top: 50px; padding-top: 20px; border-top: 2px solid #334155; text-align: center; color: #64748b;">
        <p>Deep Tech Tracker • Monitoring innovation across quantum, biotech, space, robotics, and more</p>
    </footer>
</body>
</html>
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"📱 Generated HTML report: {filename}")
    
    def export_sector_report(self, filename: str = "deep_tech_by_sector.json"):
        """Export articles grouped by sector"""
        sectors_data = {}
        
        for sector in self.SECTORS.keys():
            sector_articles = [
                article for article in self.deep_tech_articles
                if sector in article['sectors']
            ]
            if sector_articles:
                sectors_data[sector] = {
                    'count': len(sector_articles),
                    'articles': sector_articles[:20]  # Top 20 per sector
                }
        
        data = {
            'generated_at': datetime.now().isoformat(),
            'sectors': sectors_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"📑 Exported sector breakdown to {filename}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Track Deep Tech innovations")
    parser.add_argument('-f', '--feeds-file', default='deep_tech_feeds.txt',
                       help='File containing RSS feed URLs')
    parser.add_argument('-d', '--days', type=int, default=7,
                       help='Number of days back to search (default: 7)')
    parser.add_argument('-s', '--score', type=int, default=20,
                       help='Minimum relevance score 0-100 (default: 20)')
    parser.add_argument('-o', '--output', choices=['json', 'csv', 'html', 'all'],
                       default='all', help='Output format')
    parser.add_argument('--sector', help='Filter by specific sector')
    
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
    tracker = DeepTechTracker()
    tracker.scrape_deep_tech(feed_urls, days_back=args.days, 
                            min_relevance_score=args.score)
    
    # Filter by sector if specified
    if args.sector:
        tracker.deep_tech_articles = [
            article for article in tracker.deep_tech_articles
            if args.sector.lower() in article['sectors'].lower()
        ]
        print(f"\n🏷️  Filtered to {len(tracker.deep_tech_articles)} articles in '{args.sector}' sector")
    
    # Display results
    tracker.display_summary()
    
    # Export
    if args.output in ['json', 'all']:
        tracker.export_to_json()
        tracker.export_sector_report()
    if args.output in ['csv', 'all']:
        tracker.export_to_csv()
    if args.output in ['html', 'all']:
        tracker.export_html_report()


if __name__ == "__main__":
    main()
