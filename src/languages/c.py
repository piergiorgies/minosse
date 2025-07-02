from abc import ABC
from src.languages.base_language import BaseLanguage

class C(BaseLanguage):
    def get_compile_commands(self, filename: str, executable_name: str):
        return [
            "/usr/bin/g++",
            filename,
            "-fuse-ld=/usr/bin/ld",
            "-o",
            executable_name,
        ]

    def get_execute_commands(self, filename: str):
        return [f"./{filename}"]

    def get_file_extension(self):
        return '.c'