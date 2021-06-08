#!/bin/sh

WORK_HOME="/svc/collect/nudge"

echo $WORK_HOME

cd $WORK_HOME

echo "넛지 모니터링, 성과 분석 start"

/usr/local/bin/python3.9 $WORK_HOME/src/nudge_check.py
/usr/local/bin/python3.9 $WORK_HOME/src/check_union_index.py

echo "넛지 모니터링, 성과 분석 end"