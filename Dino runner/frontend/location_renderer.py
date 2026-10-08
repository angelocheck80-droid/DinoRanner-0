import math
from pathlib import Path

import pygame

from backend.constants import GROUND_Y, SCREEN_HEIGHT, SCREEN_WIDTH
from backend.day_night import (
    MAX_NIGHT_OPACITY,
    night_gradient_strength,
    twilight_glow_strength,
)


class LocationRenderer:
    def __init__(self):
        self.hint_font = pygame.font.Font(None, 22)
        self.room_font = pygame.font.Font(None, 28)
        self.room_hint_font = pygame.font.Font(None, 20)
        assets_path = Path(__file__).parent.parent / "UI"
        background = pygame.image.load(
            assets_path / "Background" / "Test2.jpg"
        ).convert()
        scale = max(
            SCREEN_WIDTH / background.get_width(),
            SCREEN_HEIGHT / background.get_height(),
        )
        scaled_size = (
            round(background.get_width() * scale),
            round(background.get_height() * scale),
        )
        background = pygame.transform.smoothscale(background, scaled_size)
        crop_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        crop_rect.center = background.get_rect().center
        self.outside_background = background.subsurface(crop_rect).copy()
        self.skyline_y = self._estimate_skyline()
        self.sky_visibility_mask = pygame.Surface(
            (SCREEN_WIDTH, GROUND_Y), pygame.SRCALPHA
        )
        for x, skyline_y in enumerate(self.skyline_y):
            pygame.draw.line(
                self.sky_visibility_mask,
                (224, 224, 255, 255),
                (x, 0),
                (x, skyline_y),
            )
        background_shadow = pygame.Surface(
            (SCREEN_WIDTH, GROUND_Y), pygame.SRCALPHA
        )
        shadow_center_x = SCREEN_WIDTH / 1.5
        shadow_center_y = GROUND_Y * 0.43
        shadow_radius_x = SCREEN_WIDTH * 0.28
        shadow_radius_y = GROUND_Y * 0.48
        
        for y in range(GROUND_Y):
            for x in range(SCREEN_WIDTH):
                distance = math.hypot(
                    (x - shadow_center_x) / shadow_radius_x,
                    (y - shadow_center_y) / shadow_radius_y,
                )
                falloff = max(0, 1 - distance)
                alpha = round(26 * falloff * falloff * (3 - 2 * falloff))
                if alpha:
                    background_shadow.set_at((x, y), (0, 0, 0, alpha))
        background_shadow.blit(
            self.sky_visibility_mask,
            (0, 0),
            special_flags=pygame.BLEND_RGBA_MULT,
        )
        self.outside_background.blit(background_shadow, (0, 0))
        gradient_path = assets_path / "Background" / "gradientmap_sky.png"
        gradient_source = pygame.image.load(gradient_path).convert_alpha()
        self.twilight_gradient = pygame.transform.smoothscale(
            gradient_source, (SCREEN_WIDTH, GROUND_Y)
        )
        for y in range(GROUND_Y):
            for x in range(SCREEN_WIDTH):
                red, green, blue, alpha = self.twilight_gradient.get_at((x, y))
                self.twilight_gradient.set_at(
                    (x, y),
                    (
                        round(red * alpha / 255),
                        round(green * alpha / 255),
                        round(blue * alpha / 255),
                        255,
                    ),
                )
        self.twilight_gradient.blit(
            self.sky_visibility_mask,
            (0, 0),
            special_flags=pygame.BLEND_RGB_MULT,
        )
        self.twilight_layer = pygame.Surface(
            (SCREEN_WIDTH, GROUND_Y), pygame.SRCALPHA
        )
        night_gradient_path = assets_path / "Background" / "gradientmap(night).png"
        self.night_gradient = pygame.transform.smoothscale(
            pygame.image.load(night_gradient_path).convert_alpha(),
            (SCREEN_WIDTH, GROUND_Y),
        )
        self.night_gradient.blit(
            self.sky_visibility_mask,
            (0, 0),
            special_flags=pygame.BLEND_RGBA_MULT,
        )
        self.night_horizon_glow = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )
        for x, skyline_y in enumerate(self.skyline_y):
            start_y = max(0, skyline_y - 34)
            end_y = min(SCREEN_HEIGHT, skyline_y + 13)
            for y in range(start_y, end_y):
                if y <= skyline_y:
                    progress = 1 - (skyline_y - y) / 34
                    alpha = round(22 * progress * progress)
                else:
                    progress = 1 - (y - skyline_y) / 13
                    alpha = round(14 * progress * progress)
                if alpha:
                    self.night_horizon_glow.set_at(
                        (x, y), (255, 255, 0, alpha)
                    )
        night_stars_path = (
            assets_path / "Background" / "gradientmap_sky(night_stars).png"
        )
        self.night_stars = pygame.transform.smoothscale(
            pygame.image.load(night_stars_path).convert_alpha(),
            (SCREEN_WIDTH, GROUND_Y),
        )
        self.night_stars.blit(
            self.sky_visibility_mask,
            (0, 0),
            special_flags=pygame.BLEND_RGBA_MULT,
        )
        self.sky_overlay = pygame.Surface(
            (SCREEN_WIDTH, GROUND_Y), pygame.SRCALPHA
        )
        fade_start_y = SCREEN_HEIGHT // 2 - 12

        for y in range(GROUND_Y):
            if y <= fade_start_y:
                alpha = 255
                color = (0, 0, 0)
            else:
                progress = (y - fade_start_y) / (GROUND_Y - 1 - fade_start_y)
                blend = progress * progress * (3 - 2 * progress)
                color = tuple(round(channel * blend) for channel in (0, 23, 100))
                alpha = round(255 - 32 * blend)
            pygame.draw.line(
                self.sky_overlay,
                (*color, alpha),
                (0, y),
                (SCREEN_WIDTH - 1, y),
            )
        self.sky_lights = pygame.Surface(
            (SCREEN_WIDTH, GROUND_Y), pygame.SRCALPHA
        )

        moon_path = assets_path / "Background" / "moon_final.png"
        moon_source = self._load_alpha_asset(moon_path, min_alpha=128)

        if moon_source:
            moon_width = round(moon_source.get_width() * 30 / moon_source.get_height())
            self.moon_image = pygame.transform.smoothscale(
                moon_source, (moon_width, 30)
            )
            self._clip_to_circle(self.moon_image)
            self.moon_image.fill(
                (224, 236, 255, 255),
                special_flags=pygame.BLEND_RGBA_MULT,
            )
            self.moon_image.set_alpha(round(255 * 0.72))
        else:
            self.moon_image = None
        self.moon_glow = pygame.Surface((64, 255), pygame.SRCALPHA)
        moon_glow_center = (31.5, 31.5)
        moon_glow_radius = 128
        for y in range(64):
            for x in range(64):
                distance = math.hypot(
                    x - moon_glow_center[0], y - moon_glow_center[1]
                )
                falloff = math.exp(-3 * (distance / moon_glow_radius) ** 2)
                alpha = round(44 * falloff)
                if alpha:
                    self.moon_glow.set_at(
                        (x, y), (175, 198, 255, alpha)
                    )
        self.ground_color = (30, 62, 44)
        self.ground_transition_height = 6
        self.ground_transition = pygame.Surface(
            (SCREEN_WIDTH, self.ground_transition_height), pygame.SRCALPHA
        )

        old_man_files = ("old_man.png", "old man 3.png")
        self.old_man_images = []
        for filename in old_man_files:
            old_man = pygame.image.load(assets_path / filename).convert_alpha()
            old_man_width = round(old_man.get_width() * 52 / old_man.get_height())
            self.old_man_images.append(
                pygame.transform.smoothscale(old_man, (old_man_width, 52))
            )
        self.old_man_bottom_offsets = [
            image.get_height() - image.get_bounding_rect(min_alpha=1).bottom
            for image in self.old_man_images
        ]

    def _load_alpha_asset(self, asset_path, min_alpha=32):
        source = pygame.image.load(asset_path).convert_alpha()
        bounds = source.get_bounding_rect(min_alpha=min_alpha)
        if bounds.width == 0 or bounds.height == 0:
            return None
        return source.subsurface(bounds).copy()

    def _clip_to_circle(self, source):
        center_x = (source.get_width() - 1) / 2
        center_y = (source.get_height() - 1) / 2
        radius = min(source.get_size()) / 2
        feather = 1.5
        for y in range(source.get_height()):
            for x in range(source.get_width()):
                distance = math.hypot(x - center_x, y - center_y)
                strength = max(0, min(1, (radius - distance) / feather))
                strength = strength * strength * (3 - 2 * strength)
                color = source.get_at((x, y))
                source.set_at(
                    (x, y),
                    (*color[:3], round(color.a * strength)),
                )
        return source

    def _estimate_skyline(self):
        skyline = []
        for x in range(SCREEN_WIDTH):
            skyline_y = GROUND_Y - 1
            for y in range(35, GROUND_Y - 8):
                red, green, blue = self.outside_background.get_at((x, y))[:3]
                local_luminance = (red + green + blue) / 3
                lower_luminance = 0
                for sample_y in range(y, y + 8):
                    sample = self.outside_background.get_at((x, sample_y))
                    lower_luminance += sum(sample[:3]) / 3
                lower_luminance /= 8
                if local_luminance < 190 and lower_luminance < 200:
                    skyline_y = y
                    break
            skyline.append(skyline_y)

        smooth_radius = 4
        return [
            round(
                sum(skyline[max(0, x - smooth_radius):x + smooth_radius + 1])
                / len(skyline[max(0, x - smooth_radius):x + smooth_radius + 1])
            )
            for x in range(SCREEN_WIDTH)
        ]

    def draw(self, screen, location, player, camera_x, night_opacity=0, now=None):
        if location.inside:
            self._draw_inside(screen)
        else:
            self._draw_outside(
                screen, location, player, camera_x, night_opacity, now
            )

    def _draw_outside(self, screen, location, player, camera_x, night_opacity, now):
        screen.blit(self.outside_background, (0, 0))
        self._draw_sky_lighting(screen, night_opacity, now)
        screen.blit(
            self.ground_transition,
            (0, GROUND_Y - self.ground_transition_height),
        )
        pygame.draw.rect(
            screen,
            self.ground_color,
            (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y),
        )
        pygame.draw.line(
            screen,
            (30, 62, 44),
            (0, GROUND_Y),
            (SCREEN_WIDTH - 1, GROUND_Y),
        )

        house_rect = pygame.Rect(
            location.house_x - camera_x,
            GROUND_Y - 125,
            location.house_width,
            125,
        )
        pygame.draw.rect(screen, (220, 159, 91), house_rect)
        roof_points = [
            (house_rect.left - 20, house_rect.top),
            (house_rect.centerx, house_rect.top - 70),
            (house_rect.right + 20, house_rect.top),
        ]
        pygame.draw.polygon(screen, (139, 73, 52), roof_points)

        door_rect = pygame.Rect(location.door_x - camera_x, GROUND_Y - 75, 42, 75)
        door_color = (242, 206, 87) if location.near_door(player) else (91, 57, 42)
        pygame.draw.rect(screen, door_color, door_rect)
        pygame.draw.circle(
            screen, (245, 224, 137), (door_rect.right - 8, door_rect.centery), 3
        )

        npc_rect = pygame.Rect(
            location.npc_x - camera_x,
            location.npc_y,
            location.npc_w,
            location.npc_h,
        )
        frame_index = 1 if location.near_npc(player) else 0
        old_man_image = self.old_man_images[frame_index]
        old_man_rect = old_man_image.get_rect(
            midbottom=(
                npc_rect.centerx,
                npc_rect.bottom + self.old_man_bottom_offsets[frame_index],
            )
        )
        screen.blit(old_man_image, old_man_rect)
    def _draw_sky_lighting(self, screen, night_opacity, now):
        twilight_strength = twilight_glow_strength(now)
        effective_night_opacity = round(
            night_opacity * (1 - 0.72 * twilight_strength)
        )
        if effective_night_opacity:
            self.sky_overlay.set_alpha(
                round(255 * effective_night_opacity / MAX_NIGHT_OPACITY)
            )
            screen.blit(self.sky_overlay, (0, 0))

        if twilight_strength:
            self.twilight_layer.blit(self.twilight_gradient, (0, 0))
            intensity = round(255 * twilight_strength)
            self.twilight_layer.fill(
                (intensity, intensity, intensity),
                special_flags=pygame.BLEND_RGB_MULT,
            )
            screen.blit(
                self.twilight_layer,
                (0, 0),
                special_flags=pygame.BLEND_RGB_ADD,
            )

        if effective_night_opacity:
            self.night_gradient.set_alpha(
                round(255 * night_gradient_strength(now))
            )
            screen.blit(self.night_gradient, (0, 0))
            self.night_horizon_glow.set_alpha(
                round(255 * night_gradient_strength(now))
            )
            screen.blit(self.night_horizon_glow, (0, 0))
            self.night_stars.set_alpha(
                round(255 * effective_night_opacity / MAX_NIGHT_OPACITY)
            )
            screen.blit(self.night_stars, (0, 0))

        self.sky_lights.fill((0, 0, 0, 0))
        moon_alpha = round(
            255 * effective_night_opacity / MAX_NIGHT_OPACITY
        )
        if moon_alpha:
            moon_position = (SCREEN_WIDTH - 28, 28)
            moon_glow_rect = self.moon_glow.get_rect(center=moon_position)
            self.sky_lights.blit(self.moon_glow, moon_glow_rect)
            if self.moon_image:
                moon_rect = self.moon_image.get_rect(center=moon_position)
                self.sky_lights.blit(self.moon_image, moon_rect)
            else:
                pygame.draw.circle(
                    self.sky_lights,
                    (245, 232, 180),
                    moon_position,
                    8,
                )

        self.sky_lights.blit(
            self.sky_visibility_mask,
            (0, 0),
            special_flags=pygame.BLEND_RGBA_MULT,
        )
        self.sky_lights.set_alpha(moon_alpha)
        screen.blit(self.sky_lights, (0, 0)) 

    def _draw_inside(self, screen):
        screen.fill((231, 205, 160))
        pygame.draw.rect(
            screen,
            (124, 83, 58),
            (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y),
        )
        pygame.draw.rect(screen, (184, 124, 77), (55, 45, 130, 35))
        pygame.draw.rect(screen, (79, 132, 164), (75, 55, 40, 25))
        pygame.draw.rect(screen, (79, 132, 164), (125, 55, 40, 25))
