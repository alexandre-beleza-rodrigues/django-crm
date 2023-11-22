#!/bin/bash

coverage run --source='.' manage.py test --verbosity=2
coverage report --fail-under=100
pylint $(git ls-files '*.py')
