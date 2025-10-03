import redis 

class RedisConnect:
    def __init__(self):
        self.redis = redis.Redis(host='lilium_redis', port=6379, db=0)

    def set_key(self,key,value):
        self.redis.set(key, value)

    def get_key(self,key):
        return self.redis.get(key)    
