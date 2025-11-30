#!/usr/bin/env python3
"""
RSS Feed Scraper Tool
A comprehensive tool for scraping and parsing RSS feeds
"""

import feedparser
import requests
import json
import csv
from datetime import datetime
from typing import List, Dict, Optional
import argparse
from urllib.parse import urlparse


class RSSFeedScraper:
    """Main class for scraping RSS feeds"""
    
    def __init__(self, user_agent: str = "RSS-Feed-Scraper/1.0"):
        self.user_agent = user_agent
        self.feeds_data = []
    
    def fetch_feed(self, feed_url: str) -> Optional[feedparser.FeedParserDict]:
        """
        Fetch and parse an RSS feed from a URL
        
        Args:
            feed_url: URL of the RSS feed
            
        Returns:
            Parsed feed data or None if error occurs
        """
        try:
            # Set custom user agent
            headers = {'User-Agent': self.user_agent}
            response = requests.get(feed_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse the feed
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                print(f"Warning: Feed may be malformed ({feed_url})")
            
            return feed
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching feed {feed_url}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error parsing feed {feed_url}: {e}")
            return None
    
    def extract_feed_info(self, feed: feedparser.FeedParserDict) -> Dict:
        """
        Extract basic feed information
        
        Args:
            feed: Parsed feed data
            
        Returns:
            Dictionary with feed metadata
        """
        return {
            'title': feed.feed.get('title', 'N/A'),
            'link': feed.feed.get('link', 'N/A'),
            'description': feed.feed.get('description', 'N/A'),
            'language': feed.feed.get('language', 'N/A'),
            'updated': feed.feed.get('updated', 'N/A'),
            'total_entries': len(feed.entries)
        }
    
    def extract_entries(self, feed: feedparser.FeedParserDict, limit: Optional[int] = None) -> List[Dict]:
        """
        Extract entries from the feed
        
        Args:
            feed: Parsed feed data
            limit: Maximum number of entries to extract (None for all)
            
        Returns:
            List of dictionaries containing entry data
        """
        entries = []
        feed_entries = feed.entries[:limit] if limit else feed.entries
        
        for entry in feed_entries:
            entry_data = {
                'title': entry.get('title', 'N/A'),
                'link': entry.get('link', 'N/A'),
                'published': entry.get('published', entry.get('updated', 'N/A')),
                'author': entry.get('author', 'N/A'),
                'summary': entry.get('summary', entry.get('description', 'N/A')),
                'tags': ', '.join([tag.term for tag in entry.get('tags', [])]) if entry.get('tags') else 'N/A',
            }
            
            # Try to extract a clean published date
            if 'published_parsed' in entry and entry.published_parsed:
                entry_data['published_date'] = datetime(*entry.published_parsed[:6]).isoformat()
            elif 'updated_parsed' in entry and entry.updated_parsed:
                entry_data['published_date'] = datetime(*entry.updated_parsed[:6]).isoformat()
            else:
                entry_data['published_date'] = 'N/A'
            
            entries.append(entry_data)
        
        return entries
    
    def scrape_feed(self, feed_url: str, limit: Optional[int] = None) -> Optional[Dict]:
        """
        Complete scraping workflow for a single feed
        
        Args:
            feed_url: URL of the RSS feed
            limit: Maximum number of entries to extract
            
        Returns:
            Dictionary with feed info and entries
        """
        print(f"Scraping feed: {feed_url}")
        
        feed = self.fetch_feed(feed_url)
        if not feed:
            return None
        
        feed_info = self.extract_feed_info(feed)
        entries = self.extract_entries(feed, limit)
        
        result = {
            'feed_url': feed_url,
            'feed_info': feed_info,
            'entries': entries,
            'scraped_at': datetime.now().isoformat()
        }
        
        self.feeds_data.append(result)
        print(f"Successfully scraped {len(entries)} entries from {feed_info['title']}")
        
        return result
    
    def scrape_multiple_feeds(self, feed_urls: List[str], limit: Optional[int] = None) -> List[Dict]:
        """
        Scrape multiple RSS feeds
        
        Args:
            feed_urls: List of RSS feed URLs
            limit: Maximum number of entries per feed
            
        Returns:
            List of scraped feed data
        """
        results = []
        
        for url in feed_urls:
            result = self.scrape_feed(url, limit)
            if result:
                results.append(result)
        
        return results
    
    def export_to_json(self, filename: str = "rss_data.json"):
        """Export scraped data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.feeds_data, f, indent=2, ensure_ascii=False)
            print(f"Data exported to {filename}")
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
    
    def export_to_csv(self, filename: str = "rss_data.csv"):
        """Export scraped entries to CSV file"""
        try:
            if not self.feeds_data:
                print("No data to export")
                return
            
            # Flatten all entries from all feeds
            all_entries = []
            for feed_data in self.feeds_data:
                feed_title = feed_data['feed_info']['title']
                for entry in feed_data['entries']:
                    entry_copy = entry.copy()
                    entry_copy['feed_name'] = feed_title
                    entry_copy['feed_url'] = feed_data['feed_url']
                    all_entries.append(entry_copy)
            
            if not all_entries:
                print("No entries to export")
                return
            
            # Write to CSV
            keys = all_entries[0].keys()
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(all_entries)
            
            print(f"Data exported to {filename}")
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
    
    def display_summary(self):
        """Display a summary of scraped data"""
        if not self.feeds_data:
            print("No feeds scraped yet")
            return
        
        print("\n" + "="*60)
        print("RSS FEED SCRAPING SUMMARY")
        print("="*60)
        
        total_entries = 0
        for feed_data in self.feeds_data:
            feed_info = feed_data['feed_info']
            num_entries = len(feed_data['entries'])
            total_entries += num_entries
            
            print(f"\nFeed: {feed_info['title']}")
            print(f"  URL: {feed_data['feed_url']}")
            print(f"  Entries scraped: {num_entries}")
            print(f"  Last updated: {feed_info['updated']}")
        
        print(f"\n{'='*60}")
        print(f"Total feeds scraped: {len(self.feeds_data)}")
        print(f"Total entries: {total_entries}")
        print(f"{'='*60}\n")


def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(
        description="RSS Feed Scraper - Extract data from RSS feeds",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape a single feed
  python rss_scraper.py -u https://example.com/feed.xml
  
  # Scrape multiple feeds
  python rss_scraper.py -u https://feed1.com/rss https://feed2.com/rss
  
  # Limit entries and export to CSV
  python rss_scraper.py -u https://example.com/feed.xml -l 10 -o csv
  
  # Read feed URLs from file
  python rss_scraper.py -f feeds.txt -o json
        """
    )
    
    parser.add_argument('-u', '--urls', nargs='+', help='RSS feed URLs to scrape')
    parser.add_argument('-f', '--file', help='File containing RSS feed URLs (one per line)')
    parser.add_argument('-l', '--limit', type=int, help='Limit number of entries per feed')
    parser.add_argument('-o', '--output', choices=['json', 'csv', 'both'], 
                       default='json', help='Output format (default: json)')
    parser.add_argument('--json-file', default='rss_data.json', help='JSON output filename')
    parser.add_argument('--csv-file', default='rss_data.csv', help='CSV output filename')
    
    args = parser.parse_args()
    
    # Collect feed URLs
    feed_urls = []
    
    if args.urls:
        feed_urls.extend(args.urls)
    
    if args.file:
        try:
            with open(args.file, 'r') as f:
                file_urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                feed_urls.extend(file_urls)
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found")
            return
    
    if not feed_urls:
        parser.print_help()
        print("\nError: Please provide at least one feed URL using -u or -f")
        return
    
    # Create scraper and scrape feeds
    scraper = RSSFeedScraper()
    scraper.scrape_multiple_feeds(feed_urls, limit=args.limit)
    
    # Display summary
    scraper.display_summary()
    
    # Export data
    if args.output in ['json', 'both']:
        scraper.export_to_json(args.json_file)
    
    if args.output in ['csv', 'both']:
        scraper.export_to_csv(args.csv_file)


if __name__ == "__main__":
    main()
