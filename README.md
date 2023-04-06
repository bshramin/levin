
# Levin
Levin is a Lightning network simulator that can be used to evaluate
the effect of changes to how the network is constructed, how payments are routed and the actions of nodes.

## Running Levin
```shell
python3 src/main.py [TEMPLATE_NAME_1] [TEMPLATE_NAME_2] [TEMPLATE_NAME_3] ...
```

### Using Docker


### Running on Microsoft Azure with Terraform
```shell
cd terraform
terraform init
terraform plan
terraform apply --auto-approve
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
