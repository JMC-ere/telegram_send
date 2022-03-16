# -*-coding:utf-8-*-
import urllib.request
import json
from datetime import datetime
from send_mail import mail_send


def check_api(ver):

    today = datetime.today().strftime("%Y.%m.%d")

    result = ""
    message = ""
    server_list = ['121.125.71.171:8080', '121.125.71.172:8080', '121.125.71.173:8080',
                   '1.255.46.181:8080', '1.255.46.182:8080', '1.255.46.183:8080', '1.255.46.184:8080']
    f = ''

    cnt = 0
    err_cnt = 0

    try:
        for server in server_list:
            if ver == "5.2.4":
                url = "http://" + server + f"/nudge/v1/if-nudge-001?if=IF-NUGDE-001&stb_id=%7B3E25080A-4345-11EA-819D-37B877ECC397%7D&model_group=STB&ver={ver}&model_name=BKO-UH400&ui_name=BKO-UH400&response_format=json&menu_id=all&menu_ids=&nudge_data"
            else:
                url = "http://" + server + f"/nudge/v1/if-nudge-001?if=IF-NUGDE-001&stb_id=%7B3E25080A-4345-11EA-819D-37B877ECC397%7D&model_group=STB&ver={ver}&model_name=BKO-UH400&ui_name=BKO-UH400&response_format=json&menu_ids=menu001,menu002,menu003,menu004,menu006,menu008,menu009,menu010,menu011,menu012,menu013,menu014,menu017,menu5206,menu5205,menu5220,menu5209,menu5208,menu5212,menu5221,menu5210&nudge_data"

            headers = {'Content-Type': 'application/json;charset=utf-8',
                       'Accept': 'application/json;charset=utf-8',
                       'Client_ID': 'client_id',
                       'TimeStamp': 'time',
                       'Auth_Val': '0xb613679a0814d9ec772f939398gff',
                       'Api_Key': 'l7xx159a8ca72966400b886a93895ec9e2e3',
                       'Trace': 'IPTV^SvcGW|1500615968194^MSGW|1500615963831',
                       'Client_IP': 'client_ip'}

            req = urllib.request.Request(url=url, headers=headers)
            f = urllib.request.urlopen(req)
            f = f.read().decode('utf-8')

            result = f

            f = json.loads(f)

            if f['result'] == '0000':
                message += f"[{server}] = [정상]<br>"
                cnt += 1
            else:
                message += f"SERVER : [{server}]  상태 : [{f}]"
                err_cnt += 1

        if cnt == 7:
            message += f"\n<7개 서버 응답 정상>"
            message += "<p>"
            message += result
            h_message = f"{ver} <{today} API CHECK> : [이슈 : 0]"

        else:
            h_message = f"{ver} <{today} API CHECK> : [이슈 : {err_cnt}]"

    except Exception as err:
        h_message = f"{ver} <{today} API CHECK> : [이슈 : {err_cnt}]"
        message += str(err)

    print(message)
    mail_send(h_message, message)


if __name__ == '__main__':
    check_api("5.2.4")
    check_api("5.3.2")
