import os
import sys
import zipfile
from datetime import datetime
from telethon import TelegramClient
import configparser
import asyncio

def create_archive(folder_path, archive_path, exclude_folders):
    # Normalize exclude folders (handle absolute, relative, and names)
    exclude_abs_paths = set()
    for folder in exclude_folders:
        folder = folder.strip()
        # Handle absolute paths
        if os.path.isabs(folder):
            exclude_abs_paths.add(os.path.abspath(folder))
        else:
            # Handle relative paths or just folder names
            exclude_abs_paths.add(os.path.abspath(os.path.join(folder_path, folder)))
    
    with zipfile.ZipFile(archive_path, 'w') as zipf:
        for root, dirs, files in os.walk(folder_path):
            # Filter directories: exclude matching folders
            dirs[:] = [d for d in dirs if os.path.abspath(os.path.join(root, d)) not in exclude_abs_paths]
            
            for file in files:
                zipf.write(os.path.join(root, file),
                           arcname=os.path.relpath(os.path.join(root, file),
                                                   os.path.join(folder_path, '..')))

async def send_to_telegram(client, channel_id, archive_path):
    channel = await client.get_entity(channel_id)
    await client.send_file(channel, archive_path)

async def main(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    
    folder_path = config['General']['FolderToArchive']
    ramdisk_path = config['General']['RamDiskPath']
    prefix = config['General']['Prefix']
    api_id = config['Telegram']['API_ID']
    api_hash = config['Telegram']['API_HASH']
    session_name = config['Telegram']['SessionName']
    channel_id = int(config['Telegram']['ChannelID'])
    exclude_folders = config['General'].get('ExcludeFolders', '').split(',')
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archive_name = f"{prefix}_{timestamp}.zip"
    archive_path = os.path.join(ramdisk_path, archive_name)
    
    create_archive(folder_path, archive_path, exclude_folders)
    
    client = TelegramClient(session_name, api_id, api_hash)
    await client.start()
    
    await send_to_telegram(client, channel_id, archive_path)
    
    await client.disconnect()
    os.remove(archive_path)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} path/to/config.ini")
        sys.exit(1)
    config_path = sys.argv[1]
    asyncio.run(main(config_path))
