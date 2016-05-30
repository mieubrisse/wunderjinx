from setuptools import setup, find_packages
from codecs import open
from os import path

script_dir = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
# with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
#     long_description = f.read()

setup(
    name='wunderjinx',
    version='0.1.0',
    description='An offline curses client for Wunderlist',
    long_description=long_description,
    url='https://github.com/mieubrisse/wunderjinx',
    author='mieubrisse',
    author_email='mieubrisse@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='wunderlist api cli',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=[
        'wunderpy2', 
        'parsedatetime', 
        'pika',
        'requests',
        ],
    entry_points={
        'console_scripts': [
            'wunderjinx = wunderjinx.wunderjinx:main',
        ],
    },
)
