import concurrent.futures
from typing import List, Dict, Optional, Callable, Any
from .sites import SiteRegistry


class MultiSiteSearch:
    
    def __init__(self):
        self.registry = SiteRegistry()
    
    def search_all(
        self,
        query: str,
        page: int = 1,
        sort_by: str = "relevance",
        duration: Optional[str] = None,
        on_site_complete: Optional[Callable[[str, int], None]] = None
    ) -> List[Dict[str, Any]]:
        all_searchers = self.registry.get_all_searchers()
        all_results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(all_searchers)) as executor:
            future_to_site = {
                executor.submit(
                    self._search_single_site,
                    searcher,
                    query,
                    page,
                    sort_by,
                    duration
                ): site_name
                for site_name, searcher in all_searchers.items()
            }
            
            for future in concurrent.futures.as_completed(future_to_site):
                site_name = future_to_site[future]
                try:
                    results = future.result()
                    all_results.extend(results)
                    
                    if on_site_complete:
                        on_site_complete(site_name, len(results))
                except Exception:
                    if on_site_complete:
                        on_site_complete(site_name, 0)
        
        return all_results
    
    def _search_single_site(
        self,
        searcher,
        query: str,
        page: int,
        sort_by: str,
        duration: Optional[str]
    ) -> List[Dict[str, Any]]:

        try:
            site_sort = sort_by
            if sort_by == "views" and "mostviewed" in searcher.get_search_filters().get("sort_by", []):
                site_sort = "mostviewed"
            
            return searcher.search(
                query=query,
                page=page,
                sort_by=site_sort,
                duration=duration
            )
        except Exception:
            return []
    
    def get_supported_sites(self) -> List[str]:

        sites = self.registry.get_all_sites()
        return [site["name"] for site in sites]
