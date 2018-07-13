#!/bin/bash
#sudo chown www-data:www-data .*
#sudo chown www-data:www-data * -R
#sudo chown www-data:www-data .hg/* -R
#sudo chown www-data:www-data /var/www/static/* -R
#sudo chown root:env /var/env/timeslots -R
sudo chmod g+rw * -R
sudo chmod -x */*.py -R
sudo chmod -x */*/*.py -R
