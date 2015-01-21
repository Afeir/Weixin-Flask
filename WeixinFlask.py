# -*- coding:utf-8 -*-
from flask import Flask,  make_response, request
from config import CONFIG
import json
import random
import string
import hashlib
import time
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'  # 相对路径写法
db = SQLAlchemy(app)


class TokenAndTicket(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(200), unique=True)
    ticket = db.Column(db.String(200), unique=True)

    def __init__(self, token, ticket):
        self.token = token
        self.ticket = ticket

    def __repr__(self):
        return "<TICKET %r>" % self.ticket


current_token_ticket = TokenAndTicket.query.first()

#error code
DONE = 200

#weixin token
WX_TOKEN_REQ = (
    "https://api.weixin.qq.com/cgi-bin/token?grant_type=%s&appid=%s&secret=%s"
    % (CONFIG['client_credential'], CONFIG["app_id"], CONFIG["secret"])
)

#weixin js_ticket
WX_TICKET_REQ = lambda x: "https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=jsapi" % x


@app.route('/nonce', methods=['GET', 'POST'])
def ge_nonce_str():
    """随机串单拿接口
    """
    return json_response(
        {
            "nonce_str": ''.join(random.sample(string.ascii_letters, 12))
        }
    )


def _ge_nonce_str():
    """all in one 接口用
    """
    return ''.join(random.sample(string.ascii_letters, 12))


def error_res_obj(code, msg):
    """错误响应
    """
    return {
        "errcode": code,
        "errmsg": msg
    }


def json_response(res):
    """包装response为json
    """
    if isinstance(res, dict) or isinstance(res, list):
        json_response_body = make_response(json.dumps(res))
    else:
        json_response_body = make_response(res)
    json_response_body.headers['Content-Type'] = "application/json;charset=UTF-8"  # 设置
    # json_response_body.headers['Access-Control-Allow-Origin'] = "*"  # 跨域
    return json_response_body


@app.route('/token', methods=['POST', 'GET'])
def get_access_token():
    """token单拿接口
    """
    token = current_token_ticket.token
    return json_response({
        "token": token
    })


@app.route('/ticket', methods=['POST', 'GET'])
def js_ticket():
    """ticket单拿接口
    """
    ticket = current_token_ticket.ticket
    return json_response({
        "ticket": ticket
    })


def _sign_ticket(nonce_str, j_ticket, timestamp, url):
    """私有签名方法
    """
    sign_dict = {
        "jsapi_ticket": j_ticket,
        "noncestr": nonce_str,
        "timestamp": timestamp,
        "url": url
    }

    tmp = []

    # 字典排序
    sign_sorted_list = sorted(sign_dict.iteritems(), key=lambda x: x[0], reverse=False)
    for item in sign_sorted_list:
        tmp.append(str(item[0]) + "=" + str(item[1]))

    _url_string = '&'.join(tmp)
    final_sign = hashlib.sha1(_url_string).hexdigest()
    return final_sign


@app.route('/all', methods=['POST', 'GET'])
def all_in_one():
    """all in one数据返回
    """
    _time_stamp = int(time.time())
    _random_str = _ge_nonce_str()
    _js_ticket = current_token_ticket.ticket
    _url = request.host_url[:-1]  # 去除/

    return json_response({
        'appId': CONFIG['app_id'],
        'timestamp': _time_stamp,
        'nonceStr': _random_str,
        'signature': _sign_ticket(_random_str, _js_ticket, _time_stamp, _url),
        'url': _url  # POST过来什么,返回什么
    })


def _detect_request():
    with app.test_request_context('/all', method=['POST', 'GET']):
        print dir(request)
        print request.host_url


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
    # _detect_request()
