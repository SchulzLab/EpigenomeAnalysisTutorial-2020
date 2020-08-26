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
The size of docker image is **approximately 10GB**. 

You can use the following command: ::

  docker run -it -P --name epigenomics -v ~/container-data:/data sivarajank/eccb:latest

The *name* parameter assigns a name to your docker image. If you used the above command, it is *epigenomics (--name)*. 
If for some reason if you exit or abort your docker image. You can use the following commands to re-login to the docker container. : ::

   docker start epigenomics
   docker attach epigenomics
   
To get out of the docker container, you can simply type *exit*.

Setup genomic data
------------------------------------------------------------------------------

Next, we need to setup the genomic data, here we will use hg38:
::
   cd rgtdata
   python setupGenomicData.py --hg38

How to access data inside the docker container
----------------------------------------------------------------------------------------------
We recommend to access the data inside the container using the proposed method, for the purposes of this tutorial.

In the aforementioned *docker run* command you might have noticed the *-v ~/container-data:/data* parameter. 
This parameter enables you to access any data you have inside the **/data** directory of your container from your local machine at **~/container-data/**.

We have shipped some preprocessed data as part of our container which can be found at **/root/EpigenomeAnalysisTutorial-2020.zip**. 
Once you are inside the docker container, please run the following command so that you can access these data from your local machine to view in IGV or view the plots : ::

   mv /root/EpigenomeAnalysisTutorial-2020.zip /data/
   cd /data
   unzip EpigenomeAnalysisTutorial-2020.zip -d EpigenomeAnalysisTutorial-2020
   
Now, you can find the folder EpigenomeAnalysisTutorial-2020 in your local machine at **~/container-data/** folder. We will run all commands under this folder during the course of the tutorial:
::
   cd EpigenomeAnalysisTutorial-2020
