#!/usr/bin/python3
# -*- coding: utf-8 -*-

import random
import math
import sys
import json
import numpy as np


class Color:
    def set_random(self):
        self.r = random.randint(0, 255)
        self.g = random.randint(0, 255)
        self.b = random.randint(0, 255)

    def set_rgb(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def set_hex(self, hexcode):
        temp = hexcode.strip('#')
        if len(temp) is not 6:
            print(hexcode, "isn't a valid color")
            return
        self.set_rgb(
            int(temp[0:2], 16),
            int(temp[2:4], 16),
            int(temp[4:6], 16)
        )

    def get_hex(self):
        '''
        Return color in #hex format
        '''
        try:
            return "#{:02x}{:02x}{:02x}".format(self.r, self.g, self.b)
        except:
            print(self.r, self.g, self.b)

    def __init__(self, *args):
        if len(args) is 3:
            self.set_rgb(args[0], args[1], args[2])
        elif len(args) is 1:
            self.set_hex(args[0])
        else:
            self.set_rgb(0, 0, 0)

    def normalize_channels(self):
        if self.r < 0:
            self.r = 0
        elif self.r > 255:
            self.r = 255
        if self.g < 0:
            self.g = 0
        elif self.g > 255:
            self.g = 255
        if self.b < 0:
            self.b = 0
        elif self.b > 255:
            self.b = 255

    def shuffle_rgb(self, randomness):
        self.r += random.randint(-randomness, randomness)
        self.g += random.randint(-randomness, randomness)
        self.b += random.randint(-randomness, randomness)
        self.normalize_channels()

    def shuffle_brightness(self, randomness):
        offset = random.randint(-randomness, randomness)
        self.r += offset
        self.g += offset
        self.b += offset
        self.normalize_channels()

    def edit_brightness(self, amount):
        self.r += amount
        self.g += amount
        self.b += amount
        self.normalize_channels()

    def print_rgb(self):
        '''
        Print color channel values
        '''
        print('\033[31mR:\033[0m', self.r)
        print('\033[32mG:\033[0m', self.g)
        print('\033[34mB:\033[0m', self.b)


class Config():
    def load_default(self):
        self.colors = [Color('#000000'), Color('#ffffff')]
        self.edge_len = 50
        self.random_colors = True
        self.random_vertex = 35
        self.height = 1080
        self.width = 1920
        self.max_color_offset = 20
        self.uniform_rgb_offset = True
        self.vertical = False

    def load(self, filename):
        try:
            with open(filename, 'r') as fp:
                jconf = json.load(fp)
                self.colors = [Color(i) for i in jconf['colors']]
                self.edge_len = jconf['edge_len']
                self.random_colors = jconf['random_colors']
                self.random_vertex = jconf['random_vertex']
                self.height = jconf['height']
                self.width = jconf['width']
                self.max_color_offset = jconf['max_color_offset']
                self.uniform_rgb_offset = jconf['uniform_rgb_offset']
                self.vertical = jconf['vertical']
        except:
            print("Error reading", filename, file=sys.stderr)
            self.load_default()

    def __init__(self, *args):
        if len(args) is 0:
            self.load_default()
        else:
            self.load(args[0])


class PointsMap():
    def generate(self, length, height, edge_len):
        '''
        Create a list of vertices that can be used to create equilateral
        triangles with edlegen as lenght of each side
        Rows with odd index are shifted to the right by edge_len/2
        '''
        steepness = edge_len
        n_row = 8 + int(float(height) / (edge_len * math.sin(math.pi / 3.0)))
        n_column = 8 + int(float(length) / edge_len)
        temp_array = []
        for i in range(0, n_row):
            for j in range(0, n_column):
                offset = i % 2
                x_off = edge_len * 3
                y_off = edge_len * 2 * math.sin(math.pi / 3.0)
                temp_array.append([float(j * edge_len + offset * edge_len / 2.0) - x_off,
                                   i * edge_len * math.sin(math.pi / 3.0) - y_off,
                                   random.uniform(-steepness, steepness)])
        self.n_column = n_column
        self.points = np.array(temp_array)

    def __init__(self, length, height, edge_len):
        self.generate(length, height, edge_len)

    def shuffle_points(self, radius):
        '''
        Returns a list of vertices moved from another list
        The movement is radial with random angle and radius between 0.3*radius
        and 1*radius
        '''
        for point in self.points:
            effective_radius = random.randint(30, 100) * radius / 100.0
            angle = random.randint(0, 360) * 2 * math.pi / 360
            point[0] += effective_radius * math.cos(angle)
            point[1] += effective_radius * math.sin(angle)


class Triangle:
    def set_points(self, p1, p2, p3):
        '''
        Set p1, p2 and p3 as vertices
        '''
        self.p1 = np.array(p1)
        self.p2 = np.array(p2)
        self.p3 = np.array(p3)

    def get_center(self):
        '''
        Return coordinates of center
        '''
        return [(self.p1[0] + self.p2[0] + self.p3[0]) / 3.0,
                (self.p1[1] + self.p2[1] + self.p3[1]) / 3.0]

    def set_color_by_pos(self, colors, max_x):
        '''
        Set self color by self position using colors' steps
        '''
        if len(colors) is 0:
            self.color = Color(0, 0, 0)
        if len(colors) is 1:
            self.color = Color(colors[0].get_hex())
        else:
            center = self.get_center()
            if center[0] <= 0:
                self.color = Color(colors[0].get_hex())
            elif center[0] >= max_x:
                self.color = Color(colors[-1].get_hex())
            else:
                n_steps = len(colors) - 1
                step_width = max_x / n_steps
                i = 0
                while i * step_width < center[0]:
                    i += 1
                i -= 1
                l_color = colors[i]
                r_color = colors[i + 1]
                percent = (center[0] % step_width) / step_width
                r = (1-percent) * l_color.r + percent * r_color.r
                g = (1-percent) * l_color.g + percent * r_color.g
                b = (1-percent) * l_color.b + percent * r_color.b
                self.color = Color(int(r), int(g), int(b))
                self.color.normalize_channels()

    def add_light_source(self, source_direction, max_color_offset):
        triangle_vector = np.cross(self.p2 - self.p1, self.p3 - self.p1)
        multiplier = np.dot(triangle_vector, source_direction)
        multiplier /= np.linalg.norm(source_direction) * np.linalg.norm(triangle_vector)
        self.color.edit_brightness(int(multiplier * max_color_offset))

    def __init__(self):
        zero = [0, 0, 0]
        self.set_points(zero, zero, zero)
        self.color = Color()

    def export_center(self):
        c = self.get_center()
        return '<circle cx="{}" cy="{}" r="5" fill="red" />'.format(c[0], c[1])

    def export_svg(self):
        '''
        Return the triangle element as svg path
        '''
        s = ('<path d="M {:.2f},{:.2f} L{:.2f},{:.2f} L{:.2f},{:.2f} Z" '
             'style="fill:{}"/>')
        s = s.format(self.p1[0], self.p1[1],
                     self.p2[0], self.p2[1],
                     self.p3[0], self.p3[1],
                     self.color.get_hex())
        return s


class SvgBox():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.head = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                     '<svg xmlns:dc="http://purl.org/dc/elements/1.1/" '
                     'xmlns:cc="http://creativecommons.org/ns#" '
                     'xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" '
                     'xmlns:svg="http://www.w3.org/2000/svg" '
                     'xmlns="http://www.w3.org/2000/svg"\n'
                     'version="1.1"\n'
                     'viewBox="0 0 {w} {h}"\n'
                     'height="{h}"\nwidth="{w}">\n')\
            .format(w=self.width, h=self.height)
        self.tbody = '<g{}>\n'
        self.defs = ('<defs>\n<linearGradient id="grad1" '
                     'x1="0%" y1="0%" x2="100%" y2="0%">\n'
                     '{}</linearGradient>\n</defs>\n')
        self.gradient = ''
        self.end = '</g>\n</svg>'

    def set_vertical(self):
        self.tbody = self.tbody.format(' transform="scale(-1, 1) rotate(90)"')

    def set_horizontal(self):
        self.tbody = self.tbody.format('')

    def set_gradient(self, colors):
        step_width = 100 / (len(colors) - 1)
        for i in range(0, len(colors)-1):
            self.gradient += ('<stop offset="{}%" style="stop-color:{}"/>\n'
                              .format(i * step_width, colors[i].get_hex()))
        self.gradient += '<stop offset="100%" style="stop-color:{}"/>'\
                         .format(colors[-1].get_hex())
        self.defs = self.defs.format(self.gradient)

    def set_bg(self, colors, vertical):
        self.set_gradient(colors)
        if vertical:
            self.defs += ('<path id="rect" d="m {},{} {},0.0 0.0,{} {},0.0 z" '
                          'fill="url(#grad1)"/>').format(0,
                                                         0,
                                                         self.height,
                                                         self.width,
                                                         -self.height)
        else:
            self.defs += ('<path id="rect" d="m {},{} {},0.0 0.0,{} {},0.0 z" '
                          'fill="url(#grad1)"/>').format(0,
                                                         0,
                                                         self.width,
                                                         self.height,
                                                         -self.width)
        self.tbody = self.tbody + self.defs

    def add_body(self, text):
        self.tbody += text

    def get_body(self):
        return self.tbody

    def export(self):
        print(self.head+self.get_body()+self.end)


