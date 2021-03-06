# ES 7.3语法备忘

## 启动
```bash
sysctl -w vm.max_map_count=262144;
chown -R jimx:jimx  /opt/elasticsearch-7.3.0;
# 使用elsearch用户启动elasticsearch
su elsearch
cd /opt/elasticsearch-7.3.0 && nohup ./bin/elasticsearch >> ./elasticsearch.log &
su elsearch
cd /opt/elasticsearch-7.3.0 && ./bin/elasticsearch 
# cd ./logs
nohup /opt/kibana-7.3.0-linux-x86_64/bin/kibana --allow-root >> /logs/kibana.log &
```

### cluster health

```bash
curl -X GET "localhost:9200/_cat/health?v"
```

### list all indices

```bash
curl -X GET "localhost:9200/_cat/indices?v"
```

### create index

```bash
curl -X PUT "localhost:9200/customer?pretty"
curl -X GET "localhost:9200/_cat/indices?v"
```

### Index and Query a Document

```bash
curl -X PUT "localhost:9200/customer/_doc/1?pretty" -H 'Content-Type: application/json' -d'
{
  "name": "John Doe"
}
'
```

- 随机指定索引

```bash
curl -X POST "localhost:9200/customer/_doc?pretty" -H 'Content-Type: application/json' -d'
{
  "name": "Jane Doe"
}
'
```

```bash
curl -X GET "localhost:9200/customer/_doc/1?pretty"
```


### Delete an Index

```bash
curl -X DELETE "localhost:9200/customer_001?pretty"
curl -X GET "localhost:9200/_cat/indices?v"
```


### Updating Documents

- 改变字段值

```bash
curl -X POST "localhost:9200/customer/_update/1?pretty" -H 'Content-Type: application/json' -d'
{
  "doc": { "name": "Jane Doe" }
}
'
curl -X GET "localhost:9200/customer/_doc/1?pretty"
```


- 增加字段

```bash
curl -X POST "localhost:9200/customer/_update/1?pretty" -H 'Content-Type: application/json' -d'
{
  "doc": { "name": "Jane Doe", "age": 20 }
}
'
curl -X GET "localhost:9200/customer/_doc/1?pretty"
```

- 使用脚本

```bash
curl -X POST "localhost:9200/customer/_update/1?pretty" -H 'Content-Type: application/json' -d'
{
  "script" : "ctx._source.age += 5"
}
'
curl -X GET "localhost:9200/customer/_doc/1?pretty"
```

### Deleting Documents

```bash
curl -X DELETE "localhost:9200/customer/_doc/2?pretty"
```

### Batch Processing

```bash
- 批量增加

curl -X POST "localhost:9200/customer/_bulk?pretty" -H 'Content-Type: application/json' -d'
{"index":{"_id":"1"}}
{"name": "John Doe" }
{"index":{"_id":"2"}}
{"name": "Jane Doe" }
'
```

- 批量修改

```bash
curl -X POST "localhost:9200/customer/_bulk?pretty" -H 'Content-Type: application/json' -d'
{"update":{"_id":"1"}}
{"doc": { "name": "John Doe becomes Jane Doe" } }
{"delete":{"_id":"2"}}
'
```

- 完整模板

```bash
curl -X POST "localhost:9200/_bulk?pretty" -H 'Content-Type: application/json' -d'
{ "index" : { "_index" : "test", "_id" : "1" } }
{ "field1" : "value1" }
{ "delete" : { "_index" : "test", "_id" : "2" } }
{ "create" : { "_index" : "test", "_id" : "3" } }
{ "field1" : "value3" }
{ "update" : {"_id" : "1", "_index" : "test"} }
{ "doc" : {"field2" : "value2"} }
'
```

### Exploring Your Data

