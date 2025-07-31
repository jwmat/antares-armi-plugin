from pathlib import Path

from setuptools import find_packages
from setuptools import setup

HERE = Path(__file__).parent
README = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name="arte",
    version="0.1.0",
    description="ARMI plug-in that applies axial thermal expansion to fuel blocks",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Justine Matten",
    author_email="jwmatten@gmail.com",
    python_requires=">=3.10",
    packages=find_packages(exclude=("tests",)),
    install_requires=[
        "armi @ git+https://github.com/terrapower/armi.git@0.5.1",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.1",
            "pre-commit",
            "pylint",
        ],
    },
    entry_points={
        "armi.plugins": [
            "arte = arte.plugin:ArtePlugin",
        ],
    },
)