def main():
    config = Config("config.json")
    if config.vertical == 'random':
        if random.randint(0, 1):
            config.vertical = True
        else:
            config.vertical = False
    if config.vertical:
        map = PointsMap(config.height, config.width, config.edge_len)
        box = SvgBox(config.width, config.height)
        map.shuffle_points(config.random_vertex * config.edge_len / 100)
        box.set_vertical()
        max_axis_value = config.height
    else:
        map = PointsMap(config.width, config.height, config.edge_len)
        box = SvgBox(config.width, config.height)
        map.shuffle_points(config.random_vertex * config.edge_len / 100)
        box.set_horizontal()
        max_axis_value = config.width
    if config.random_colors is True:
        left = Color()
        right = Color()
        left.set_random()
        right.set_random()
        colors = [left, right]
    else:
        colors = config.colors
    box.set_bg(colors, config.vertical)
    source_direction = np.array([1, 0, 0])
    # /\ - shape
    for i in range(0, len(map.points)-map.n_column):
        if i % map.n_column != map.n_column-1:
            offset_odd_row = (i//map.n_column) % 2
            t = Triangle()
            t.set_points(
                map.points[i],
                map.points[i+1],
                map.points[i+map.n_column+offset_odd_row])
            t.set_color_by_pos(colors, max_axis_value)
            if config.uniform_rgb_offset:
                t.add_light_source(source_direction, config.max_color_offset)
            else:
                t.color.shuffle_rgb(config.max_color_offset)
            box.add_body(t.export_svg()+'\n')
    # \/ - shape
    for i in range(map.n_column, len(map.points)-1):
        if i % map.n_column != map.n_column-1:
            offset_odd_row = (i//map.n_column) % 2
            t = Triangle()
            t.set_points(
                map.points[i],
                map.points[i+1],
                map.points[i-map.n_column+offset_odd_row])
            t.set_color_by_pos(colors, max_axis_value)
            if config.uniform_rgb_offset:
                t.add_light_source(source_direction, config.max_color_offset)
            else:
                t.color.shuffle_rgb(config.max_color_offset)
            box.add_body(t.export_svg()+'\n')
    box.export()


if __name__ == "__main__":
    main()
