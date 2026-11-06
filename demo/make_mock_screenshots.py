"""Draw fictional iOS-style settings screenshots for the demo (no real people/devices).

Usage: .venv/bin/python demo/make_mock_screenshots.py   -> demo/screenshots/*.png
Persona: "Jordan Sample" (survivor). "Alex" is the former partner. All names/emails fake.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent / "screenshots"
W, H = 600, 1080
BG, CARD, INK, MUTED, BLUE, GREEN, RED, LINE = ((242, 242, 247), (255, 255, 255), (0, 0, 0),
                                                 (120, 120, 128), (0, 122, 255), (52, 199, 89),
                                                 (255, 59, 48), (225, 225, 230))


def font(size, bold=False):
    for f in ("/System/Library/Fonts/SFNS.ttf", "/System/Library/Fonts/Helvetica.ttc"):
        try:
            return ImageFont.truetype(f, size, index=1 if (bold and f.endswith(".ttc")) else 0)
        except OSError:
            continue
    return ImageFont.load_default()


F, FB, FS, FT = font(24), font(32, True), font(19), font(15)


class Screen:
    def __init__(self, back, title, big_title=True):
        self.img = Image.new("RGB", (W, H), BG)
        self.d = ImageDraw.Draw(self.img)
        self.d.text((24, 56), "9:41", fill=INK, font=font(20, True))
        # status bar: signal dots, battery outline
        for i in range(4):
            self.d.ellipse([W - 118 + i * 11, 66, W - 112 + i * 11, 72], fill=INK)
        self.d.rounded_rectangle([W - 62, 60, W - 24, 78], radius=5, outline=INK, width=2)
        self.d.rounded_rectangle([W - 59, 63, W - 32, 75], radius=3, fill=INK)
        self.d.rectangle([W - 23, 66, W - 20, 72], fill=INK)
        self.d.text((24, 100), "‹ " + back, fill=BLUE, font=F)
        if big_title:
            self.d.text((24, 150), title, fill=INK, font=FB)
            self.y = 215
        else:
            self.d.text((W / 2 - 40, 102), title, fill=INK, font=font(22, True))
            self.y = 160

    def header(self, text):
        self.d.text((40, self.y), text.upper(), fill=MUTED, font=FT)
        self.y += 30

    def group(self, rows):
        """rows: list of dicts {t, sub, right, toggle, color, chevron}"""
        top = self.y
        h = sum(74 if r.get("sub") else 56 for r in rows)
        self.d.rounded_rectangle([20, top, W - 20, top + h], radius=14, fill=CARD)
        y = top
        for i, r in enumerate(rows):
            rh = 74 if r.get("sub") else 56
            self.d.text((40, y + (14 if r.get("sub") else 15)), r["t"],
                        fill=r.get("color", INK), font=F)
            if r.get("sub"):
                self.d.text((40, y + 46), r["sub"], fill=MUTED, font=FS)
            if r.get("right"):
                w = self.d.textlength(r["right"], font=FS)
                self.d.text((W - 70 - w, y + 18), r["right"], fill=MUTED, font=FS)
            if "toggle" in r:
                on = r["toggle"]
                x0, y0 = W - 96, y + 14
                self.d.rounded_rectangle([x0, y0, x0 + 56, y0 + 32], radius=16,
                                         fill=GREEN if on else (229, 229, 234))
                cx = x0 + 42 if on else x0 + 16
                self.d.ellipse([cx - 13, y0 + 3, cx + 13, y0 + 29], fill=CARD)
            elif r.get("chevron", True):
                self.d.text((W - 52, y + 15), "›", fill=(199, 199, 204), font=F)
            if i < len(rows) - 1:
                self.d.line([40, y + rh, W - 20, y + rh], fill=LINE, width=1)
            y += rh
        self.y = top + h + 18

    def note(self, text):
        self.d.text((40, self.y), text, fill=MUTED, font=FT)
        self.y += 34

    def save(self, name):
        OUT.mkdir(parents=True, exist_ok=True)
        self.img.save(OUT / name)
        print("wrote", OUT / name)


def apple_id_devices():
    s = Screen("Settings", "Apple Account")
    s.group([{"t": "Jordan Sample", "sub": "j.sample@example.com"}])
    s.header("Devices")
    s.group([{"t": "Jordan's iPhone", "sub": "This iPhone 15"},
             {"t": "Home iPad", "sub": "iPad Air"},
             {"t": "MacBook Air", "sub": "MacBook Air 13\""}])
    s.group([{"t": "Sign Out", "color": RED, "chevron": False}])
    s.save("apple_id_devices.png")


def safety_check_people():
    s = Screen("Safety Check", "Manage Sharing & Access", big_title=False)
    s.header("People you share with")
    s.group([{"t": "Alex", "sub": "Location (Find My)"},
             {"t": "Sam Sample", "sub": "Shared Album: Family Trip"}])
    s.note("Tap a person to review what they can see.")
    s.header("Location sharing")
    s.group([{"t": "Share My Location", "toggle": True},
             {"t": "Sharing from", "right": "This device", "chevron": False}])
    s.save("safety_check_people.png")


def sign_in_security():
    s = Screen("Apple Account", "Sign-In & Security", big_title=False)
    s.header("Email & phone numbers")
    s.group([{"t": "j.sample@example.com", "sub": "Primary email"},
             {"t": "+1 (555) 010-4477", "sub": "Trusted phone number"},
             {"t": "+1 (555) 010-9921", "sub": "Trusted phone number"}])
    s.header("Recovery")
    s.group([{"t": "Recovery email", "sub": "alex.m.1988@example.com"},
             {"t": "Account Recovery", "right": "1 contact"}])
    s.header("Security")
    s.group([{"t": "Change Password"},
             {"t": "Two-Factor Authentication", "right": "On"}])
    s.save("sign_in_security.png")


def location_services_apps():
    s = Screen("Privacy & Security", "Location Services", big_title=False)
    s.group([{"t": "Location Services", "toggle": True}])
    s.group([{"t": "Maps", "right": "While Using"},
             {"t": "FamilyLocate", "right": "Always"},
             {"t": "Messages", "right": "While Using"},
             {"t": "Photos", "right": "Never"},
             {"t": "Weather", "right": "While Using"}])
    s.note("A hollow arrow indicates an app may receive your location under certain conditions.")
    s.save("location_services_apps.png")


def family():
    s = Screen("Settings", "Family")
    s.group([{"t": "Alex", "sub": "Organizer"},
             {"t": "Jordan Sample", "sub": "Me"},
             {"t": "Sam Sample", "sub": "Child"}])
    s.header("Shared with family")
    s.group([{"t": "Location Sharing", "right": "On"},
             {"t": "Purchase Sharing", "right": "On"},
             {"t": "Screen Time", "right": "Off"}])
    s.save("family.png")


def text_forwarding():
    s = Screen("Messages", "Text Message Forwarding", big_title=False)
    s.note("Allow these devices to send and receive text messages from this iPhone.")
    s.group([{"t": "Home iPad", "toggle": True},
             {"t": "MacBook Air", "toggle": True},
             {"t": "Jordan's Mac mini", "toggle": False}])
    s.save("text_forwarding.png")


def vpn_device_management():
    s = Screen("General", "VPN & Device Management", big_title=False)
    s.header("VPN")
    s.group([{"t": "VPN", "right": "Not Connected"}])
    s.header("Configuration profile")
    s.group([{"t": "Device Monitor", "sub": "MonitorCo Ltd — Verified"}])
    s.save("vpn_device_management.png")


if __name__ == "__main__":
    for fn in (apple_id_devices, safety_check_people, sign_in_security,
               location_services_apps, family, text_forwarding, vpn_device_management):
        fn()
