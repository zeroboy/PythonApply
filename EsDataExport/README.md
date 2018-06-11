#### 	多线程导出ES数据到csv(前端grid生成查询参数)


![github](https://zeroboy.cn/clienttasklist.jpg "github")

```ruby
异步导出思路：

1.客户端grid生成查询参数并base64编码后请求sh脚本  
  nohup bash  syncexport.sh eyJnc3NpZCI6IjIwMTA0IiwibG9ndHlwZSI6ImJvbHVhbmFseSIsImxvZ2RhdGVfc3RhcnQiOiIyMDE4LTA2LTAxIDAwOjAwIiwibG9nZGF0ZV9lbmQiOiIyMDE4LTA2LTA2IDAwOjAwIiwibWFqb3Jsb2d0eXBlIjoiSm9pbkxvZ04iLCJfc2VhcmNoIjpmYWxzZSwibmQiOjE1Mjg0NTI2MTEzODIsInJvd3MiOjUwLCJwYWdlIjoxLCJzaWR4IjoiY3RpbWUiLCJzb3JkIjoiZGVzYyIsInJlY29yZHMiOjExNDEwNn0=  >/dev/null 2>&1 &

2.脚本将参数继续传给py执行

3.py生成 初始化数据库数据并执行 然后根据数据量生成相应数量的线程 客户端查看生成任务展示

4.py 监听线程数变化 回调更新数据库数据

配置
  ES    三台集群(单台4核32G)
  硬盘  阿里云ssd(IO较差 IO在主要生成时间中占比最重)