[点击](http://www.json-generator.com/)生成json数据[`accounts.json`](./accounts.json)，放到`/root/xiazai/`

```bash
cd /root/xiazai;
curl -H "Content-Type: application/json" -XPOST "localhost:9200/bank/_bulk?pretty&refresh" --data-binary "@accounts.json"
curl "localhost:9200/_cat/indices?v"
```

### The Search API

- URL

```bash
curl -X GET "localhost:9200/bank/_search?q=*&sort=account_number:asc"
```

- body

```bash
curl -X GET "localhost:9200/bank/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": { "match_all": {} },
  "sort": [
    { "account_number": "asc" }
  ]
}
'
```

#### Introducing the Query Language

- 原始

```bash
curl -X GET "localhost:9200/bank/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": { "match_all": {} }
}
'
```

- 限定size

```bash
curl -X GET "localhost:9200/bank/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": { "match_all": {} },
  "size": 1
}
'
```

- 限定起始

```bash
curl -X GET "localhost:9200/bank/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": { "match_all": {} },
  "from": 10,
  "size": 10
}
'
```

- 限定排序规则

```bash
curl -X GET "localhost:9200/bank/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": { "match_all": {} },
  "sort": { "balance": { "order": "desc" } }
}
'
```

### Executing Searches

- 返回指定字段

```bash
curl -X GET "localhost:9200/bank/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": { "match_all": {} },
  "_source": ["account_number", "balance"]
}
'
```

- 引入`match`，查询指定字段

```bash
curl -X GET "localhost:9200/bank/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": { "match": { "account_number": 20 } }
}
'
```

- 包含mill

```bash
curl -X GET "localhost:9200/bank/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": { "match": { "address": "mill" } }
}
'
```

- 包含mill 或 lane

```bash
curl -X GET "localhost:9200/bank/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": { "match": { "address": "mill lane" } }
}
'
```

- 包含 mill 和 lane

```bash
curl -X GET "localhost:9200/bank/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": { "match_phrase": { "address": "mill lane" } }
}
'
```

- 引入`bool`查询：must。和

```bash
curl -X GET "localhost:9200/bank/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must": [
        { "match": { "address": "mill" } },
        { "match": { "address": "lane" } }
      ]
    }
  }
}
'
```

- bool查询：should。或

```bash
curl -X GET "localhost:9200/bank/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "should": [
        { "match": { "address": "mill" } },
        { "match": { "address": "lane" } }
      ]
    }
  }
}
'
```

- 混合查询

```bash
curl -X GET "localhost:9200/bank/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must": [
        { "match": { "age": "40" } }
      ],
      "must_not": [
        { "match": { "state": "ID" } }
      ]
    }
  }
}
'
```


### Executing Filters

- 引入`filters`。

```bash
curl -X GET "localhost:9200/bank/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must": { "match_all": {} },
      "filter": {
        "range": {
          "balance": {
            "gte": 20000,
            "lte": 30000
          }
        }
      }
    }
  }
}
'
```

### Executing Aggregations

- 类似SQL GROUP BY

```bash
curl -X GET "localhost:9200/bank/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "group_by_state": {
      "terms": {
        "field": "state.keyword"
      }
    }
  }
}
'
```

等价于`SELECT state, COUNT(*) FROM bank GROUP BY state ORDER BY COUNT(*) DESC LIMIT 10;`

`group_by_state`可自定义。`size=0`表明不想看搜索结果。

- 嵌套查询

```bash
curl -X GET "localhost:9200/bank/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "group_by_state": {
      "terms": {
        "field": "state.keyword"
      },
      "aggs": {
        "average_balance": {
          "avg": {
            "field": "balance"
          }
        }
      }
    }
  }
}
'
```

`avg`和`term`是关键字。

- 增加降序排列

```bash
curl -X GET "localhost:9200/bank/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "group_by_state": {
      "terms": {
        "field": "state.keyword",
        "order": {
          "average_balance": "desc"
        }
      },
      "aggs": {
        "average_balance": {
          "avg": {
            "field": "balance"
          }
        }
      }
    }
  }
}
'
```

- 按年龄分组查询

```bash
curl -X GET "localhost:9200/bank/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "group_by_age": {
      "range": {
        "field": "age",
        "ranges": [
          {
            "from": 20,
            "to": 30
          },
          {
            "from": 30,
            "to": 40
          },
          {
            "from": 40,
            "to": 50
          }
        ]
      },
      "aggs": {
        "group_by_gender": {
          "terms": {
            "field": "gender.keyword"
          },
          "aggs": {
            "average_balance": {
              "avg": {
                "field": "balance"
              }
            }
          }
        }
      }
    }
  }
}
'
```

## ik分词器官方手册

https://github.com/medcl/elasticsearch-analysis-ik


```bash
curl -X PUT http://localhost:9200/index?pretty

curl -X POST http://localhost:9200/index/_mapping?pretty -H 'Content-Type:application/json' -d'
{
  "properties": {
      "content": {
          "type": "text",
          "analyzer": "ik_max_word",
          "search_analyzer": "ik_smart"
      }
  }
}'

curl -X POST http://localhost:9200/index/_create/1?pretty -H 'Content-Type:application/json' -d'
{"content":"美国留给伊拉克的是个烂摊子吗"}
'
curl -X POST http://localhost:9200/index/_create/2?pretty -H 'Content-Type:application/json' -d'
{"content":"公安部：各地校车将享最高路权"}
'
curl -X POST http://localhost:9200/index/_create/3?pretty -H 'Content-Type:application/json' -d'
{"content":"中韩渔警冲突调查：韩警平均每天扣1艘中国渔船"}
'
curl -X POST http://localhost:9200/index/_create/4?pretty -H 'Content-Type:application/json' -d'
{"content":"中国驻洛杉矶领事馆遭亚裔男子枪击 嫌犯已自首"}
'

curl -X POST http://localhost:9200/index/_search?pretty -H 'Content-Type:application/json' -d'
{
    "query" : { "match" : { "content" : "中国" }},
    "highlight" : {
        "pre_tags" : ["<tag1>", "<tag2>"],
        "post_tags" : ["</tag1>", "</tag2>"],
        "fields" : {
            "content" : {}
        }
    }
}
'
```

- mapping for ES7.3

```bash
curl -X PUT "localhost:9200/my_index?pretty" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": { 
      "title":    { "type": "text"  }, 
      "name":     { "type": "text"  }, 
      "age":      { "type": "integer" },  
      "created":  {
        "type":   "date", 
        "format": "strict_date_optional_time||epoch_millis"
      }
    }
  }
}
'
```


## Query DSL » Specialized queries » Distance feature query


curl -X PUT "localhost:9200/items?pretty" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "name": {
        "type": "keyword"
      },
      "production_date": {
        "type": "date"
      },
      "location": {
        "type": "geo_point"
      }
    }
  }
}
'


