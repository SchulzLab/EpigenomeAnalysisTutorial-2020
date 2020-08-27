=============
What you need
=============

You need to have a **laptop/desktop** with the following software installed (see detailed instructions below)

* `Docker <https://docs.docker.com/get-docker/>`_ 
   - Having a docker user account is not necessary for the purposes of the tutorial.
* `IGV <https://software.broadinstitute.org/software/igv/download>`_


Download docker image
------------------------------------------------------------------------------

Please **download the docker image** we have prepared for the purposes of this tutorial **before** the tutorial. 
The size of docker image is **approximately 15GB**. 

You can use the following command: ::

  docker run -it -P --name epigenomics -v ~/container-data:/data sivarajank/eccb:latest

The *name* parameter assigns a name to your docker image. If you used the above command it is *epigenomics (--name)*. 
If, for some reason, you exit or abort your docker image, you can use the following commands to re-login to the docker container. : ::

   docker start epigenomics
   docker attach epigenomics
   
To get out of the docker container, you can simply type *exit*.

If, for some reason, we ask you to update the docker container, you need to exit the docker container and execute::

   docker pull sivarajank/eccb:latest
   
After that you can execute the docker start and attach commands mentioned earlier.

How to access data inside the docker container
----------------------------------------------------------------------------------------------
We recommend to access the data inside the container using the proposed method, for the purposes of this tutorial.

In the aforementioned *docker run* command you might have noticed the *-v ~/container-data:/data* parameter. 
This parameter enables you to access any data you have inside the **/data** directory of your container from your local machine at **~/container-data/**. The **/data** directory is mirrored to your local **~/container-data/** folder, meaning that everything you do (remove, edit, add etc.) in you local folder **~/container-data/** will also be changed in the **/data** folder and vice-versa. This has the advantage that we can create files like plots inside of Docker, write them to the **/data** directory and you can easily access them outside of Docker by looking into the **~/container-data/** folder.  

We have shipped some preprocessed data as part of our container which can be found at **/root/EpigenomeAnalysisTutorial-2020.zip**. 
Once you are inside the docker container, please run the following command so that you can access this data from your local machine to view in IGV or view the plots : ::

   mv /root/EpigenomeAnalysisTutorial-2020 /data/
   cd /data
   
Now, you can find the folder EpigenomeAnalysisTutorial-2020 in your local machine at **~/container-data/** folder. We will run all commands under this folder during the course of the tutorial. Please take care to keep this directory as you current directory. 
::
   cd EpigenomeAnalysisTutorial-2020
