import logging
import json
import time
from concurrent import futures

from openai import OpenAI, NOT_GIVEN
from tqdm.auto import tqdm

from .prompting import NewsExtractionPromptManager
from package.scraper import NewsDict
from typing_extensions import TypedDict, NotRequired


class ResponseType: # NOTE: Consider using enums
    TEXT = "text"
    JSON = "json"


class IncidentAddress(TypedDict):
    name: NotRequired[str]
    province: NotRequired[str]
    district: NotRequired[str]
    subdistrict: NotRequired[str]


class NewsPostProcessDict(NewsDict):
    crime_type: list[str]
    num_victims: int
    incident_datetime: str
    incident_address: dict


class NewsLLMExtractor(object):

    def __init__(
        self,
        seed: int = 42,
        temperature: float = 0.7,
        model_name: str = "gpt-4o-mini", # NOTE: Suggest parametizing this argument with `DEFAULT_MODEL_NAME``
        max_retry: int = 3, # NOTE: Also, parametizing this to a CONSTRANCE
    ) -> None:
        self.seed = seed
        self.temperature = temperature
        self.model_name = model_name
        self.max_retry = max_retry
        self.prompt_manger = NewsExtractionPromptManager()
        self._client = OpenAI()

    @property
    def system_prompt(self) -> str:
        return self.prompt_manger.system_prompt()
    
    def complete(
        self,
        prompt: str,
        response_format: str = ResponseType.TEXT
    ) -> dict | str:
        response_format = response_format.lower().strip()
        assert response_format in [ResponseType.JSON, ResponseType.TEXT], \
            f"Response format not supported, we only support json|text"
        
        retry = 0 # Consider using module retry(https://pypi.org/project/retry/)
        while True:
            try:
                completion = self._client.chat.completions.create(
                    model=self.model_name,
                    response_format=NOT_GIVEN if response_format == ResponseType.TEXT else { "type": "json_object" },
                    temperature=self.temperature,
                    seed=self.seed,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt},
                    ]
                )
                response = completion.choices[0].message.content

                if response_format == ResponseType.TEXT:
                    assert isinstance(response, str)
                elif response_format == ResponseType.JSON:
                    response = json.loads(response)
                    assert isinstance(response, dict)
                else: # NOTE: I don't think this is reachable according to line 43
                    raise ValueError(f"No response format found: {response_format}")
                
                # break if API calls successfully
                break
                
            # retry until max_retry reached
            except Exception as e: # NOTE: As mentioned at line 46
                response = None
                retry += 1
                
                if retry > self.max_retry:
                    raise e
                else:
                    time.sleep(3)
        
        return response
    
    def _get_extract_news_prompt(
        self,
        title: str,
        abstract: str,
        content: str
    ) -> str:
        return self.prompt_manger.extract_info(
            title=title,
            abstract=abstract,
            content=content
        )
    
    def postprocess_llm_response(self, response: dict) -> dict:
        # ensure AD
        d, m, y = response["incident_datetime"].split("/")
        y = int(y)
        if y > 2500:
            # AD
            y -= 543
        response["incident_datetime"] = f"{d}/{m}/{y}"
        return response

    
    def extract_news_info(self, news: dict, max_retry: int = 3) -> dict:
        n_retries = 0
        while True:
            try:
                response =  self.complete(
                    prompt=self._get_extract_news_prompt(
                        title=news["title"],
                        abstract=news["abstract"],
                        content=news["content"]
                    ),
                    response_format=ResponseType.JSON
                )
                response = self.postprocess_llm_response(response)
                break 
            except ValueError as e:
                n_retries += 1
                logging.warning(f"Can't validate output:\n{response}\nRetrying...")

                if n_retries > max_retry:
                    raise e
                
        news.update(response)
                
        return news
    
    def batch_extract(self, news: list, num_workers: int = 5) -> list:
        results = []

        # Define a worker function to handle each news item
        def extract_single_news(news_item):  # NOTE: Function inside function will be hard for unit tests, consider put it outside + Add output type hint
            try:
                return self.extract_news_info(news_item)
            except Exception as e:
                logging.error(f"Error processing news item {news_item.get('title', 'Unknown')}: {str(e)}")
                return None

        # Use ThreadPoolExecutor with specified num_workers
        with futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            # Submit all news items to be processed concurrently
            future_to_news = {executor.submit(extract_single_news, news_item): news_item for news_item in news}

            # Use tqdm to track the progress of completed futures
            for future in tqdm(futures.as_completed(future_to_news), total=len(news), desc="Extracting News Info"):  # Consider to add an option to disable `tqdm`. Otherwise, it will cause log unreadble once deployed.
                result = future.result()
                if result:
                    results.append(result)

        return results
