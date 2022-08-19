import dataclasses
import datetime
import requests
import json
from math import ceil

@dataclasses.dataclass
class Answer:
    id: str
    date: datetime.datetime
    content: str

class QuoraSearchScrapper:
    def __init__(self, key, cookie):
        self.url = 'https://id.quora.com/graphql/gql_para_POST?q=SearchResultsListQuery'
        self._cookies = { "m-b_strict": cookie }
        self._headers = {
            'Content-Type': 'application/json',
            'Quora-Formkey': key
        }

    def get_items(self, **kwargs):
        return self._transform(self._fetch_api(**kwargs))

    def _fetch_api(self, word, n_result=10):
        total = ceil(n_result/10)
        limit = 0
        offset = -1

        result = []

        for i in range(total):
            if n_result >= 10:
                limit += 10
            else:
                limit += n_result

            res = requests.post(self.url, headers=self._headers, cookies=self._cookies, data=self._get_body(word=word, limit=limit, offset=offset))

            json_data = res.json()
            raw_data = json_data['data']['searchConnection']['edges']

            result.extend(raw_data)

            n_result -= limit
            offset += 10

        return result

    def _get_body(self, word, limit = 10, offset = -1):
        body = {
            "queryName": "SearchResultsListQuery",
            "variables": {
                "query": word,
                "resultType": "answer",
                "time": "all_times",
                "first": limit,
                "after": str(offset)
            },
            "extensions": {
                "hash": "ae3901b756cc33934180d0f2920729b8b018e544a0781fc6d7dd928bf523559b"
            }
        }

        return json.dumps(body)

    def _transform(self, raw_data):
        for edge in raw_data:
            data = edge['node']['previewAnswer']

            content = json.loads(data['content'])

            text = ''

            for section in content['sections']:
                for span in section['spans']:
                    text = text + span['text'] + ' '

            s = data['creationTime']/1000000

            kwargs = {
                'id': data['id'],
                'date': datetime.datetime.fromtimestamp(s),
                'content': text
            }

            yield Answer(**kwargs)