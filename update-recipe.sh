# update recipe:

sudo su - registry
pyenv install 3.9
pyenv global 3.9.22
python -m venv /apps/registry/venv-3.9
source ~/venv-3.9/bin/activate

cd avram
pyenv local 3.9.22

pip install --upgrade pip
pip install -r requirements.txt
pip install mod-wsgi
pip install mysqlclient mysql
pip install certbot

cd ..

./mod_wsgi-express setup-server \
    /apps/registry/avram/collection_registry/wsgi.py \
    --port=18880 \
    --user registry \
    --group registry \
    --server-root=/apps/registry/servers/3-9-mod_wsgi-express 

mkdir -p /apps/registry/servers/3-9-mod_wsgi-express/logs

# check for drift, change for stage or prod
cp ~/servers/mod_wsgi-express/httpd.conf ~/avram/httpd/httpd.conf.stage
cd ~/avram 
git status
# should be clean except .python-version

cp ~/servers/mod_wsgi-express/httpd.conf ~/servers/3-9-mod_wsgi-express/

mv venv venv-3.8
mv venv-3.9 venv

ls /venv/lib/python3.9/site-packages/mod_wsgi/server/
vi ~/servers/3-9-mod_wsgi-express/httpd.conf file 
# search for "LoadModule wsgi_module" & change the path to the new file listed above

vi ~/servers/3-9/mod_wsgi-express/apachectl
# change all instances of 3-9-mod_wsgi-express to mod_wsgi-express
mv mod_wsgi-express/ 3-8-mod_wsgi-express
mv 3-9-mod_wsgi-express/ mod_wsgi-express

mv ~/servers/3-8-mod_wsgi-express/httpd.pid ~/servers/mod_wsgi-express/
monit restart http
