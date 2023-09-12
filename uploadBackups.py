import os
import sys
import argparse
import zipfile
from collections import defaultdict
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient


def parse_args():
    parser = argparse.ArgumentParser(description='Upload backups to Azure Blob Storage')
    parser.add_argument('--password', required=True, help='Zip password')
    parser.add_argument('--backup-dir', required=True, help='Backup directory')
    parser.add_argument('--connection-string', required=True, help='Azure Blob Storage connection string')
    return parser.parse_args()


def main():
    args = parse_args()

    password = args.password
    backup_dir = args.backup_dir
    connection_str = args.connection_string

    if not os.path.exists(backup_dir):
        print(f"Backup directory '{backup_dir}' does not exist. Exiting.")
        sys.exit()

    backup_ext = '.zst'
    container_name = "proxmox-backups"

    blob_service_client = BlobServiceClient.from_connection_string(connection_str)
    container_client = blob_service_client.get_container_client(container_name)
    if not container_client.exists():
        container_client.create_container()

    files_to_upload = enumerate_backups_to_upload(backup_dir, backup_ext)
    upload_files(container_client, backup_dir, password, files_to_upload)


def enumerate_backups_to_upload(backup_dir, backup_ext):
    # Enumerate backups in local backup path
    # Return list of backups to upload
    latest_files = defaultdict(str)

    # Enumerate files in the directory
    for filename in os.listdir(backup_dir):
        # Check if the file has the desired extension
        if filename.endswith(backup_ext):
            # Extract the ID from the filename
            id = filename.split('-')[2]
            # Check if the file is newer than the latest file for this ID
            if filename > latest_files[id]:
                latest_files[id] = filename

    return latest_files.values()

def build_zip_filename(file_path, host):
    # Create a filename for the zip file
    # Format: <filename>.<host>.zip
    return f"{file_path}.{host}.zip"

def zip_and_encrypt_file(file_path, password, host):
    # Encrypt the file
    print(f"\nZipping and Encrypting:\n\t{file_path}")
    zip_file_path = build_zip_filename(file_path, host)
    with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_LZMA) as zip_file:
        zip_file.setpassword(password.encode("utf-8"))
        zip_file.write(file_path)
        print("Done")
    return zip_file_path


def upload_files(container_client, backup_dir, password, files_to_upload):
    try:
        for file in files_to_upload:
            file_path = os.path.join(backup_dir, file)
            with open(f"{file_path}.notes", mode="r") as data:
                host = data.read()
            enc_path = build_zip_filename(file_path, host)
            blob_name = os.path.basename(enc_path).replace('_', '-')
            blob_client = container_client.get_blob_client(blob=blob_name)
            if blob_client.exists() == False:
                zip_and_encrypt_file(file_path, password, host)
                print(f"\nUploading:\n\t{enc_path}")
                print(f"Target blob: {blob_name}. Target container: {container_client.container_name}")
                with open(enc_path, mode="rb") as data:
                    blob_client.upload_blob(data)
                print("Upload complete")
            else:
                print("Backup already exists in blob storage")

            # Delete the file after upload
            os.remove(enc_path)
            print("Deleted local file")
    except Exception as ex:
        print('Exception:')
        print(ex)


if __name__ == "__main__":
    main()
