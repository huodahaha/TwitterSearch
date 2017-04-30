# start hbase service
./hbase-1.2.5/bin/start-hbase.sh
./hbase-1.2.5/bin/hbase-daemon.sh start thrift

# reset database
python ./reset_database.py
