import logging
from concurrent import futures
from datetime import datetime
from typing import Optional, List, Dict

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from tqdm.auto import tqdm


class ThaiRathScraper(object):
    
    def __init__(self, num_worker: int = 5) -> None:  # Default num_worker to 5 for better performance
        self.endpoint = "https://api.thairath.co.th/tr-api/v1.1/thairath-online"
        self.num_worker = num_worker
        
    def load_more(
        self, 
        limit: int, 
        ts: int = int(datetime.now().timestamp())
    ) -> list:
        endpoint = f"{self.endpoint}/loadmore?path=news/crime&ts={ts}&limit={limit}"
        r = requests.get(endpoint)
        
        if r.status_code == 200:
            return r.json()
        
        raise ConnectionError(r.text)
        
    def is_div_content_candidate(self, div: Tag) -> bool:
        if not isinstance(div, Tag):
            return False
        
        if "class" not in div.attrs:
            return False
        
        if any("article-content" in _c for _c in div.get("class")):
            return True
        return False
    
    def preprocess_raw_content(self, text: str) -> str:
        text = text.strip().replace("\xa0\xa0", "\n\n")
        text = text.replace("\xa0", " ")
        return text
        
    def get_content_from_soup(self, soup: BeautifulSoup) -> Optional[str]:
        candidates = [
            div for div in soup.find_all("div") 
            if self.is_div_content_candidate(div)
        ]

        if len(candidates) == 0:
            return None
        
        if len(candidates) != 1:
            logging.warning(f"Page got more than 1 candidate, selecting first element")
        candidate = candidates[0]
        
        if len(list(candidate.children)) != 1:
            logging.warning(f"article-content children got more than 1 child, selecting first element")
        content_div = list(next(candidates[0].children).children)[1:]
        
        content = "\n\n".join([
            self.preprocess_raw_content(_c.text)
            for _c in content_div])
        
        return content
        
    def get_news_content(self, url: str) -> Optional[str]:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        
        content = self.get_content_from_soup(soup)
        if content is None:
            logging.warning(f"News ({url}) error!")
        return content
    
    def scrape_page(
        self, 
        ts: int = int(datetime.now().timestamp()), 
        amt: int = 100,
        page_no: Optional[int] = None
    ) -> List[Dict]:
        page = self.load_more(amt, ts=ts)["items"]
        
        news = []
        with futures.ThreadPoolExecutor(max_workers=self.num_worker) as executor:
            future_to_url = {executor.submit(self.get_news_content, _item["canonical"]): _item for _item in page}
            
            desc = "scraping" if page_no is None else f"scraping page {page_no}"
            for future in tqdm(futures.as_completed(future_to_url), total=len(page), desc=desc, unit="news", leave=True):
                item = future_to_url[future]
                try:
                    content = future.result()
                    if content:
                        news.append({
                            "section": item["section"],
                            "topic": item["topic"],
                            "title": item["title"],
                            "abstract": item["abstract"],
                            "content": content,
                            "publish_time": item["publishTime"]
                        })
                except Exception as exc:
                    logging.warning(f"News ({item['canonical']}) generated an exception: {exc}")
        
        return news
    
    def _update_min_ts(self, news: list, offset: int = 1) -> int:
        ts = list(map(
            lambda _n: datetime.strptime(_n["publish_time"], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp(),
            news
        ))
        ts = min(ts) - offset
        return ts
    
    def scrape(self, amt: int) -> list:
        page_no = 1
        news = self.scrape_page(amt=amt, page_no=page_no)
        page_no += 1

        while len(news) < amt:
            ts = self._update_min_ts(news)
            news.extend(self.scrape_page(ts=ts, page_no=page_no))
            page_no += 1
        return news
