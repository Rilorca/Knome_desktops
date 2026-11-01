import time
from unittest.mock import MagicMock
from evdev import ecodes
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../gnome-meta-scroll")))
from gnome_meta_scroll import MetaScrollManager

class MockEvent:
    def __init__(self, ev_type, code, value):
        self.type = ev_type
        self.code = code
        self.value = value

def test_meta_key_state():
    mock_dbus = MagicMock()
    mgr = MetaScrollManager(debounce_interval=0.1, dbus_interface=mock_dbus)

    assert not mgr.meta_pressed
    # Press Left Meta
    mgr.handle_event(MockEvent(ecodes.EV_KEY, ecodes.KEY_LEFTMETA, 1))
    assert mgr.meta_pressed

    # Release Left Meta
    mgr.handle_event(MockEvent(ecodes.EV_KEY, ecodes.KEY_LEFTMETA, 0))
    assert not mgr.meta_pressed

    # Press Right Meta
    mgr.handle_event(MockEvent(ecodes.EV_KEY, ecodes.KEY_RIGHTMETA, 1))
    assert mgr.meta_pressed

    # Autorepeat Right Meta
    mgr.handle_event(MockEvent(ecodes.EV_KEY, ecodes.KEY_RIGHTMETA, 2))
    assert mgr.meta_pressed

    # Release Right Meta
    mgr.handle_event(MockEvent(ecodes.EV_KEY, ecodes.KEY_RIGHTMETA, 0))
    assert not mgr.meta_pressed

def test_wheel_without_meta_does_nothing():
    mock_dbus = MagicMock()
    mgr = MetaScrollManager(debounce_interval=0.1, dbus_interface=mock_dbus)

    # Scroll without Meta pressed
    result = mgr.handle_event(MockEvent(ecodes.EV_REL, ecodes.REL_WHEEL, 1))
    assert not result
    mock_dbus.invokeShortcut.assert_not_called()

def test_wheel_with_meta_triggers_shortcuts():
    mock_dbus = MagicMock()
    mgr = MetaScrollManager(debounce_interval=0.05, dbus_interface=mock_dbus)

    # Press Meta
    mgr.handle_event(MockEvent(ecodes.EV_KEY, ecodes.KEY_LEFTMETA, 1))

    # Scroll Up (value > 0) -> Left / Previous desktop
    result_up = mgr.handle_event(MockEvent(ecodes.EV_REL, ecodes.REL_WHEEL, 1))
    assert result_up
    mock_dbus.invokeShortcut.assert_called_with("Switch One Desktop to the Left")

    time.sleep(0.06)
    # Scroll Down (value < 0) -> Right / Next desktop
    result_down = mgr.handle_event(MockEvent(ecodes.EV_REL, ecodes.REL_WHEEL, -1))
    assert result_down
    mock_dbus.invokeShortcut.assert_called_with("Switch One Desktop to the Right")

def test_debounce_filters_fast_spins():
    mock_dbus = MagicMock()
    mgr = MetaScrollManager(debounce_interval=0.1, dbus_interface=mock_dbus)

    mgr.handle_event(MockEvent(ecodes.EV_KEY, ecodes.KEY_LEFTMETA, 1))
    # First scroll succeeds
    assert mgr.handle_event(MockEvent(ecodes.EV_REL, ecodes.REL_WHEEL, 1))
    # Immediate second scroll gets debounced
    assert not mgr.handle_event(MockEvent(ecodes.EV_REL, ecodes.REL_WHEEL, 1))
    assert mock_dbus.invokeShortcut.call_count == 1

    time.sleep(0.12)
    # Scroll after debounce interval succeeds
    assert mgr.handle_event(MockEvent(ecodes.EV_REL, ecodes.REL_WHEEL, 1))
    assert mock_dbus.invokeShortcut.call_count == 2

def test_hires_wheel_with_meta_triggers_shortcuts():
    mock_dbus = MagicMock()
    mgr = MetaScrollManager(debounce_interval=0.05, dbus_interface=mock_dbus)

    # Press Meta
    mgr.handle_event(MockEvent(ecodes.EV_KEY, ecodes.KEY_LEFTMETA, 1))

    # Scroll Up via high-res wheel (value 120)
    result_up = mgr.handle_event(MockEvent(ecodes.EV_REL, ecodes.REL_WHEEL_HI_RES, 120))
    assert result_up
    mock_dbus.invokeShortcut.assert_called_with("Switch One Desktop to the Left")

    time.sleep(0.06)
    # Scroll Down via high-res wheel (value -120)
    result_down = mgr.handle_event(MockEvent(ecodes.EV_REL, ecodes.REL_WHEEL_HI_RES, -120))
    assert result_down
    mock_dbus.invokeShortcut.assert_called_with("Switch One Desktop to the Right")

def test_multi_device_and_disconnect_safety():
    mock_dbus = MagicMock()
    mgr = MetaScrollManager(debounce_interval=0.05, dbus_interface=mock_dbus)

    # Press Left Meta on keyboard 1 and Right Meta on keyboard 2
    mgr.handle_event(MockEvent(ecodes.EV_KEY, ecodes.KEY_LEFTMETA, 1), device_path="/dev/input/event12")
    mgr.handle_event(MockEvent(ecodes.EV_KEY, ecodes.KEY_RIGHTMETA, 1), device_path="/dev/input/event5")
    assert mgr.meta_pressed

    # Releasing Left Meta on keyboard 1 keeps meta_pressed True because keyboard 2 still holds Right Meta
    mgr.handle_event(MockEvent(ecodes.EV_KEY, ecodes.KEY_LEFTMETA, 0), device_path="/dev/input/event12")
    assert mgr.meta_pressed

    # If keyboard 2 disconnects without sending key-up, release_device_keys cleans up its state
    mgr.release_device_keys("/dev/input/event5")
    assert not mgr.meta_pressed
