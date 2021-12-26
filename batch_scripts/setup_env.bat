call cd ..
call conda env create -f environment.yml
call conda activate wpdhack
call ipython kernel install --user --name=wpdhack
pause