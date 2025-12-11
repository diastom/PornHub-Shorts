"""
Multi-Site Download Example - RedLight API

This example demonstrates advanced multi-site download patterns including:
- Mixed site batch downloads
- Site-specific organization
- Error handling across sites
- Progress tracking
"""

from RedLight import (
    BatchDownloader,
    SiteRegistry,
    DownloadVideo,
    GetVideoInfo
)
from pathlib import Path
import time


def example_mixed_batch_download():
    """Download videos from multiple sites in one batch"""
    
    print("="*60)
    print("Example 1: Mixed Site Batch Download")
    print("="*60)
    
    # Mix URLs from all supported sites
    urls = [
        "https://www.pornhub.com/view_video.php?viewkey=xxxxx",
        "https://www.eporner.com/video-xxxxx/title",
        "https://spankbang.com/xxxxx/video/title",
        "https://www.xvideos.com/video.xxxxx/title",
        "https://xhamster.com/videos/video-title-xxxxx",
        "https://www.xnxx.com/video-xxxxx/title"
    ]
    
    # RedLight automatically handles all sites
    downloader = BatchDownloader(
        concurrent=True,
        max_workers=4,
        quality="720"
    )
    
    downloader.AddUrls(urls)
    
    print(f"Downloading {len(urls)} videos from multiple sites...\n")
    
    # Track progress
    completed = []
    failed = []
    
    def on_complete(url, path):
        completed.append((url, path))
        print(f"✓ {Path(path).name}")
    
    def on_error(url, error):
        failed.append((url, error))
        print(f"✗ {url[:50]}... - {error}")
    
    results = downloader.DownloadAll(
        on_complete=on_complete,
        on_error=on_error
    )
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Success: {len(completed)}, Failed: {len(failed)}")
    print("="*60)


