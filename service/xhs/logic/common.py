from lib.logger import logger
import requests
import execjs
import json

HOST = 'https://edith.xiaohongshu.com'

COMMON_HEADERS = headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "content-type": "application/json;charset=UTF-8",
    "dnt": "1",
    "origin": "https://www.xiaohongshu.com",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://www.xiaohongshu.com/",
    "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
}


def common_request(uri: str, params: dict, headers: dict, need_sign: bool = True, post: bool = True) -> tuple[dict, bool]:
    """
    请求 xhs
    :param uri: 请求路径
    :param params: 请求参数
    :param headers: 请求头
    :return: 返回数据和是否成功
    """
    url = f'{HOST}{uri}'
    headers.update(COMMON_HEADERS)

    if post:
        if need_sign:
            xhs_sign_obj = execjs.compile(open('lib/js/xhs.js').read())
            sign_header = xhs_sign_obj.call('sign', uri, params, headers.get('cookie', ''))
            headers.update(sign_header)

        logger.info(f'url: {url}, request {url}, params={params}, headers={headers}')
        body = json.dumps(params, separators=(',', ':'), ensure_ascii=False)
        response = requests.post(url, data=body, headers=headers)
    else:
        if params.get('image_formats', None):
            params['image_formats'] = ','.join(params['image_formats'])
        params_str = '&'.join(f'{k}={v}' for k, v in params.items())  # 防止url encode
        uri = f'{uri}?{params_str}'
        url = f'{url}?{params_str}'

        if need_sign:
            xhs_sign_obj = execjs.compile(open('lib/js/xhs.js').read())
            sign_header = xhs_sign_obj.call('sign', uri, None, headers.get('cookie', ''))
            headers.update(sign_header)

        logger.info(f'url: {url}, request {url}, params={params}, headers={headers}')
        response = requests.get(url, headers=headers)

    logger.info(
        f'url: {url}, params: {params}, response, code: {response.status_code}, body: {response.text}')

    if response.status_code != 200:
        logger.error(
            f'url: {url}, params: {params}, request error, code: {response.status_code}, body: {response.text}')
        return {}, False
    if response.json().get('code', 0) != 0:
        logger.error(
            f'url: {url}, params: {params}, request error, code: {response.status_code}, body: {response.text}')
        return response.json(), False

    return response.json(), True