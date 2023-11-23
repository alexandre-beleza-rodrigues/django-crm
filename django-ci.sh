#!/bin/bash

coverage run --source='.' manage.py test --verbosity=2
coverage report --fail-under=98
coverage html
pylint $(git ls-files '*.py')
