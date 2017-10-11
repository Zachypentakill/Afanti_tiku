
import time
import asyncio
from mathjax_render.render import RenderProxy

render_proxy = RenderProxy()


async def test():

    tm = time.time()
    for _ in range(100):
        rs = await render_proxy.render('$\\frac{2}{3}$')

    s = time.time() - tm
    ss = s / 100
    print('-------------------', s, ss)


loop = asyncio.get_event_loop()
ts = asyncio.wait([test(), test(), test(), test(), test(), test(), test(), test(), test(), test()])
loop.run_until_complete(ts)
