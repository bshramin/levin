# Levin
Levin is a Lightning Network simulator for evaluating network construction, payment routing, and node behavior in the Lightning Network.

## Features
- Simulate Lightning Network topology and behavior
- Evaluate different routing strategies
- Test node actions and their impact
- Support for concurrent transactions
- Configurable network parameters
- Data persistence and analysis

## Getting Started

### Prerequisites
- Python 3.x
- Pipenv (for dependency management)

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/levin.git
cd levin

# Install dependencies
pipenv install
```

### Running Levin
```bash
# Activate virtual environment
pipenv shell

# Run simulation with templates
python3 src/main.py [TEMPLATE_NAME_1] [TEMPLATE_NAME_2] [TEMPLATE_NAME_3] ...
```

### Deployment Options

#### Using Docker
[Coming Soon]

#### Microsoft Azure Deployment
Levin can be automatically deployed to Microsoft Azure using Terraform. The deployment process:
1. Creates necessary Azure resources
2. Uploads and executes the simulation
3. Downloads results
4. Automatically cleans up resources

To deploy:
1. Configure template files in `terraform/run.sh` using `CONFIG_FILES_TO_RUN` (space-separated list)
2. Run the deployment:
```bash
bash clean.sh
cd terraform
bash run.sh
```

## Development Status

### Compression Features
- ✅ Channel re-opening
- ✅ Re-opening count tracking
- ✅ Multiple run averaging
- ✅ Simplified debugging numbers
- ✅ Initial channel opening tracking
- ✅ Network data file input

### Transparency Features
- ✅ Concurrent agent execution
- ✅ Hop-based transaction delays
- ✅ Query limits per route
- ✅ Random delay variation
- ✅ Parallel path queries
- ✅ Partial path node querying
- ⬜ Multipath payment support

## License
MIT License
Copyright (c) 2024 Levin
