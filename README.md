# ezmeral-df-with-ray
Ray on HPE Ezmeral Data Fabric

## Introduction

Today the HPE Ezmeral Data Fabric does not provide the Ray software in the EEP. What a pity, as we could use a DF cluster for AI/LLM with GPU having the data sets ready on the same nodes. Hopefully Ray is not too complex to install, the provided two scripts simplify even more the installation and construction of a Ray cluster:
-	[ray-install.sh](Source-code/ray-install.sh) (install Ray, obviously)
-	[go-ray.sh](Source-code/go-ray.sh) (deploys a ray cluster on a set of nodes, including thus the case where nodes are those of a Data Fabric)

You will find below example of use of these two scripts, including the deployment of a pretrained LLM model to translate from English to French. You will see below how to change the source and destination languages ;) no worries!

## Installing Ray

First we need to install the Ray software on Data Fabric nodes. The __ray-install.sh__ script should work under the following Linux distributions:
-	Redhat
-	Rocky linux
-	Debian
-	ubuntu

let’s install Ray in /opt/RAY

    root@df-1:\~# ./ray-install.sh /opt/RAY

For airgap environment, this script relies on the distro package management tools and on python3-pip tool. Both tool must have a repository available in the airgap environment, which is usually the case for the linux package management system. For the python3-pip, the repository must be passed as second argument:

    root@df-1:\~# ./ray-install.sh
    usage: ./ray-install.sh <installation path> [ <airgap pip repo URL> ]
    root@df-1:\~#

## Deploying a Ray cluster

Once the Ray software is installed on a set of nodes, one of them has to be selected as the _“head node"_. The head node will be then entry point for connecting to the cluster, to submit jobs and even to distribute inference request among the many possible instances a model deployment can be sized. The other nodes (pure worker nodes) will be accessible through the _head node_ to process the jobs and workload like inference.

### Start the head node

On the head node run the following:

    root@df-1:\~# ./go-ray.sh /opt/RAY head

This will display something like the below output where you will be given the IP address to provide to other nodes to connect to (df-1 or its IP address 10.13.25.131 in the following examples):

    Usage stats collection is disabled.

    Local node IP: 10.13.25.131

    --------------------
    Ray runtime started.
    --------------------

    Next steps
      To add another node to this Ray cluster, run
        ray start --address='10.13.25.131:6379'

      To connect to this Ray cluster:
        import ray
        ray.init()

      To submit a Ray job using the Ray Jobs CLI:
        RAY_ADDRESS='http://10.13.25.131:8265' ray job submit --working-dir . -- python my_script.py

      See https://docs.ray.io/en/latest/cluster/running-applications/job-submission/index.html
      for more information on submitting Ray jobs to the Ray cluster.

      To terminate the Ray runtime, run ray stop

      To view the status of the cluster, use ray status

      To monitor and debug Ray, view the dashboard at 10.13.25.131:8265

      If connection to the dashboard fails, check your firewall settings and network configuration.

You should now be able already to connect to the dashboard as described above, in particular, looking at the “cluster” tab you will see only one node for now (the head node):

![Dashboard view of the head node alone](Snapshots/Image1.jpg)

### Start all other nodes

On all other nodes run the following command using the IP address (or FQDN) of the head node reported previously:

    ./go-ray.sh /opt/RAY worker df-1

Of course better using clustershell to simplify the deployment on many nodes (df-2 to df-5) in a single command:

    clush -b -w df-[2-5] ./go-ray.sh /opt/RAY worker df-1

After a few seconds, the “cluster” tab of the dashboard should display all the nodes involved in the cluster (including the head node):

![Dashboard view of the node with all workers](Snapshots/Image2.jpg)

## Submitting a job

### Example 1

To submit a job, we must first activate the python virtual environment (venv) where the _ray-install.py_ script installed Ray
(this was the path __/opt/RAY__ we were using above to illustrate the installation script).
On a node where Ray has been installed (we can also install ray using _ray-install.py_ on a node that will not be part of the cluster (!) and get this way a client node), open a shell session and type the following:

> root@df-1:\~# source /opt/RAY/bin/activate<br>
> (RAY) root@df-1:\~#

As you see, the prompt has changed reporting now you are under the (RAY) venv. Submitting a job is done the following way (which is also provided in the output shown above while starting the head node):

    RAY_ADDRESS='http://df-1:8265' ray job submit --working-dir . -- python my_script.py

For example, you can use the [__prime.py__](Examples/prime.py) script which list the prime number below a given max number. First create a new
directory for a working directory on a node of the cluster and copy the __prime.py__ script in there:

    root@df-1:~# source /opt/RAY/bin/activate
    (RAY) root@df-1:~# mkdir Working
    (RAY) root@df-1:~# cd Working
    (RAY) root@df-1:~# wget https://github.com/Edrusb/ezmeral-df-with-ray/blob/main/Examples/prime.py
    (RAY) root@df-1:~# export RAY_ADDRESS='http://df-1:8265'

Then submit the job to the ray cluster:

    (RAY) root@df-1:\~/Working# ray  job submit --working-dir . -- python3 prime.py 100
    
