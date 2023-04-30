import argparse
import os
from cryptography.fernet import Fernet


def parse_args():
    parser = argparse.ArgumentParser(description='Decrypt backups')
    parser.add_argument('--key', required=True, help='Encryption key')
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument('--backup-dir', required=False, help='Backup directory')
    target_group.add_argument('--file', required=False, help='File to decrypt')
    return parser.parse_args()


def decrypt_file(file_path, enc_key):
    print(f"\nDecrypting:\n\t{file_path}")
    with open(file_path, 'rb') as f:
        data = f.read()
    fernet = Fernet(enc_key)
    decrypted = fernet.decrypt(data)
    dec_path = file_path.replace('.enc', '')
    with open(dec_path, 'wb') as f:
        f.write(decrypted)
    print(f"Decrypted file saved to: {dec_path}")


def main():
    args = parse_args()
    enc_key = args.key.encode()
    if args.backup_dir:
        if not os.path.isdir(args.backup_dir):
            print(f"Error: {args.backup_dir} is not a valid directory.")
            return
        files = [os.path.join(args.backup_dir, f) for f in os.listdir(args.backup_dir)]
    else:
        if not os.path.isfile(args.file):
            print(f"Error: {args.file} is not a valid file.")
            return
        files = [args.file]

    for file in files:
        decrypt_file(file, enc_key)


if __name__ == "__main__":
    main()
