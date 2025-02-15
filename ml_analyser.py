import os.path
import re
import html
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

if os.path.exists("./ml_models"):
    MODEL_PATH = "./ml_models"
else:
    MODEL_PATH = 'MarieAngeA13/Sentiment-Analysis-BERT'

class CommentAnalyser:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
        self.sentiment_pipeline = self._get_pipeline()

    def _get_pipeline(self, task: str = "sentiment-analysis", batch_size: int = 8) -> pipeline:
        return pipeline(
            task=task,
            # batch_size - кількість скільки буде за 1 раз оброблятися коментарів
            # по суті не критично але може бути вузьким місцем при великому потоці
            batch_size=batch_size,
            model=self.model,
            tokenizer=self.tokenizer
        )

    def analyse_comments(self, comments: list) -> list:
        cleaned_comments = self._input_comment_cleaner(comments=comments)
        results = self.sentiment_pipeline(cleaned_comments)
        if results:
            return [
                {'tone': r['label'], 'score': round(r['score'], 2)}
                for r in results
            ]
        return []

    @staticmethod
    def _input_comment_cleaner(comments: list[str]) -> list[str]:
        cleaned_comments = []
        for comment in comments:
            text = html.unescape(comment)
            text = re.sub(r"<.*?>", "", text)
            text = re.sub(r"@\w+", "", text)
            text = re.sub(r"#\w+", "", text)
            text = re.sub(r"[^\w\s’']", "", text)
            text = re.sub(r"\s+", " ", text).strip()
            cleaned_comments.append(text)
        return cleaned_comments
