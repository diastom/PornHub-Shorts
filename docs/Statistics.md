# 📊 Download Statistics

RedLight v1.0.14 provides comprehensive download analytics.

## Quick Start

```python
from RedLight import GetStatistics

stats = GetStatistics()

# Get summary
summary = stats.get_summary()
print(f"Total downloads: {summary['total_downloads']}")
print(f"Total size: {summary['total_size_formatted']}")

# Display dashboard
stats.display_dashboard()
```

## DownloadStatistics Class

### Methods

| Method | Description |
|--------|-------------|
| `get_summary()` | Overall statistics |
| `get_by_site()` | Stats grouped by site |
| `get_by_quality()` | Stats grouped by quality |
| `get_daily_counts(days=30)` | Daily download counts |
| `get_top_searches(limit=10)` | Most searched queries |
| `display_dashboard()` | Rich-formatted dashboard |
| `display_site_breakdown()` | Per-site table |
| `display_quality_chart()` | Quality distribution |
| `display_timeline()` | Download timeline |

### Summary Data

```python
stats = GetStatistics()
summary = stats.get_summary()

summary['total_downloads']      # Total count
summary['total_size']           # Bytes
summary['total_size_formatted'] # "1.5 GB"
summary['average_quality']      # Average quality
summary['favorite_site']        # Most used site
summary['favorite_quality']     # Most used quality
summary['downloads_today']      # Today's count
summary['downloads_this_week']  # This week
summary['downloads_this_month'] # This month
```

### Per-Site Statistics

```python
by_site = stats.get_by_site()

for site, data in by_site.items():
    print(f"{site}: {data['count']} downloads, {data['size_formatted']}")
```

### Quality Distribution

```python
by_quality = stats.get_by_quality()

for quality, data in by_quality.items():
    print(f"{quality}p: {data['count']} ({data['percentage']:.1f}%)")
```

## CLI Statistics Menu

Access via interactive mode → `6. View Statistics`:

```
📊 Statistics Menu
1. View Dashboard
2. Site Breakdown
3. Quality Distribution
4. Timeline (Last 30 Days)
5. Search Stats
6. Back
```

### Dashboard Output

```
╭────────────────── Statistics Dashboard ──────────────────╮
│                                                          │
│  Total Downloads: 142        Total Size: 15.3 GB        │
│  Favorite Site:   PornHub    Favorite Quality: 1080p    │
│                                                          │
│  Today: 5    This Week: 23    This Month: 89            │
│                                                          │
╰──────────────────────────────────────────────────────────╯
```

## Storage

Statistics are derived from the download history database:
```
~/.RedLight/downloads.db
```

## See Also

- [Download History](API.md#download-history)
- [API Functions](API.md)
