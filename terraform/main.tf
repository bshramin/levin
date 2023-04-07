data "archive_file" "levin" {
  type        = "zip"
  source_dir  = "../"
  output_path = "./project_zips/levin-${timestamp()}.zip"
  excludes = [
    "terraform",
    "logs/*",
    "stats/*",
    ".vscode",
    ".idea",
    "README.md",
    ".git",
  ]
}

# Virtual network
resource "azurerm_virtual_network" "levin" {
  name                = "levin-virtual-network"
  address_space       = ["10.0.0.0/16"]
  location            = "Canada Central"
  resource_group_name = "testing-tenancy"
}

# Subnet
resource "azurerm_subnet" "levin" {
  name                 = "levin-subnet"
  address_prefixes     = ["10.0.1.0/24"]
  virtual_network_name = azurerm_virtual_network.levin.name
  resource_group_name  = "testing-tenancy"
}

# Public IP address
resource "azurerm_public_ip" "levin" {
  name                = "levin-public-ip"
  location            = "Canada Central"
  resource_group_name = "testing-tenancy"
  allocation_method   = "Dynamic"
}

# Network interface
resource "azurerm_network_interface" "levin" {
  name                = "levin-network-interface"
  location            = "Canada Central"
  resource_group_name = "testing-tenancy"

  ip_configuration {
    name                          = "levin-ip-configuration"
    subnet_id                     = azurerm_subnet.levin.id
    public_ip_address_id          = azurerm_public_ip.levin.id
    private_ip_address_allocation = "Dynamic"
  }
}

# Virtual machine
resource "azurerm_virtual_machine" "levin" {
  name                          = "levin-vm"
  location                      = "Canada Central"
  resource_group_name           = "testing-tenancy"
  network_interface_ids         = [azurerm_network_interface.levin.id]
  vm_size                       = "Standard_F72s_v2"
  delete_os_disk_on_termination = true

  storage_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-focal"
    sku       = "20_04-lts-gen2"
    version   = "latest"
  }

  storage_os_disk {
    name              = "levin-os-disk"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = "Standard_LRS"
  }

  os_profile {
    computer_name  = "levin-vm"
    admin_username = "levin"
  }

  os_profile_linux_config {
    disable_password_authentication = true
    ssh_keys {
      path     = "/home/levin/.ssh/authorized_keys"
      key_data = var.ssh_pub_key
    }
  }
}

data "azurerm_public_ip" "levin" {
  name                = azurerm_public_ip.levin.name
  resource_group_name = azurerm_virtual_machine.levin.resource_group_name
}
