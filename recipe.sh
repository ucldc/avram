# Meant to be run in an interactive shell session, not as a script

# install system dependencies
# required for registry app
sudo dnf install httpd-devel mariadb105-devel
# required for certbot
sudo dnf install augeas-libs
# required for monit
sudo dnf install pam-devel
# required for pyenv
sudo dnf install gcc make patch zlib-devel bzip2 \
    bzip2-devel readline-devel sqlite \
    sqlite-devel openssl-devel \
    tk-devel libffi-devel xz-devel

# required for shibboleth
curl -X POST \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "platform=amazonlinux2023" \
    https://shibboleth.net/cgi-bin/sp_repo.cgi \
    -o shib_amazonlinux2023.repo
sudo dnf config-manager --add-repo shib_amazonlinux2023.repo
rm shib_amazonlinux2023.repo
sudo dnf install -y mod_ssl shibboleth

# required for monit
wget  https://mmonit.com/monit/dist/monit-5.35.0.tar.gz
tar zxvf monit-5.35.0.tar.gz 
cd monit-5.35.0/
./configure
sudo make && sudo make install
cd ..
sudo rm -rf monit-5.35.0 monit-5.35.0.tar.gz 

sudo su - registry

curl -fsSL https://pyenv.run | bash

vi .bash_profile
# add the following lines to .bashrc
# export PYENV_ROOT="$HOME/.pyenv"
# [[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
# eval "$(pyenv init - bash)"
source .bash_profile

pyenv install 3.8
pyenv global 3.8
python -m venv /apps/registry/venv
source ~/venv/bin/activate
git clone https://github.com/ucldc/avram
cd avram
git checkout -b dockerize origin/dockerize

pip install --upgrade pip
pip install -r requirements.txt
pip install mod-wsgi
pip install mysqlclient mysql
pip install certbot

cd ..
git clone https://github.com/ucldc/oaiapp ./oaiapp
cd avram
ln -s ../oaiapp/oai oai

vi ~/.bash_profile
# add the following lines to .bash_profile
# source ~/venv/bin/activate
# alias certbot='certbot --config-dir ~/letsencrypt/config/ --work-dir ~/letsencrypt/work/ --logs-dir ~/letsencrypt/logs/'

mkdir -p /apps/registry/servers
mod_wsgi-express setup-server \
    /apps/registry/avram/collection_registry/wsgi.py \
    --port=18880 \
    --user registry \
    --group registry \
    --server-root=/apps/registry/servers/mod_wsgi-express 

mkdir -p /apps/registry/servers/mod_wsgi-express/logs
cp httpd/httpd.conf ~/servers/mod_wsgi-express/

cp -r ~/avram/shibboleth ~/servers/
cp ~/servers/shibboleth/etc/shibboleth2.xml.stage ~/servers/shibboleth/etc/shibboleth2.xml
curl http://md.incommon.org/certs/inc-md-cert-mdq.pem -o ~/servers/shibboleth/etc/inc-md-cert-mdq.pem
# copy incommon.pem from old prod server to new prod server
# copy sp-cert.pem from old prod server to new prod server
# copy sp-key.pem from old prod server to new prod server

# copy local_settings.py from old prod server to new prod server
# update ALLOWED_HOSTS to include hostnames for new server
cp ~/avram/collection_registry/stage_settings.py ~/avram/collection_registry/local_settings.py
vi ~/avram/collection_registry/local_settings.py
# update with environment variables

cp -r ~/avram/monit ~/monit
mkdir ~/monit/log
mkdir ~/monit/config
mv ~/monit/.monitrc ~
chmod 700 ~/.monitrc

python manage.py collectstatic --noinput
mkdir ~/dbdumps
mkdir ~/letsencrypt
mkdir ~/webroot

# copy letsencrypt/config/live/registry.cdlib.org/ from old prod server to new prod server
# OR
certbot certonly # --apache # will throw an error
> 3
> oacops@cdlib.org
> registry-stg.cdlib.org
> /apps/registry/webroot
# make sure to run apache before running certbot so it can find the webroot

# as awieliczka
sudo cp /apps/registry/avram/registry.service /etc/systemd/system/registry.service
sudo systemctl daemon-reload
sudo systemctl start registry
sudo systemctl enable registry
systemctl status registry




# set up cron jobs at some point
* * * * * ~/avram/rikolti_status.sh
7 1 * * * ~/avram/dbdump.sh
30 1 * * * ~/avram/logrotate.sh
42 3 * * * /apps/registry/venv/bin/certbot --config-dir ~/letsencrypt/config/ --work-dir ~/letsencrypt/work/ --logs-dir ~/letsencrypt/logs/ renew --post-hook "/apps/registry/servers/mod_wsgi-express/apachectl graceful"




# helpful command to manualy start shibboleth
# /usr/sbin/shibd -p /apps/registry/servers/shibboleth/var/shibd.pid -f -c /apps/registry/servers/shibboleth/etc/shibboleth2.xml
