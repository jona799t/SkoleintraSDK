from setuptools import setup, find_packages
from pathlib import Path

VERSION = '0.0.1'
DESCRIPTION = 'Log ind på alle sider som bruger skoleintra kun ved brug af python'
long_description = (Path(__file__).parent / "README.md").read_text()

# Setting up
setup(
    name="skoleintra",
    version=VERSION,
    author="jona799t",
    #author_email="<not@available.com>",
    url = 'https://github.com/jona799t/skoleintra-api',
    description=DESCRIPTION,
    long_description=long_description,
    license_files = ('LICENSE.txt',),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=["bs4", "httpx==0.22.0", "requests", "unilogin"],
    keywords=['python', 'skoleintra', 'elevintra'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)