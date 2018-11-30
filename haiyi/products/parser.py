import xlrd
from haiyi.tools.es_handler import ES_Conn, bulk_index, create_new_index
import json
#
# temp_src = {
#     '_index': 'haiyi_es',
#     '_type': 'doc',  # '_type' field is discouraged since ES 6.x, just use the 'doc' as default
#     '_source': {'model_id': '123213',
#                 'name': 'watch',
#                 'quantity': 10,
#                 'price_3w': 1,
#                 'price_1w': 2,
#                 'price_3k': 3,
#                 'price_retail': 4,
#                 },
#     '_id': 123321,
#     'doc_as_upsert': True,
#     '_op_type': 'index'
# }


def read_xls(index):
    workbook = xlrd.open_workbook('/Users/dings/Downloads/商品信息11.23.xls', on_demand=True)
    worksheet = workbook.sheet_by_index(0)
    i = 2
    cell = worksheet.cell(i, 0)
    try:
        #yield temp_src
        while (cell):
            data = {
                '_index': index,
                '_type': 'doc',  # '_type' field is discouraged since ES 6.x, just use the 'doc' as default
                '_source': {
                    'model_id': worksheet.cell(i, 0).value,
                    'name': worksheet.cell(i, 1).value,
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
es.conn(hosts='localhost', port=9200, es_payload_limit=100)


def index_docs():
    index = 'haiyi_es'
    result = create_new_index(es.es, index)
    print(result)
    # docs=[]
    # for p in read_xls():
    #     docs.append(p)
    succ, fail = bulk_index(es=es.es, index=index, generator=read_xls)
    print(succ, fail)


def search(message):
    es_request = []
    # req_head = json.dumps({'index': 'haiyi_es'}) + ' \n'
    req_body = {'query': {'match': {'name':message}}}
    # es_request.append(req_head)
    es_request.append(json.dumps(req_body) + ' \n')
    res = es.es.search(index='haiyi_es', body=req_body, request_timeout=120)
    print(res)


#index_docs()
search('美丽工匠')
