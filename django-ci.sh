#!/bin/bash

python manage.py test
pylint $(git ls-files '*.py')
