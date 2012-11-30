.. _tutorial:

First steps
===========

Setting up
----------

First make sure you have `Postgres <http://www.postgresql.org/>`_ 
running and `pip <http://pypi.python.org/pypi/pip>`_ installed. 

If you are using Arch Linux pip is named pip2 and you need to
tweak line 3 in *bootstrap.sh* accordingly.

Get the project to your drive. Open up a console and do::

    git clone git@bitbucket.org:mkawalec/astronet.git

Then do::

    cd astronet
    ./bootstrap

If finishes with no errors (there will be ONE error coming from postgres,
just ignore it:-) ) you should be good to go::

    python2 runserver.py

Then open your favourite browser and point it to localhost:5000

Working with it
---------------

If you are ready to change something in the code, that is what you
need to do:

0. Update git repo::
        
        git pull

1. In another terminal set the coffescript compiler to automatically
   compile files that changed::
        
        cd astronet && cake watch

2. Make sure that the server is running (in another terminal)::

        python2 runserver

And now edit what you want to edit.

For git usage, it seems that a good tutorial can be `found here <https://confluence.atlassian.com/display/BITBUCKET/Bitbucket+101>`_
