# OTKV: Our KV-Archetecture

## Thomas Knickerbocker, Owen Ratgen

## CSCI5980: Special Topics - Cloud Computing

## 1. Implementation Process

We were able to get our KV-Store to use consistent hashing through a Python library called "uhashring" where it takes in N nodes that use N different hosts to ensure consistent hashing is being performed properly. We originally had our docker container working originally but we ran into a huge roadblock with DragonflyDB and need to discuss about whether or not we can still use it.

## 2. Statistics

1 KV-Store Final Results:
Total operations: 600
Total time: 0.86 seconds 
Throughput: 700.36 operations per second
Average Latency: 0.00858 seconds per operation
![Unknown](https://github.com/user-attachments/assets/86a1c0a7-d3b1-4ec2-8417-84912365c99d)

2 KV-Stores Final Results:
Total operations: 600
Total time: 0.75 seconds
Throughput: 804.66 operations per second
Average Latency: 0.00757 seconds per operation
![Unknown-2](https://github.com/user-attachments/assets/8b52d8db-5ed6-4615-b5ec-9237af92d232)

3 KV-Stores Final Results:
Total operations: 600
Total time: 0.67 seconds
Throughput: 900.71 operations per second
Average Latency: 0.00665 seconds per operation
![Unknown-3](https://github.com/user-attachments/assets/836ce81e-3181-482d-a766-a880ee0f13ba)

From the previous statistics and graphs, it is quite obvious that the more servers we have for consistent hashing, the lower the overall and average latency will be but the higher the overall throughput will be. There are tradeoffs to the two but I would take performance over number of operations in a heart beat.

## TO RUN:

Run 1 KV-Value nodes locally:
mac build (all separate terminals): $) redis-server <br/>
then:<br/>
python3 main.py<br/>

Run 2 KV-Value nodes locally:<br/>
mac build (all separate terminals): $) redis-server<br/>
redis-server --port 6380<br/>
then:<br/>
python3 main.py<br/>

Run 3 KV-Value nodes locally:<br/>
mac build (all separate terminals): $) redis-server<br/>
redis-server --port 6380<br/>
redis-server --port 6381<br/>
then:<br/>
python3 main.py<br/>

