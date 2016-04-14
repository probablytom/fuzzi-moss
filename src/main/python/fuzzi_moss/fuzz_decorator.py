"""
@author probablytom
@author tws
"""
import ast
import inspect
from workflow_transformer import WorkflowTransformer


# noinspection PyPep8Naming
class fuzz(object):
    """
    The general purpose decorator for applying fuzzings to functions containing workflow steps.

    Attributes:
        enable_fuzzings is by default set to True, but can be set to false to globally disable fuzzing.
    """

    _fuzzings_cache = {}

    enable_fuzzings = True

    def __init__(self, fuzz_operator):
        self.fuzz_operator = fuzz_operator

    def __call__(self, func):
        def wrap(*args, **kwargs):

            if not fuzz.enable_fuzzings:
                return func(*args, **kwargs)

            func_source_lines = inspect.getsourcelines(func)[0]

            while func_source_lines[0][0:4] == '    ':
                for i in range(0, len(func_source_lines)):
                    func_source_lines[i] = func_source_lines[i][4:]

            func_source = ''.join(func_source_lines)

            # Mutate using the visitor class.
            original_syntax_tree = ast.parse(func_source)
            workflow_transformer = WorkflowTransformer(self.fuzz_operator)
            fuzzed_syntax_tree = workflow_transformer.visit(original_syntax_tree)

            # Compile the newly mutated function into a module and then extract the mutated function definition.
            compiled_module = compile(fuzzed_syntax_tree, inspect.getsourcefile(func), 'exec')

            fuzzed_function = func
            fuzzed_function.func_code = compiled_module.co_consts[0]
            fuzz._fuzzings_cache[(func, self.fuzz_operator)] = fuzzed_function

            # Execute the mutated function.
            return fuzzed_function(*args, **kwargs)

        return wrap

    @staticmethod
    def reset():
        fuzz._fuzzings_cache = {}
