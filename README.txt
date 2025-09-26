1/ Recommended: create a venv in DISP using >python3 -m venv <directory_of_venv>
2/ in >DISP/ activate venv using >source venv/bin/activate 
3/ while in the venv and DISP/: >pip3 install -e .
This will notably install numpy and matplotlib in the venv
4/ >python3 main/launcher.py ;  to launch the demo ;

If you do not desire to use a venv, skip step 1 and 2.

If you want latex fonts on graphs, you need a working latex installation
In plotters/disp.mplstyle, uncomment the two last lines.
