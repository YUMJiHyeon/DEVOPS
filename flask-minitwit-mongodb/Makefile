define CLEAN_SCRIPT
use test;
db.dropDatabase();
endef

cleandb:
	mongo ${CLEAN_SCRIPT}

filldb:
	python sqlite_to_mongo.py

dumpdb:
	mongodump  --db test --gzip

start:
	python minitwit.py

startdb:
	brew services start mongodb-community@4.2

stopdb:
	brew services stop mongodb-community@4.2

deploy_local:
	vagrant up

deploy_remote:
	rm db_ip.txt | vagrant up | python store_ip.py
