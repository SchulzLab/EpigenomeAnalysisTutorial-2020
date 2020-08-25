=============
What you need
=============

You need to have a **laptop/desktop** with the following software installed (see detailed instructions below)

* `Docker <https://docs.docker.com/get-docker/>`_ 
   - Having a docker user account is not necessary for the purposes of the tutorial. 
* `IGV <https://software.broadinstitute.org/software/igv/download>`_

======================
Download docker image
======================


Please **download the docker image** we have prepared for the purposes of this tutorial **before** the tutorial. 
The size of docker image is **approximately 10GB**. 

You can use the following command: ::

  docker run -it -P --name epigenomics -v ~/container-data:/data sivarajank/eccb:latest

The different parameters are explained below.
+------------+------------------------------------------------------------------------------------------------------------------------------------------+
| params     |  explanation                                                                                                                             |
+============+==========================================================================================================================================+
| --name     | xxxxxxxxxxxxxxxxxxxxxxxxx                                                                                                                |
+------------+------------------------------------------------------------------------------------------------------------------------------------------+
| -v         | path to the output directory                                                                                                             |
+------------+------------------------------------------------------------------------------------------------------------------------------------------+


======================
Prepare the data
======================
TODO
