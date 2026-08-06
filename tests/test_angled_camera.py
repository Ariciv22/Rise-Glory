import math
import unittest

from rg_map import CAMERA_ANGLE_DEGREES, Camera, Tile


class AngledCameraTests(unittest.TestCase):
    def test_camera_uses_diagonal_angle(self):
        camera = Camera()
        self.assertEqual(camera.angle_degrees, CAMERA_ANGLE_DEGREES)
        self.assertEqual(camera.angle_degrees, 30.0)

    def test_rotation_preserves_distance_and_does_not_stretch_hexes(self):
        camera = Camera()
        points = [(0.0, 0.0), (130.0, -45.0)]
        rotated = [camera.rotate_world(x, y) for x, y in points]

        world_distance = math.dist(points[0], points[1])
        rotated_distance = math.dist(rotated[0], rotated[1])

        self.assertAlmostEqual(world_distance, rotated_distance)

    def test_apply_and_unapply_are_inverse_operations(self):
        camera = Camera()
        camera.x = 420
        camera.y = 275
        camera.zoom = 1.35

        screen_point = camera.apply(183.25, -91.75)
        world_point = camera.unapply(*screen_point)

        self.assertAlmostEqual(world_point[0], 183.25)
        self.assertAlmostEqual(world_point[1], -91.75)

    def test_zoom_keeps_same_world_point_under_cursor(self):
        camera = Camera()
        camera.x = 250
        camera.y = 160
        camera.zoom = 0.8
        cursor = (730, 410)

        before = camera.unapply(*cursor)
        camera.zoom_at(cursor, 1.1)
        after = camera.unapply(*cursor)

        self.assertAlmostEqual(before[0], after[0])
        self.assertAlmostEqual(before[1], after[1])

    def test_tile_click_area_uses_same_rotation_as_drawing(self):
        camera = Camera()
        camera.x = 0
        camera.y = 0
        camera.zoom = 1
        tile = Tile(1, 0, 0, 0, 0, "plains")

        self.assertTrue(tile.contains(camera.apply(0, 0), camera))

        original_edge_lengths = [
            math.dist(tile.points[index], tile.points[(index + 1) % 6])
            for index in range(6)
        ]
        screen_points = tile.screen_points(camera)
        screen_edge_lengths = [
            math.dist(screen_points[index], screen_points[(index + 1) % 6])
            for index in range(6)
        ]

        for original, projected in zip(original_edge_lengths, screen_edge_lengths):
            self.assertAlmostEqual(projected, original * camera.zoom)


if __name__ == "__main__":
    unittest.main()
