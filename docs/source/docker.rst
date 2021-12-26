.. _docker:

Docker Install
--------------


As an alternative to pip and installing QGIS from the website, dependencies can be installed docker. 
Docker is also used for CI testing and generating sphinx docs.

Set the environment variable ``DATA_DIR`` to the desired storage location, this
path will be mounted as a volume within the container. 
The default paths will be used inside this directory 
(see :ref:`Configuring <Configuring>`)

.. code-block:: sh

  $ echo "DATA_DIR=/home/$USER/ais/" > .env  


An SSH server is included in the docker image so that X11 forwarding can be used to display the QGIS application window.
Create a new SSH key to connect to the container. 
The ``-X`` option is used when connecting to enable forwarding

.. code-block:: sh

  $ ssh-keygen -f ~/.ssh/id_aisdb -N ''


Create and start the aisdb environment and sphinx docs with ``docker-compose up``. 
Possible options are ``aisdb``, ``docs``, or ``test``

  
.. code-block:: sh

  $ docker-compose up aisdb docs

  ...

  aisdb_sshd  | Starting environment over SSH
  aisdb_sshd  | 
  aisdb_sshd  | ssh -X -i ~/.ssh/id_aisdb ais_env@2001:3984:3989::2
  aisdb_sshd  | 
  aisdb_sshd  | Server listening on 0.0.0.0 port 22.
  aisdb_sshd  | Server listening on :: port 22.
  aisdb_docs  | 
  aisdb_docs  | > AISDB@0.1.0 start
  aisdb_docs  | > node server.js
  aisdb_docs  | 
  aisdb_docs  | Docs available at http://172.23.0.2:8085
  aisdb_docs  | Docs available at http://[2001:3984:3989::3]:8085


Copy the container address and connect to the container

.. code-block:: sh

  $ ssh -X -i ~/.ssh/id_aisdb ais_env@2001:3984:3989::2

  Last login: Sun Dec 19 11:41:23 2021 from 172.22.0.1
  Python 3.10.1 (main, Dec 11 2021, 17:22:55) [GCC 11.1.0] on linux
  Type "help", "copyright", "credits" or "license" for more information.
  >>>

