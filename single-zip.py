import os
import sys
import zipfile
from datetime import datetime
from telethon import TelegramClient
import configparser
import asyncio

def create_archive(folder_path, archive_path):
    with zipfile.ZipFile(archive_path, 'w') as zipf:
        for root, dirs, files in os.walk(folder_path):
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
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archive_name = f"{prefix}_{timestamp}.zip"
    archive_path = os.path.join(ramdisk_path, archive_name)
    
    create_archive(folder_path, archive_path)
    
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
