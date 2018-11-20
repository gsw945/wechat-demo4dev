# -*- coding: utf-8 -*-
import socket
import socks

# virtual lan built via [ntop/n2n], wechat ip white list verificating bypassed via proxy
socks.set_default_proxy(socks.SOCKS5, "10.0.0.11", 3080)
socket.socket = socks.socksocket
# ################# code begin #################
import os


proj_root = os.path.abspath(os.path.dirname(__file__))
os.environ['PROJ_ROOT'] = proj_root


from flask import Flask, abort, make_response, request, jsonify
from src.wechat import process_response, jsapi_response

app = Flask(
    __name__,
    static_url_path='/web'
)


# https://dormousehole.readthedocs.io/en/latest/quickstart.html#id7
@app.route('/apps/<string:sub_domain>/', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def view_main(sub_domain):
    resp = process_response(sub_domain)
    if resp is None:
        return abort(500)
    return resp

@app.route('/apps/<string:sub_domain>/ajax', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def view_ajax(sub_domain):
    return jsonify({
        'hello': 'world'
    })

@app.route('/apps/<string:sub_domain>/jsapi', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def view_jsapi(sub_domain):
    resp = jsapi_response(sub_domain)
    if resp is None:
        return abort(500)
    return resp

@app.before_request
def hook_before_request(*args, **kwargs):
    print(args, kwargs)
    print(request.url)

for rule in app.url_map.iter_rules():
    print(rule.rule, rule.endpoint)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5656, debug=True)