
## Prepare

```
yum install epel-release
yum install htop tinyproxy redis
```

## Set tinyproxy


## Use proxies

```python
>>> from adsl_server.proxy import Proxy
>>> _proxy = Proxy()
>>> proxy = _proxy.get()
>>> print(proxy)
>>> '1.1.1.1:9990'
```
