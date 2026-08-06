import unittest

from rg_map import Camera, ISOMETRIC_Y_SCALE, Tile


class IsometricCameraTests(unittest.TestCase):
    def test_apply_flattens_vertical_axis(self):
        camera = Camera()
        camera.x = 0
        camera.y = 0
        camera.zoom = 1

        self.assertEqual(camera.apply(100, 0), (100, 0))
        self.assertAlmostEqual(camera.apply(0, 100)[1], 100 * ISOMETRIC_Y_SCALE)

    def test_unapply_restores_world_coordinates(self):
        camera = Camera()
        camera.x = 320
        camera.y = 180
        camera.zoom = 1.35

        screen_point = camera.apply(245.5, -91.25)
        restored = camera.unapply(*screen_point)

        self.assertAlmostEqual(restored[0], 245.5)
        self.assertAlmostEqual(restored[1], -91.25)

    def test_zoom_keeps_world_point_under_cursor(self):
        camera = Camera()
        camera.x = 220
        camera.y = 140
        camera.zoom = 0.8
        mouse = (730, 415)

        before = camera.unapply(*mouse)
        camera.zoom_at(mouse, 1.1)
        after = camera.unapply(*mouse)

        self.assertAlmostEqual(before[0], after[0])
        self.assertAlmostEqual(before[1], after[1])

    def test_tile_hit_polygon_uses_isometric_projection(self):
        camera = Camera()
        camera.x = 0
        camera.y = 0
        camera.zoom = 1
        tile = Tile(1, 0, 0, 0, 0, "plains")

        points = tile.screen_points(camera)
        width = max(point[0] for point in points) - min(point[0] for point in points)
        height = max(point[1] for point in points) - min(point[1] for point in points)

        self.assertGreater(width, height)
        self.assertTrue(tile.contains((0, 0), camera))


if __name__ == "__main__":
    unittest.main()
