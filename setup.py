#/usr/bin/env python

from distutils.core import setup

setup(
    name='hvacmon',
    description='Monitors HVAC status on Raspberry Pi',
    version='0.1.0',
    packages=['hvacmon'],
    entry_points={
        'console_scripts': [
            'hvacmon = hvacmon.__main__:main'
        ]
    },
    author='Sean Kelly',
    license='TBD',
    author_email='theseankelly@outlook.com',
    url='https://github.com/theseankelly/hvacmon'
)