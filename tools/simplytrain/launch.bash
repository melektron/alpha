#!/usr/bin/bash

echo start hihi
cd /home/alpha/alpha/tools/simplytrain
echo "Starting alpha simplytrain server in screen"
# https://unix.stackexchange.com/a/612110
# In case of any future net permissino issues, check out: https://superuser.com/a/892391
# (basically add the file /etc/authbind/byport/<PORT>, make it owned by alpha, 
# add u+x permissions and make sure authbind is installed (apt install authbind).)
screen -DmS alpha /usr/bin/bash -c "source venv/bin/activate && uwsgi --http 0.0.0.0:1234 --master -p 4 -w wsgi:app"
echo "Screen has exited with code $?"
exit $?