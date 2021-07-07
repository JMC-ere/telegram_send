# -*-coding:utf-8-*-
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
from send_mail import mail_send

today = datetime.today()
this_day = today.strftime("%Y.%m.%d")
one_days_before = (today - timedelta(1)).strftime("%Y-%m-%d")
tow_days_before = (today - timedelta(2)).strftime("%Y.%m.%d")


def check_index():

    err_cnt = 0

    try:
        # ES Connect
        es_client = Elasticsearch(['121.125.71.147',
                                   '121.125.71.148',
                                   '121.125.71.149'],
                                  port=9200, timeout=20,
                                  http_auth=('elastic', 'wtlcnNyrDPVko01lZfIl'))
        es_client.info()

        index_name = "index-nudge-result-union"

        query = """
        {
          "size": 0,
          "query": {
            "bool": {
              "filter": [
                {
                  "range": {
                    "log_time": {
                      "from": "%sT00:00:00.000Z",
                      "to": "%sT23:59:59.999Z"
                    } 
                  }
                }
              ]
            }
          },"aggs": {
            "NAME": {
              "terms": {
                "field": "action_body.category",
                "size": 1000
              }
            }
          }
        }
        """

        response = es_client.search(index=index_name, body=query % (one_days_before, one_days_before))
        list_day = response['aggregations']['NAME']['buckets']

        message = ""

        if not list_day:
            message += "ALIAS ERROR"

        for day in list_day:
            if day['doc_count'] != 0:
                message += f"{str(day['key'])} : {str(day['doc_count'])} 건<br>"
            else:
                err_cnt += 1

        h_message = f"넛지 성과 분석 ({one_days_before}) 이슈 : {err_cnt}건"

        mail_send(h_message, message)
        print(h_message + message)

    except Exception as es_err:
        print(es_err)
        h_message = f"넛지 성과 분석 ({one_days_before}) 이슈 : {err_cnt}건"
        err_message = "넛지 성과 분석 ERROR : "
        err_message += str(es_err)
        # bot.sendMessage(chat_id='1228894509', text=err_message)


if __name__ == '__main__':
    check_index()

