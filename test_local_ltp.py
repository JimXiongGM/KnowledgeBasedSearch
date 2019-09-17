import requests
import json,time

def fun1():
    uri_base = 'http://127.0.0.1:9090/ltp'
    data = {'s': '我们都是中国人', 'x': 'n', 't': 'all'}
    start = time.time()
    response = requests.get(uri_base, data=data)
    rdata = response.json()
    end = time.time()
    print(json.dumps(rdata, indent=4, ensure_ascii=False))
    print ('time cost : %.4f s' % (end - start))


from pyltp import SentenceSplitter

def fun2():
    sents = SentenceSplitter.split('元芳你怎么看？我就趴窗口上看呗！')  # 分句
    print ('\n'.join(sents))


if __name__ == "__main__":
    fun2()