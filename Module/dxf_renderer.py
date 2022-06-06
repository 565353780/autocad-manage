#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import numpy as np

from Data.shape import Point

from Module.dxf_loader import DXFLoader

class DXFRenderer(DXFLoader):
    def __init__(self):
        super(DXFRenderer, self).__init__()

        self.image_width = None
        self.image_height = None
        self.free_width = None

        self.trans_point = None
        self.scale = None

        self.render_image_width = None
        self.render_image_height = None

        self.line_color = [0, 255, 0]
        self.circle_color = [0, 255, 255]

        self.image = None
        return

    def setImageSize(self, image_width, image_height, free_width):
        if image_width <= 2 * free_width or image_height <= 2 * free_width:
            print("[ERROR][DXFRenderer::setImageSize]")
            print("\t free_width out of range!")
            return False
        self.image_width = image_width
        self.image_height = image_height
        self.free_width = free_width
        return True

    def updateImageTrans(self):
        min_point = self.bbox.min_point
        self.trans_point = Point(-min_point.x, -min_point.y, -min_point.z)

        self.scale = float("inf")
        render_scale = float("inf")
        diff_point = self.bbox.diff_point
        if diff_point.x > 0:
            self.scale = min(self.scale,
                             1.0 * (self.image_width - 2.0 * self.free_width) / diff_point.x)
            render_scale = min(render_scale, 1.0 * self.image_width / diff_point.x)
        if diff_point.y > 0:
            self.scale = min(self.scale,
                             1.0 * (self.image_height - 2.0 * self.free_width) / diff_point.y)
            render_scale = min(render_scale, 1.0 * self.image_height / diff_point.y)

        if self.scale == float("inf"):
            self.scale = 1.0
        if render_scale == float("inf"):
            render_scale = 1.0

        self.render_image_width = int(diff_point.x * render_scale)
        self.render_image_height = int(diff_point.y * render_scale)
        return True

    def getImagePosition(self, world_potision):
        image_position = Point(
            int(self.free_width + (world_potision.x + self.trans_point.x) * self.scale),
            int(self.free_width + (world_potision.y + self.trans_point.y) * self.scale),
            int(self.free_width + (world_potision.z + self.trans_point.z) * self.scale))
        return image_position

    def getWorldPosition(self, image_position):
        world_potision = Point(
            1.0 * (image_position.x - self.free_width) / self.scale - self.trans_point.x,
            1.0 * (image_position.y - self.free_width) / self.scale - self.trans_point.y,
            1.0 * (image_position.z - self.free_width) / self.scale - self.trans_point.z)
        return world_potision

    def drawLine(self):
        for line in self.line_list:
            start_point_in_image = self.getImagePosition(line.start_point)
            end_point_in_image = self.getImagePosition(line.end_point)
            cv2.line(self.image,
                     (start_point_in_image.x, start_point_in_image.y),
                     (end_point_in_image.x, end_point_in_image.y),
                     np.array(self.line_color, dtype=np.float) / 255.0,
                     1, 4)
        return True

    def drawCircle(self):
        for circle in self.circle_list:
            center_in_image = self.getImagePosition(circle.center)
            radius_in_image = int(circle.radius * self.scale)
            cv2.circle(self.image,
                       (center_in_image.x, center_in_image.y),
                       radius_in_image,
                       n.array(self.circle_color, dtype=np.float) / 255.0,
                       1, 8, 0)
        return True

    def drawShape(self):
        self.drawLine()
        self.drawCircle()
        return True

    def render(self, wait_key=0):
        self.updateImageTrans()
        self.image = np.zeros((self.render_image_height, self.render_image_width, 3))

        if not self.drawShape():
            print("[ERROR][DXFRenderer::render]")
            print("\t drawShape failed!")
            return False

        cv2.imshow("DXFRenderer::render", self.image)
        cv2.waitKey(wait_key)
        return True

def demo():
    dxf_file_path = "/home/chli/chLi/Download/DeepLearning/Dataset/CAD/test1.dxf"
    image_width = 1600
    image_height = 900
    free_width = 50
    wait_key = 0

    dxf_renderer = DXFRenderer()
    dxf_renderer.loadFile(dxf_file_path)

    dxf_renderer.setImageSize(image_width, image_height, free_width)
    dxf_renderer.render(wait_key)

    #  dxf_renderer.outputInfo()
    return True

if __name__ == "__main__":
    demo()

