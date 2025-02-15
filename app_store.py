import requests
import logging

logging.basicConfig(level='INFO')

class AppStore:
    BASE_URL = 'https://itunes.apple.com/us/rss/customerreviews'

    @classmethod
    def get_reviews(cls, app_id: int, page: int) -> dict:
        logging.info(f"Fetching AppStore reviews for app_id={app_id}, page={page}")

        try:
            url = f'{cls.BASE_URL}/page={page}/id={app_id}/sortBy=mostRecent/json'
            response = requests.get(url)
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Error fetching reviews: {e}")
            return {}

    @classmethod
    def _parse_single_review(cls, review: dict) -> dict:
        return {
            'userName': review.get('author', {}).get('name', {}).get('label', 'Unknown'),
            'reviewDate': review.get('updated', {}).get('label', 'Unknown'),
            'rating': review.get('im:rating', {}).get('label', 0),
            'title': review.get('title', {}).get('label', ""),
            'content': review.get('content', {}).get('label', "")
        }

    @classmethod
    def parse_reviews(cls, reviews_response: dict) -> list:
        reviews = reviews_response.get('feed', {}).get('entry')

        if not reviews:
            logging.error(f"No reviews found in response")
            return []

        return [
            cls._parse_single_review(r)
            for r in reviews
        ]
