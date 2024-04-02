#!usr/bin/env python3
"""
python3 makepyproject.py    
"""
import json
import os
import jinja2
import jjcli
from glob import glob

def main():    
    name = "sentiment_analysis"
    __version__ = "0.1.0"
    autores = ["Francisca Barros", "Rafael Correia", "Robert Szabo"]
    emails = ["pg53816@uminho.pt","pg54162@uminho.pt","pg54194@uminho.pt"]
    numeros =  ["53816","54162","54194"]

    pp = jinja2.Template('''

    [build-system]
    requires = ["flit_core >=3.2,<4"]
    build-backend = "flit_core.buildapi"

    [project]
    name = "{{name}}"
    authors = [
        {name = "{{autor1}}", email = "{{email1}}", numero = {{numero1}}},
        {name = "{{autor2}}", email = "{{email2}}", numero = {{numero2}}},
        {name = "{{autor3}}", email = "{{email3}}", numero = {{numero3}}}
    ]
    version = "{{version}}"
    readme = "README.md"
    classifiers = [
        "License :: OSI Approved :: MIT License",
    ]
    requires-python = ">=3.8"
    dynamic = ["description"]

    dependencies = [
        "spacy"
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
                     "email3": emails[2],
                     "numero1": numeros[0],
                     "numero2": numeros[1],
                     "numero3": numeros[2]}))



if __name__ == "__main__":
    main()