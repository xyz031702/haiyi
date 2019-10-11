from elasticsearch import Elasticsearch
from ssl import create_default_context
from elasticsearch.helpers import bulk
import logging
import json
from xml.sax.saxutils import escape
from django.conf import settings

logger = logging.getLogger(__name__)


class ES_Conn(object):
    __instance = None

    def __init__(self):
        if not ES_Conn.__instance:
            ES_Conn.__instance = self.__conn(
                hosts=[settings.ES_HOST],
                port=settings.ES_PORT,
                es_payload_limit=100)
        self.__dict__['_ES_conn__instance'] = ES_Conn.__instance

    def __conn(self, hosts, port, es_payload_limit, username=None, password=None, cert=None, **kwargs):
        if cert:
            context = create_default_context(cafile="path/to/cert.pem")
            es = Elasticsearch(
                hosts,
                http_auth=(username, password),
                scheme="https",
                port=port,
                ssl_context=context
            )
        elif username and password:
            es = Elasticsearch(
                hosts,
                http_auth=(username, password),
                scheme="https",
                port=port
            )
        else:
            es = Elasticsearch(
                hosts,
                scheme="http",
                port=port
            )
        if not es.ping():
            raise Exception('wrong_params_to_connect_es=%s' % locals())
        return es

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, key, value):
        return setattr(self.__instance, key, value)


def bulk_optimized(func):
    # https://qbox.io/blog/maximize-guide-elasticsearch-indexing-performance-part-2
    def func_wrapper(index, xls_file, generator, **kwargs):
        # es = kwargs['es']  # type:Elasticsearch
        # index = kwargs['index']
        payload = '{ "index": { "refresh_interval": "-1", "blocks": {"read_only_allow_delete": "false"}}, "translog.durability":"async"}'
        es = ES_Conn()
        es.indices.put_settings(index=index, body=payload)
        result = func(es, index, xls_file, generator, **kwargs)
        es.indices.refresh()
        return result

    return func_wrapper


@bulk_optimized
def bulk_index(es, index, xls_file, generator, **kwargs):
    logger.info('bulk_index|index=%s', index)
    success, fail = bulk(es, generator(index, xls_file, **kwargs))
    return success, fail


def bulk_index_1(index, generator):
    es = ES_Conn()
    logger.info('bulk_index|index=%s', index)
    success, fail = bulk(es, generator())
    return success, fail


def create_new_index(index):
    es = ES_Conn()
    index_exist = es.indices.exists(index)
    if index_exist:
        es.indices.delete(index=index, ignore=[400, 404])
    r = es.indices.create(index=index)
    logger.info('create_index|index=%s, result=%s', index, r)
    return {}


def get_doc_count(index):
    return ES_Conn().count(index).get('count', 0)


def search(message):
    WECHAT_LIMIT = 2000
    print('keyword=%s' % message)
    es_request = []
    # req_head = json.dumps({'index': 'haiyi_es'}) + ' \n'
    req_body = {'query': {'match': {'name': message}}}
    # es_request.append(req_head)
    es_request.append(json.dumps(req_body) + ' \n')
    res = ES_Conn().search(index='haiyi_es', body=req_body, request_timeout=120)
    docs = []
    count = 0
    for hit in res.get('hits', {}).get('hits'):
        src = hit['_source']
        pname = escape(src['real_name'].strip())
        quality = int(src['quantity']) if src['quantity'] else 0
        content = f"<a href='www.baidu.com'>{pname}</a>\n" \
                  f"库存数量: {quality}\n" \
                  f"实际成本: {src['real_cost']}元\n" \
                  f"市场成本: {src['market_cost']}元\n" \
                  f"3w售价: {src['price_3w']}元\n" \
                  f"1w售价：{src['price_1w']}元\n" \
                  f"3k售价：{src['price_3k']}元\n" \
                  f"零售价格：{src['price_retail']}元\n" \
                  f"热卖程度：{src['hot']}\n" \
                  f"采购难度：{src['difficulty']}"
        count += 1
        if count >= 20:
            break
        docs.append(content)
    return docs



def dialog_search(keyword, index):
    print('dialog_match|keyword=%s' % keyword)
    es_request = []
    # req_head = json.dumps({'index': 'haiyi_es'}) + ' \n'
    req_body = {'query': {'match': {'question': keyword.strip()}}}
    # es_request.append(req_head)
    es_request.append(json.dumps(req_body) + ' \n')
    res = ES_Conn().search(index=index, body=req_body, request_timeout=120)
    docs = []
    count = 0
    return res.get('hits', {}).get('hits')
