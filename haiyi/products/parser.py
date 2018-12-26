import xlrd
from haiyi.tools.es_handler import ES_Conn, bulk_index, create_new_index
import json
import jieba
from django.conf import settings
import os
import logging
from xml.sax.saxutils import escape

logger = logging.getLogger(__name__)


def read_xls(index, xls_file):
    # xls_file = os.path.join(settings.BASE_DIR, settings.UPLOAD_FOLDER, 'products11.23.xls')
    logging.info('read_xls|index=%s, xls_file=$s', index, xls_file)
    workbook = xlrd.open_workbook(xls_file, on_demand=True)
    worksheet = workbook.sheet_by_index(0)
    i = 2
    cell = worksheet.cell(i, 0)
    try:
        # yield temp_src
        while (cell):
            product_name = jieba.cut_for_search(worksheet.cell(i, 1).value)
            columns = [
                ('model_id', 'str'),
                ('real_name', 'str'),
                ('quantity', 'int'),
                ('real_cost', 'float'),
                ('market_cost', 'float'),
                ('price_3w', 'float'),
                ('price_1w', 'float'),
                ('price_3k', 'float'),
                ('price_retail', 'float'),
                ('hot', 'int'),
                ('difficulty', 'int')
            ]
            j = 0
            src = {}
            for c in columns:
                v = worksheet.cell(i, j).value
                if c[1] == 'str':
                    v = v.strip()
                elif c[1] == 'int':
                    v = int(v) if v else 0
                elif c[1] == 'float':
                    v = round(float(v), 2) if v else 0
                src[c[0]] = v
                j += 1
            src['name'] = ' '.join(product_name)

            data = {
                '_index': index,
                '_type': 'doc',  # '_type' field is discouraged since ES 6.x, just use the 'doc' as default
                '_source': src,
                '_id': worksheet.cell(i, 0).value,
                'doc_as_upsert': True,
                '_op_type': 'index'
            }
            yield data
            i += 1
            cell = worksheet.cell(i, 0)
    except Exception as e:
        logger.error(f'exception:{e}')
    finally:
        workbook.release_resources()


es = ES_Conn()
es.conn(hosts=['localhost', 'elasticsearch_haiyi'], port=9200, es_payload_limit=100)


def index_docs(xls_file):
    index = 'haiyi_es'
    result = create_new_index(es.es, index)
    print(result)
    succ, fail = bulk_index(es=es.es, index=index, xls_file=xls_file, generator=read_xls)
    logger.info('indexing|succ=%s, fail=%s', succ, fail)
    return succ


def search(message):
    message = ' '.join(jieba.cut_for_search(message))
    print('keyword=%s' % message)
    es_request = []
    # req_head = json.dumps({'index': 'haiyi_es'}) + ' \n'
    req_body = {'query': {'match': {'name': message}}}
    # es_request.append(req_head)
    es_request.append(json.dumps(req_body) + ' \n')
    res = es.es.search(index='haiyi_es', body=req_body, request_timeout=120)
    docs = []
    count = 0
    for hit in res.get('hits', {}).get('hits'):
        src = hit['_source']
        pname = escape(src['real_name'].strip())
        quality = int(src['quantity']) if src['quantity'] else 0
        str = f"<a href='www.baidu.com'>{pname}</a>\n" \
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
        if count >= 9:
            break
        docs.append(str)
    return docs

    # index_docs()
    # search('美丽工匠')
