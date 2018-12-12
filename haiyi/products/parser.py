import xlrd
from haiyi.tools.es_handler import ES_Conn, bulk_index, create_new_index
import json
import jieba
from django.conf import settings
import os


def read_xls(index):
    xls_file = os.path.join(settings.BASE_DIR, settings.STATIC_URL, 'products11.23.xls')
    workbook = xlrd.open_workbook(xls_file, on_demand=True)
    worksheet = workbook.sheet_by_index(0)
    i = 2
    cell = worksheet.cell(i, 0)
    try:
        # yield temp_src
        while (cell):
            product_name = jieba.cut_for_search(worksheet.cell(i, 1).value)
            data = {
                '_index': index,
                '_type': 'doc',  # '_type' field is discouraged since ES 6.x, just use the 'doc' as default
                '_source': {
                    'model_id': worksheet.cell(i, 0).value,
                    'name': ' '.join(product_name),
                    'real_name': worksheet.cell(i, 1).value,
                    'quantity': worksheet.cell(i, 2).value,
                    'price_3w': worksheet.cell(i, 3).value,
                    'price_1w': worksheet.cell(i, 4).value,
                    'price_3k': worksheet.cell(i, 5).value,
                    'price_retail': worksheet.cell(i, 6).value,
                },
                '_id': worksheet.cell(i, 0).value,
                'doc_as_upsert': True,
                '_op_type': 'index'
            }
            yield data
            i += 1
            cell = worksheet.cell(i, 0)
    except Exception as e:
        print(f'exception:{e}')


es = ES_Conn()
es.conn(hosts=['localhost', 'elasticsearch_haiyi'], port=9200, es_payload_limit=100)


def index_docs():
    index = 'haiyi_es'
    result = create_new_index(es.es, index)
    print(result)
    succ, fail = bulk_index(es=es.es, index=index, generator=read_xls)
    print(succ, fail)


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
    for hit in res.get('hits',{}).get('hits'):
        src = hit['_source']
        docs.append(
            {
                '商品': src['real_name'],
                '编号': src['model_id'],
                '库存': src['quantity'],
                '3万价格': src['price_3w'],
                '1万价格': src['price_1w'],
                '3千价格': src['price_3k'],
                '零售价格': src['price_retail'],
            }
        )
    return docs


# index_docs()
# search('美丽工匠')


'''
>>> search('美丽')
keyword=%s 美丽
{'took': 12, 'timed_out': False, '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0}, 'hits': {'total': 206, 'max_score': 6.4444027, 'hits': [{'_index': 'haiyi_es', '_type': 'doc', '_id': '07.01.001.0.68', '_score': 6.4444027, '_source': {'model_id': '07.01.001.0.68', 'name': '美丽 工匠 粉扑 收纳 架', 'quantity': '9', 'price_3w': '8.00', 'price_1w': '9.00', 'price_3k': '10.00', 'price_retail': '12.00'}}, {'_index': 'haiyi_es', '_type': 'doc', '_id': '02.02.005.003', '_score': 6.1840105, '_source': {'model_id': '02.02.005.003', 'name': 'Lancome 兰蔻 美丽 人生 香水 set', 'quantity': '0', 'price_3w': '398.00', 'price_1w': '398.00', 'price_3k': '0.00', 'price_retail': '498.00'}}, {'_index': 'haiyi_es', '_type': 'doc', '_id': '07.01.001.004', '_score': 6.128104, '_source': {'model_id': '07.01.001.004', 'name': '美丽 工匠   美容 洁 面巾   100 抽   （ 一般 贸易 ）', 'quantity': '6', 'price_3w': '16.00', 'price_1w': '17.00', 'price_3k': '18.00', 'price_retail': '19.00'}}, {'_index': 'haiyi_es', '_type': 'doc', '_id': '07.01.001.014', '_score': 5.5795836, '_source': {'model_id': '07.01.001.014', 'name': '美丽 工匠   沐浴 手套   白色 （ 一般 贸易 ）', 'quantity': '6', 'price_3w': '7.50', 'price_1w': '8.00', 'price_3k': '9.00', 'price_retail': '12.00'}}, {'_index': 'haiyi_es', '_type': 'doc', '_id': '01.02.101.066', '_score': 5.577439, '_source': {'model_id': '01.02.101.066', 'name': '欧缇丽 葡萄 葡萄籽 美白 喷雾 200ml', 'quantity': '28', 'price_3w': '78.00', 'price_1w': '80.00', 'price_3k': '90.00', 'price_retail': '108.00'}}, {'_index': 'haiyi_es', '_type': 'doc', '_id': '07.01.001.036', '_score': 5.3903213, '_source': {'model_id': '07.01.001.036', 'name': '美丽 工匠 粉扑 套装 （ 3 只装 ） （ 一般 贸易 ）', 'quantity': '13', 'price_3w': '25.00', 'price_1w': '26.00', 'price_3k': '30.00', 'price_retail': '36.00'}}, {'_index': 'haiyi_es', '_type': 'doc', '_id': '07.01.001.030', '_score': 5.3814845, '_source': {'model_id': '07.01.001.030', 'name': '美丽 工匠   沐浴 手套   粉色 （ 一般 贸易 ）', 'quantity': '0', 'price_3w': '7.50', 'price_1w': '8.00', 'price_3k': '9.00', 'price_retail': '18.00'}}, {'_index': 'haiyi_es', '_type': 'doc', '_id': '07.01.001.008', '_score': 5.3358216, '_source': {'model_id': '07.01.001.008', 'name': '美丽 工匠   完美 电 睫毛 眼睫毛 夹   银色   新款 （ 一般 贸易 ）', 'quantity': '39', 'price_3w': '7.00', 'price_1w': '8.00', 'price_3k': '9.00', 'price_retail': '12.00'}}, {'_index': 'haiyi_es', '_type': 'doc', '_id': '07.01.001.006', '_score': 5.2134776, '_source': {'model_id': '07.01.001.006', 'name': '美丽 工匠   兔 耳朵 干发帽   粉色 （ 一般 贸易 ）', 'quantity': '7', 'price_3w': '15.00', 'price_1w': '16.00', 'price_3k': '17.00', 'price_retail': '20.00'}}, {'_index': 'haiyi_es', '_type': 'doc', '_id': '07.01.001.010', '_score': 5.2134776, '_source': {'model_id': '07.01.001.010', 'name': '美丽 工匠   猫 耳朵 束发 带   粉色 （ 一般 贸易 ）', 'quantity': '0', 'price_3w': '6.00', 'price_1w': '6.50', 'price_3k': '7.00', 'price_retail': '16.00'}}]}}'''
