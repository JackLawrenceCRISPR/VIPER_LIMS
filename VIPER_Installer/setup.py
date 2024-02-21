from setuptools import setup, find_packages
import codecs
import os

with codecs.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.1.3'
DESCRIPTION = 'A free and open-source LIMS software with scriptable modules.'
LONG_DESCRIPTION = 'A free and open-source LIMS software with scriptable modules. Deploy a Client or Server with: VIPER_LIMS.VIPER_Installer.deploy("Client","Directory")'

# Setting up
setup(
    name="VIPER-LIMS",
    version=VERSION,
    url ="https://github.com/JackLawrenceCRISPR/VIPER-LIMS",
    author="VIPER-LIMS (Jack Lawrence)",
    author_email="<JackLawrenceCRISPR@gmail.com>",
    license="MIT",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    requires=["requests"],
    python_requires=">=3.7",
    keywords=['python', 'installer', 'lims', 'science'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
	"Intended Audience :: Science/Research",
	"Intended Audience :: System Administrators",
	"Intended Audience :: End Users/Desktop",
	"Framework :: Flask",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Android",
	"License :: OSI Approved :: MIT License",
	"Natural Language :: English",
	"Topic :: Scientific/Engineering",
	"Topic :: Database",
    ]
)
