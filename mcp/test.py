from cache import Cache

cache = Cache("cache")

# cache.set("key", "value", ttl=100)

print(cache.get("key"))