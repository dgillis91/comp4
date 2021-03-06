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


class Operator:
    def __init__(self, token):
        self.token = token


class BinaryArithmeticOperator(Operator):
    def __init__(self, token, instruction):
        Operator.__init__(self, token)
        self.instruction = instruction


class RelationalOperator(Operator):
    def __init__(self, token, branch_false_op):
        Operator.__init__(self, token)
        self.branch_false_op = branch_false_op



NO_ACTION_SET = set([
    'program', 'block', 'stats', 'mstat', 'stat'
])

RELATIONAL_OPERATION_MAP = {
    '<': RelationalOperator('<', 'BRZPOS'),
    '>': RelationalOperator('>', 'BRZNEG'),
    '>>': RelationalOperator('>>', 'BRNEG'),
    '<<': RelationalOperator('<<', 'BRPOS'),
    '<>': RelationalOperator('<>', 'BRZERO'),
}

BINARY_OPERATION_MAP = {
    '+': BinaryArithmeticOperator('+', 'ADD'),
    '*': BinaryArithmeticOperator('*', 'MULT'),
    '/': BinaryArithmeticOperator('/', 'DIV')
}

OPERATION_MAP = {
    '/': 'DIV',
    '*': 'MULT'
}


name_generator = NameGenerator()


def code_generator_rec(target_writer, node):
    global name_generator
    if node is None:
        return
    elif node.label in NO_ACTION_SET:
        for child in node.children:
            code_generator_rec(target_writer, child)
        return
    elif node.label == 'variables' and node.tokens:
        name_generator.add_variable_to_list(node.tokens[0].payload, node.tokens[2].payload)
        for child in node.children:
            code_generator_rec(target_writer, child)
        return
    elif node.label == 'intk':
        target_writer.write('READ {}'.format(node.tokens[0].payload))
        return
    elif node.label == 'expr':
        # Expands down to N
        if len(node.children) == 1:
            code_generator_rec(target_writer, node.children[0])
        # Expands to subtraction
        else:
            code_generator_rec(target_writer, node.children[1])
            temp_var_name = name_generator.make_variable()
            target_writer.write('STORE {}'.format(temp_var_name))
            code_generator_rec(target_writer, node.children[0])
            target_writer.write('SUB {}'.format(temp_var_name))
        return 
    elif node.label == 'out':
        code_generator_rec(target_writer, node.children[0])
        temp_var_name = name_generator.make_variable()
        target_writer.write('STORE {}'.format(temp_var_name))
        target_writer.write('WRITE {}'.format(temp_var_name))
        return
    elif node.label == 'r':
        if node.tokens[0].group in ['digit', 'id']:
            target_writer.write('LOAD {}'.format(node.tokens[0].payload))
        # Parens
        else:
            code_generator_rec(target_writer, node.children[0])
        return 
    elif node.label == 'assign':
        code_generator_rec(target_writer, node.children[0])
        target_writer.write('STORE {}'.format(node.tokens[0].payload))
        return
    elif node.label == 'n':
        # Expands to a
        if len(node.tokens) == 0:
            code_generator_rec(target_writer, node.children[0])
        # Multiplication or division
        else:
            operator = BINARY_OPERATION_MAP[node.tokens[0].payload]
            code_generator_rec(target_writer, node.children[1])
            temp_var_name = name_generator.make_variable()
            target_writer.write('STORE {}'.format(temp_var_name))
            code_generator_rec(target_writer, node.children[0])
            target_writer.write('{} {}'.format(operator.instruction, temp_var_name))
        return 
    elif node.label == 'a':
        if len(node.tokens) == 0:
            code_generator_rec(target_writer, node.children[0])
        else:
            code_generator_rec(target_writer, node.children[1])
            temp_var_name = name_generator.make_variable()
            target_writer.write('STORE {}'.format(temp_var_name))
            code_generator_rec(target_writer, node.children[0])
            target_writer.write('ADD {}'.format(temp_var_name))
        return
    elif node.label == 'm':
        code_generator_rec(target_writer, node.children[0])
        if len(node.tokens) > 0:
            target_writer.write('MULT -1')
        return 
    elif node.label == 'iffy':
        # Right side of compare
        code_generator_rec(target_writer, node.children[2])
        temp_var_name = name_generator.make_variable()
        target_writer.write('STORE {}'.format(temp_var_name))
        code_generator_rec(target_writer, node.children[0])
        target_writer.write('SUB {}'.format(temp_var_name))
        relational_operator = node.children[1].tokens[0].payload
        relational_operation = RELATIONAL_OPERATION_MAP[relational_operator]
        # Requires two branches
        if relational_operator == '==':
            label_name = name_generator.make_label()
            target_writer.write('BRNEG {}'.format(label_name))
            target_writer.write('BRPOS {}'.format(label_name))
            code_generator_rec(target_writer, node.children[3])
            target_writer.write('{}: NOOP'.format(label_name))
        else:
            label_name = name_generator.make_label()
            target_writer.write('{} {}'.format(relational_operation.branch_false_op, label_name))
            code_generator_rec(target_writer, node.children[3])
            target_writer.write('{}: NOOP'.format(label_name))
        return
    elif node.label == 'loop':
        loop_label = name_generator.make_label()
        target_writer.write('{}: NOOP'.format(loop_label))
        break_label = name_generator.make_label()
        code_generator_rec(target_writer, node.children[2])
        temp_var_name = name_generator.make_variable()
        target_writer.write('STORE {}'.format(temp_var_name))
        code_generator_rec(target_writer, node.children[0])
        target_writer.write('SUB {}'.format(temp_var_name))
        relational_operator = node.children[1].tokens[0].payload
        relational_operation = RELATIONAL_OPERATION_MAP[relational_operator]
        if relational_operator == '==':
            target_writer.write('BRNEG {}'.format(break_label))
            target_writer.write('BRPOS {}'.format(break_label))
            code_generator_rec(target_writer, node.children[3])
        else:
            label_name = name_generator.make_label()
            target_writer.write('{} {}'.format(relational_operation.branch_false_op, break_label))
            code_generator_rec(target_writer, node.children[3])
        target_writer.write('BR {}'.format(loop_label))
        target_writer.write('{}: NOOP'.format(break_label))


def code_generator(target_writer, tree):
    global name_generator
    code_generator_rec(target_writer, tree)
    target_writer.write('STOP')
    for variable_name, variable_init in name_generator.variables:
        target_writer.write('{} {}'.format(variable_name, variable_init))
    return