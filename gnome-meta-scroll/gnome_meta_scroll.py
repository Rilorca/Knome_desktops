#!/usr/bin/env python3
import asyncio
import os
import sys
import time
import evdev
from evdev import ecodes
import pyudev

class MetaScrollManager:
    def __init__(self, debounce_interval=0.18, dbus_interface=None):
        self.debounce_interval = debounce_interval
        self.last_trigger_time = 0.0
        self.pressed_keys = set()
        self.dbus_interface = dbus_interface
        if self.dbus_interface is None:
            self._init_dbus()

    @property
    def meta_pressed(self):
        return len(self.pressed_keys) > 0

    def release_device_keys(self, device_path):
        self.pressed_keys = {k for k in self.pressed_keys if k[0] != device_path}

    def _init_dbus(self):
        try:
            import dbus
            bus = dbus.SessionBus()
            obj = bus.get_object("org.kde.kglobalaccel", "/component/kwin")
            self.dbus_interface = dbus.Interface(obj, "org.kde.kglobalaccel.Component")
        except Exception as e:
            self.dbus_interface = None

    def trigger_switch(self, direction):
        now = time.time()
        if now - self.last_trigger_time < self.debounce_interval:
            return False
        self.last_trigger_time = now

        action = "Switch One Desktop to the Left" if direction > 0 else "Switch One Desktop to the Right"
        try:
            if not self.dbus_interface:
                self._init_dbus()
            if self.dbus_interface:
                self.dbus_interface.invokeShortcut(action)
                return True
        except Exception as e:
            self._init_dbus()
        return False

    def handle_event(self, event, device_path="default"):
        if event.type == ecodes.EV_KEY:
            if event.code in (ecodes.KEY_LEFTMETA, ecodes.KEY_RIGHTMETA):
                if event.value > 0:
                    self.pressed_keys.add((device_path, event.code))
                else:
                    self.pressed_keys.discard((device_path, event.code))
        elif event.type == ecodes.EV_REL and self.meta_pressed:
            # Handle standard wheel as well as high-resolution wheel
            # In high-res wheel, one notch is typically ±120
            if event.code == ecodes.REL_WHEEL and event.value != 0:
                return self.trigger_switch(event.value)
            elif hasattr(ecodes, "REL_WHEEL_HI_RES") and event.code == ecodes.REL_WHEEL_HI_RES and event.value != 0:
                return self.trigger_switch(event.value)
        return False


def is_candidate_device(dev):
    try:
        caps = dev.capabilities()
        has_meta = ecodes.EV_KEY in caps and (
            ecodes.KEY_LEFTMETA in caps[ecodes.EV_KEY] or ecodes.KEY_RIGHTMETA in caps[ecodes.EV_KEY]
        )
        has_wheel = ecodes.EV_REL in caps and (
            ecodes.REL_WHEEL in caps[ecodes.EV_REL]
            or (hasattr(ecodes, "REL_WHEEL_HI_RES") and ecodes.REL_WHEEL_HI_RES in caps[ecodes.EV_REL])
            or ecodes.REL_HWHEEL in caps[ecodes.EV_REL]
            or (hasattr(ecodes, "REL_HWHEEL_HI_RES") and ecodes.REL_HWHEEL_HI_RES in caps[ecodes.EV_REL])
        )
        return has_meta or has_wheel
    except Exception:
        return False


async def handle_device(dev, manager):
    try:
        async for event in dev.async_read_loop():
            manager.handle_event(event, dev.path)
    except Exception:
        pass
    finally:
        manager.release_device_keys(dev.path)


async def monitor_hotplug(tasks, manager):
    loop = asyncio.get_running_loop()
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='input')
    monitor.start()

    while True:
        device = await loop.run_in_executor(None, monitor.poll, 2.0)
        if device and device.action == 'add' and device.device_node and device.device_node.startswith('/dev/input/event'):
            await asyncio.sleep(0.5)  # give permissions/udev time to settle
            try:
                dev = evdev.InputDevice(device.device_node)
                if is_candidate_device(dev) and dev.path not in tasks:
                    tasks[dev.path] = asyncio.create_task(handle_device(dev, manager))
            except Exception:
                pass


async def main():
    manager = MetaScrollManager()
    tasks = {}

    for path in evdev.list_devices():
        try:
            dev = evdev.InputDevice(path)
            if is_candidate_device(dev):
                tasks[dev.path] = asyncio.create_task(handle_device(dev, manager))
        except Exception:
            pass

    asyncio.create_task(monitor_hotplug(tasks, manager))

    while True:
        # Check active tasks and prune dead ones
        dead = [p for p, t in tasks.items() if t.done()]
        for p in dead:
            del tasks[p]
        await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
