# -*- coding: utf-8 -*-
"""
Created on Mon Dec 27 18:36:36 2021

@author: Ruben
"""

# https://stackoverflow.com/questions/21591462/get-heading-and-pitch-from-pixels-on-street-view
# https://martinmatysiak.de/blog/view/panomarker

import numpy as np

class PhotoProjection(object):

    def __init__(self, fov, width, height, h0, p0):
        self.fov = fov
        self.width = width
        self.height = height
        self.h0 = np.radians(h0)
        self.p0 = np.radians(p0)
        self.x0, self.y0, self.z0 = self.__hp2xyz(self.h0, self.p0)

    def __repr__(self):

        return f"width={self.width}, height={self.height}, h0={self.h0}, p0={self.p0}, fov={self.fov}"

    def __hp2xyz(self, hi, pi):

        f = (self.width/2) / np.tan(np.radians(self.fov)/2)

        xi = f * np.cos(pi) * np.sin(hi)
        yi = f * np.cos(pi) * np.cos(hi)
        zi = f * np.sin(pi)

        return xi, yi, zi

    def __unit_vectors(self):
        # unit vectors: compute the derivatives of the spherical coordinates by the heading and pitch parameters at (p0, h0)
        vx = -np.sin(self.p0) * np.sin(self.h0)
        vy = -np.sin(self.p0) * np.cos(self.h0)
        vz = np.cos(self.p0)

        ux = np.sign(np.cos(self.p0)) * np.cos(self.h0)
        uy = -np.sign(np.cos(self.p0)) * np.sin(self.h0)
        uz = 0

        return (ux, uy, uz), (vx, vy, vz)

    def pixels2vectors(self, u, v):

        # some given pixel coordinates in the image

        # pixel coordinate to pixel offsets (to the right and to the top) from the viewport center
        du = u - (self.width/2)  # u - u0
        dv = (self.height / 2) - v  # v0 - v

        (ux, uy, uz), (vx, vy, vz) = self.__unit_vectors()

        # 3D coordinates of the point on the viewport matching the (du, dv) pixel offset in the viewport
        x = self.x0 + du * ux + dv * vx
        y = self.y0 + du * uy + dv * vy
        z = self.z0 + du * uz + dv * vz
        # print(f"x={x:.0f}, y={y:.0f}, z={z:.0f}")

        # radius, heading, pitch
        R = np.sqrt(x * x + y * y + z * z)
        h = np.degrees(np.arctan2(x, y))
        p = np.degrees(np.arcsin(z / R))
        # print(f"R={R:.0f}, h={np.degrees(h):.0f} ,p={np.degrees(p):.0f}")

        return h, p

    def vectors2pixels(self, h, p):
        # our coordinate system: camera at (0,0,0), heading = pitch = 0 at (0,R,0) calculate 3d coordinates of viewport center and target

        x, y, z = self.__hp2xyz(np.radians(h), np.radians(p))

        nDotD = self.x0 * x + self.y0 * y + self.z0 * z
        nDotC = self.x0 * self.x0 + self.y0 * self.y0 + self.z0 * self.z0

        # pov·pov / poi·pov

        # nDotD == |targetVec| * |currentVec| * cos(theta)
        # nDotC == |currentVec| * |currentVec| * 1
        # Note: |currentVec| == |targetVec| == R

        # t is the scale to use for the target vector such that its end touches the image plane.
        # t == (distance from camera to image plane through target) / (distance from camera to target == R)
        t = nDotC / nDotD

        # (tx, ty, tz) are the coordinates of the intersection point between a line through camera and target with the image plane
        tx = t * x
        ty = t * y
        tz = t * z

        # u and v are the basis vectors for the image plane
        (ux, uy, uz), (vx, vy, vz) = self.__unit_vectors()  # ojo: algo distinto

        # normalize horiz. basis vector to obtain orthonormal basis
        ul = np.sqrt(ux * ux + uy * uy + uz * uz)
        ux /= ul
        uy /= ul
        uz /= ul

        # project the intersection point t onto the basis to obtain offsets in terms of actual pixels in the viewport
        du = tx * ux + ty * uy + tz * uz
        dv = tx * vx + ty * vy + tz * vz

        u, v = (self.width/2) + du, (self.height/2) - dv

        # print(f"u={u:.0f}, v={v:.0f}")

        return u, v
