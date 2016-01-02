from setuptools import setup, find_packages
import re

VERSIONFILE = "src/staldates/ui/_version.py"
verstr = "unknown"
try:
    verstrline = open(VERSIONFILE, "rt").read()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        verstr = mo.group(1)
except EnvironmentError:
    print "unable to find version in %s" % (VERSIONFILE,)
    raise RuntimeError("if %s exists, it is required to be well-formed" % (VERSIONFILE,))

setup(
    name='av-control',
    version=verstr,
    description='User interface for controlling the A/V devices at St Aldates church',
    author='James Muscat',
    author_email='jamesremuscat@gmail.com',
    url='https://github.com/staldates/av-control',
    install_requires=['avx>=0.96.dev', 'PySide'],
    setup_requires=['nose>=1.0'],
    tests_require = ['mock'],
    dependency_links = [
        "lib/" # find local copies of packages here
    ],
    packages=find_packages('src', exclude=["*.tests"]),
    package_dir = {'':'src'},
    entry_points={
        'console_scripts': [
            'av-control = staldates.avcontrol:main'
        ],
    }
)