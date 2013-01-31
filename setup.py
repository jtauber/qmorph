from setuptools import setup


setup(
    name = "qmorph",
    version = "0.1dev1",
    
    description = "tabular data querying and pivoting with particular application to linguistic morphology",
    url = "http://github.com/jtauber/qmorph",
    
    author = "James Tauber",
    author_email = "jtauber@jtauber.com",
    
    license = "MIT",
    
    classifiers = [
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    
    py_modules = [
        "qmorph",
    ],
)