from mathjax_render import rendering

args = dict(
        table = '`question_db_offline`.`youxuepai_parse_0807`',
        is_latex = True,  #是否含有latex
        is_mml = True,   #是否含有mathml
        latex_tag = '<span class="afanti-latex">'
)

rendering.start(args)

record_dict = {
        'question_html': '',
        'option_html': '',
        'spider_source': 4,
        'answer_all_html': ''
}

cols, values = zip(*record_dict.items())

sql = 'insert into {table} ({cols}) values ({values})'.format(
        table= 'youxuepai_parse_0807',
        cols= ', '.join(['`%s`' % col for col in cols]),
        values= ', '.join(['`%s`' for col in cols])
)