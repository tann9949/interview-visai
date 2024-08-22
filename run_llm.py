import json
import logging
import os
from argparse import ArgumentParser, Namespace

from dotenv import load_dotenv

from package.llm import NewsLLMExtractor

if load_dotenv():
    logging.info(f".env file loaded")


def run_parser() -> Namespace:
    parser = ArgumentParser()

    parser.add_argument("--input-path", "-i", type=str, default="data/news.jsonl", help="path to scraped data")
    parser.add_argument("--output-path", "-o", type=str, default="data/news_processed.jsonl", help="path to processed output data")

    return parser.parse_args()


def read_news(input_path: str) -> list:
    with open(input_path, "r") as fp:
        news = [json.loads(_l) for _l in fp.readlines()]
    logging.info(f"Total of {len(news)} news loaded")
    return news


def save_output(output: list, output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(args.output_path, "w") as fp:
        for _n in output:
            fp.write(json.dumps(_n, ensure_ascii=False)+"\n")


def main(args: Namespace) -> None:
    news = read_news(args.input_path)
    llm = NewsLLMExtractor()

    output = llm.batch_extract(news)
    save_output(output, args.output_path)


if __name__ == "__main__":
    args = run_parser()
    main(args)
