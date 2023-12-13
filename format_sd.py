import subprocess

def get_volume_name(disk_identifier):
    info_result = subprocess.run(['diskutil', 'info', disk_identifier], capture_output=True, text=True)
    info_lines = info_result.stdout.split('\n')
    volume_name_line = next((line for line in info_lines if 'Volume Name:' in line), None)
    if volume_name_line:
        return volume_name_line.split(':')[1].strip()
    else:
        return 'Not Mounted or No Volume Name'

def get_attached_drives():
    result = subprocess.run(['diskutil', 'list'], capture_output=True, text=True)
    lines = result.stdout.split('\n')

    drives = []
    current_drive = None

    for line in lines:
        if 'external' in line or 'internal' in line:
            if current_drive:
                drives.append(current_drive)
            drive_identifier = line.split()[0]
            current_drive = {
                'identifier': drive_identifier,
                'description': line,
                'volume_name': get_volume_name(drive_identifier),
                'partitions': []
            }
        elif current_drive and '0:' in line:
            partition_info = line.strip()
            current_drive['partitions'].append(partition_info)
    
    if current_drive:
        drives.append(current_drive)

    return drives

def format_sd_card(disk, file_system):
    # Set a valid volume name for the given file system
    volume_name = "UNTITLED"  # Common default volume name for new drives
    if file_system == "MS-DOS FAT32":
        volume_name = "NO_NAME"  # FAT32 has a restriction on volume name length and character set

    format_command = ['diskutil', 'eraseDisk', file_system, volume_name, disk]
    try:
        subprocess.run(format_command, check=True)
        print(f"Drive formatted to {file_system} with volume name {volume_name} successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during formatting: {e}")

def main():
    drives = get_attached_drives()
    if not drives:
        print("No drives found.")
        return

    print("Available drives:")
    for i, drive in enumerate(drives):
        print(f"{i + 1}. {drive['description']} - Volume Name: {drive['volume_name']}")
        for partition in drive['partitions']:
            print(f"   {partition}")

    choice = int(input("Select the drive to format (e.g., 1, 2, ...): "))
    if choice < 1 or choice > len(drives):
        print("Invalid choice.")
        return

    disk_identifier = drives[choice - 1]['identifier']

    print("Choose file system format:")
    print("1. exFAT")
    print("2. FAT32")
    print("3. MacOS Extended Journaled")
    fs_choice = input("Enter your choice (1, 2, or 3): ")

    file_system = ""
    if fs_choice == '1':
        file_system = "exFAT"
    elif fs_choice == '2':
        file_system = "MS-DOS FAT32"
    elif fs_choice == '3':
        file_system = "JHFS+"
    else:
        print("Invalid file system choice.")
        return

    confirmation = input(f"Are you sure you want to format {disk_identifier} to {file_system}? This will erase all data on the drive. Type 'yes' to confirm: ")
    if confirmation.lower() == 'yes':
        format_sd_card(disk_identifier, file_system)
    else:
        print("Formatting cancelled.")

if __name__ == "__main__":
    main()
