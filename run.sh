#! /usr/bin/sh

_PATH="./Versions/"


scripts=$(printf %q $_PATH "new_job_")
for _file in `ls "$scripts"*`
do
	echo $_file
	nohup python -u $_file > /dev/null &
done
