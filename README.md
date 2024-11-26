# OTKV: Our KV-Archetecture

## Thomas Knickerbocker, Owen Ratgen

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

3 KV-Stores Final Results:
Total operations: 600
Total time: 0.67 seconds
Throughput: 900.71 operations per second
Average Latency: 0.00665 seconds per operation
![Unknown-3](https://github.com/user-attachments/assets/836ce81e-3181-482d-a766-a880ee0f13ba)

From the previous statistics and graphs, it is quite obvious that the more servers we have for consistent hashing, the lower the overall and average latency will be but the higher the overall throughput will be. There are tradeoffs to the two but I would take performance over number of operations in a heart beat.

#### DEVNOTES:

**IF RUNNING REGULARLY**

1. Go into directory kv_store, download rust if you haven't already here https://doc.rust-lang.org/cargo/getting-started/installation.html#:~:text=Install%20Rust%20and%20Cargo&text=Installing%20Rust%20using%20rustup%20will%20also%20install%20cargo%20.&text=It%20will%20download%20a%20script%2C%20and%20start%20the%20installation, and then, in the terminal, run:
```
cargo build --release
cargo run --release
```
3. Go into a new terminal and run:
```
pip3 install -r requirements.txt
python3 benchmark.py
```
from the base directory
