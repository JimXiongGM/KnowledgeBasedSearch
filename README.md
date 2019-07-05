# Knowledge-Based Search Engine

基于知识图谱+Elasticsearch的法律文本搜索引擎。[官网](https://www.elastic.co/cn/downloads/)


## 安装配置elasticsearch

运行如下命令下载配置启动elasticsearch。

```bash
mkdir xiazai;
cd xiazai;
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.2.0-linux-x86_64.tar.gz;
tar -zxvf elasticsearch-7.2.0-linux-x86_64.tar.gz -C /opt/
# 创建非root账户
groupadd elsearch;
useradd elsearch -g elsearch -p elasticsearch;
chown -R elsearch:elsearch  /opt/elasticsearch-7.2.0;
# 配置外网访问等
echo '
# allow all hosts
network.host: 0.0.0.0
# set master node
cluster.initial_master_nodes: ["node-1"]
' >> /opt/elasticsearch-7.2.0/config/elasticsearch.yml;
# 临时增加vm内存
sysctl -w vm.max_map_count=262144;
# 使用elsearch用户启动elasticsearch
su elsearch;
cd /opt/elasticsearch-7.2.0;
# 默认bin/elasticsearch 
# -d 后台启动
bin/elasticsearch -d -Ecluster.name=xgm_cluster_name -Enode.name=xgm_node_name;
# 查询进程
ps aux|grep elasticsearch;
exit
```

默认端口是`9200`


## 安装配置Kibana

必须先启动elasticsearch，再启动kibana。

```bash
cd xiazai;
wget https://artifacts.elastic.co/downloads/kibana/kibana-7.2.0-linux-x86_64.tar.gz;
tar -xzvf kibana-7.2.0-linux-x86_64.tar.gz -C /opt/;
# 配置
echo '
# set ES host
elasticsearch.hosts: ["http://master:9200"]
# allow all hosts
server.host: "0.0.0.0"
# set language
i18n.locale: "zh-CN"
' >> /opt/kibana-7.2.0-linux-x86_64/config/kibana.yml;
# 后台启动
cd /opt/kibana-7.2.0-linux-x86_64;
# 默认 bin/kibana --allow-root
nohup bin/kibana --allow-root &
```


## 查看端口

```bash
lsof -i:5601
```







