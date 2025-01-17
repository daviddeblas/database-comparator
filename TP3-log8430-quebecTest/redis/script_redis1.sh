#!/bin/bash

## Run the container for Redis DB and run the tests
printf "\nRunning Benchmarks on Redis DB, results can be found in the redis folder \n\n"
docker-compose -f docker-compose.yml up --scale redis-master=1 --scale redis-replica=2 -d

# Initialisation des fichiers de résultats (écraser le contenu existant)
echo "Initializing results for Load Redis Tests" > ../results/outputLoadRedis.csv
echo "Initializing results for Run Redis Tests" > ../results/outputRunRedis.csv

cd ../YCSB
for i in {1..10}
do
  # Workload A
  printf "\n##################################################################################\n" >> ../results/outputLoadRedis.csv
  printf "Loading data workload A try $i\n" >> ../results/outputLoadRedis.csv
  ./bin/ycsb load redis -s -P workloads/workloada -p "redis.host=127.0.0.1" -p "redis.port=6379" -p "redis.clustert=true" >> ../results/outputLoadRedis.csv

  printf "\n##################################################################################\n" >> ../redis/outputRunRedis.csv
  printf "Running test workload A try $i\n" >> ../results/outputRunRedis.csv
  ./bin/ycsb run redis -s -P workloads/workloada -p "redis.host=127.0.0.1" -p "redis.port=6379" -p "redis.clustert=true" >> ../results/outputRunRedis.csv

  # Workload B
  printf "\n##################################################################################\n" >> ../results/outputLoadRedis.csv
  printf "Loading data workload B try $i\n" >> ../results/outputLoadRedis.csv
  ./bin/ycsb load redis -s -P workloads/workloadb -p "redis.host=127.0.0.1" -p "redis.port=6379" -p "redis.clustert=true" >> ../results/outputLoadRedis.csv

  printf "\n##################################################################################\n" >> ../results/outputRunRedis.csv
  printf "Running test workload B try $i\n" >> ../results/outputRunRedis.csv
  ./bin/ycsb run redis -s -P workloads/workloadb -p "redis.host=127.0.0.1" -p "redis.port=6379" -p "redis.clustert=true" >> ../results/outputRunRedis.csv

  # Workload C
  printf "\n##################################################################################\n" >> ../results/outputLoadRedis.csv
  printf "Loading data workload C try $i\n" >> ../results/outputLoadRedis.csv
  ./bin/ycsb load redis -s -P workloads/workloadc -p "redis.host=127.0.0.1" -p "redis.port=6379" -p "redis.clustert=true" >> ../results/outputLoadRedis.csv

  printf "\n##################################################################################\n" >> ../results/outputRunRedis.csv
  printf "Running test workload C try $i\n" >> ../results/outputRunRedis.csv
  ./bin/ycsb run redis -s -P workloads/workloadc -p "redis.host=127.0.0.1" -p "redis.port=6379" -p "redis.clustert=true" >> ../results/outputRunRedis.csv
done

cd ../redis
docker-compose -f docker-compose.yml down -v
printf "\nFinished benchmarking Redis DB \n\n"
