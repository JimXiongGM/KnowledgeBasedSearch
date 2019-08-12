# ELK环境搭建

## 目录

- [准备](#1)
- [mysql数据准备](#2)
- [安装配置elasticsearch 7.3](#3)
- [安装配置Logstash](#4)
- [更新mysql数据](#5)
- [查询效果](#6)
- [使用ik分词器](#7)
- [安装Kibana](#8)

## <p id=1>准备

本文参考网络资料，搭建Elasticsearch 7.3 + logstash 7.3 + kibana 7.3环境，并从mysql 8.0中通过logstash导入数据到es中，使用ik分词器建立索引并进行搜索。

将如下文件放入`/root/xiazai/`。点击可进入文件下载页面。

1. [`elasticsearch-7.3.0-linux-x86_64.tar.gz`](https://www.elastic.co/cn/downloads/elasticsearch)
2. [`elasticsearch-analysis-ik-7.3.0.zip`](https://github.com/medcl/elasticsearch-analysis-ik/releases)
3. [`logstash-7.3.0.tar.gz`](https://www.elastic.co/cn/downloads/logstash)
4. [`mysql-connector-java-8.0.16.jar`](https://dev.mysql.com/downloads/connector/j/) **下拉列表中选择Platform Independent，解压.tar.gz可得到该jar**
5. [`kibana-7.3.0-linux-x86_64.tar.gz`](https://www.elastic.co/cn/start)


## <p id=2>mysql数据准备

mysql环境搭建可参考[MySQL8.0环境搭建](https://github.com/JimXiongGM/BigDataProject/blob/master/Documentations/MySql_8.0.md)。

此处的参考资料为[How to keep Elasticsearch synced with a RDBMS using Logstash](https://www.elastic.co/blog/how-to-keep-elasticsearch-synchronized-with-a-relational-database-using-logstash)

进入mysql：`mysql -u root -p`，创建测试用表。

```sql
CREATE DATABASE es_db;
USE es_db;
DROP TABLE IF EXISTS es_table;
CREATE TABLE es_table (
  id BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY unique_id (id),
  client_name VARCHAR(256) NOT NULL,
  modification_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  insertion_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 测试数据
INSERT INTO es_table (id, client_name) VALUES (1, 'Jim Carrey');
INSERT INTO es_table (id, client_name) VALUES (2, 'Mike Myers');
INSERT INTO es_table (id, client_name) VALUES (3, 'Bryan Adams');
```


## <p id=3>安装配置elasticsearch 7.3

运行如下命令配置elasticsearch。首先需要配置好JAVA12，可以参考[这里](https://github.com/JimXiongGM/BigDataProject/blob/master/Documentations/NewUbuntu18.md#10).

将放到`/root/xiazai/`文件夹下。

```bash
cd /root/xiazai/;
tar -zxvf elasticsearch-7.3.0-linux-x86_64.tar.gz -C /opt/

# 创建非root账户 es必须使用非root用户运行
groupadd elsearch;
useradd elsearch -g elsearch -p elasticsearch;
chown -R elsearch:elsearch  /opt/elasticsearch-7.3.0;
cd /opt/elasticsearch-7.3.0;

# 配置外网访问等
echo '
# allow all hosts
# network.host: 0.0.0.0

# set master node
cluster.name: xgm_Cluster
node.name: xgm_Node
cluster.initial_master_nodes: xgm_Node
' >> ./config/elasticsearch.yml;

# 指定java12
# 使用java 8 也行，但是启动会有warning
sed -i 's/JAVA_HOME/JAVA12_HOME/g' ./bin/elasticsearch-env;

# 安装中文分词器
./bin/elasticsearch-plugin install file:///root/xiazai/elasticsearch-analysis-ik-7.3.0.zip

# 修改内存设置
sed -i 's/-Xms1g/-Xms2g/g' ./config/jvm.options;
sed -i 's/-Xmx1g/-Xmx10g/g' ./config/jvm.options;

# 使用elsearch用户启动elasticsearch
su elsearch
cd /opt/elasticsearch-7.3.0 && nohup ./bin/elasticsearch >> ./elasticsearch.log &
exit

# 非后台启动
# su elsearch
# cd /opt/elasticsearch-7.3.0 && ./bin/elasticsearch 

# 查询进程
ps aux|grep elasticsearch;

# 测试是否成功
curl -X GET "localhost:9200"
```


## <p id=4>安装配置Logstash

必须先启动elasticsearch。

参考资料为[这个](https://juejin.im/post/5d1886d4e51d45775b419c22)和[这个](https://zhuanlan.zhihu.com/p/40177683)。

此外，插件`logstash-input-jdbc`的用法在[这里](https://www.elastic.co/guide/en/logstash/current/plugins-inputs-jdbc.html)

```bash
cd /root/xiazai;
tar -xzvf logstash-7.3.0.tar.gz -C /opt/;
# test
# cd /opt/logstash-7.3.0;
# ./bin/logstash -e 'input { stdin { } } output { stdout {} }';
# CTRL-D  to exit
cd /opt/logstash-7.3.0/;

# 请自行修改内存设置
sed -i 's/-Xms1g/-Xms2g/g' ./config/jvm.options;
sed -i 's/-Xmx1g/-Xmx10g/g' ./config/jvm.options;

# 安装插件 logstash-input-jdbc
./bin/logstash-plugin install logstash-input-jdbc;

# 配置和mysql的交互
cp /root/xiazai/mysql-connector-java-8.0.16.jar /opt/logstash-7.3.0/lib/;
# 请自行修改数据库密码
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
    last_run_metadata_path => "/opt/logstash-7.3.0/data/mysql_test_1"
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
      index => "mysql_test_1"
      document_id => "%{[@metadata][_id]}"
  }
}
' > ./config/mysql_test_1.conf;

# 启动
./bin/logstash -f ./config/mysql_test_1.conf --config.reload.automatic

# 后台启动
# nohup ./bin/logstash -f ./config/mysql_test_1.conf --config.reload.automatic >> /logs/logstash.log &
```

开启新的终端，查看es中是否有新的index。

```bash
curl -X GET "localhost:9200/_cat/indices?v"

curl -X GET "localhost:9200/mysql_test_1/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": { "match_all": {} }
}
'
```

## <p id=5>更新mysql数据

保持logstash终端开启，开启新终端，向mysql中插入新的数据。

```sql
USE es_db;
INSERT INTO es_table (id, client_name) VALUES (4, '中国驻洛杉矶领事馆遭亚裔男子枪击 嫌犯已自首');
INSERT INTO es_table (id, client_name) VALUES (5, '领馆分为总领事馆，领事馆，副领事馆和领事代理处，负责管理当地本国侨民和其它领事事务。');
exit
```

继续使用命令确认更新。

```bash
curl -X GET "localhost:9200/_cat/indices?v"

curl -X GET "localhost:9200/mysql_test_1/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": { "match_all": {} }
}
'
```

## <p id=6>查询效果

查询index：`mysql_test_1`。

```bash
curl -X GET "localhost:9200/mysql_test_1/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": { "match": { "client_name": "领事馆" } },
  "size" : 1
}
'
curl -X GET "localhost:9200/mysql_test_1/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": { "match": { "client_name": "事馆领" } },
  "size" : 1
}
'
# 展示匹配结果
curl -X POST http://localhost:9200/mysql_test_1/_search?pretty -H 'Content-Type:application/json' -d'
{
    "query" : { "match" : { "client_name" : "领事馆" }},
    "highlight" : {
        "pre_tags" : ["<tag1>", "<tag2>"],
        "post_tags" : ["</tag1>", "</tag2>"],
        "fields" : {
            "client_name" : {}
        }
    }
}
'
```

可以看到，`领事馆`查询结果的最高分为`3.6995318`，`事馆领`查询结果的最高分为`3.6995318`。`领事馆`被<tag>标签按字切分。

## <p id=7>使用ik分词器

因为ES默认将中文按字切分，因此`领事馆`与`事馆领`的查询结果是相同的。接下来使用ik分词器，对logstash传入数据进行自动分词。

**注意**，不少网络资料显示应修改logstash的模板文件，并使用`template_overwrite`等关键字指定文件路径，但根据笔者实验，并不需要。只需要提前建立好索引，指定mapping值即可。对比过程可以参考笔者的另一篇文档[`logstash_template_对比.md`](./logstash_template_对比.md)。

另外，我们需要**手动增加索引**，并指定分词器。

```bash
# 建立索引 指定analyzer "client_name"为需要分词的字段
curl -X PUT http://localhost:9200/mysql_test_2?pretty
curl -X POST http://localhost:9200/mysql_test_2/_mapping?pretty -H 'Content-Type:application/json' -d'
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
# 请自行修改数据库密码
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
    last_run_metadata_path => "/opt/logstash-7.3.0/data/mysql_test_2"
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
        index => "mysql_test_2"
        document_id => "%{[@metadata][_id]}"
  }
}
' > ./config/mysql_test_2.conf;

# 启动
./bin/logstash -f ./config/mysql_test_2.conf --config.reload.automatic
```

新开一个终端。

```bash
curl -X GET "localhost:9200/_cat/indices?v"
curl -X GET "localhost:9200/mysql_test_2/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": { "match": { "client_name": "领事馆" } },
  "size" : 1
}
'
curl -X GET "localhost:9200/mysql_test_2/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": { "match": { "client_name": "事馆领" } },
  "size" : 1
}
'
# 展示匹配结果
curl -X POST http://localhost:9200/mysql_test_2/_search?pretty -H 'Content-Type:application/json' -d'
{
    "query" : { "match" : { "client_name" : "领事馆" }},
    "highlight" : {
        "pre_tags" : ["<tag1>", "<tag2>"],
        "post_tags" : ["</tag1>", "</tag2>"],
        "fields" : {
            "client_name" : {}
        }
    }
}
'
```

可以看到，`领事馆`查询结果的最高分为`0.95738393`，`事馆领`查询结果的最高分为`1.850861`。  且`领事馆`被<tag>标签正确分割。


## <p id=8>安装Kibana

必须先启动elasticsearch，再启动kibana。

```bash
cd /root/xiazai;
tar -xzvf kibana-7.3.0-linux-x86_64.tar.gz -C /opt/;
cd /opt/kibana-7.3.0-linux-x86_64;
# 配置
echo '
# set ES host
elasticsearch.hosts: ["http://localhost:9200"]
# allow all hosts
server.host: "0.0.0.0"
# set language
i18n.locale: "zh-CN"
' >> ./config/kibana.yml;
# 后台启动
nohup bin/kibana --allow-root &
```

访问`http://localhost:5601`即可。

## <p id=9>ES 7.3语法备忘

[ES 7.3语法备忘.md](./ES_7.3语法备忘.md)
