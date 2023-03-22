# Levin

## Running Levin
```shell
python3 src/main.py [TEMPLATE_NAME_1] [TEMPLATE_NAME_2] [TEMPLATE_NAME_3] ...
```

### Using Docker


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
- [ ] When do they decide to reopen a channel in the real network?
- [ ] Read network data from file
- [ ] Upper bound for the real network
- 

## Transparent TODO:
- [X] Run concurrent agents
- [X] add delay to sending transactions on for each hop
- [X] Limit the number of queries per route
- [ ] Add multipath payment
- [ ] Add randomness to the delays
- 
