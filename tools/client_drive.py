"""Drives the Minecraft Java client on a Mac with real input, for tools/trailer.py: keys and mouse buttons go to the
game as macOS input events, the way cobblemon-bedrock's tools/client_drive.py drives the Bedrock client on Windows.

    python tools/client_drive.py key f1          # hide or show the HUD (it toggles)
    python tools/client_drive.py use             # right mouse button: cast, reel in, use the post
    python tools/client_drive.py attack 4.5      # hold the left mouse button for 4.5 seconds: break a block
    python tools/client_drive.py hotbar 3        # select hotbar slot 3
    python tools/client_drive.py focus           # bring the game to the front

Every input lands in whatever app is in front, so the game is brought to the front first, and this is only for
stretches when nobody is using the Mac. It needs the Accessibility permission for the app it runs under (Quartz's
CGPreflightPostEventAccess says whether it has it). Needs pyobjc-framework-Quartz.
"""

import sys
import time

import AppKit
import Quartz

# macOS virtual key codes
KEYS = {"f1": 122, "f2": 120, "f3": 99, "f5": 96, "f11": 103, "escape": 53, "e": 14, "q": 12,
        "1": 18, "2": 19, "3": 20, "4": 21, "5": 23, "6": 22, "7": 26, "8": 28, "9": 25}


def focus(app: str = "java") -> bool:
    for running in AppKit.NSWorkspace.sharedWorkspace().runningApplications():
        if (running.localizedName() or "").lower() == app:
            running.activateWithOptions_(AppKit.NSApplicationActivateIgnoringOtherApps)
            time.sleep(0.3)
            return True
    return False


def key(name: str, hold: float = 0.06) -> None:
    code = KEYS[name.lower()]
    for down in (True, False):
        event = Quartz.CGEventCreateKeyboardEvent(None, code, down)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)
        if down:
            time.sleep(hold)


def _mouse(down_type, up_type, button, hold: float) -> None:
    where = Quartz.CGEventGetLocation(Quartz.CGEventCreate(None))
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, Quartz.CGEventCreateMouseEvent(None, down_type, where, button))
    time.sleep(hold)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, Quartz.CGEventCreateMouseEvent(None, up_type, where, button))


def use(hold: float = 0.08) -> None:
    """The right mouse button: use the held item, or use what the crosshair is on."""
    _mouse(Quartz.kCGEventRightMouseDown, Quartz.kCGEventRightMouseUp, Quartz.kCGMouseButtonRight, hold)


def attack(hold: float = 0.08) -> None:
    """The left mouse button, held: hit, or break the block under the crosshair."""
    _mouse(Quartz.kCGEventLeftMouseDown, Quartz.kCGEventLeftMouseUp, Quartz.kCGMouseButtonLeft, hold)


def hotbar(slot: int) -> None:
    key(str(slot))


if __name__ == "__main__":
    verb, *rest = sys.argv[1:]
    if not Quartz.CGPreflightPostEventAccess():
        sys.exit("this app may not post input events (System Settings > Privacy & Security > Accessibility)")
    focus()
    if verb == "key": key(rest[0])
    elif verb == "use": use()
    elif verb == "attack": attack(float(rest[0]) if rest else 0.08)
    elif verb == "hotbar": hotbar(int(rest[0]))
