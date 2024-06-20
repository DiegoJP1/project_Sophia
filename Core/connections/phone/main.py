import asyncio
from bleak import BleakScanner

async def scan_devices():
    devices = await BleakScanner.discover()
    print("Dispositivos Bluetooth encontrados:")
    for device in devices:
        print(f"  - {device}")
loop = asyncio.get_event_loop()
loop.run_until_complete(scan_devices())
