import argparse
import os
import zipfile

def parse_args():
    parser = argparse.ArgumentParser(description='Decrypt backups')
    parser.add_argument('--password', required=True, help='Zip password')
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument('--backup-dir', required=False, help='Backup directory')
    target_group.add_argument('--file', required=False, help='File to decrypt')
    return parser.parse_args()


def decrypt_file(file_path, password):
    print(f"\nDecrypting:\n\t{file_path}")
    with zipfile.ZipFile(file_path, "r") as zip_file:
        zip_file.setpassword(password.encode("utf-8"))
        zip_file.extractall()


def main():
    args = parse_args()
    password = args.password
    if args.backup_dir:
        if not os.path.isdir(args.backup_dir):
            print(f"Error: {args.backup_dir} is not a valid directory.")
            return
        files = [os.path.join(args.backup_dir, f) for f in os.listdir(args.backup_dir) if os.path.splitext(f)[1] == ".zip"]

    else:
        if not os.path.isfile(args.file):
            print(f"Error: {args.file} is not a valid file.")
            return
        files = [args.file]

    for file in files:
        print(f'Decrypting {file}')
        decrypt_file(file, password=password)


if __name__ == "__main__":
    main()
