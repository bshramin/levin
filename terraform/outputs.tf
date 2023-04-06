output "vm_public_ip" {
  value = data.azurerm_public_ip.levin.ip_address
}

output "zip_file" {
  value = data.archive_file.levin.output_path
}
