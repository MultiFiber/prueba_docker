from django.core.cache import cache as django_cache


class MultifiberCache(object):

	def get(self, key_cache):
		print (django_cache._cache.keys())
		return django_cache.get(key_cache)

	def set(self, key_cache, value, time, **kwargs):
		return django_cache.set(key_cache, value, time)

	def delete(self, key_cache, **kwargs):
		return django_cache.delete(key_cache)

cache = MultifiberCache()