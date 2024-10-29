# import redis

# pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
# r = redis.Redis(connection_pool=pool)

# # Check specific keys
# r.keys('*')


# # Check number of keys in database
# r.dbsize()

# # set key value
# r.set('key', 'value')
# r.set('key', 'value', ex=10, nx=True)

# # get value by key
# value = r.get('key')

# # syntax : delete keys
# r.delete('key')
# r.delete('key1', 'key2', 'key3')

# # Check if key exists
# r.exists('key')

# # set expiry to key
# expireInSeconds = 30
# r.expire('key', expireInSeconds)


# # remove expiry from key
# r.persist('key')

# # find (remaining) time to live of a key
# r.ttl('key')

# # increment a number
# r.incr('key')

# # decrement a number
# r.decr('key')

# # use the method below to execute commands directly
# r.execute_command('SET', 'key', 'value')
