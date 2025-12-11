"""
Multi-Site Search Example - RedLight API

This example demonstrates how to search across all supported sites
and download results.
"""

from RedLight import MultiSiteSearch, DownloadVideo
from pathlib import Path


def search_all_sites_example(query):
    """Search across all 6 sites simultaneously"""
    
    print("="*60)
    print(f"Searching for: '{query}'")
    print("="*60)
    
    # Create multi-site searcher
    searcher = MultiSiteSearch()
    
    # Get supported sites
    sites = searcher.get_supported_sites()
    print(f"Searching across {len(sites)} sites: {', '.join(sites)}\n")
    
    # Search all sites
    print("Searching...")
    results = searcher.search_all(query, page=1)
    
    print(f"\n✓ Found {len(results)} total results")
    
    # Group results by site
    by_site = {}
    for video in results:
        site = video['site']
        if site not in by_site:
            by_site[site] = []
        by_site[site].append(video)
    
    # Display results per site
    print("\nResults by site:")
    print("-"*60)
    for site, videos in by_site.items():
        print(f"\n{site}: {len(videos)} results")
        for i, v in enumerate(videos[:5], 1):  # Show top 5 from each
            print(f"  {i}. {v['title'][:50]}...")
            print(f"     Duration: {v.get('duration', 'N/A')} | Views: {v.get('views', 'N/A')}")
    
    return by_site


def download_top_from_each_site(results_by_site, max_per_site=1):
    """Download top N results from each site"""
    
    print("\n" + "="*60)
    print(f"Downloading top {max_per_site} from each site")
    print("="*60)
    
    downloaded = {}
    
    for site, videos in results_by_site.items():
        print(f"\n[{site}]")
        site_downloads = []
        
        for i, video in enumerate(videos[:max_per_site], 1):
            try:
                print(f"  {i}/{max_per_site} Downloading: {video['title'][:40]}...")
                
                # Create site-specific directory
                output_dir = f"./downloads/{site}"
                Path(output_dir).mkdir(parents=True, exist_ok=True)
                
                # Download
                video_path = DownloadVideo(
                    video['url'],
                    output_dir=output_dir,
                    quality="720"
                )
                
                site_downloads.append(video_path)
                print(f"      ✓ Saved: {Path(video_path).name}")
                
            except Exception as e:
                print(f"      ✗ Error: {e}")
        
        downloaded[site] = site_downloads
    
    # Summary
    print("\n" + "="*60)
    print("Download Summary:")
    print("-"*60)
    total =  0
    for site, videos in downloaded.items():
        count = len(videos)
        total += count
        print(f"  {site}: {count} videos")
    print(f"\nTotal: {total} videos downloaded")
    print("="*60)
    
    return downloaded


def interactive_search_and_download():
    """Interactive search and download"""
    
    print("\n" + "="*60)
    print("Interactive Multi-Site Search")
    print("="*60)
    
    while True:
        query = input("\nEnter search term (or 'quit' to exit): ")
        
        if query.lower() in ('quit', 'q', 'exit'):
            break
        
        if not query.strip():
            print("Please enter a search term")
            continue
        
        # Search
        results_by_site = search_all_sites_example(query)
        
        if not results_by_site:
            print("\nNo results found")
            continue
        
        # Ask if user wants to download
        download = input("\nDownload top result from each site? (y/n): ")
        
        if download.lower() in ('y', 'yes'):
            download_top_from_each_site(results_by_site, max_per_site=1)
    
    print("\n👋 Goodbye!")


def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║         RedLight DL - Multi-Site Search Example            ║
╚════════════════════════════════════════════════════════════╝
    
This example demonstrates:
1. Searching across all 6 supported sites simultaneously
2. Grouping and displaying results by site
3. Downloading top results from each site
4. Organizing downloads by site in separate folders

Supported sites: PornHub, Eporner, Spankbang, XVideos, xHamster, XNXX
    """)
    
    # Example 1: Simple search
    print("Example 1: Simple Multi-Site Search")
    print("-"*60)
    query = "sample search"  # Replace with your search term
    results = search_all_sites_example(query)
    
    # Example 2: Downloaded top results (commented out by default)
    # Uncomment the line below to download
    # download_top_from_each_site(results, max_per_site=2)
    
    # Example 3: Interactive mode (commented out by default)
    # Uncomment the line below for interactive searching
    # interactive_search_and_download()
    
    print("\n✓ Example complete!")


if __name__ == "__main__":
    main()
