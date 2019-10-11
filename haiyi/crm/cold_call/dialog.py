from yaml import safe_load
import json
import uuid
from haiyi.tools.es_handler import dialog_search
from haiyi.tools.es_handler import bulk_index_1

customers = {}


def init():
    filename = "dialog_script.yaml"
    bulk_index_1(index=get_index(), generator=dialog_index(filename))


def get_index():
    return "es_dialog_script"


def uuid_question(question):
    uuid_x = uuid.uuid3(uuid.NAMESPACE_DNS, question)
    return str(uuid_x)


def dialog_index(file):
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
    with open(file, "r") as r:
        l = safe_load(r)
    for c in l["customer"]:
        for k, v in c.items():
            customers[k] = v

    l.pop("customer")
    for k, v in l.items():
        anws = []
        for u in v["answers"]:
            element = "%s|%s" % (",".join(u["customers"]), u["content"])
            anws.append(element)
        data = {
            "_id": uuid_question(v["question"]),
            "_index": get_index(),
            "_type": "doc",  # '_type' field is discouraged since ES 6.x, just use the 'doc' as default
            "_source": {"question": v["question"]},
            "question": v["question"],
            "answers": anws,
            "doc_as_upsert": True,
            "_op_type": 'index'
        }
        yield data


# memory={}
def dialog_search_v1(keyword):
    result = {}
    customer_type = "all"
    arr = keyword.split(" ")
    if len(arr) > 1 and str(arr[0]).strip().upper() in ["A", "B", "C", "D", "E", "F"]:
        customer_type = str(arr[0]).strip().upper()
        keyword = "".join(arr[1:])
    hits = dialog_search(keyword, get_index())
    answers = []
    for hit in hits:
        src = hit['_source']
        # q = src["question"]
        i = 0
        for ans in src["answers"]:
            arr = ans.split("|")
            customers = arr[0].split(",")
            if customer_type == "all" or customer_type in customers:
                answers.append("%s. %s" % (i, arr[1]))
    return "\n".join(answers)
