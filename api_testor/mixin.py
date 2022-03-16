import requests
from django.views import generic


class TopicListMixin:

    @staticmethod
    def get_topic_list():
        return requests.get('http://127.0.0.1:8000/api/topic/').json()