EXECUTION_RESULTS = {
    'ACCEPTED': 1,
    'WRONG_ANSWER': 2,
    'TIME_LIMIT': 3,
    'MEMORY_LIMIT': 4,
    'COMPILATION_ERROR': 5
}

class CompilationError(Exception):
    
    stderr: str = None

    def __init__(self, stderr, *args):
        super().__init__(*args)
        self.stderr = stderr
