import logging
import time

from dotenv import load_dotenv

load_dotenv()

import statistics
from collections import Counter
from datetime import datetime

from mongo_client import reviews_collection
from app_store import AppStore
from ml_analyser import CommentAnalyser
from llm import LLM

llm = LLM()
comment_analyser = CommentAnalyser()
store = AppStore()


def get_tasks():
    return list(reviews_collection.find({
        'status': 'created'
    }))


def set_status_task(task_id: str):
    return reviews_collection.update_one(
        {'taskId': task_id},
        {'$set': {
            'status': 'done'
        }}
    )


def get_reviews(app_id: int, pages: int = 2) -> list:
    raw_reviews = []
    for page in range(1, pages+1):
        reviews = store.get_reviews(app_id=app_id, page=page)
        if not reviews:
            break
        raw_reviews.extend(store.parse_reviews(reviews))
    return raw_reviews


def evaluate_reviews(reviews: list) -> list:
    review_text_only = [r.get('content', '') for r in reviews]
    evaluated_comments = comment_analyser.analyse_comments(
        comments=review_text_only
    )
    full_reviews = []
    for review, score in zip(reviews, evaluated_comments):
        full_reviews.append({**review, **score})
    return full_reviews


def get_user_prompt(reviews: list):
    return f"""
We have up to {len(reviews)} negative reviews about our app, each separated by a newline character (\\n).
Please analyze all reviews collectively and do the following:

1. Identify the main recurring issues and common themes mentioned by users.
2. Determine the possible causes of each major issue (e.g., technical limitations, poor UX, missing functionality, etc.).
3. Propose concrete improvements or solutions for each major issue, focusing on those that can be implemented quickly within a limited budget.
4. Prioritize each suggested improvement (e.g., high, medium, or low priority) based on its potential impact on user satisfaction and implementation complexity.

Filter through all reviews and present your findings in a summarized format, without necessarily quoting each review verbatim.

List of negative reviews (separated by \\n):
<reviews>
{'\n'.join(reviews)}
</reviews>
"""

def get_llm_analyse(reviews: list) -> str:
    negative_comments = [
        r.get('content')
        for r in reviews
        if r.get('tone') == 'negative'
    ]
    return llm.generate_response(
        user_prompt=get_user_prompt(reviews=negative_comments),
    )


def get_basic_stats(reviews: list):
    # потрібно використовувати лейбли, бо інколи може не бути якихось оцінок
    rating_labels = ['5', '4', '3', '2', '1']
    rating = [int(r.get('rating', 0)) for r in reviews]
    sentiments = [r.get('tone') for r in reviews]
    # середнє та медіана
    mean = statistics.mean(rating)
    median = statistics.median(rating)
    # відсоткове співвідношення
    total_count = len(rating)
    count_rating = Counter(rating)
    percentages = {key: round(count_rating.get(int(key), 0) / total_count * 100, 2) for key in rating_labels}
    # відсоткове співвідношення типу коментарів
    sentm_total_count = len(sentiments)
    sentm_count_rating = Counter(sentiments)
    sentimental_perc = {k: round(v / sentm_total_count * 100, 2) for k, v in sentm_count_rating.items()}
    return {
        'mean': mean,
        'median': median,
        # доводиться ключ переводити в стрінг для правильного збереження в БД
        'sentimentalPercent': {str(key): value for key, value in sentimental_perc.items()},
        'percentCount': percentages
    }

def save_data(
        task_id: str,
        basic_stats: dict,
        raw_reviews: list,
        evaluated_reviews: list,
        llm_insight: str
):
    return reviews_collection.update_one(
        {'taskId': task_id},
        {'$set': {
            'basicStats': basic_stats,
            'rawReviews': raw_reviews,
            'evaluatedReviews': evaluated_reviews,
            'llmInsight': llm_insight,
            'reviewDate': datetime.now()
        }}
    )

def main():
    while True:
        try:
            tasks = get_tasks()

            for task in tasks:
                app_id = task.get('appId')
                reviews = get_reviews(app_id=app_id)
                if not reviews:
                    set_status_task(task_id=task.get('taskid'))
                    continue
                evaluated_reviews = evaluate_reviews(reviews=reviews)
                llm_insight = get_llm_analyse(reviews=evaluated_reviews)
                basic_stats = get_basic_stats(reviews=evaluated_reviews)
                save_data(
                    task_id=task.get('taskId'),
                    basic_stats=basic_stats,
                    raw_reviews=reviews,
                    evaluated_reviews=evaluated_reviews,
                    llm_insight=llm_insight
                )
                set_status_task(task_id=task.get('taskId'))
        except Exception as e:
            logging.error(f'Task processing error, {e}')
        finally:
            logging.info('There are no new tasks. Waiting 30 sec...')
            time.sleep(30)

if __name__ == '__main__':
    main()
