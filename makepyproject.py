#!usr/bin/env python3
"""
python3 makepyproject.py    
"""

import jinja2
from glob import glob

def main():    
    name = "sentiment_analysis"
    __version__ = "0.2.1"
    autores = ["Francisca Barros", "Rafael Correia", "Robert Szabo"]
    emails = ["pg53816@uminho.pt","pg54162@uminho.pt","pg54194@uminho.pt"]

    pp = jinja2.Template('''

    [build-system]
    requires = ["flit_core >=3.2,<4"]
    build-backend = "flit_core.buildapi"

    [project]
    name = "{{name}}"
    authors = [
        {name = "{{autor1}}", email = "{{email1}}"},
        {name = "{{autor2}}", email = "{{email2}}"},
        {name = "{{autor3}}", email = "{{email3}}"}
    ]
    version = "{{version}}"
    readme = "README.md"
    classifiers = [
        "License :: OSI Approved :: MIT License",
    ]
    requires-python = ">=3.8"
    dynamic = ["description"]

    dependencies = [
        "spacy",
        "jjcli",
        "matplotlib"                 
    ]

    [project.scripts]
    {{name}} = "{{name}}:main"

    ''')


    with open("pyproject.toml", "w") as out:
        out.write(pp.render({"version":__version__,
                     "name":name,
                     "autor1": autores[0],
                     "autor2": autores[1],
                     "autor3": autores[2],
                     "email1": emails[0],
                     "email2": emails[1],
                     "email3": emails[2]}))

if __name__ == "__main__":
    main()