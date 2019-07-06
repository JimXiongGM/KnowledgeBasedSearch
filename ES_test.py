from elasticsearch import Elasticsearch
import json,sys

def fun1():
    # 创建 Index
    es = Elasticsearch()
    result = es.indices.create(index='news', ignore=400)
    print(result)

def fun2():
    # 删除
    es = Elasticsearch()
    result = es.indices.delete(index='news', ignore=[400, 404])
    print(result)

def fun3():
    # 插入数据
    es = Elasticsearch()
    es.indices.create(index='news', ignore=400)
    data = {'title': '美国留给伊拉克的是个烂摊子吗', 'url': 'http://view.news.qq.com/zt2011/usa_iraq/index.htm'}
    result = es.create(index='news', doc_type='politics', id=1, body=data)
    print(result)

def fun4():
    # 更新
    es = Elasticsearch()
    data = {
        'title': '美国留给伊拉克的是个烂摊子吗',
        'url': 'http://view.news.qq.com/zt2011/usa_iraq/index.htm',
        'date': '2011-12-16'
    }
    # new add 
    data = {"doc": data}
    result = es.update(index='news', doc_type='politics', body=data, id=1)
    print(result)

def fun5():
    # 删除数据
    es = Elasticsearch()
    # result = es.delete(index='news', doc_type='politics', id=1)
    result = es.indices.delete(index='news', ignore=[400, 404])
    print(result)

def fun6():
    # 需要中文分词器
    es = Elasticsearch()
    mapping = {
        'properties': {
            'title': {
                'type': 'text',
                'analyzer': 'ik_max_word',
                'search_analyzer': 'ik_max_word'
            }
        }
    }
    es.indices.delete(index='news', ignore=[400, 404])
    es.indices.create(index='news', ignore=400)
    # add include_type_name = True
    result = es.indices.put_mapping(index='news', doc_type='politics', body=mapping , include_type_name = True)
    print(result)

def fun7():
    # 插入与查询
    es = Elasticsearch()
    es.indices.create(index='news', ignore=400)
    datas = [
        {
            'title': '美国留给伊拉克的是个烂摊子吗',
            'url': 'http://view.news.qq.com/zt2011/usa_iraq/index.htm',
            'date': '2011-12-16'
        },
        {
            'title': '公安部：各地校车将享最高路权',
            'url': 'http://www.chinanews.com/gn/2011/12-16/3536077.shtml',
            'date': '2011-12-16'
        },
        {
            'title': '中韩渔警冲突调查：韩警平均每天扣1艘中国渔船',
            'url': 'https://news.qq.com/a/20111216/001044.htm',
            'date': '2011-12-17'
        },
        {
            'title': '中国驻洛杉矶领事馆遭亚裔男子枪击 嫌犯已自首',
            'url': 'http://news.ifeng.com/world/detail_2011_12/16/11372558_0.shtml',
            'date': '2011-12-18'
        }
    ]

    for i,data in enumerate(datas):
        es.create(index='news', doc_type='politics',id = i, body=data ,ignore=[400,409])

    # result = es.search(index='news', doc_type='politics')
    result = es.search(index='news', filter_path=['hits.hits._id', 'hits.hits._type'])
    print(result)

def fun8():
    # 全文检索
    dsl = {
        'query': {
            'match': {
                'title': '中国 领事馆'
            }
        }
    }

    es = Elasticsearch()
    result = es.search(index='news', body=dsl)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    fun = int(sys.argv[1])
    if fun == 1:
        fun1()
    elif fun == 2:
        fun2()
    elif fun == 3:
        fun3()
    elif fun == 4:
        fun4()
    elif fun == 5:
        fun5()
    elif fun == 6:
        fun6()
    elif fun == 7:
        fun7()
    elif fun == 8:
        fun8()
    else:
        print ('error , fun : ',fun)       






'''
scp ES_test.py root@master:/root/xiazai/
'''