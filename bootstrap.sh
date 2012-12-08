#!/bin/bash
echo "Installing packages"
sudo pip install gevent flask sphinx psycopg2 pylibmc markdown
rm -rf build

echo "Setting up the database"
echo "DROP DATABASE astronet"|psql -U postgres
cat astronet/sql/00-database.sql|psql -U postgres
cat astronet/sql/*.sql|psql -U postgres -d astronet

echo "Compiling coffescript"
cd astronet && cake build && cd ..

echo "Creating default configuration"
touch astronet/config.cfg
echo "SECRET_KEY = 'ddsnfkrjoireklfjdslkiro43213213m5,tsrfdeldmfxruc'
SALT = 'nfkren<F4><F4>ffdsdsdfdewdsdfvvv'
DB = 'astronet'
TRAP_BAD_REQUEST_ERRORS = False" > astronet/config.cfg

echo "Generating documentation"
cd docs && make html && ln -s _build/html/index.html ../index.html && cd ..

echo "You should now be able to start a server using 'python2 runserver.py'"
echo "Thank you for using this fine utility"
echo "If you want to change some config variables, you will find them"
echo "in astronet/config.cfg"