def example_organized_downloads():
    """Download and organize videos by site"""
    
    print("\n" + "="*60)
    print("Example 2: Organized Multi-Site Downloads")
    print("="*60)
    
    urls = [
        "https://www.pornhub.com/view_video.php?viewkey=xxxxx",
        "https://www.eporner.com/video-xxxxx/title",
        "https://spankbang.com/xxxxx/video/title",
        "https://www.xvideos.com/video.xxxxx/title",
        "https://xhamster.com/videos/video-title-xxxxx",
        "https://www.xnxx.com/video-xxxxx/title"
    ]
    
    registry = SiteRegistry()
    results = {"success": {}, "failed": []}
    
    for url in urls:
        # Detect site
        site_name = registry.detect_site(url)
        
        if not site_name:
            results["failed"].append((url, "Unsupported site"))
            print(f"✗ Unsupported: {url[:50]}...")
            continue
        
        # Create site-specific directory
        output_dir = f"./downloads/{site_name}"
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        try:
            # Get info
            print(f"\n[{site_name}] Processing...")
            info = GetVideoInfo(url)
            print(f"  Title: {info['title'][:50]}...")
            
            # Download
            video_path = DownloadVideo(url, output_dir=output_dir, quality="720")
            
            if site_name not in results["success"]:
                results["success"][site_name] = []
            results["success"][site_name].append(video_path)
            
            print(f"  ✓ Saved to: {output_dir}/")
            
        except Exception as e:
            results["failed"].append((url, str(e)))
            print(f"  ✗ Error: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print("Organization Summary:")
    print("-"*60)
    for site, videos in results["success"].items():
        print(f"  {site}: {len(videos)} videos")
    if results["failed"]:
        print(f"  Failed: {len(results['failed'])}")
    print("="*60)
    
    print("\nFiles organized in:")
    print("  ./downloads/pornhub/")
    print("  ./downloads/eporner/")
    print("  ./downloads/spankbang/")
    print("  ./downloads/xvideos/")
    print("  ./downloads/xhamster/")
    print("  ./downloads/xnxx/")
    
    return results


def example_site_specific_downloaders():
    """Use site-specific downloaders for advanced control"""
    
    print("\n" + "="*60)
    print("Example 3: Site-Specific Downloaders")
    print("="*60)
    
    from RedLight import (
        PornHubDownloader,
        EpornerDownloader,
        SpankBangDownloader,
        XVideosDownloader,
        XHamsterDownloader,
        XNXXDownloader
    )
    
    # PornHub downloader
    print("\n[PornHub] HLS Streaming")
    ph = PornHubDownloader(output_dir="./downloads/pornhub")
    print("  ✓ Configured for HLS streaming downloads")
    
    # Eporner downloader
    print("\n[Eporner] Ultra-Fast aria2c")
    ep = EpornerDownloader(output_dir="./downloads/eporner")
    print("  ✓ Configured for aria2c downloads")
    
    # Spankbang downloader
    print("\n[Spankbang] Hybrid Delivery")
    sb = SpankBangDownloader(output_dir="./downloads/spankbang")
    print("  ✓ Configured for hybrid MP4/HLS downloads")
    
    # XVideos downloader
    print("\n[XVideos] Intelligent Fallback")
    xv = XVideosDownloader(output_dir="./downloads/xvideos")
    print("  ✓ Configured for MP4/HLS fallback")
    
    print("\n[xHamster] HLS Multi-Quality")
    xh = XHamsterDownloader(output_dir="./downloads/xhamster")
    print("  ✓ Configured for HLS streaming with geo-fallback")
    
    print("\n[XNXX] Multi-Quality MP4/HLS")
    xn = XNXXDownloader(output_dir="./downloads/xnxx")
    print("  ✓ Configured for MP4/HLS downloads")
    
    print("\nEach downloader is optimized for its specific site!")


def example_error_handling():
    """Robust error handling for multi-site downloads"""
    
    print("\n" + "="*60)
    print("Example 4: Error Handling")
    print("="*60)
    
    urls = [
        "https://www.pornhub.com/view_video.php?viewkey=valid",
        "https://www.eporner.com/video-xxxxx/title",
        "https://unsupported-site.com/video",  # This will fail
        "https://www.xvideos.com/video.xxxxx/title"
    ]
    
    registry = SiteRegistry()
    
    for url in urls:
        site_name = registry.detect_site(url)
        
        if not site_name:
            print(f"✗ [{url.split('/')[2]}] Unsupported site")
            continue
        
        try:
            print(f"\n[{site_name}] Attempting download...")
            
            # Download with error handling
            video_path = DownloadVideo(url, quality="720")
            
            # Verify download
            if Path(video_path).exists():
                file_size = Path(video_path).stat().st_size / (1024 * 1024)  # MB
                print(f"  ✓ Success: {file_size:.2f}MB")
            else:
                print(f"  ✗ File not found after download")
                
        except Exception as e:
            print(f"  ✗ Error: {type(e).__name__}: {e}")
            print(f"     Skipping to next video...")


def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║       RedLight DL - Multi-Site Download Examples           ║
╚════════════════════════════════════════════════════════════╝

This example demonstrates:
• Mixed site batch downloads
• Site-specific organization
• Site-specific downloaders
• Comprehensive error handling

Supported sites: PornHub, Eporner, Spankbang, XVideos, xHamster, XNXX
""")
    
    # Run examples
    # Example 1: Mixed batch (commented - requires valid URLs)
    # example_mixed_batch_download()
    
    # Example 2: Organized downloads (commented - requires valid URLs)
    # example_organized_downloads()
    
    # Example 3: Site-specific downloaders (safe to run)
    example_site_specific_downloaders()
    
    # Example 4: Error handling (commented - requires valid URLs)
    # example_error_handling()
    
    print("\n" + "="*60)
    print("✓ Examples complete!")
    print("="*60)
    print("\nNote: Uncomment the example functions in main() to test")
    print("with real URLs from supported sites.")


if __name__ == "__main__":
    main()
