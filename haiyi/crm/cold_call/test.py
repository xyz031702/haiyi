import openpyxl
import uuid
import pprint

def uuid_question(question):
    uuid_x = uuid.uuid3(uuid.NAMESPACE_DNS, question)
    return str(uuid_x)

def get_index():
    return "es_dialog_script"


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

    wb = openpyxl.load_workbook("/Users/dings/github/haiyi/dialog.xlsx", data_only=True)
    sheet = wb["Sheet1"]
    row_id = 4
    u = None

    while True:
        if not __cell(sheet, "C", row_id):
            break
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
            u.answers.append(anw.strip())
        if __cell(sheet, "C", row_id) and not __cell(sheet, "A", row_id):
            if u:
                customers = all
                if __cell(sheet, "D", row_id):
                    customers = __cell(sheet, "D", row_id)
                anw = "%s|%s" % (customers, __cell(sheet, "C", row_id))
                u.answers.append(anw.strip())
        row_id += 1

for u in dialog_index_excel():
    pp=pprint.PrettyPrinter(4)
    pp.pprint(u)
    print("\n")