import logging
from concurrent import futures
from datetime import datetime
from typing import Optional
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from tqdm.auto import tqdm

from typing_extensions import TypedDict


class NewsDict(TypedDict):
    url: str
    section: str
    topic: str
    title: str
    abstract: str
    content: str
    publish_time: str


# ENDPOINT = "https://api.thairath.co.th/tr-api/v1.1/thairath-online"


class ThaiRathScraper(object): #  NOTE: Just `class ThaiRathScraper:` could be fine
    # endpoint = ENDPOINT # Initial endpoint once the class is created
    def __init__(self, num_worker: int = 5) -> None:  # Default num_worker to 5 for better performance # NOTE: Type `None` here is not needed for __init__ function we can assume it returns None
        self.endpoint = "https://api.thairath.co.th/tr-api/v1.1/thairath-online" # FIXME: self.endpoint seems to be a constance we can initialize it once class is created.
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
        r.raise_for_status()  # Add Raise the connection error
        soup = BeautifulSoup(r.content, "html.parser")
        
        content = self.get_content_from_soup(soup)
        if content is None:
            logging.warning(f"News ({url}) error!")
        return content
    
    def scrape_page(
        self, 
        ts: Optional[int] = None, 
        amt: int = 100,
        page_no: Optional[int] = None
    ) -> list[NewsDict]:  # NOTE: Editted from List[Dict]
        if ts is None:
            ts = int(datetime.now().timestamp())
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
                            "url": item["canonical"],
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
    
    @staticmethod  # NOTE: If self is not used, replace this method with static method
    def _update_min_ts(news: list[NewsDict], offset: int = 1) -> int:
        ts = list(map(
            # lambda _n: datetime.strptime(_n["publish_time"], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp(), # NOTE: Time zone awareness. As the datetime is already in UTC, we can just use the `datetime.fromisoformat` function. This preserves timezone notation.
            lambda _n: datetime.fromisoformat(_n["publish_time"]).timestamp(),
            news
        ))
        ts = min(ts) - offset
        return ts

    @staticmethod
    def _update_min_ts_suggest_edit(news: list[NewsDict], offset: int = 1) -> int: # Suggest edit
        """Update minimum timestamp.

        NOTE: The format datetime in ISO8601 format.
        Therefore, they can be compared with in stirng format.

        Args:
            news (list[NewsDict]): _description_
            offset (int, optional): _description_. Defaults to 1.

        Returns:
            int: _description_
        """
        min_datetime = min(metadata["publish_time"] for metadata in news)
        min_ts = datetime.fromisoformat(min_datetime).timestamp()
        ts = min_ts - offset
        return ts
    
    def scrape(self, amt: int) -> list[NewsDict]:
        page_no = 1 # FIXME: Unnecessary variable declaration
        news = self.scrape_page(amt=amt, page_no=page_no) # FIXME: Can be `news = self.scrape_page(amt=amt, page_no=1)`
        page_no += 1 # FIXME: `page_no = 2`

        while len(news) < amt:
            ts = self._update_min_ts(news)
            news.extend(self.scrape_page(ts=ts, page_no=page_no))
            page_no += 1
        return news

# NOTE: Add Docstring for each function will be helpful for reader.
# NOTE: Use code linter will be helpful for align coding standards
# NOTE: Using TypeDict for Dict typing

def test_update_min_ts():
    samples = [
        {"publish_time": "2024-01-03T00:00:00.00Z"},
        {"publish_time": "2024-01-02T00:00:00.00Z"},
        {"publish_time": "2024-01-01T00:00:00.00Z"}
    ]

    assert ThaiRathScraper._update_min_ts(samples) == ThaiRathScraper._update_min_ts_suggest_edit(samples)

