from yaml import safe_load
import json
import uuid
from haiyi.tools.es_handler import dialog_search
from haiyi.tools.es_handler import bulk_index_1
import logging
import re
logger = logging.getLogger(__name__)

customers = {}


def init():
    filename = "dialog_script.yaml"
    bulk_index_1(index=get_index(), generator=dialog_index)


def get_index():
    return "es_dialog_script"


def uuid_question(question):
    uuid_x = uuid.uuid3(uuid.NAMESPACE_DNS, question)
    return str(uuid_x)


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
def dialog_search_v1(keyword):
    result = {}
    customer_type = "ABCDEF"
    pattern="^([A-F]|[a-f])+,"
    x = re.match(pattern, keyword)
    if x:
        customer_type=x
        keyword = keyword.split(",")[1]
    customer_type_set = set(list(customer_type))
    hits = dialog_search(keyword, get_index())
    answers = []
    for hit in hits:
        src = hit['_source']
        logger.info("dialog_search_v1|src=%s", src)
        # q = src["question"]
        i = 0
        for ans in src["answers"]:
            arr = ans.split("|")
            customers = arr[0].split(",")

            if customer_type_set.issubset(set(customers)):
                answers.append("%s. %s" % (i, arr[1]))
    return "\n".join(answers)