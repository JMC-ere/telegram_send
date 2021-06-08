# -*-coding:utf-8-*-
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
import telegram
import logging.handlers

today = datetime.today()
yesterday = today - timedelta(days=1)
# log_path = "../logs/" + today.strftime("%Y-%m-%d") + ".log"
# logger = logging.getLogger(__name__)
# fileHandler = logging.FileHandler(log_path)
# formatter = logging.Formatter('[%(asctime)s][%(filename)s:%(lineno)s] >> %(message)s')
# fileHandler.setFormatter(formatter)
# logger.addHandler(fileHandler)
# logger.setLevel(level=logging.INFO)


def send_message():

    index_es = ''
    bot = telegram.Bot(token="1049808110:AAGUYRvxgZLYNcmQFn3p8yO9VSqzQyPavls")

    try:
        bot = telegram.Bot(token="1049808110:AAGUYRvxgZLYNcmQFn3p8yO9VSqzQyPavls")

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
        # arr_kr_type = {'zapping': 'Zapping시 컨텐츠 제안',
        #                'vod-recom': '본방사수 실패한 컨텐츠 제안',
        #                'interest': '관심 컨텐츠의 신규 에피소드',
        #                'prepurchase': '구매중 이탕 컨텐츠 가격할인',
        #                'dcmark': '찜하고 시청하지 않은 컨텐츠 가격할인',
        #                'noresult': '검색시 미수급 컨텐츠 수급',
        #                'nolgs': '시청 종료일이 다가오는 컨텐츠 시청제안',
        #                'active': '관심 VOD'}

        # type 이 색인이 되지 않으면 결과가 수집되지 않음.
        for row in result_es:
            print(row)
            if row['key'] in arr_type:
                arr_type.remove(row['key'])

        #  안정화 기간 지나면 삭제-------------------start-----------------------
        test_list = []
        t_cnt = 0

        message_text = datetime.today().strftime("%Y-%m-%d") + " NUDGE 모니터링 결과 \n\n"

        check_alias = index_es.indices.exists_alias(name="index-nudge-complete-all")

        # 알리아스 체크------------start
        if check_alias:
            check_alias_name = index_es.indices.get_alias(name="index-nudge-complete-all")
            key = check_alias_name.keys()
            alias_message = "\nAlias Name : " + list(key)[0]
            bot.sendMessage(chat_id='1228894509', text=alias_message)
        else:
            alias_message = "\n" + "Alias Name : Alias Error"
        # 알리아스 체크------------end

        if len(arr_type) > 0:
            for type1 in arr_type:
                message_text += type1 + " : " + "empty [*확인필요*]\n"

        for es_row in result_es:
            test_list.append(es_row['doc_count'])

            if test_list[t_cnt] != 0:
                message_text += es_row['key'] + " : " + str(format(test_list[t_cnt], ',')) + "건\n"

            t_cnt = t_cnt + 1

        test_list.clear()

        message_text += alias_message

        bot.sendMessage(chat_id='1228894509', text=message_text)
        bot.sendMessage(chat_id='976803858', text=message_text)
        # bot.sendMessage(chat_id='1070666335', text=message_text)
        #  안정화 기간 지나면 삭제-------------------end-------------------------

        index_es.close()
        # logger.info("telegram_send message success")

    except Exception as e:
        index_es.close()
        message = today.strftime("%Y.%m.%d") + " NUDGE 모니터링 모듈 이슈\n"
        message += str(e.__cause__)
        # logger.error(e)
        bot.sendMessage(chat_id='1228894509', text=message)
        bot.sendMessage(chat_id='976803858', text=message)
        # bot.sendMessage(chat_id='1070666335', text=message)


if __name__ == '__main__':
    send_message()
