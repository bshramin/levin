
# Virtual network
resource "azurerm_virtual_network" "example" {
  name                = "my-virtual-network"
  address_space       = ["10.0.0.0/16"]
  location            = "East US"
  resource_group_name = "testing-tenancy"
}

# Subnet
resource "azurerm_subnet" "example" {
  name                 = "my-subnet"
  address_prefixes       = ["10.0.1.0/24"]
  virtual_network_name = azurerm_virtual_network.example.name
  resource_group_name  = "testing-tenancy"
}

# Public IP address
resource "azurerm_public_ip" "example" {
  name                = "my-public-ip"
  location            = "East US"
  resource_group_name = "testing-tenancy"
  allocation_method   = "Dynamic"
}

# Network interface
resource "azurerm_network_interface" "example" {
  name                = "my-network-interface"
  location            = "East US"
  resource_group_name = "testing-tenancy"

  ip_configuration {
    name                          = "my-ip-configuration"
    subnet_id                     = azurerm_subnet.example.id
    public_ip_address_id          = azurerm_public_ip.example.id
    private_ip_address_allocation = "Dynamic"
  }
}

# Virtual machine
resource "azurerm_virtual_machine" "example" {
  name                  = "my-virtual-machine"
  location              = "East US"
  resource_group_name   = "testing-tenancy"
  network_interface_ids = [azurerm_network_interface.example.id]
  vm_size               = "Standard_DS1_v2"

  storage_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "16.04-LTS"
    version   = "latest"
  }

  storage_os_disk {
    name              = "my-os-disk"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = "Standard_LRS"
  }

  os_profile {
    computer_name  = "my-computer-name"
    admin_username = "adminuser"
  }

  os_profile_linux_config {
    disable_password_authentication = true
    ssh_keys {
      path     = "/home/adminuser/.ssh/authorized_keys"
      key_data = "[SSH_PUBLIC_KEY_HERE]"
    }
  }
}
