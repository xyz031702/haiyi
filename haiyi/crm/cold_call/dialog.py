from yaml import safe_load
import json
import uuid
from haiyi.tools.es_handler import dialog_search
from haiyi.tools.es_handler import bulk_index_1, create_new_index
import logging
import re
import openpyxl

logger = logging.getLogger(__name__)

customers = {}


def get_index():
    return "es_dialog_script"


def init():
    result = create_new_index(get_index())
    print(result)
    bulk_index_1(index=get_index(), generator=dialog_index_excel)


def uuid_question(question):
    uuid_x = uuid.uuid3(uuid.NAMESPACE_DNS, question)
    return str(uuid_x)


def dialog_index_excel():
    def __cell(sheet, column_label, row_id):
        v = sheet[f"{column_label}{row_id}"].value
        if not v:
            return v
        v = str(v).replace("\"", "").replace("\n", "")
        try:
            d = int(v)
            return d
        except Exception as e:
            return v

    class unit(object):
        def __init__(self):
            self.question = ""
            self.answers = []

    all = "A,B,C,D,E,F"

    wb = openpyxl.load_workbook("dialog.xlsx", data_only=True)
    sheet = wb["Sheet1"]
    row_id = 4
    u = None

    while True:
        if not __cell(sheet, "C", row_id):
            if row_id >= 147:
                break
            else:
                row_id += 1
                continue
        if __cell(sheet, "A", row_id):
            if u:
                data = {
                    "_id": uuid_question(u.question),
                    "_index": get_index(),
                    "_type": "doc",  # '_type' field is discouraged since ES 6.x, just use the 'doc' as default
                    "_source": {
                        "question": u.question,
                        "answers": u.answers
                    },
                    "doc_as_upsert": True,
                    "_op_type": 'index'
                }
                print(row_id)
                yield data

            u = unit()
            u.question = __cell(sheet, "B", row_id)
            customers = all
            if __cell(sheet, "D", row_id):
                customers = __cell(sheet, "D", row_id)
            anw = "%s|%s" % (customers, __cell(sheet, "C", row_id))
            u.answers.append(anw)
        if __cell(sheet, "C", row_id) and not __cell(sheet, "A", row_id):
            if u:
                customers = all
                if __cell(sheet, "D", row_id):
                    customers = __cell(sheet, "D", row_id)
                anw = "%s|%s" % (customers, __cell(sheet, "C", row_id))
                u.answers.append(anw)
        row_id += 1


def dialog_index():
    """
    :param unit:
    {
        "question": "text of the questions",
        "answers:":[
            {
                "content": "text of the content",
                "customers": [customerID, ...]
            }
            ...
        ]
    }
    :return:
    """
    filename = "dialog_script.yaml"
    with open(filename, "r") as r:
        l = safe_load(r)
    for c in l["customer"]:
        for k, v in c.items():
            customers[k] = v

    l.pop("customer")
    for k, v in l.items():
        question = v["content"]
        anws = []
        for u in v["answers"]:
            element = "%s|%s" % (u["customer"], u["content"])
            anws.append(element)
        data = {
            "_id": uuid_question(question),
            "_index": get_index(),
            "_type": "doc",  # '_type' field is discouraged since ES 6.x, just use the 'doc' as default
            "_source": {
                "question": question,
                "answers": anws
            },
            "doc_as_upsert": True,
            "_op_type": 'index'
        }
        yield data


# memory={}
def dialog_huashu(keyword, match_most=10):
    # TODO：add user authentication
    """
    :param keyword:
    :param match_most: if multiple questions are matched, we return the first 10
    :return:
    """
    keyword = keyword.replace("，", ",")
    logger.info("dialog_huashu|keyword=%s", keyword)
    customer_type = "abcdef"
    pattern = "^([A-Z|a-z])+,"
    x = re.match(pattern, keyword)
    if x:
        customer_type = x.group().replace(",", "").lower()  # lower the case
        keyword = keyword.split(",")[1]
    customer_type_set = set(list(customer_type))  # remove duplicate input,e.g.:  Aaa
    hits = dialog_search(keyword, get_index())
    answers = []
    if hits:
        src = hits[0]['_source']
        i = 1
        for ans in src["answers"]:
            arr = ans.split("|")
            customers = arr[0].lower().split(",")  # lower the case, remove duplicate input,e.g.:  Aaa
            logger.info("dialog_search_v1|customer_type_set=%s,customers=%s, ans=%s", customer_type_set, set(customers),
                        ans)
            if customer_type_set.intersection(set(customers)):
                answers.append("[%s]. %s" % (i, arr[1]))
                i += 1
        return "\n".join(answers)
        # only take the most matched question
    else:
        return "我暂时不清楚"
