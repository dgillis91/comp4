# TODO: Replace prints with writing
# TODO: Refactor ... a bit
# TODO: Implement:
# loops
# ro
# if
# parens
class NameGenerator:
    def __init__(self, variable_prefix='T', label_prefix='L'):
        self._variable_counter = -1
        self._label_counter = -1
        self._variable_prefix = variable_prefix
        self._label_prefix = label_prefix
        self.variables = list()

    def make_label(self):
        self._label_counter += 1
        return '{}{}'.format(self._label_prefix, self._label_counter)

    def make_variable(self):
        self._variable_counter += 1
        var = '{}{}'.format(self._variable_prefix, self._variable_counter)
        self.add_variable_to_list(var)
        return var

    def add_variable_to_list(self, name, initial_value=0):
        self.variables.append((name, initial_value))


NO_ACTION_SET = set([
    'program', 'block', 'stats', 'mstat', 'stat'
])

OPERATION_MAP = {
    '/': 'DIV',
    '*': 'MULT'
}


name_generator = NameGenerator()


def code_generator_rec(target_path, node):
    global name_generator
    if node is None:
        return
    elif node.label in NO_ACTION_SET:
        for child in node.children:
            code_generator_rec(target_path, child)
        return
    elif node.label == 'variables' and node.tokens:
        name_generator.add_variable_to_list(node.tokens[0].payload, node.tokens[2].payload)
        for child in node.children:
            code_generator_rec(target_path, child)
        return
    elif node.label == 'intk':
        print('READ {}'.format(node.tokens[0].payload))
        return
    elif node.label == 'expr':
        # Expands down to N
        if len(node.children) == 1:
            code_generator_rec(target_path, node.children[0])
        # Expands to subtraction
        else:
            code_generator_rec(target_path, node.children[1])
            temp_var_name = name_generator.make_variable()
            print('STORE {}'.format(temp_var_name))
            code_generator_rec(target_path, node.children[0])
            print('SUB {}'.format(temp_var_name))
        return 
    elif node.label == 'out':
        code_generator_rec(target_path, node.children[0])
        temp_var_name = name_generator.make_variable()
        print('STORE {}'.format(temp_var_name))
        print('WRITE {}'.format(temp_var_name))
        return
    # TODO: Add support for parens.
    elif node.label == 'r':
        if node.tokens[0].group in ['digit', 'id']:
            print('LOAD {}'.format(node.tokens[0].payload))
        return 
    elif node.label == 'assign':
        code_generator_rec(target_path, node.children[0])
        print('STORE {}'.format(node.tokens[0].payload))
        return
    elif node.label == 'n':
        # Expands to a
        if len(node.tokens) == 0:
            code_generator_rec(target_path, node.children[0])
        # Multiplication or division
        else:
            operation = OPERATION_MAP[node.tokens[0].payload]
            code_generator_rec(target_path, node.children[1])
            temp_var_name = name_generator.make_variable()
            print('STORE {}'.format(temp_var_name))
            code_generator_rec(target_path, node.children[0])
            print('{} {}'.format(operation, temp_var_name))
        return 
    elif node.label == 'a':
        if len(node.tokens) == 0:
            code_generator_rec(target_path, node.children[0])
        else:
            code_generator_rec(target_path, node.children[1])
            temp_var_name = name_generator.make_variable()
            print('STORE {}'.format(temp_var_name))
            code_generator_rec(target_path, node.children[0])
            print('ADD {}'.format(temp_var_name))
        return
    elif node.label == 'm':
        code_generator_rec(target_path, node.children[0])
        if len(node.tokens) > 0:
            print('MULT -1')
        return 


def code_generator(target_path, tree):
    global name_generator
    code_generator_rec(target_path, tree)
    print('STOP')
    for variable_name, variable_init in name_generator.variables:
        print('{} {}'.format(variable_name, variable_init))
    return