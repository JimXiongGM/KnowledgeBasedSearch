import requests
import json,time

def fun1(lxml='n'):
    #uri_base = 'http://127.0.0.1:9090/ltp'
    uri_base = 'http://playkg.top:19090/ltp'
    data = {'s': '我们都是中国人', 'x': lxml, 't': 'all'}
    start = time.time()
    response = requests.get(uri_base, data=data)
    if lxml == 'n':
        rdata = response.json()        
        print(json.dumps(rdata, indent=4, ensure_ascii=False))
    else:
        print (response)

    end = time.time()
    print ('time cost : %.4f s' % (end - start))




if __name__ == "__main__":
    fun1(lxml='n')









