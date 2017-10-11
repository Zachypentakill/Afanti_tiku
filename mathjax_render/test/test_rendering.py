
from mathjax_render import rendering

args = dict(
    db = 'test',
    table = 'test_latex',
    cols = [('a', 'b')],
    update_cols = {},
    condition = '',
    latex_tag = '',
    is_latex = True,
    is_mml = False,
    test = True,
)

rendering.start(args)
