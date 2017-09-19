from ants.utils import RuleManager


class CompleteParser(RuleManager):
    NAME = "complete_parser"
    rules = ['replace_pos', 'remove_red']
    path = ['parsers/parsers/']