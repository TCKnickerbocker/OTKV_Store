# OTKV: Our KV-Archetecture
## Thomas Knickerbocker, Owen Ratgen 
## CSCI5980: Special Topics - Cloud Computing

## 1. Design Decisions
The architecture of OTKV consists of a primary thread which handles incoming requests by delegating them to a thread handler based upon their request type. The thread handler then calls the appropriate function, which will return a value indicating whether it was successful or not. If returns don't occur for some time, another thread will be started for the same function, and after a timeout, if neither thread has returned a failure is issued to the client.
Locks are utilized for operations involving writing to the kv store to maintain a synchronous system, however this can lead to bottlenecks, especially if the thread currently acquiring the lock sporadically dies, so future changes to alleviate this issue are proposed in the 'future changes' section below.

### File Structure:
- benchmark.py: a testfile that can be run to evaluate the latency and throughput of the kv store
-  base.py: the base of the flask app. Includes logging and handlers for different operations
- set_value.py: handles value setting within the kv store
- get_value.py: handles value retrieval within the kv store
- delete_key.py: handles key deletion within the kv store
- kc_store.py: initializes the kv_store variable and its accompanying lock


## 2. Challenges faced & how they were Overcame:
Thread Safety: One of the major challenges was ensuring thread safety for the kv_store. To avoid race conditions, we implemented locks sections of code that wrote to or deleted from the key value store.
Timeout Handling: Implementing a robust timeout mechanism required careful management of threads. Threads that exceeded the defined timeout were terminated and retried.
Logging: Logging operations in a multi-threaded environment had to be handled carefully to avoid bottlenecks. We used a separate logging thread to asynchronously write operations to the log file, and would periodically write the contents of the entire kv_store to a separate logfile.

## 3. Assumptions:
- Run under the assumption that all requests are incoming to a single port, and there is only one node working to handle them 
- Timeouts and retry mechanisms were set to conservative values, assuming that most requests would be processed quickly under normal conditions.

## 4. Potential improvements and features for future versions:
- Distributed Architecture: Future versions could include a distributed setup where the key-value store is spread across multiple nodes, enabling horizontal scaling.
- Timeout detection for nodes acquiring locks: could be implemented via 'pulses' being sent from worker threads to the primary control thread
- Faster Task Delegation via having a layer of controlets handle more of the returning logic once a request has been received by the server 
- Chaining nodes and 'dirty copies' to  allow for faster synchronous responses at distributed scale
- Adding a queue of tasks to the multiple threads working under the master thread, and perhaps having a thread-safe way to access that
- Adding data replication to nodes increased safety in the event of failures
- Improved hashing of kv_store via a custom class and data structure
- Machine learning to adjust which jobs are sent to which nodes via estimation of task length, task priority, and efficiency of respective nodes




#### DEVNOTES:
Run on local:
mac build: $) docker run -p 6379:6379 --ulimit memlock=-1 docker.dragonflydb.io/dragonflydb/dragonfly
or redis-server for regular redis
then:
python3 main.py
or 
docker build compose
