from setuptools import setup

setup(
    name='code_scan',
    version='1.0',
    author='DC',
    description='A command-line tool to run security tools within a docker container',
    packages=['codescan'],
    install_requires=[
        'docker',
        'gitpython'
    ],
    entry_points={
        'console_scripts': [
            'codescan = codescan.codescan:main'
        ]
    }
)
