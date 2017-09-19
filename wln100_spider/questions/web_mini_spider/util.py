
import requests

HEADERS = {
'Accept-Encoding': 'gzip, deflate',
'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Cache-Control': 'no-cache',
'Connection': 'keep-alive',
}


def request(qid):
    url = 'http://www.wln100.com/Test/{}.html'.format(qid)
    for _ in range(3):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
        except Exception:
            continue

        return '该试题信息不存在！' not in resp.text


def binary_search(begin, end):
    print(begin, end)
    if end - begin < 2:
        return begin

    mid = (begin + end) // 2
    m = request(mid)

    if m:
        return binary_search(mid, end)
    else:
        return binary_search(begin, mid)


def get_max_qid():
    return binary_search(993138, 2000000)


def test():
    m = get_max_qid()
    print('ok', m)


if __name__ == '__main__':
    test()
