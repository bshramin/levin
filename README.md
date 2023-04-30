
# Levin
Levin is a Lightning network simulator that can be used to evaluate
the effect of changes to how the network is constructed, how payments are routed and the actions of nodes.

## Running Levin
```shell
python3 src/main.py [TEMPLATE_NAME_1] [TEMPLATE_NAME_2] [TEMPLATE_NAME_3] ...
```

### Using Docker
[TODO]

### Running on Microsoft Azure with Terraform
This project is capable of automatically deploying Levin to Microsoft Azure using Terraform.
It will then upload the code to the VM and run it. After the simulation is completed it will download the results.
And finally it will destroy the VM and all the resources created on Azure.

First you need to write the name of the configuration files you want to run in `terraform/run.sh` for key `CONFIG_FILES_TO_RUN`, it's a space separated list. Then you can run:
```shell
bash clean.sh
cd terraform
bash run.sh
```


## Development
Use Pipenv to manage the virtual environment and dependencies.

### Activate the virtual environment
```bash
pipenv shell
```



## Compression TODO:
- [X] Add re-opening
- [X] Add count re-openings till number of transactions
- [X] Run multiple times and average
- [X] Decrease numbers to make debugging simpler
- [X] count initial channel openning as reopenning
- [X] Read network data from file


## Transparent TODO:
- [X] Run concurrent agents
- [X] add delay to sending transactions on for each hop
- [X] Limit the number of queries per route
- [ ] Add multipath payment
- [X] Add randomness to the delays
- [X] Queries of a path get executed in parallel
- [X] Only query half of the nodes in the path
