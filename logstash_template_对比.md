# logstash模板文件使用对比

## 目录

- [指定模板文件: ik_max_word.json + 自动索引](#1)
- [不指定模板文件 + 手动索引](#3)
- [指定模板文件 + 手动索引](#4)
- [总结对比](#5)

## <p id=1>指定模板文件: ik_max_word.json + 自动索引

接上文[`ELK环境搭建`](./ELK环境搭建.md)。

**注意**，这里没有手动创建索引，通过logstash自动创建。

使用`mysql_test_3.conf`文件。相比上文的配置文件`mysql_test_1.conf`，只增加了`template_overwrite`、`template`两个字段。其中`template`指向`ik_mysql_test_3.json`文件，该文件只增加了`"analyzer": "ik_max_word"`字段。该json文件如何获得？仔细查看上文打开的logstash终端的输出，找到如下信息，将其中的`manage_template`字段复制出来即可。

```bash
[INFO ][logstash.outputs.elasticsearch] Attempting to install template {:manage_template=>{"index_patterns"=>"logstash-*", "version"=>60001,  ...... >"half_float"}}}}}}}
```

```bash
cd /opt/logstash-7.3.0/;

echo '{
    "index_patterns": "logstash-*",
    "version": 60001,
    "settings": {
        "index.refresh_interval": "5s",
        "number_of_shards": 1
    },
    "mappings": {
        "dynamic_templates": [
            {
                "message_field": {
                    "path_match": "message",
                    "match_mapping_type": "string",
                    "mapping": {
                        "type": "text",
                        "norms": false,
                        "analyzer": "ik_max_word",
                        "search_analyzer": "ik_smart"
                    }
                }
            },
            {
                "string_fields": {
                    "match": "*",
                    "match_mapping_type": "string",
                    "mapping": {
                        "type": "text",
                        "norms": false,
                        "analyzer": "ik_max_word",
                        "search_analyzer": "ik_smart",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    }
                }
            }
        ],
        "properties": {
            "@timestamp": {
                "type": "date"
            },
            "@version": {
                "type": "keyword"
            },
            "geoip": {
                "dynamic": true,
                "properties": {
                    "ip": {
                        "type": "ip"
                    },
                    "location": {
                        "type": "geo_point"
                    },
                    "latitude": {
                        "type": "half_float"
                    },
                    "longitude": {
                        "type": "half_float"
                    }
                }
            }
        }
    }
}' > ./config/ik_max_word.json

echo 'input {
  jdbc {
    jdbc_driver_library => "/opt/logstash-7.3.0/lib/mysql-connector-java-8.0.16.jar"
    jdbc_driver_class => "com.mysql.jdbc.Driver"
    jdbc_connection_string => "jdbc:mysql://localhost:3306/es_db?characterEncoding=utf8&useSSL=false"
    jdbc_user => "root"
    jdbc_password => "xiong"
    jdbc_paging_enabled => true
    tracking_column => "unix_ts_in_secs"
    use_column_value => true
    tracking_column_type => "numeric"
    schedule => "*/10 * * * * *"    # 10 seconds
    last_run_metadata_path => "/opt/logstash-7.3.0/data/mysql_test_3"
    statement => "SELECT *, UNIX_TIMESTAMP(modification_time) AS unix_ts_in_secs FROM es_table WHERE (UNIX_TIMESTAMP(modification_time) > :sql_last_value AND modification_time < NOW()) ORDER BY modification_time ASC"
  }
}
filter {
  mutate {
    copy => { "id" => "[@metadata][_id]"}
    remove_field => ["id", "@version", "unix_ts_in_secs"]
  }
}
output {
  # stdout { codec =>  "rubydebug"}
  elasticsearch {
        index => "mysql_test_3"
        document_id => "%{[@metadata][_id]}"
        template_overwrite => true
        template => "/opt/logstash-7.3.0/config/ik_max_word.json"
  }
}
' > ./config/mysql_test_3.conf;

# 启动
./bin/logstash -f ./config/mysql_test_3.conf --config.reload.automatic
```

### <p id=2>查询效果

查询index：`mysql_test_3`。

```bash
curl -X GET "localhost:9200/_cat/indices?v"
curl -X GET "localhost:9200/mysql_test_3/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": { "match": { "client_name": " 领事馆" } },
  "size" : 1
}
'
curl -X GET "localhost:9200/mysql_test_3/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": { "match": { "client_name": "事馆领" } },
  "size" : 1
}
'
```

可以看到，`领事馆`查询结果的最高分为`3.6995318`，`事馆领`查询结果的最高分为`3.6995318`。没有变化。


## <p id=3>不指定模板文件 + 手动索引

不指定模板文件，**手动增加索引**，并指定分词器。详见[`ELK环境搭建`](./ELK环境搭建.md)，此方法是成功的。

## <p id=4>指定模板文件 + 手动索引

指定模板文件`ik_max_word.json`，**手动增加索引**，并指定分词器。

```bash
curl -X PUT http://localhost:9200/mysql_test_4?pretty
curl -X POST http://localhost:9200/mysql_test_4/_mapping?pretty -H 'Content-Type:application/json' -d'
{
  "properties": {
      "client_name": {
          "type": "text",
          "analyzer": "ik_max_word",
          "search_analyzer": "ik_smart"
      }
  }
}'
curl -X GET "localhost:9200/_cat/indices?v"

cd /opt/logstash-7.3.0/;
echo 'input {
  jdbc {
    jdbc_driver_library => "/opt/logstash-7.3.0/lib/mysql-connector-java-8.0.16.jar"
    jdbc_driver_class => "com.mysql.jdbc.Driver"
    jdbc_connection_string => "jdbc:mysql://localhost:3306/es_db?characterEncoding=utf8&useSSL=false"
    jdbc_user => "root"
    jdbc_password => "xiong"
    jdbc_paging_enabled => true
    tracking_column => "unix_ts_in_secs"
    use_column_value => true
    tracking_column_type => "numeric"
    schedule => "*/10 * * * * *"    # 10 seconds
    last_run_metadata_path => "/opt/logstash-7.3.0/data/mysql_test_4"
    statement => "SELECT *, UNIX_TIMESTAMP(modification_time) AS unix_ts_in_secs FROM es_table WHERE (UNIX_TIMESTAMP(modification_time) > :sql_last_value AND modification_time < NOW()) ORDER BY modification_time ASC"
  }
}
filter {
  mutate {
    copy => { "id" => "[@metadata][_id]"}
    remove_field => ["id", "@version", "unix_ts_in_secs"]
  }
}
output {
  # stdout { codec =>  "rubydebug"}
  elasticsearch {
        index => "mysql_test_4"
        document_id => "%{[@metadata][_id]}"
        template_overwrite => true
        template => "/opt/logstash-7.3.0/config/ik_max_word.json"
  }
}
' > ./config/mysql_test_4.conf;

# 启动
./bin/logstash -f ./config/mysql_test_4.conf --config.reload.automatic
```
new window

```bash

curl -X GET "localhost:9200/mysql_test_4/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": { "match": { "client_name": "领事馆" } },
  "size" : 1
}
'
curl -X GET "localhost:9200/mysql_test_4/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": { "match": { "client_name": "事馆领" } },
  "size" : 1
}
'
curl -X GET "localhost:9200/_cat/indices?v"
```

可以看到，`领事馆`查询结果的最高分为`0.95738393`，`事馆领`查询结果的最高分为`1.850861`。也是成功的。

## <p id=5>总结对比

由实验可知，如果手动增加索引并指定哪个字段需要分词，logstash不论是否增加模板文件都能成功。反之，如果由logstash自动增加索引，无论是否指定模板都会失败。因此手动增加索引，不指定模板是较好的选择。