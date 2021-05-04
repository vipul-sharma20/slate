import redis


class Cache:
    def __init__(self, type="in_memory", **kwargs):
        self.type = type
        if type == "redis":
            self.cache = redis.Redis(host=kwargs["host"], port=kwargs["port"], db=0)
        else:
            self.cache = {}

        self.func_map = {
            "redis": {"set": self._set_redis_key, "get": self._get_redis_key},
            "in_memory": {
                "set": self._set_in_memory_key,
                "get": self._get_in_memory_key,
            },
        }

    def set(self, key, value):
        self.func_map[self.type]["set"](key, value)

    def get(self, key):
        return self.func_map[self.type]["get"](key)

    def _set_redis_key(self, key: str, value):
        self.cache.set(key, value)

    def _set_in_memory_key(self, key, value):
        self.cache[key] = value

    def _get_redis_key(self, key):
        return self.cache.get(key)

    def _get_in_memory_key(self, key):
        return self.cache.get(key)
