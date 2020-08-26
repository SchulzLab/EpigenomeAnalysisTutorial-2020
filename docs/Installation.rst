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

The *name* parameter assigns a name to your docker image. If you used the above command, it is *epigenomics (--name)*. 
If for some reason if you exit or abort your docker image. You can use the following commands to re-login to the docker container. : ::

   docker start epigenomics
   docker attach epigenomics
   
To get out of the docker container, you can simply type *exit*.

===============================================
How to access data inside the docker container
================================================

We recommend to access the data inside the container using the following method, for the purposes of this tutorial. 
In the aforementioned *docker run* command you might have noticed the * -v ~/container-data:/data * parameter. 
This parameter enables you to access whatever data you have inside the directory (*/data*) of your container.


======================
Prepare the data
======================
TODO
