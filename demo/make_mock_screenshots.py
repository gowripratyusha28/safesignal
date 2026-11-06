"""Draw fictional iOS-style settings screenshots for the demo (no real people/devices).

Usage: .venv/bin/python demo/make_mock_screenshots.py   -> demo/screenshots/*.png
Persona: "Jordan Sample" (survivor). "Alex" is the former partner. All names/emails fake.

Rendering notes (visual only; screen content is defined in the functions at the bottom):
- Drawn at 2x a 390x844 phone canvas (780x1688 px) so text stays crisp for the vision step.
- Text is vertically centred in rows, long notes wrap, chevrons/toggles are drawn shapes.
- Fonts: macOS system font when available, otherwise Inter / Lato / DejaVu.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent / "screenshots"

S = 2                      # render scale
LW, LH = 390, 844          # logical phone size (points)
W, H = LW * S, LH * S

BG = (242, 242, 247)
CARD = (255, 255, 255)
INK = (0, 0, 0)
MUTED = (110, 110, 118)
FAINT = (196, 196, 202)
BLUE = (0, 122, 255)
GREEN = (52, 199, 89)
RED = (255, 59, 48)
LINE = (220, 220, 225)
TOGGLE_OFF = (229, 229, 234)

MARGIN = 16                # group inset from screen edge
PAD = 16                   # text inset inside a group
ROW = 46                   # plain row height
ROW_SUB = 62               # row height with a subtitle
RADIUS = 11

_REGULAR = ["/System/Library/Fonts/SFNS.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/opentype/inter/Inter-Regular.otf",
            "/usr/share/fonts/truetype/lato/Lato-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
_BOLD = ["/Library/Fonts/SF-Pro-Display-Semibold.otf",
         "/System/Library/Fonts/Helvetica.ttc",          # index 1 = bold
         "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf",
         "/usr/share/fonts/truetype/lato/Lato-Bold.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]


def font(size, bold=False):
    """size is in points; returns a font at render scale."""
    for f in (_BOLD if bold else _REGULAR):
        try:
            idx = 1 if (bold and f.endswith(".ttc")) else 0
            return ImageFont.truetype(f, size * S, index=idx)
        except OSError:
            continue
    return ImageFont.load_default()


F_BODY = font(17)
F_SUB = font(14)
F_FOOT = font(13)
F_HEAD = font(13)
F_BACK = font(17)
F_NAV = font(17, True)
F_LARGE = font(32, True)
F_TIME = font(16, True)


def p(*vals):
    """Points -> pixels."""
    return [v * S for v in vals] if len(vals) > 1 else vals[0] * S


class Screen:
    def __init__(self, back, title, big_title=True):
        self.img = Image.new("RGB", (W, H), BG)
        self.d = ImageDraw.Draw(self.img)
        self._status_bar()
        self._nav(back, title, big_title)

    # ---------------------------------------------------------------- chrome
    def _status_bar(self):
        d = self.d
        d.text((p(40), p(27)), "9:41", fill=INK, font=F_TIME, anchor="lm")
        # signal bars
        x = LW - 98
        for i, h in enumerate((4, 6, 8, 10)):
            d.rounded_rectangle(p(x + i * 5, 32 - h, x + i * 5 + 3, 32), radius=p(1), fill=INK)
        # battery
        bx = LW - 70
        d.rounded_rectangle(p(bx, 21, bx + 25, 33), radius=p(4), outline=INK, width=round(p(1)))
        d.rounded_rectangle(p(bx + 2, 23, bx + 21, 31), radius=p(2), fill=INK)
        d.rounded_rectangle(p(bx + 26, 25, bx + 28, 29), radius=p(1), fill=INK)

    def _chevron(self, x, y, size, color, width, left=False):
        """Draw a > (or <) centred at (x, y) in points."""
        dx = -size / 2 if left else size / 2
        pts = [(x - dx, y - size), (x + dx, y), (x - dx, y + size)]
        self.d.line([(p(a), p(b)) for a, b in pts], fill=color, width=round(p(width)), joint="curve")

    def _nav(self, back, title, big_title):
        d = self.d
        cy = 66
        self._chevron(22, cy, 7.5, BLUE, 2.6, left=True)
        d.text((p(34), p(cy)), back, fill=BLUE, font=F_BACK, anchor="lm")
        back_end = 34 + d.textlength(back, font=F_BACK) / S
        title_w = d.textlength(title, font=F_NAV) / S
        fits_inline = LW / 2 - title_w / 2 > back_end + 8
        if big_title or not fits_inline:
            # large title, shrunk if needed so it never runs off the screen
            size = 32
            while size > 20 and d.textlength(title, font=font(size, True)) / S > LW - 2 * (MARGIN + 4):
                size -= 1
            d.text((p(MARGIN + 4), p(112)), title, fill=INK, font=font(size, True), anchor="ls")
            self.y = 136
        else:
            d.text((p(LW / 2), p(cy)), title, fill=INK, font=F_NAV, anchor="mm")
            self.y = 100

    # --------------------------------------------------------------- content
    def header(self, text):
        self.y += 6
        self.d.text((p(MARGIN + PAD), p(self.y + 10)), text.upper(), fill=MUTED, font=F_HEAD, anchor="lm")
        self.y += 26

    def group(self, rows):
        """rows: list of dicts {t, sub, right, toggle, color, chevron}"""
        d = self.d
        top = self.y
        h = sum(ROW_SUB if r.get("sub") else ROW for r in rows)
        d.rounded_rectangle(p(MARGIN, top, LW - MARGIN, top + h), radius=p(RADIUS), fill=CARD)
        y = top
        right_edge = LW - MARGIN - PAD
        for i, r in enumerate(rows):
            rh = ROW_SUB if r.get("sub") else ROW
            mid = y + rh / 2
            x = MARGIN + PAD
            if r.get("sub"):
                d.text((p(x), p(mid - 9)), r["t"], fill=r.get("color", INK), font=F_BODY, anchor="lm")
                d.text((p(x), p(mid + 12)), r["sub"], fill=MUTED, font=F_SUB, anchor="lm")
            else:
                d.text((p(x), p(mid)), r["t"], fill=r.get("color", INK), font=F_BODY, anchor="lm")

            if "toggle" in r:
                on = r["toggle"]
                tw, th = 51, 31
                x0, y0 = right_edge - tw, mid - th / 2
                d.rounded_rectangle(p(x0, y0, x0 + tw, y0 + th), radius=p(th / 2),
                                    fill=GREEN if on else TOGGLE_OFF)
                cx = x0 + tw - th / 2 if on else x0 + th / 2
                knob = th / 2 - 2
                d.ellipse(p(cx - knob, mid - knob + 0.6, cx + knob, mid + knob + 0.6), fill=(0, 0, 0, 20))
                d.ellipse(p(cx - knob, mid - knob, cx + knob, mid + knob), fill=CARD)
            else:
                chev = r.get("chevron", True)
                rx = right_edge - (16 if chev else 0)
                if r.get("right"):
                    d.text((p(rx), p(mid)), r["right"], fill=MUTED, font=F_BODY, anchor="rm")
                if chev:
                    self._chevron(right_edge - 4, mid, 5.5, FAINT, 2.2)

            if i < len(rows) - 1:
                d.line(p(MARGIN + PAD, y + rh, LW - MARGIN, y + rh), fill=LINE, width=max(1, S // 2 + 1))
            y += rh
        self.y = top + h + 18

    def note(self, text):
        """Footnote text, wrapped to the group width."""
        max_w = p(LW - 2 * (MARGIN + PAD))
        words, lines, cur = text.split(), [], ""
        for w in words:
            trial = (cur + " " + w).strip()
            if self.d.textlength(trial, font=F_FOOT) <= max_w:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        for ln in lines:
            self.d.text((p(MARGIN + PAD), p(self.y + 8)), ln, fill=MUTED, font=F_FOOT, anchor="lm")
            self.y += 18
        self.y += 14

    def save(self, name):
        # home indicator
        self.d.rounded_rectangle(p(LW / 2 - 67, LH - 13, LW / 2 + 67, LH - 8), radius=p(3), fill=INK)
        OUT.mkdir(parents=True, exist_ok=True)
        self.img.save(OUT / name, optimize=True)
        print("wrote", OUT / name)


# ------------------------------------------------------------------ screens
# Content below is unchanged from the original generator.

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
