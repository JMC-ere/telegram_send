# -*-coding:utf-8-*-
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
from send_mail import mail_send


def send_message():
    today = datetime.today()
    yesterday = today - timedelta(days=1)
    yesterday = yesterday.strftime('%Y.%m.%d')

    es_client = ''

    index_name = "index-nudge-complete-all"
    yesterday_index_name = f"index-nudge-complete-all-{yesterday}"

    err_count = 0

    es_client = Elasticsearch(
        ["121.125.71.151", "121.125.71.152", "121.125.71.153", "121.125.71.154", "121.125.71.155"],
        port=9200, max_retries=500,
        http_auth=("elastic", "X7XsyxLzbrFDFMyOy3Wd"))

    body = """
            {
               "size": 0,
               "query": {
                 "match_all": {}
               },"aggs": {
                 "group_by_state": {
                   "terms": {
                     "field": "nudge_type",
                     "size": 10
                   }
                 }
               }
             }
             """

    message_text = '<table style="border-collapse: collapse" border="1px">'

    message_text += f"<tr><th>구분</th><th>{today.strftime('%Y.%m.%d')}</th><th>{yesterday}</th></tr>"

    #  Alias Check start
    check_alias = es_client.indices.exists_alias(name=index_name)
    if check_alias:
        check_alias_name = es_client.indices.get_alias(name="index-nudge-complete-all")
        key = check_alias_name.keys()
        alias_message = "Alias Name : " + list(key)[0]
    else:
        alias_message = "Alias Name : Alias Error"
    # Alias Check end

    result_es = es_client.search(index=index_name, body=body)
    yesterday_result_es = es_client.search(index=yesterday_index_name, body=body)

    result_es = result_es['aggregations']['group_by_state']['buckets']
    yesterday_result_es = yesterday_result_es['aggregations']['group_by_state']['buckets']

    arr_type = ['zapping', 'vod-recom', 'interest', 'prepurchase', 'dcmark', 'noresult', 'nolgs', 'active']

    dict_result = {}
    yesterday_dict_result = {}

    for result in result_es:
        if result['key'] != '':
            dict_result[result['key']] = result['doc_count']

    for result in yesterday_result_es:
        if result['key'] != '':
            yesterday_dict_result[result['key']] = result['doc_count']

    for key_type in arr_type:
        if key_type in dict_result:
            message_text += f"<tr><td>{key_type}</td><td>{str(format(dict_result[key_type], ','))} 건</td>"
            print(dict_result)
        else:
            print(dict_result)
            message_text += f"<tr><td>{key_type}</td><td> Empty [*확인필요*]</td>"
            err_count += 1

        if key_type in yesterday_dict_result:
            message_text += f"<td>{str(format(yesterday_dict_result[key_type], ','))} 건</td></tr>"
        else:
            message_text += f"<td>0 건</td></tr>"

    message_text += f"</table><br>"

    message_text += alias_message

    h_message_text = datetime.today().strftime("%Y-%m-%d") + f" NUDGE 모니터링 결과 이슈 : {err_count}건"

    mail_send(h_message_text, message_text)


if __name__ == '__main__':
    send_message()