curl -X PUT "localhost:9200/items/_doc/1?refresh&pretty" -H 'Content-Type: application/json' -d'
{
  "name" : "chocolate",
  "production_date": "2018-02-01",
  "location": [-71.34, 41.12]
}
'
curl -X PUT "localhost:9200/items/_doc/2?refresh&pretty" -H 'Content-Type: application/json' -d'
{
  "name" : "chocolate",
  "production_date": "2018-01-01",
  "location": [-71.3, 41.15]
}
'
curl -X PUT "localhost:9200/items/_doc/3?refresh&pretty" -H 'Content-Type: application/json' -d'
{
  "name" : "chocolate",
  "production_date": "2017-12-01",
  "location": [-71.3, 41.12]
}
'

- Boost documents based on date


curl -X GET "localhost:9200/items/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must": {
        "match": {
          "name": "chocolate"
        }
      },
      "should": {
        "distance_feature": {
          "field": "production_date",
          "pivot": "7d",
          "origin": "now"
        }
      }
    }
  }
}
'

- Boost documents based on location


curl -X GET "localhost:9200/items/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must": {
        "match": {
          "name": "chocolate"
        }
      },
      "should": {
        "distance_feature": {
          "field": "location",
          "pivot": "1000m",
          "origin": [-71.3, 41.15]
        }
      }
    }
  }
}
'
## Painless Scripting Language [7.3] » Painless contexts » Ingest processor context

```bash
cd /root/xiazai/;
head -n 100 seats.json > seats_demo.json;
curl -X DELETE localhost:9200/seats
curl -X POST "localhost:9200/seats/seat?pretty" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "theatre":  { "type": "keyword" },
      "play":     { "type": "text"    },
      "actors":   { "type": "text"    },
      "row":      { "type": "integer" },
      "number":   { "type": "integer" },
      "cost":     { "type": "double"  },
      "sold":     { "type": "boolean" },
      "datetime": { "type": "date"    },
      "date":     { "type": "keyword" },
      "time":     { "type": "keyword" }
    }
  }
}
'


curl -X PUT "localhost:9200/_ingest/pipeline/seats?pretty" -H 'Content-Type: application/json' -d'
{
    "description": "update datetime for seats",
    "processors": [
      {
        "script": {
          "source": "String[] split(String s, char d) { int count = 0; for (char c : s.toCharArray()) { if (c == d) { ++count; } } if (count == 0) { return new String[] {s}; } String[] r = new String[count + 1]; int i0 = 0, i1 = 0; count = 0; for (char c : s.toCharArray()) { if (c == d) { r[count++] = s.substring(i0, i1); i0 = i1 + 1; } ++i1; } r[count] = s.substring(i0, i1); return r; } String[] dateSplit = split(ctx.date, (char)\"-\"); String year = dateSplit[0].trim(); String month = dateSplit[1].trim(); if (month.length() == 1) { month = \"0\" + month; } String day = dateSplit[2].trim(); if (day.length() == 1) { day = \"0\" + day; } boolean pm = ctx.time.substring(ctx.time.length() - 2).equals(\"PM\"); String[] timeSplit = split(ctx.time.substring(0, ctx.time.length() - 2), (char)\":\"); int hours = Integer.parseInt(timeSplit[0].trim()); int minutes = Integer.parseInt(timeSplit[1].trim()); if (pm) { hours += 12; } String dts = year + \"-\" + month + \"-\" + day + \"T\" + (hours < 10 ? \"0\" + hours : \"\" + hours) + \":\" + (minutes < 10 ? \"0\" + minutes : \"\" + minutes) + \":00+08:00\"; ZonedDateTime dt = ZonedDateTime.parse(dts, DateTimeFormatter.ISO_OFFSET_DATE_TIME); ctx.datetime = dt.getLong(ChronoField.INSTANT_SECONDS)*1000L;"
        }
      }
    ]
}
'

curl -X POST localhost:9200/seats/seat/_bulk?pipeline=seats -H "Content-Type: application/x-ndjson" --data-binary "@/root/xiazai/seats_demo.json"

curl -X GET "localhost:9200/seats/seat/1?pretty"
```


