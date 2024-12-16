# News Analysis ThaiRath
Repository for conducting a prelim analysis on Thai criminal news.

Here're the example files that is an output to the scripts:
- [news.jsonl](https://drive.google.com/file/d/1UazCCSs8ShHySmsl5HC7I6qfiA6AosfY/view?usp=sharing)
- [news_processed.jsonl](https://drive.google.com/file/d/1bv0FiG-JhYaLDrFjxYRbb6Va0m-kOPdA/view?usp=sharing)

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

## Editor
Camera man