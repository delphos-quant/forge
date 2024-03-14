import subprocess
from os import path
from codecs import open
from setuptools import setup, find_packages

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

try:
    version = (
        subprocess.run(["git", "describe", "--tags"], stdout=subprocess.PIPE)
        .stdout.decode("utf-8")
        .strip()
    )

    if "-" in version:
        v, i, s = version.split("-")
        version = v + "+" + i + ".git." + s

    assert "-" not in version
    assert "." in version

except Exception as e:
    print(f"Warning: Unable to fetch version from Git. Using fallback version.")
    version = "0.0.1"  # Fallback version

with open("dxforge/VERSION", "w", encoding="utf-8") as fh:
    fh.write("%s\n" % version)

setup(
    name="dxforge",
    version=version,
    description="API-based suite for orchestrating quantitative analysis systems.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/divergex/dxforge",
    author="Rafael Zimmer",
    author_email="rzimmerde@gmail.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
)