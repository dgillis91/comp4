
class NameGenerator:
    def __init__(self, variable_prefix='T', label_prefix='L'):
        self._variable_counter = -1
        self._label_counter = -1
        self._variable_prefix = variable_prefix
        self._label_prefix = label_prefix

    def make_label(self):
        self._label_prefix += 1
        return '{}{}'.format(self._label_prefix, self._label_counter)

    def make_variable(self):
        self._variable_prefix += 1
        return '{}{}'.format(self._variable_prefix, self._variable_counter)


NO_ACTION_SET = set([
    'program', 'block', 'stats', 'mstat', 'stat'
])


variables = list()

def code_generator_rec(target_path, node):
    global variables
    if node is None:
        return
    elif node.label in NO_ACTION_SET:
        for child in node.children:
            code_generator_rec(target_path, child)
        return
    elif node.label == 'variables' and node.tokens:
        variables.append((node.tokens[0].payload, node.tokens[2].payload))
        for child in node.children:
            code_generator_rec(target_path, child)
        return
    elif node.label == 'intk':
        print('READ {}'.format(node.tokens[0].payload))
        return



def code_generator(target_path, tree):
    global variables
    code_generator_rec(target_path, tree)
    print('STOP')
    for variable_name, variable_init in variables:
        print('{} {}'.format(variable_name, variable_init))
    return