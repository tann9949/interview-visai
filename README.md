# News Analysis ThaiRath
Repository for conducting a prelim analysis on Thai criminal news.

## Usage
### Scraping Criminal news
To scrape the news from Thairath, run the following command:
```bash
python scrape.py --output-path /path/to/save/output.jsonl --amt 1000
```
Here's the breakdown of each argument:
|Argument|type|desc|
|:-------|:--:|:--:|
|`--output-path`|`str`|Path to saved output|
|`--amt`|`int`|Amount to scrape|

### Run LLM to extract information
To extract additinoal information using the LLM, run the following command:
```bash
python scrape.py --input-path /path/to/scraped/news.jsonl --output-path /path/to/saved/file.jsonl
```

## License
This code is the property of [VISAI.AI Co., Ltd.](https://visai.ai/) and is provided for internal use only. Any distribution, copying, or modification of this code is strictly prohibited.

## Author
Skibidi Toilet
