"""
Batch Download Example - PHShorts API

This example demonstrates batch downloading with concurrent and 
sequential modes, progress tracking, and error handling.
"""

from PHShorts import BatchDownloader


def main():
    print("=== PHShorts Batch Download Example ===\n")
    
    # Example URLs (replace with actual URLs)
    urls = [
        "https://www.pornhub.com/view_video.php?viewkey=example1",
        "https://www.pornhub.com/view_video.php?viewkey=example2",
        "https://www.pornhub.com/view_video.php?viewkey=example3",
    ]
    
    # Example 1: Sequential Download
    print("📥 Example 1: Sequential Download\n")
    downloader = BatchDownloader(
        output_dir="./batch_sequential",
        concurrent=False,  # One-by-one
        quality="720"
    )
    
    downloader.AddUrls(urls)
    
    def progress_callback(completed, total, current_url):
        print(f"[{completed}/{total}] Processing: {current_url[:50]}...")
    
    def complete_callback(url, path):
        print(f"✓ Downloaded: {path}")
    
    def error_callback(url, error):
        print(f"✗ Failed {url}: {error}")
    
    results = downloader.DownloadAll(
        on_progress=progress_callback,
        on_complete=complete_callback,
        on_error=error_callback
    )
    
    print(f"\n✅ Sequential complete: {len(results)}/{len(urls)} videos\n")
    
    # Example 2: Concurrent Download
    print("\n📥 Example 2: Concurrent Download\n")
    downloader2 = BatchDownloader(
        output_dir="./batch_concurrent",
        concurrent=True,  # Simultaneous
        max_workers=3,  # Max 3 at a time
        quality="best"
    )
    
    downloader2.AddUrls(urls)
    
    results2 = downloader2.DownloadAll(
        on_progress=progress_callback,
        on_complete=complete_callback,
        on_error=error_callback
    )
    
    print(f"\n✅ Concurrent complete: {len(results2)}/{len(urls)} videos")
    
    # Example 3: Add URLs individually
    print("\n📥 Example 3: Building Queue Dynamically\n")
    downloader3 = BatchDownloader()
    
    for url in urls:
        downloader3.AddUrl(url)
        print(f"Added to queue: {url[:50]}...")
    
    print(f"\nQueue size: {downloader3.QueueSize}")
    
    # Clear queue example
    downloader3.ClearQueue()
    print(f"Queue cleared. New size: {downloader3.QueueSize}")


if __name__ == "__main__":
    main()
