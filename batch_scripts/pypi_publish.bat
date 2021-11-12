call cd ..
call conda activate evtdemand
call python setup.py sdist bdist_wheel
call twine upload --skip-existing dist/*
pause