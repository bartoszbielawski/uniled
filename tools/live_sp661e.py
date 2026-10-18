"""Live check of the real UniledBleDevice (no Home Assistant) against an SP661E.
Run from the repo root with Bluetooth access, BanlanX closed and the HA entry disabled:
    python tools/live_sp661e.py            # connect + read state only
    python tools/live_sp661e.py --toggle   # also power off/on and set brightness
"""
import asyncio
import logging
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "custom_components", "uniled"))

from bleak import BleakScanner

from lib.const import *  # noqa
from lib.ble.device import UniledBleDevice

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(name)s: %(message)s")
logging.getLogger("bleak").setLevel(logging.INFO)


async def main(toggle: bool) -> None:
    print("scanning 10 s ...")
    found = await BleakScanner.discover(timeout=10, return_adv=True)
    target = next(
        ((d, a) for d, a in found.values() if 0x5053 in a.manufacturer_data), None
    )
    if not target:
        sys.exit("no BanlanX (0x5053) device found")
    ble, adv = target
    print("found", ble.address, repr(ble.name), "rssi", adv.rssi)

    dev = UniledBleDevice({}, ble, adv, None)
    print("model:", dev.model.model_name if dev.model else None, "| name:", dev.name)
    if not dev.model:
        sys.exit("model not resolved")

    ok = await dev.update()
    print("update ok:", ok)
    print("status:", dev.master.status.dump())
    print("features:", [type(f).__name__ for f in dev.master.features])

    if ok and toggle:
        ch = dev.master
        for label, attr, value in (
            ("power off", ATTR_UL_POWER, False),
            ("power on", ATTR_UL_POWER, True),
            ("brightness 64", ATTR_HA_BRIGHTNESS, 64),
            ("brightness 255", ATTR_HA_BRIGHTNESS, 255),
        ):
            print(">>>", label)
            print("   result:", await dev.async_set_state(ch, attr, value))
            await asyncio.sleep(3)
        await dev.update()
        print("final status:", dev.master.status.dump())
    await dev.stop()


asyncio.run(main("--toggle" in sys.argv))
