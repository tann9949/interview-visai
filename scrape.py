import json
import logging
import os
from argparse import ArgumentParser, Namespace

from package.scraper import ThaiRathScraper

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def run_parser() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--output-path", "-o", type=str, default="data/news.jsonl", help="Output path to scraped news")
    parser.add_argument("--amt", "-a", type=int, default=1_000, help="Number of scraped documents")
    return parser.parse_args()

def main(args: Namespace) -> None:
    # scrape
    scraper = ThaiRathScraper()
    news = scraper.scrape(amt=args.amt)

    # save
    os.makedirs(os.path.dirname(args.output_path), exist_ok=True)
    with open(args.output_path, "w") as fp:
        for _n in news:
            fp.write(json.dumps(_n)+"\n")


if __name__ == "__main__":
    args = run_parser()
    main(args)
