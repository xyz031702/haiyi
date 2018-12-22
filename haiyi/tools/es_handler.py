from elasticsearch import Elasticsearch
from ssl import create_default_context
from elasticsearch.helpers import bulk
import logging

logger = logging.getLogger(__name__)


class ES_Conn(object):
    def __init__(self):
        self.es = None

    def conn(self, hosts, port, es_payload_limit, username=None, password=None, cert=None, **kwargs):
        if cert:
            context = create_default_context(cafile="path/to/cert.pem")
            self.es = Elasticsearch(
                hosts,
                http_auth=(username, password),
                scheme="https",
                port=port,
                ssl_context=context
            )
        elif username and password:
            self.es = Elasticsearch(
                hosts,
                http_auth=(username, password),
                scheme="https",
                port=port
            )
        else:
            self.es = Elasticsearch(
                hosts,
                scheme="http",
                port=port
            )
        self.es_params = kwargs
        if not self.es.ping():
            raise Exception('wrong_params_to_connect_es=%s' % locals())


def bulk_optimized(func):
    # https://qbox.io/blog/maximize-guide-elasticsearch-indexing-performance-part-2
    def func_wrapper(es: Elasticsearch, index, xls_file, generator, **kwargs):
        # es = kwargs['es']  # type:Elasticsearch
        # index = kwargs['index']
        payload = '{ "index": { "refresh_interval": "-1", "blocks": {"read_only_allow_delete": "false"}}, "translog.durability":"async"}'
        es.indices.put_settings(index=index, body=payload)
        result = func(es, index, xls_file, generator, **kwargs)
        es.indices.refresh()
        return result

    return func_wrapper


@bulk_optimized
def bulk_index(es: Elasticsearch, index, xls_file, generator, **kwargs):
    logger.info('bulk_index|index=%s', index)
    success, fail = bulk(es, generator(index, xls_file, **kwargs))
    return success, fail


def create_index(es: Elasticsearch, index):
    logger.info('create_index')
    index_exist = es.indices.exists(index)
    if not index_exist:
        try:
            r = es.indices.create(index=index)
            logger.info('create_index|result=%s', r)
            return r
        except Exception as e:
            return {'error': 'cannot_create_es_index|index=%s,error=%s' % (index, str(e))}
    logger.info('create_index|index=%s exists', index)
    return {}


def create_new_index(es: Elasticsearch, index):
    index_exist = es.indices.exists(index)
    if index_exist:
        es.indices.delete(index=index, ignore=[400, 404])
    r = es.indices.create(index=index)
    logger.info('create_index|index=%s, result=%s', index, r)
    return {}


def is_exist_index(es: Elasticsearch, index):
    return es.indices.exists(index)


def get_doc_count(es: Elasticsearch, index):
    return es.count(index).get('count', 0)