> Job submission server address: http://df-1:8265<br>
> 2024-08-26 15:57:30,554 INFO dashboard_sdk.py:385 -- Package gcs://_ray_pkg_0ce46dc9bac19eb0.zip already exists, skipping upload.<br>
> <br>
> -------------------------------------------------------<br>
> Job 'raysubmit_6TkMA4yeKnD6JPsU' submitted successfully<br>
> -------------------------------------------------------<br>
> <br>
> Next steps<br>
>   Query the logs of the job:<br>
>     ray job logs raysubmit_6TkMA4yeKnD6JPsU<br>
>   Query the status of the job:<br>
>     ray job status raysubmit_6TkMA4yeKnD6JPsU<br>
>   Request the job to be stopped:<br>
>     ray job stop raysubmit_6TkMA4yeKnD6JPsU<br>
><br>
> Tailing logs until the job exits (disable with --no-wait):<br>
> 2024-08-26 15:57:33,152 INFO worker.py:1432 -- Using address 10.13.25.131:6379 set in the environment variable RAY_ADDRESS<br>
> 2024-08-26 15:57:33,153 INFO worker.py:1567 -- Connecting to existing Ray cluster at address: 10.13.25.131:6379...<br>
> 2024-08-26 15:57:33,168 INFO worker.py:1743 -- Connected to Ray cluster. View the dashboard at http://10.13.25.131:8265<br>
> **[2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]**<br>
> <br>
> ------------------------------------------<br>
> Job 'raysubmit_6TkMA4yeKnD6JPsU' succeeded<br>
> ------------------------------------------<br>
> <br>
> (RAY) root@df-1:\~/Working#<br>

***Note***: This script is just for illustration purposes, it is not efficient to spawn so many small tasks.

### Example 2: LLM (no GPU required)

The [__translate.py__](Examples/translate.py) deploys a pre-trained model for inference using **Ray Serve** and let you interact with it to translate English sentences to French. The model used requires the "transformers" and "torch" modules which we have not been installed in the Ray's venv on cluster nodes. We could rely in the _realtime environmenent_ feature or Ray to perform this operartion on-fly but it would last only for the time the model is in inference. As these packages are quite big we will do else.

> **Note:** this would be done quite the same way as we did with prime.py above:
> - copy the __translate.py__ script in an empty directory,
> - change your current directory to it
> - activate the Ray venv
> - set the environment variable RAY_ADDRESS to point to the Ray head
>
> The only difference would take place when submitting the job, using the **--runtime-env-json** argument:
>
>    (RAY) root@df-1:~# ray job submit --working-dir . --runtime-env-json={"pip": [ "torch", "transformers" ] } -- python3 translate.py job launch 5
>

Here we will instead install once and for all those two modules in each Ray venv of the Ray cluster (nodes df-1 to df-5):

    clush -b -w df-[1-5] "source /opt/RAY/bin/activate ; python3 -m pip install torch transformers"

then we can submit the job on the head node (df-1) as previously done:

    root@df-1:~# cd Working
    (RAY) root@df-1:\~/Working# wget https://github.com/Edrusb/ezmeral-df-with-ray/blob/main/Examples//translate.py
    (RAY) root@df-1:\~/Working# export RAY_ADDRESS='http://df-1:8265'
    (RAY) root@df-1:\~/Working# ray job submit --working-dir . -- python3 translate.py launch job 5

This will launch **Ray Serve** and "application" with 5 instances to address requests of translation. 

![Dashboard view with Ray Serve in action](Snapshots/Image3.jpg)

You can check the Ray dashboard both the "jobs" and "serve" tabs to see the evolution of the status of the deployment process.

Once the script has completed and the model is deployed successfully, you can ask for translation using the following command:

    (RAY) root@df-1:~/Working# ./translate.py ask df-1 "Success is the ability to go from one failure to another with no loss of enthusiasm."

            Success is the ability to go from one failure to another with no loss of enthusiasm.
    translates to:
            Le succès est la capacité de passer d'un échec à un autre sans perte d'enthousiasme.

    (RAY) root@df-1:~/Working#

 here we did not submit a job to Ray but only connected using HTTP to one of the model instances (we connect to the head node which acts as a load-balancer) to request the translation of the provided message.

 ### How to change the languages?
Hey! No worries, this is very simple!

You will have to edit the _translate.py_ script and change the **translation_en_to_fr** string to something else like like:

    @serve.deployment(num_replicas=num_instances, ray_actor_options={"num_cpus": 1, "num_gpus": 0})
    class Translator:
        def __init__(self):
            # Load model
            self.model = pipeline("translation_en_to_de", model="t5-small")

also either delete the existing deployed model before re-deploying this modified one:

    (RAY) root@df-1:\~/Working# ray job submit --working-dir . -- python3 translate.py stop job
 
or make a copy of this _transate.py_ script to also modify the line here replacing "translate" by "translate2" to avoid conflicting with the already deployed model and have more than one model available at a time:

    inf_name = "translate2"

![Two models in inference](Snapshots/Image4.jpg)

    (RAY) root@df-1:~/Working# ./translate2.py ask df-1 "Success is the ability to go from one failure to another with no loss of enthusiasm."

            Success is the ability to go from one failure to another with no loss of enthusiasm.
    translates to:
            Erfolg ist die Fähigkeit, von einem failure zu einem anderen zu gehen ohne Verlust an Ent


To go further using these models and pipelines have a look at the output of this following snippet:

    from transformers import pipeline
    help(pipeline)

    


