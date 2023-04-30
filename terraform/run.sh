# Prepare the environment and variables
CONFIG_FILES_TO_RUN="from_file"
SSH_PUBLIC_KEY="$HOME/.ssh/id_rsa.pub"
SSH_PRIVATE_KEY="$HOME/.ssh/id_rsa"
VARIABLES="ssh_pub_key=$(cat "$SSH_PUBLIC_KEY")"

# Create the Infra
terraform fmt
terraform init
terraform plan -var="$VARIABLES"
terraform apply --auto-approve -var="$VARIABLES"
VM_PUBLIC_IP="$(terraform output -raw vm_public_ip)"
ZIP_FILE="$(terraform output -raw zip_file)"
sleep 2

# Run the simulation
ssh -o StrictHostKeyChecking=no -i "$SSH_PRIVATE_KEY" levin@"$VM_PUBLIC_IP" "rm -rf *"
scp -o StrictHostKeyChecking=no -i "$SSH_PRIVATE_KEY" "$ZIP_FILE" levin@"$VM_PUBLIC_IP":~/levin.zip
ssh -o StrictHostKeyChecking=no -i "$SSH_PRIVATE_KEY" levin@"$VM_PUBLIC_IP" "sudo apt update; sudo apt install zip unzip python3-pip -y; pip3 install --user pipenv"
ssh -o StrictHostKeyChecking=no -i "$SSH_PRIVATE_KEY" levin@"$VM_PUBLIC_IP" "unzip -o levin.zip; sh clean.sh; pip3 install -r requirements.txt; python3 src/main.py $CONFIG_FILES_TO_RUN"
scp -r -o StrictHostKeyChecking=no -i "$SSH_PRIVATE_KEY" levin@"$VM_PUBLIC_IP":~/stats/ ./simulation_results/
scp -r -o StrictHostKeyChecking=no -i "$SSH_PRIVATE_KEY" levin@"$VM_PUBLIC_IP":~/logs/ ./simulation_results/

## Simulation is finished, destroy the VM
terraform destroy --auto-approve -var="$VARIABLES"
