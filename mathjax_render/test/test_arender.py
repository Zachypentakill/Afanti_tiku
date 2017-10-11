
import asyncio
from aphantomjs import APhantom
from parser import Parser


tex = r'$\frac{gggggg}{vvvvvvv}$'

tex = r"""
<div style="background:white;"><fieldset id="6df1ed57-9e9b-4bc0-aa93-9c7b5d6cc8cf" class="quesborder" s="math"><div class="pt1"><!--B1--><span class="qseq"></span>（2016春•惠山区期末）在代数式<span class="afanti-latex" latex-base64="XGZyYWN7eF57Mn19e3h9">\(\displaystyle\frac{x^{2}}{x}\)</span>、<span class="afanti-latex" latex-base64="XGZyYWN7MX17Mn0=">\(\displaystyle\frac{1}{2}\)</span>、<span class="afanti-latex" latex-base64="XGZyYWN7eF57Mn0rMX17Mn0=">\(\displaystyle\frac{x^{2}+1}{2}\)</span>、<span class="afanti-latex" latex-base64="XGZyYWN7M3h5fXvPgH0=">\(\displaystyle\frac{3xy}{π}\)</span>、<span class="afanti-latex" latex-base64="XGZyYWN7M317eCt5fQ==">\(\displaystyle\frac{3}{x+y}\)</span>、a+<span class="afanti-latex" latex-base64="XGZyYWN7MX17bX0=">\(\displaystyle\frac{1}{m}\)</span>中，分式的个数有（　　）<!--E1--></div><div class="pt2"><!--B2--><table style="width:100%" class="ques quesborder"><tr><td style="width:23%" class="selectoption"><label class="">A．2个</label></td><td style="width:23%" class="selectoption"><label class=" s">B．3个</label></td><td style="width:23%" class="selectoption"><label class="">C．4个</label></td><td style="width:23%" class="selectoption"><label class="">D．5个</label></td></tr></table><!--E2--></div><div class="ptline"></div><div class="pt3"><!--B3--><em>【考点】</em><a href="http://www.jyeoo.com/math/ques/detail/6df1ed57-9e9b-4bc0-aa93-9c7b5d6cc8cf" onclick="openPointCard('math','61');return false;">分式的定义</a>．<!--E3--></div><div class="pt5"><!--B5--><em>【分析】</em>根据分式的定义，可以判断出题中六个代数式只有3个为分式，由此得出结论．<!--E5--></div><div class="pt6"><!--B6--><em>【解答】</em>解：在代数式<span class="afanti-latex" latex-base64="XGZyYWN7eF57Mn19e3h9">\(\displaystyle\frac{x^{2}}{x}\)</span>、<span class="afanti-latex" latex-base64="XGZyYWN7MX17Mn0=">\(\displaystyle\frac{1}{2}\)</span>、<span class="afanti-latex" latex-base64="XGZyYWN7eF57Mn0rMX17Mn0=">\(\displaystyle\frac{x^{2}+1}{2}\)</span>、<span class="afanti-latex" latex-base64="XGZyYWN7M3h5fXvPgH0=">\(\displaystyle\frac{3xy}{π}\)</span>、<span class="afanti-latex" latex-base64="XGZyYWN7M317eCt5fQ==">\(\displaystyle\frac{3}{x+y}\)</span>、a+<span class="afanti-latex" latex-base64="XGZyYWN7MX17bX0=">\(\displaystyle\frac{1}{m}\)</span>中，<br />分式有<span class="afanti-latex" latex-base64="XGZyYWN7eF57Mn19e3h9">\(\displaystyle\frac{x^{2}}{x}\)</span>，<span class="afanti-latex" latex-base64="XGZyYWN7M317eCt5fQ==">\(\displaystyle\frac{3}{x+y}\)</span>，a+<span class="afanti-latex" latex-base64="XGZyYWN7MX17bX0=">\(\displaystyle\frac{1}{m}\)</span>，<br />∴分式的个数是3个．<br />故选B．<!--E6--></div><div class="pt7"><!--B7--><em>【点评】</em>本题考查了分式的 定义，解题的关键是熟悉分式的定义．本题属于基础题，难度不大，解决该题型题目时，将分式的定义来观察各代数式即可．<!--E7--></div><div class="pt9"><span class="qcp">声明：本试题解析著作权属菁优网所有，未经书面同意，不得复制发布。</span><!--B9--><span>答题：<input type="button" class="vip210" disabled />曹先生老师　2016/5/3</span><!--E9--></div></fieldset><span class="fieldtip"><label style="float:right;margin-right:10px" title="“难度系数(系数值区间为0~1)”反映试题的难易程度。&#13系数值越大，试题就越容易；系数值越小，试题难度越大">难度：<em style="color:red">0.80</em></label><label style="float:right;margin-right:10px" title="“真题次数”指试题在大型考试中出现的次数。&#13次数越多，试题常考指数越高；次数越少，试题常考指数越低。">真题：<em style="color:red">3</em></label><label style="float:right;margin-right:10px" title="“组卷次数”指试题在用户组卷过程中被使用的次数。&#13次数越多，试题热度越高；次数越少，试题热度越低。">组卷：<em style="color:red">88</em></label><a href="http://www.jyeoo.com/math/ques/detail/6df1ed57-9e9b-4bc0-aa93-9c7b5d6cc8cf" onclick="closeBox();Test2.testDoing(this,'math','6df1ed57-9e9b-4bc0-aa93-9c7b5d6cc8cf',3);return false"><em class="btn-ui test"></em>训练</a><a href="http://www.jyeoo.com/math/ques/detail/6df1ed57-9e9b-4bc0-aa93-9c7b5d6cc8cf" onclick="closeBox();Test2.favorite(this,'math','6df1ed57-9e9b-4bc0-aa93-9c7b5d6cc8cf',0);return false"><em class="btn-ui favo"></em>收藏</a><a href="javascript:void(0)" onclick="openConfirm('【下载确认】','math','6df1ed57-9e9b-4bc0-aa93-9c7b5d6cc8cf','1')"><em class="btn-ui down"></em>下载</a></span></div>
"""


parser = Parser()

async def run(aphantom):
    p = await aphantom.render(tex)
    # p = p.decode()
    x = parser.get_render_html(p)
    print(x)

    with open('/tmp/t/e.html', 'w') as fd:
        fd.write(x)


def test():
    loop = asyncio.get_event_loop()
    aphantom = APhantom(executable_path='phantomjs')
    asyncio.ensure_future(aphantom.init_queue())
    asyncio.ensure_future(run(aphantom))
    loop.run_forever()


if __name__ == '__main__':
    test()
