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

echo "Generating documentation"
cd docs && make html && ln -s _build/html/index.html ../index.html && cd ..

echo "You should now be able to start a server using 'python2 runserver.py'"
echo "Thank you for using this fine utility"