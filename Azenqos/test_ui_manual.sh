for i in `ls ui_test*.py`; do bash -c "python3 $i || kill \$PPID"; done
