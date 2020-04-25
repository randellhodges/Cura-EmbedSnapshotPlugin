# Original source by Ultimaker, modified
# https://github.com/Ultimaker/Cura/blob/master/cura/Snapshot.py

# Copyright (c) 2018 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.
import numpy

from PyQt5 import QtCore
from PyQt5.QtGui import QImage

#from cura.PreviewPass import PreviewPass
from .PreviewPass import PreviewPass

from UM.Logger import Logger

from UM.Application import Application
from UM.Math.Matrix import Matrix
from UM.Math.Vector import Vector
from UM.Scene.Camera import Camera
from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator


class Snapshot:
    @staticmethod
    def getImageBoundaries(image: QImage):
        # Look at the resulting image to get a good crop.
        # Get the pixels as byte array
        pixel_array = image.bits().asarray(image.byteCount())
        width, height = image.width(), image.height()
        # Convert to numpy array, assume it's 32 bit (it should always be)
        pixels = numpy.frombuffer(pixel_array, dtype=numpy.uint8).reshape([height, width, 4])
        # Find indices of non zero pixels
        nonzero_pixels = numpy.nonzero(pixels)
        min_y, min_x, min_a_ = numpy.amin(nonzero_pixels, axis=1)
        max_y, max_x, max_a_ = numpy.amax(nonzero_pixels, axis=1)

        return min_x, max_x, min_y, max_y

    ##  Return a QImage of the scene
    #   Uses PreviewPass that leaves out some elements
    @staticmethod
    def snapshot(width = 300, height = 300):

        scene = Application.getInstance().getController().getScene()
        active_camera = scene.getActiveCamera()

        render_width, render_height = active_camera.getWindowSize()
        render_width = int(render_width)
        render_height = int(render_height)

        preview_pass = PreviewPass(render_width, render_height)

        root = scene.getRoot()
        camera = Camera("snapshot", root)

        # determine zoom and look at
        bbox = None
        for node in DepthFirstIterator(root):
            if not getattr(node, "_outside_buildarea", False):
                if node.callDecoration("isSliceable") and node.getMeshData() and node.isVisible() and not node.callDecoration("isNonThumbnailVisibleMesh"):
                    if bbox is None:
                        bbox = node.getBoundingBox()
                    else:
                        bbox = bbox + node.getBoundingBox()
        # If there is no bounding box, it means that there is no model in the buildplate
        if bbox is None:
            return None

        look_at = bbox.center

        # guessed size so the objects are hopefully big
        size = max(bbox.width, bbox.height, bbox.depth * 0.5)

        # Looking from this direction (x, y, z) in OGL coordinates
        looking_from_offset = Vector(-1, 1, 2)
        if size > 0:
            # determine the watch distance depending on the size
            looking_from_offset = looking_from_offset * size * 1.75

        camera.setPosition(look_at + looking_from_offset)
        camera.lookAt(look_at)

        fovy = 30
        last_size = 0

        while True:

            projection_matrix = Matrix()

            # Somehow the aspect ratio is also influenced in reverse by the screen width/height
            # So you have to set it to render_width/render_height to get 1
            projection_matrix.setPerspective(fovy, render_width / render_height, 1, 500)
            camera.setProjectionMatrix(projection_matrix)

            preview_pass.setCamera(camera)
            preview_pass.render()

            pixel_output = preview_pass.getOutput()

            try:
                min_x, max_x, min_y, max_y = Snapshot.getImageBoundaries(pixel_output)
            except ValueError:
                return None

            size = max((max_x - min_x) / render_width, (max_y - min_y) / render_height)

            #Logger.log("d", "RLH - fovy = %.4f, last_size = %.4f, size = %.4f", fovy, last_size, size)

            if size > 0.8 or (last_size >= size):
                break
            else:
                # make it big and allow for some empty space around
                fovy *= 0.9  # strangely enough this messes up the aspect ratio: fovy *= size * 1.1
                last_size = size

        # Scale it to the correct size
        scaled_image = pixel_output.scaled(
            width, height,
            aspectRatioMode = QtCore.Qt.KeepAspectRatio,
            transformMode = QtCore.Qt.SmoothTransformation)

        return scaled_image
