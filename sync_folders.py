import os
import shutil
import hashlib
import time
import argparse
from datetime import datetime


def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def sync_folders(source, replica, log_file):

    source_files = {}
    replica_files = {}

    for dirpath, _, filenames in os.walk(source):
        for filename in filenames:
            source_file_path = os.path.join(dirpath, filename)
            relative_path = os.path.relpath(source_file_path, source)
            source_files[relative_path] = calculate_md5(source_file_path)

    for dirpath, _, filenames in os.walk(replica):
        for filename in filenames:
            replica_file_path = os.path.join(dirpath, filename)
            relative_path = os.path.relpath(replica_file_path, replica)
            replica_files[relative_path] = calculate_md5(replica_file_path)

    with open(log_file, 'a') as log:
        def log_action(action, path):
            message = f"{datetime.now()} - {action}: {path}"
            print(message)
            log.write(message + '\n')

        for relative_path, md5_hash in source_files.items():
            source_path = os.path.join(source, relative_path)
            replica_path = os.path.join(replica, relative_path)

            if relative_path not in replica_files:
                os.makedirs(os.path.dirname(replica_path), exist_ok=True)
                shutil.copy2(source_path, replica_path)
                log_action("Created", replica_path)
            elif replica_files[relative_path] != md5_hash:
                shutil.copy2(source_path, replica_path)
                log_action("Updated", replica_path)

        for relative_path in replica_files:
            if relative_path not in source_files:
                replica_path = os.path.join(replica, relative_path)
                os.remove(replica_path)
                log_action("Deleted", replica_path)


def main():
    parser = argparse.ArgumentParser(description="Synchronizing two folders.")
    parser.add_argument("source", help="Path to source folder")
    parser.add_argument("replica", help="Path to the replica folder")
    parser.add_argument("log_file", help="Path to log file")
    parser.add_argument("interval", type=int, help="Synchronization interval in seconds")

    args = parser.parse_args()

    while True:
        sync_folders(args.source, args.replica, args.log_file)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
