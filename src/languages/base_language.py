from abc import ABC, abstractmethod

class BaseLanguage:
    @abstractmethod
    def get_compile_commands(self, filename: str, executable_name: str):
        pass

    @abstractmethod
    def get_execute_commands(self, filename: str):
        pass

    @abstractmethod
    def get_file_extension(self):
        pass