# Proxmox to Azure backups
Purpose of this project is to encrypt and back up Proxmox backups from local storage to Azure

## Contents
This repository contains two scripts:

### uploadBackups.py
This script iterates over all backups in a specified directory, encrypts them using a supplied encryption key and creates a new encrypted backup. 
Finally, it uploads the backup to an Azure Blob Storage container.

### decryptBackups.py
This script recieves a folder / file and decrypts the backup that was encrypted using the previous script

