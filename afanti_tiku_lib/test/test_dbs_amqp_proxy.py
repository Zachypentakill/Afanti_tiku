
from afanti_tiku_lib.dbs.amqp_proxy import RabbitMQProxy

rb_proxy = RabbitMQProxy()

queue = rb_proxy.make_queue('', 'test', raw=False)

queue.put([1,2])

print(queue.get())
