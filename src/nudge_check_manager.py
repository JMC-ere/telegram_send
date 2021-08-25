# -*-coding:utf-8-*-
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
from send_mail import mail_send


def send_message():

    manager_email = ''

    today = datetime.today()
    week_ago = today - timedelta(days=7)
    week_ago = week_ago.strftime('%Y.%m.%d')

    es_client = ''

    # 증감률 보고 기준
    send_message_num = 50

    # -50% 이하면 메일발송
    send_count = 0

    index_name = "index-nudge-complete-all"
    week_ago_index_name = f"index-nudge-complete-all-{week_ago}"

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

    message_text += f'<tr><th>로직 구분</th><th>{week_ago}</th><th>{today.strftime("%Y.%m.%d")}</th><th>전주 대비 증감률</th><th>전주 대비 증감건수</th></tr>'

    #  Alias Check start
    # check_alias = es_client.indices.exists_alias(name=index_name)
    # if check_alias:
    #     check_alias_name = es_client.indices.get_alias(name="index-nudge-complete-all")
    #     key = check_alias_name.keys()
    #     alias_message = "Alias Name : " + list(key)[0]
    # else:
    #     alias_message = "Alias Name : Alias Error"
    # Alias Check end

    result_es = es_client.search(index=index_name, body=body)
    week_ago_result_es = es_client.search(index=week_ago_index_name, body=body)

    result_es = result_es['aggregations']['group_by_state']['buckets']
    week_ago_result_es = week_ago_result_es['aggregations']['group_by_state']['buckets']

    arr_type = {'zapping': 'Zapping시 컨텐츠 제안',
                'vod-recom': '본방사수 실패한 컨텐츠 제안',
                'interest': '관심 컨텐츠의 신규 에피소드',
                'prepurchase': '구매 중 이탈 컨텐츠 가격할인',
                'dcmark': '찜하고 시청하지 않은 컨텐츠 안내',
                'noresult': '검색시 미수급 컨텐츠 수급',
                'nolgs': '시청 종료일이 다가오는 컨텐츠 시청 제안',
                'active': '관심 VOD'}

    dict_result = {}
    week_ago_dict_result = {}

    for result in result_es:
        if result['key'] != '':
            dict_result[result['key']] = result['doc_count']

    for result in week_ago_result_es:
        if result['key'] != '':
            week_ago_dict_result[result['key']] = result['doc_count']

    for key_type in list(arr_type.keys()):

        if key_type in week_ago_dict_result:
            message_text += f'<tr><td>{arr_type[key_type]}</td><td style="text-align:right;">{str(format(week_ago_dict_result[key_type], ","))}건</td>'
        else:
            message_text += f'<tr><td>{arr_type[key_type]}</td><td style="text-align:right;">0건</td>'
            week_ago_dict_result[key_type] = 0

        if key_type in dict_result:
            message_text += f'<td style="text-align:right;">{str(format(dict_result[key_type], ","))}건</td>'
        else:
            message_text += f'<td style="text-align:right;"> Empty [*확인필요*]</td>'
            err_count += 1
            dict_result[key_type] = 0

        a_week_ago_count = week_ago_dict_result[key_type]
        today_count = dict_result[key_type]
        up_down = (today_count-a_week_ago_count)/a_week_ago_count * 100

        up_down_count = dict_result[key_type] - week_ago_dict_result[key_type]

        # 증감률
        if up_down > 0:
            if up_down >= send_message_num:
                send_count = 1
                message_text += f'<td><p style="text-align:right;"><font color="blue"><b>+{str(format(up_down, ".2f"))}% </b></font></p></td>'
                message_text += f'<td><p style="text-align:right;"><font color="blue"><b>+{str(format(up_down_count, ","))}</b></font></p></td></tr>'
            else:
                message_text += f'<td><p style="text-align:right;"><font color="black">+{str(format(up_down, ".2f"))}% </font></p></td>'
                message_text += f'<td><p style="text-align:right;"><font color="black">+{str(format(up_down_count, ","))}</font></p></td></tr>'
        elif up_down < 0:
            if up_down <= -send_message_num:
                send_count = 1
                message_text += f'<td><p style="text-align:right;"><font color="red"><b>{str(format(up_down, ".2f"))}% </b></font></p></td>'
                message_text += f'<td><p style="text-align:right;"><font color="red"><b>{str(format(up_down_count, ","))}</b></font></p></td></tr>'
            else:
                message_text += f'<td><p style="text-align:right;"><font color="black">{str(format(up_down, ".2f"))}% </font></p></td>'
                message_text += f'<td><p style="text-align:right;"><font color="black">{str(format(up_down_count, ","))}</font></p></td></tr>'
        else:
            message_text += f'<td><p style="text-align:right;"><font color="black">{str(format(up_down, ".2f"))}% </font></p></td>'
            message_text += f'<td><p style="text-align:right;"><font color="black">{str(format(up_down_count, ","))}</font></p></td></tr>'

        # 전주 대비 증감건수
        # if up_down > 0:
        #     if up_down >= send_message_num:
        #         message_text += f'<td><p style="text-align:right;"><font color="blue">증가 {str(format(week_ago_dict_result[key_type] - dict_result[key_type], ","))}</font></p></td></tr>'
        #     else:
        #         message_text += f'<td><p style="text-align:right;"><font color="black">증가 {str(format(week_ago_dict_result[key_type] - dict_result[key_type], ","))}</font></p></td></tr>'
        # elif up_down < 0:
        #     if up_down <= send_message_num:
        #         message_text += f'<td><p style="text-align:right;"><font color="red">감소 {str(format(week_ago_dict_result[key_type] - dict_result[key_type], ","))}</font></p></td></tr>'
        #     else:
        #         message_text += f'<td><p style="text-align:right;"><font color="black">감소 {str(format(week_ago_dict_result[key_type] - dict_result[key_type], ","))}</font></p></td></tr>'
        # else:
        #     message_text += f'<td><p style="text-align:right;"><font color="black">{str(format(week_ago_dict_result[key_type] - dict_result[key_type], ","))}</font></p></td></tr>'

    message_text += f"</table><br>"

    # message_text += alias_message

    h_message_text = datetime.today().strftime("%Y-%m-%d") + f" NUDGE 증감률 모니터링 결과 이슈 : {err_count}건"
    if send_count <= 1:
        mail_send(title=h_message_text, content=message_text, send_bool=send_count, manager=manager_email)
    else:
        print("TEST")


if __name__ == '__main__':
    send_message()
    # print("testing")
