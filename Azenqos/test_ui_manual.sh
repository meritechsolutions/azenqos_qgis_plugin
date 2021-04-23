for i in `ls ui_test*.py`; do bash -c "echo \"TESTING: $i\" && python3 $i || kill \$PPID"; done
echo "SUCCESS"
