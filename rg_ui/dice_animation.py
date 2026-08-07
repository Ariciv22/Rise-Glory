import math
import random
from pathlib import Path

import pygame


DICE_ROLL_DURATION_MS = 1450
DICE_FRAME_MS = 55


def _now_ms():
    return pygame.time.get_ticks()


def _clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def _ease_out_cubic(value):
    value = _clamp(value)
    return 1.0 - (1.0 - value) ** 3


def visible_face_numbers(main_value):
    """Return unique values for the visible faces of the procedural d20."""
    main_value = int(main_value)
    if not 1 <= main_value <= 20:
        raise ValueError("Wartosc scianki k20 musi miescic sie w zakresie 1-20")

    offsets = (0, 7, 13, 3, 10, 16, 5, 18, 9)
    values = []
    for offset in offsets:
        candidate = ((main_value - 1 + offset) % 20) + 1
        if candidate not in values:
            values.append(candidate)
    return values


class DiceRollAnimation:
    """Time-based k20 roll state independent from rendering frame rate."""

    def __init__(self, duration_ms=DICE_ROLL_DURATION_MS):
        self.duration_ms = int(duration_ms)
        self.rolling = False
        self.target = None
        self.started_at = None
        self.visual_seed = 0

    def start(self, result=None, now_ms=None, rng=None):
        if self.rolling or self.target is not None:
            return False

        rng = rng or random
        value = int(result if result is not None else rng.randint(1, 20))
        if not 1 <= value <= 20:
            raise ValueError("Rzut k20 musi miescic sie w zakresie 1-20")

        self.target = value
        self.started_at = int(_now_ms() if now_ms is None else now_ms)
        self.visual_seed = rng.randint(1, 2_000_000_000)
        self.rolling = True
        return True

    def progress(self, now_ms=None):
        if not self.rolling or self.started_at is None:
            return 1.0 if self.target is not None else 0.0
        now_ms = int(_now_ms() if now_ms is None else now_ms)
        return _clamp((now_ms - self.started_at) / max(1, self.duration_ms))

    def display_value(self, now_ms=None):
        if self.target is None:
            return None
        if not self.rolling:
            return self.target

        now_ms = int(_now_ms() if now_ms is None else now_ms)
        frame = max(0, (now_ms - self.started_at) // DICE_FRAME_MS)
        value = ((self.visual_seed + frame * 7 + frame * frame * 3) % 20) + 1
        if self.progress(now_ms) > 0.88:
            return self.target
        return value

    def update(self, now_ms=None):
        if not self.rolling:
            return None
        if self.progress(now_ms) < 1.0:
            return None
        self.rolling = False
        return self.target

    def stop(self):
        self.rolling = False


class PremiumD20Renderer:
    """Premium procedural renderer with optional PNG frame overrides."""

    def __init__(self, asset_root=None):
        self.asset_root = Path(asset_root) if asset_root else None
        self._roll_frames = None
        self._final_frames = {}
        self._font_cache = {}

    def _font(self, size, bold=True):
        key = (int(size), bool(bold))
        if key not in self._font_cache:
            self._font_cache[key] = pygame.font.SysFont("georgia", key[0], bold=key[1])
        return self._font_cache[key]

    def _load_image(self, path):
        try:
            return pygame.image.load(str(path)).convert_alpha()
        except (pygame.error, FileNotFoundError):
            return None

    def _load_roll_frames(self):
        if self._roll_frames is not None:
            return self._roll_frames
        self._roll_frames = []
        if self.asset_root:
            folder = self.asset_root / "roll"
            if folder.exists():
                for path in sorted(folder.glob("*.png")):
                    image = self._load_image(path)
                    if image:
                        self._roll_frames.append(image)
        return self._roll_frames

    def _load_final_frame(self, result):
        result = int(result)
        if result in self._final_frames:
            return self._final_frames[result]
        image = None
        if self.asset_root:
            candidates = [
                self.asset_root / "settle" / f"{result:02d}" / "final.png",
                self.asset_root / "final" / f"{result:02d}.png",
            ]
            for path in candidates:
                image = self._load_image(path)
                if image:
                    break
        self._final_frames[result] = image
        return image

    def _asset_frame(self, animation, final_value, now_ms):
        if animation.rolling:
            frames = self._load_roll_frames()
            if frames:
                progress = animation.progress(now_ms)
                index = min(len(frames) - 1, int(progress * len(frames)))
                return frames[index]
        if final_value is not None:
            return self._load_final_frame(final_value)
        return None

    def _draw_glow(self, screen, center, radius, strength):
        glow = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        gc = (glow.get_width() // 2, glow.get_height() // 2)
        for step in range(7, 0, -1):
            alpha = int(8 + 12 * strength) * step
            pygame.draw.circle(
                glow,
                (231, 145, 42, min(105, alpha)),
                gc,
                int(radius * (0.75 + step * 0.13)),
            )
        screen.blit(glow, glow.get_rect(center=center), special_flags=pygame.BLEND_RGBA_ADD)

    def _draw_particles(self, screen, center, radius, animation, now_ms):
        if animation.target is None:
            return
        progress = animation.progress(now_ms) if animation.rolling else 1.0
        rng = random.Random(animation.visual_seed)
        count = 20
        layer = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        for index in range(count):
            base_angle = rng.uniform(math.pi * 0.05, math.pi * 0.95)
            speed = rng.uniform(0.55, 1.25)
            phase = (progress * speed + index / count) % 1.0
            spread = radius * (0.35 + phase * 1.05)
            x = center[0] + math.cos(base_angle) * spread * rng.choice((-1, 1))
            y = center[1] + radius * 0.62 - math.sin(base_angle) * radius * phase * 0.65
            alpha = int(180 * (1.0 - phase) * (0.35 + progress * 0.65))
            size = max(1, int(radius * rng.uniform(0.012, 0.035) * (1.0 - phase * 0.5)))
            pygame.draw.circle(layer, (255, 174, 58, alpha), (int(x), int(y)), size)
        screen.blit(layer, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    def _geometry(self, size, main_value):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        c = size / 2
        r = size * 0.43

        outer = [
            (c, c - r),
            (c + r * 0.55, c - r * 0.72),
            (c + r * 0.92, c - r * 0.18),
            (c + r * 0.78, c + r * 0.46),
            (c + r * 0.35, c + r * 0.88),
            (c - r * 0.35, c + r * 0.88),
            (c - r * 0.78, c + r * 0.46),
            (c - r * 0.92, c - r * 0.18),
            (c - r * 0.55, c - r * 0.72),
        ]

        dark = (36, 19, 10)
        bronze = (91, 48, 18)
        gold = (223, 154, 55)
        bright = (255, 205, 105)
        amber_1 = (111, 50, 14)
        amber_2 = (169, 82, 20)
        amber_3 = (214, 121, 30)

        pygame.draw.polygon(surface, dark, outer)
        pygame.draw.polygon(surface, gold, outer, max(3, size // 85))

        v_top = outer[0]
        v_ur = outer[2]
        v_lr = outer[4]
        v_ll = outer[5]
        v_ul = outer[7]
        center_top = (c, c - r * 0.32)
        center_bottom = (c, c + r * 0.30)
        center_left = (c - r * 0.39, c + r * 0.05)
        center_right = (c + r * 0.39, c + r * 0.05)

        faces = [
            ([v_top, v_ul, center_top], amber_1),
            ([v_top, center_top, v_ur], amber_2),
            ([v_ul, center_left, center_top], amber_2),
            ([center_top, center_left, center_bottom], amber_3),
            ([center_top, center_bottom, center_right], amber_2),
            ([center_top, center_right, v_ur], amber_1),
            ([v_ul, outer[6], center_left], amber_1),
            ([center_left, outer[6], v_ll, center_bottom], amber_2),
            ([center_bottom, v_ll, v_lr], amber_1),
            ([center_bottom, v_lr, outer[3], center_right], amber_2),
            ([center_right, outer[3], v_ur], amber_1),
        ]
        for points, color in faces:
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, bronze, points, max(2, size // 115))

        glow = pygame.Surface((size, size), pygame.SRCALPHA)
        for ring in range(5, 0, -1):
            pygame.draw.circle(
                glow,
                (255, 153, 35, 15 + ring * 12),
                (int(c), int(c - r * 0.02)),
                int(r * (0.12 + ring * 0.055)),
            )
        surface.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        lines = [
            (v_top, center_top),
            (v_ul, center_top),
            (v_ur, center_top),
            (center_top, center_left),
            (center_top, center_right),
            (center_left, center_bottom),
            (center_right, center_bottom),
            (center_left, v_ul),
            (center_right, v_ur),
            (center_bottom, v_ll),
            (center_bottom, v_lr),
        ]
        for start, end in lines:
            pygame.draw.line(surface, dark, start, end, max(8, size // 26))
            pygame.draw.line(surface, gold, start, end, max(3, size // 80))

        for point in (v_top, v_ul, v_ur, center_top, center_left, center_right, center_bottom, v_ll, v_lr):
            pygame.draw.circle(surface, dark, (int(point[0]), int(point[1])), max(7, size // 22))
            pygame.draw.circle(surface, gold, (int(point[0]), int(point[1])), max(4, size // 35))
            pygame.draw.circle(surface, bright, (int(point[0] - size * 0.008), int(point[1] - size * 0.008)), max(1, size // 90))

        if main_value is not None:
            numbers = visible_face_numbers(main_value)
            positions = [
                (c, c - r * 0.03, 0, 1.0),
                (c, c - r * 0.60, 0, 0.46),
                (c - r * 0.58, c - r * 0.25, -22, 0.42),
                (c + r * 0.58, c - r * 0.25, 22, 0.42),
                (c - r * 0.47, c + r * 0.36, 18, 0.38),
                (c + r * 0.47, c + r * 0.36, -18, 0.38),
            ]
            for value, (x, y, angle, scale) in zip(numbers, positions):
                number_font = self._font(max(15, int(size * 0.19 * scale)), bold=True)
                shadow = number_font.render(str(value), True, (42, 20, 8))
                label = number_font.render(str(value), True, (255, 216, 125))
                if angle:
                    shadow = pygame.transform.rotozoom(shadow, angle, 1.0)
                    label = pygame.transform.rotozoom(label, angle, 1.0)
                surface.blit(shadow, shadow.get_rect(center=(int(x + 2), int(y + 3))))
                surface.blit(label, label.get_rect(center=(int(x), int(y))))

        return surface

    def draw(self, screen, center, radius, animation, final_value=None, now_ms=None):
        now_ms = int(_now_ms() if now_ms is None else now_ms)
        progress = animation.progress(now_ms) if animation.rolling else 1.0
        display_value = animation.display_value(now_ms) if animation.target is not None else final_value
        asset = self._asset_frame(animation, final_value, now_ms)

        if animation.rolling:
            eased = _ease_out_cubic(progress)
            angle = 1080.0 * eased + math.sin(progress * math.pi * 9.0) * (1.0 - progress) * 16.0
            if progress < 0.72:
                jump = -math.sin((progress / 0.72) * math.pi) * radius * 0.48
            else:
                landing = (progress - 0.72) / 0.28
                jump = -abs(math.sin(landing * math.pi * 2.0)) * radius * 0.12 * (1.0 - landing)
            scale = 1.0 + math.sin(progress * math.pi) * 0.09
            if 0.70 < progress < 0.82:
                scale *= 0.94 + abs(progress - 0.76) * 0.75
            shake = math.sin(progress * math.pi * 18.0) * (1.0 - progress) * radius * 0.045
        else:
            angle = 0.0
            jump = 0.0
            scale = 1.0
            shake = 0.0

        draw_center = (int(center[0] + shake), int(center[1] + jump))
        shadow_width = int(radius * (1.25 + (0.35 if animation.rolling else 0.0) * (1.0 - progress)))
        shadow_height = max(9, int(radius * 0.23 * (1.0 - min(0.75, -jump / max(1, radius)))))
        shadow = pygame.Surface((shadow_width * 2, shadow_height * 4), pygame.SRCALPHA)
        pygame.draw.ellipse(
            shadow,
            (0, 0, 0, 118),
            (0, shadow_height, shadow_width * 2, shadow_height * 2),
        )
        screen.blit(shadow, shadow.get_rect(center=(center[0], center[1] + int(radius * 0.72))))

        strength = 0.65 + (0.35 * math.sin(progress * math.pi * 5.0) ** 2 if animation.rolling else 0.20)
        self._draw_glow(screen, draw_center, radius, strength)
        self._draw_particles(screen, center, radius, animation, now_ms)

        if asset:
            base = pygame.transform.smoothscale(asset, (int(radius * 2.35), int(radius * 2.35)))
        else:
            base = self._geometry(max(180, int(radius * 2.55)), display_value)

        if animation.rolling and progress < 0.82:
            for trail_index, alpha in ((2, 28), (1, 46)):
                trail_angle = angle - trail_index * (18 + 20 * (1.0 - progress))
                trail = pygame.transform.rotozoom(base, trail_angle, scale * (1.0 - trail_index * 0.025))
                trail.set_alpha(alpha)
                offset = (draw_center[0] - trail_index * 5, draw_center[1] + trail_index * 3)
                screen.blit(trail, trail.get_rect(center=offset))

        die = pygame.transform.rotozoom(base, angle, scale)
        screen.blit(die, die.get_rect(center=draw_center))

        if not animation.rolling and final_value is not None:
            pulse = (math.sin(now_ms / 230.0) + 1.0) / 2.0
            ring = pygame.Surface((radius * 3, radius * 3), pygame.SRCALPHA)
            pygame.draw.circle(
                ring,
                (255, 199, 92, int(38 + pulse * 36)),
                (ring.get_width() // 2, ring.get_height() // 2),
                int(radius * (0.95 + pulse * 0.04)),
                max(2, radius // 30),
            )
            screen.blit(ring, ring.get_rect(center=center), special_flags=pygame.BLEND_RGBA_ADD)
