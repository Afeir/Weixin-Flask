# -*- coding:utf-8 -*-
# job for token & ticket
import requests
from WeixinFlask import TokenAndTicket, db
from WeixinFlask import WX_TOKEN_REQ, WX_TICKET_REQ
import json


def _check_data(model_name):
    return len(model_name.query.all())


def main_job():
    if _check_data(TokenAndTicket) == 0:  # 如果记录为空,去微信拿一次新数据
        _access_res = requests.get(WX_TOKEN_REQ)
        _access_token = json.loads(_access_res.text)["access_token"]

        #拿到后去拿js_ticket
        if _access_token:
            _ticket_res = requests.get(WX_TICKET_REQ(_access_token))
            _js_ticket = json.loads(_ticket_res.text)["ticket"]
            if _js_ticket:
                unique_token_ticket = TokenAndTicket(_access_token, _js_ticket)
                db.session.add(unique_token_ticket)
                db.session.commit()


if __name__ == "__main__":
    main_job()