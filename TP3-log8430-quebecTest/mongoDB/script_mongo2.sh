#!/bin/bash

## Run the container for MongoDB and run the tests
printf "\nRunning Benchmarks on MongoDB, results can be found in the results folder \n\n"
docker-compose -f docker-compose2.yml up -d

# Wait for containers to be fully ready
sleep 20

# Initialize the replica set
echo "Initializing MongoDB Replica Set..."
docker exec primary mongosh --eval '
rs.initiate({
  _id: "myReplicaSet",
  members: [
    {_id: 0, host: "192.168.5.2:27017", priority: 2},
    {_id: 1, host: "192.168.5.3:27017", priority: 1},
    {_id: 2, host: "192.168.5.4:27017", priority: 1},
    {_id: 3, host: "192.168.5.5:27017", priority: 1},
    {_id: 4, host: "192.168.5.6:27017", priority: 1}
  ]
});
'

# Wait for the PRIMARY node to be elected
echo "Waiting for the replica set to elect a PRIMARY..."
sleep 20

docker exec primary mongosh --eval 'rs.status()'

cd ../YCSB

# Écraser les fichiers de résultats au début
echo "Initializing results for Load Async Mongo Tests - 3 nodes configuration" > ../results/outputLoadAsyncMongo3tests2.csv
echo "Initializing results for Run Async Mongo Tests - 3 nodes configuration" > ../results/outputRunAsyncMongo3tests2.csv

for i in {1..10}
do
  # Supprimer la collection existante avant de charger les données
  docker exec primary mongosh --eval 'db.getSiblingDB("ycsb").usertable.drop()'

  printf "\n##################################################################################\n" >> ../results/outputLoadAsyncMongo3tests2.csv
  printf "Loading workload A try $i\n" >> ../results/outputLoadAsyncMongo3tests2.csv
  ./bin/ycsb load mongodb-async -s -P workloads/workloada -p mongodb.url="mongodb://192.168.5.2:27017/ycsb?replicaSet=myReplicaSet" >> ../results/outputLoadAsyncMongo3tests2.csv

  printf "\n##################################################################################\n" >> ../results/outputRunAsyncMongo3tests2.csv
  printf "Running test workload A try $i\n" >> ../results/outputRunAsyncMongo3tests2.csv
  ./bin/ycsb run mongodb-async -s -P workloads/workloada -p mongodb.url="mongodb://192.168.5.2:27017/ycsb?replicaSet=myReplicaSet" >> ../results/outputRunAsyncMongo3tests2.csv

  # Repeat for workloads B and C
  for workload in "workloadb" "workloadc"; do
    # Supprimer la collection existante avant de charger les données
    docker exec primary mongosh --eval 'db.getSiblingDB("ycsb").usertable.drop()'

    printf "\n##################################################################################\n" >> ../results/outputLoadAsyncMongo3tests2.csv
    printf "Loading workload $workload try $i\n" >> ../results/outputLoadAsyncMongo3tests2.csv
    ./bin/ycsb load mongodb-async -s -P workloads/$workload -p mongodb.url="mongodb://192.168.5.2:27017/ycsb?replicaSet=myReplicaSet" >> ../results/outputLoadAsyncMongo3tests2.csv

    printf "\n##################################################################################\n" >> ../results/outputRunAsyncMongo3tests2.csv
    printf "Running test workload $workload try $i\n" >> ../results/outputRunAsyncMongo3tests2.csv
    ./bin/ycsb run mongodb-async -s -P workloads/$workload -p mongodb.url="mongodb://192.168.5.2:27017/ycsb?replicaSet=myReplicaSet" >> ../results/outputRunAsyncMongo3tests2.csv
  done
done

cd ../mongoDB
docker-compose -f docker-compose2.yml down -v
printf "\nFinished benchmarking MongoDB \n\n"
