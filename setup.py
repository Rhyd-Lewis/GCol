from setuptools import setup, find_packages

# read the contents of the README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='gcol',
    version='1.5.2',
    author='Rhyd Lewis',
    author_email='lewisr9@cardiff.ac.uk',
    url="https://github.com/Rhyd-Lewis/GCol",
    description='A Python Library for Graph Coloring',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        ],
    python_requires='>=3.7',
    install_requires=['networkx>=3.0', 'matplotlib>=3.8'],
    extras_require = {
        'testing': ["pytest"],
        'documentation': ["pandas"],
    }
)
