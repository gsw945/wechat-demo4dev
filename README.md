# wechat-demo4dev
微信Demo（用于开发演示）

## 使用步骤
```bash
pip install -r requirements.txt
python run.py
```

## 开发注意
* 将程序放置于服务器，将服务器IP添加到微信IP白名单，即可去掉`run.py`中的代理部分的代码
* nginx配置文件: `app-nginx.conf`
* 微信开发参数: `src/wechat.py` 中的 `CFG`
