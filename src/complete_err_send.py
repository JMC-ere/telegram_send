# -*-coding:utf-8-*-
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
import telegram
import logging.handlers

today = datetime.today()
yesterday = today - timedelta(days=1)
log_path = "../logs/" + today.strftime("%Y-%m-%d") + ".log"
logger = logging.getLogger(__name__)
fileHandler = logging.FileHandler(log_path)
formatter = logging.Formatter('[%(asctime)s][%(filename)s:%(lineno)s] >> %(message)s')
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
logger.setLevel(level=logging.INFO)


def change_alias():
    es_check = True

    try:
        index_es = Elasticsearch(
            ["121.125.71.151", "121.125.71.152", "121.125.71.153", "121.125.71.154", "121.125.71.155"],
            port=9200, max_retries=500,
            http_auth=("elastic", "X7XsyxLzbrFDFMyOy3Wd"))

        index_name = "index-nudge-complete-all-{}".format(today.strftime("%Y.%m.%d"))
        index_name_yesterday = "index-nudge-complete-all-{}".format(yesterday.strftime("%Y.%m.%d"))

        if index_es.indices.exists(index=index_name):
            # 어제날짜 complete-all alias 삭제
            index_es.indices.delete_alias(index=[index_name_yesterday], name='index-nudge-complete-all')
            # 오늘날짜 complete-all alias 추가
            index_es.indices.put_alias(index=[index_name], name='index-nudge-complete-all')
            index_es.close()
        else:
            bot = telegram.Bot(token="1049808110:AAGUYRvxgZLYNcmQFn3p8yO9VSqzQyPavls")

            message = datetime.today().strftime("%Y-%m-%d") + " NUDGE 모니터링 결과 \n\n"
            message += "'index-nudge-complete-all-{}' 또는\n".format(today.strftime("%Y.%m.%d"))
            message += "'index-nudge-complete-all-{}' 가 존재하지 않습니다.".format(yesterday.strftime("%Y.%m.%d"))

            bot.sendMessage(chat_id='1228894509', text=message)
            # bot.sendMessage(chat_id='976803858', text=message)
            # bot.sendMessage(chat_id='1070666335', text=message)

        logger.info("success change_alias")

    except Exception as alias_e:
        es_check = False
        logger.error(alias_e)

    return es_check


def send_message(check):
    try:
        bot = telegram.Bot(token="1136684466:AAGbpu5NjIhrVKr3tK6VKelS1AOSF2PgW5A")

        if check:
            index_es = Elasticsearch(
                ["121.125.71.151", "121.125.71.152", "121.125.71.153", "121.125.71.154", "121.125.71.155"],
                port=9200, max_retries=500,
                http_auth=("elastic", "X7XsyxLzbrFDFMyOy3Wd"))

            index_name = "index-nudge-complete-all"

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

            result_es = index_es.search(index=index_name, body=body)
            result_es = result_es['aggregations']['group_by_state']['buckets']

            arr_type = ['zapping', 'vod-recom', 'interest', 'prepurchase', 'dcmark', 'noresult', 'nolgs', 'active']

            # type 이 색인이 되지 않으면 결과가 수집되지 않음.
            for row in result_es:
                print(row)
                if row['key'] in arr_type:
                    arr_type.remove(row['key'])

            # if len(arr_type) > 0:
            #     message = datetime.today().strftime("%Y-%m-%d") + " NUDGE 모니터링 결과 \n\n"
            #     message += "확인필요 TYPE: \n"
            #     for type in arr_type:
            #         message += "'" + type + "' is empty\n"
            #
            #     bot.sendMessage(chat_id='1228894509', text=message)
            #     bot.sendMessage(chat_id='976803858', text=message)
            #     bot.sendMessage(chat_id='1070666335', text=message)

            #  안정화 기간 지나면 삭제-------------------start-----------------------
            test_list = []
            t_cnt = 0

            message_text = datetime.today().strftime("%Y-%m-%d") + " NUDGE 모니터링 결과 \n\n"

            if len(arr_type) > 0:
                for type1 in arr_type:
                    message_text += type1 + " : " + "empty [*확인필요*]\n"

            for es_row in result_es:
                test_list.append(es_row['doc_count'])

                if test_list[t_cnt] != 0:
                    message_text += es_row['key'] + " : " + str(test_list[t_cnt]) + "건\n"

                t_cnt = t_cnt + 1

            test_list.clear()

            bot.sendMessage(chat_id='1228894509', text=message_text)
            # bot.sendMessage(chat_id='976803858', text=message_text)
            # bot.sendMessage(chat_id='1070666335', text=message_text)
            #  안정화 기간 지나면 삭제-------------------end-------------------------

            index_es.close()
        else:
            message = datetime.today().strftime("%Y-%m-%d") + " NUDGE 모니터링 결과 \n\n"
            message += "<Elastic Search Connection Error>"

        logger.info("telegram_send message success")

    except Exception as e:
        index_es.close()
        message = today.strftime("%Y.%m.%d") + " NUDGE 모니터링 모듈 이슈\n"
        message += str(e.__cause__)
        logger.error(e)
        bot.sendMessage(chat_id='1228894509', text=message)
        # bot.sendMessage(chat_id='976803858', text=message)
        # bot.sendMessage(chat_id='1070666335', text=message)


if __name__ == '__main__':
    alias_check = change_alias()
    send_message(alias_check)
