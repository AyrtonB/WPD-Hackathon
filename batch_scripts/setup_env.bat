call cd ..
call conda env create -f environment.yml
call conda activate evtdemand
call ipython kernel install --user --name=evtdemand
pause