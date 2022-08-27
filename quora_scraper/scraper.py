import dataclasses
import datetime
import requests
import json
from math import ceil

_QUORA_HASH='5c3c2040ed58afdb13717a7b62eba4a60fb3c70545f06cf2699a50581e42db17'
_QUORA_FORMKEY='699fcc4d2c4cebf1c5258ef316fb7666'
_QUORA_BSTRICT='q6V1AnQMyWyLkyBaQzKMPw=='

@dataclasses.dataclass
class Answer:
    id: str
    date: datetime.datetime
    content: str

class QuoraSearchScrapper:
    def __init__(self, key=_QUORA_FORMKEY, cookie=_QUORA_BSTRICT):
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
                "hash": _QUORA_HASH
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