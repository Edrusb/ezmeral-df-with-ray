# ezmeral-df-with-ray
Ray on Ezmeral Data Fabric

## Introduction

Today the Ezmeral Data Fabric does not provide the Ray software in the EEP. What a pity, as we could use a DF cluster for AI/LLM with GPU having the data sets ready on the same nodes. Hopefully Ray is not too complex to install, the provided two scripts simplify even more the installation and construction of a Ray cluster:
-	ray-install.sh (install Ray, obviously)
-	go-ray.sh (deploys a ray cluster on a set of nodes, including thus the case where nodes are those of a Data Fabric)

## Installing Ray

First we need to install the Ray software on Data Fabric nodes. The ray-install.sh script should work under the following Linux distributions:
-	Redhat
-	Rocky linux
-	Debian
-	ubuntu

let’s install Ray in /opt/RAY

    ./ray-install.sh /opt/RAY

For airgap environment, this script replies on the distro package management tools and on python3-pip tool. Both tool must have a repository available in the airgap environment, which is usually the case for the linux package management system. For the python3-pip, the repository must be passed as second argument:

    # ./ray-install.sh
    usage: ./ray-install.sh <installation path> [ <airgap pip repo URL> ]
    #

## Deploying a Ray cluster

Once the Ray software is installed on a set of nodes, one of them has to be selected as the _“head node"_. The head node will be then entry point for connecting to the cluster and to submit jobs. The other nodes (pure worker nodes) will be accessible through the _head node_.

### Start the head node

On the head node run the following:

    ./go-ray.sh /opt/RAY head

This will output something like the below output where you will be given the IP address to provide to other nodes to connect to:

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

![Dashboard view of the head node alone]()

### Start all other nodes

On all other nodes run the following command using the IP address of the head node reported previously:

    ./go-ray.sh /opt/RAY worker 10.13.25.131

Of course better using clustershell to simplify the deployment on many nodes in a single command:

    clush -b -w df-[2-5] ./go-ray.sh /opt/RAY worker 10.13.25.131
    
After a few seconds, the “cluster” tab of the dashboard should display all the nodes involved in the cluster (including the head node):

![Dashboard view of the node with all workers]()
