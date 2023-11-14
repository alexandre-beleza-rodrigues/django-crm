#!/bin/bash

python manage.py test --verbosity=2
pylint $(git ls-files '*.py')
