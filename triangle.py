# -*- coding: latin-1 -*-
'''
Usage: python triangle.py width height edgelen randomness_points randomness_colors left_color right_color uniform_mode random_colors > file.svg
'''
import random
import math
import sys
import json

def create_array_map(length, height, edgelen):
    '''
    Return a list of vertices that can be used to create equilater triangles with edlegen as lenght of each side
    Rows with odd index are shifted to the right by edgelen/2
    '''
    n_row_max = 5+int(float(height)/(edgelen*math.sin(math.pi/3.0)))
    n_column_max = 5+int(float(length)/edgelen)
    temp_array = []
    for i in range(0, n_row_max):
        for j in range(0, n_column_max):
            offset = 0
            if i%2 == 1:
                offset = 1
            temp_array.append([float(j*edgelen+offset*edgelen/2.0), i*edgelen*math.sin(math.pi/3.0)])
    return n_column_max, temp_array

def move_points_random(arry, radius):
    '''
    Returns a list of vertices moved from another list
    The movement is radial with random angle and radius between 0.3*radius and 1*radius
    '''
    for i in range(0, len(arry)):
        effective_radius = random.randint(30, 100)*radius/100.0
        angle = random.randint(0, 360)*2*math.pi/360
        arry[i][0] += effective_radius*math.cos(angle)
        arry[i][1] += effective_radius*math.sin(angle)
    return arry

def rgb_to_int(color_string):
    '''
    Reads hex color as #xxxxxx or xxxxxx and returns RGB components as integers
    '''
    a = []
    if color_string[0] == '#':
        color_string = color_string[1:]
    if len(color_string) != 6:
        print "Error in color argument"
        exit()
    while color_string:
        a.append(int(color_string[0:2], 16))
        color_string = color_string[2:]
    return a[0], a[1], a[2]

def hard_gradient(x_cor, max_x, first_color, second_color, randomness):
    '''
    Returns linear gradient color between two colors depending on position of the first vertex
    '''
    a, b, c = rgb_to_int(first_color)
    d, e, f = rgb_to_int(second_color)
    percent = x_cor/float(max_x)
    if x_cor < 0:
        percent = 0
    if x_cor > max_x:
        percent = 1.0
    a = d*percent+a*(1-percent)
    b = e*percent+b*(1-percent)
    c = f*percent+c*(1-percent)
    return near_random_color(a, b, c, randomness)

def hard_gradient_center(vertices, max_x, first_color, second_color, randomness, uniform):
    '''
    Returns linear gradient color between two colors depending on position of all vertices
    '''
    a, b, c = rgb_to_int(first_color)
    d, e, f = rgb_to_int(second_color)
    x_cor = (vertices[0][0]+vertices[1][0]+vertices[2][0])/3.0
    if x_cor < 0:
        x_cor = 0
    if x_cor > max_x:
        x_cor = max_x
    percent = x_cor/float(max_x)
    
    a = d*percent+a*(1-percent)
    b = e*percent+b*(1-percent)
    c = f*percent+c*(1-percent)
    if uniform:
        return uniform_near_random_color(a, b, c, randomness)
    return near_random_color(a, b, c, randomness)
def near_random_color(a, b, c, randomness):
    '''
    Changes every rgb channel independently
    '''
    a = a +random.randint(-randomness, randomness)
    if a < 0:
        a = 0
    if a > 255:
        a = 255
    b = b +random.randint(-randomness, randomness)
    if b < 0:
        b = 0
    if b > 255:
        b = 255
    c = c +random.randint(-randomness, randomness)
    if c < 0:
        c = 0
    if c > 255:
        c = 255
    return '%02x%02x%02x'%(a, b, c)

def uniform_near_random_color(a, b, c, randomness):
    '''
    Same as near_random_color() but the randomness should only affect the brightness
    '''
    offset = random.randint(0, randomness)
    a = a+offset
    if a < 0:
        a = 0
    if a > 255:
        a = 255
    b = b+offset
    if b < 0:
        b = 0
    if b > 255:
        b = 255
    c = c+offset
    if c < 0:
        c = 0
    if c > 255:
        c = 255
    return '%02x%02x%02x'%(a, b, c)

def random_color():
    a = random.randint(0, 255)
    b = random.randint(0, 255)
    c = random.randint(0, 255)
    return '%02x%02x%02x'%(a, b, c)

def add_path(vertices, color):
    '''
    Creates the triangle element as svg path given its three points as a list and its colour
    '''
    first_v = vertices[0]
    second_v = vertices[1]
    third_v = vertices[2]
    string = '<path d="m '
    string += str(first_v[0])
    string += ','
    string += str(first_v[1])
    string += " "
    string += str(second_v[0]-first_v[0])
    string += ','
    string += str(second_v[1]-first_v[1])
    string += " "
    string += str(third_v[0]-second_v[0])
    string += ','
    string += str(third_v[1]-second_v[1])
    string += ' z" style="fill:#'+color+'"/>'
    return string

def insert_vertex(arry):
    '''
    Draws the vertices of the given list of points
    For debugging purpose
    '''
    for i in range(0, len(arry)):
        print '<circle cx="'+str(arry[i][0])+'" cy="'+str(arry[i][1])+'" r="1.5" fill="#ff0000" stroke-width="5"/>'
def load_config(namefile):
    fp = open(namefile, 'r')
    data = json.load(fp)
    fp.close()
    return data['width'], data['height'], data['edgelen'], data['randomvertex'], data['randomcolor'], data['firstcolor'], data['secondcolor'], data['uniform_rgb_offset'], data['randomcolors']

def save_config(namefile, arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9):
    fp = open(namefile, 'w')
    config = dict(width=arg1, height=arg2, edgelen=arg3, randomvertex=arg4, randomcolor=arg5, firstcolor=arg6, secondcolor=arg7, uniform_rgb_offset=arg8, randomcolors=arg9)
    json.dump(config, fp)
    fp.close()
def main():
    if len(sys.argv) < 2:
        width, heigth, size_edge, randomness, color_randomness, left_color, right_color, uniform_rgb_offset, random_colors = load_config("config.json")
    else:
        width = int(sys.argv[1])
        heigth = int(sys.argv[2])
        size_edge = float(sys.argv[3])
        randomness = float(sys.argv[4])
        color_randomness = int(sys.argv[5])
        left_color = sys.argv[6]
        right_color = sys.argv[7]
        uniform_rgb_offset = int(sys.argv[8])
        random_colors = int (sys.argv[9])
        save_config("config.json", width, heigth, size_edge, randomness, color_randomness, left_color, right_color, uniform_rgb_offset, random_colors)
    n_columns, array = create_array_map(width, heigth, size_edge)
    array = move_points_random(array, randomness*size_edge/100)


    base_text = '<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://creativecommons.org/ns#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg"\n'
    base_text += 'version="1.1"\nviewBox="0 0 %s %s"\nheight="%spx"\nwidth="%spx">\n'%(width, heigth, heigth, width)
    if random_colors == 1:
        a = random.randint(0, 255)
        b = random.randint(0, 255)
        c = random.randint(0, 255)
        d = random.randint(0, 255)
        e = random.randint(0, 255)
        f = random.randint(0, 255)
        left_color = '%02x%02x%02x'%(a, b, c)
        right_color = '%02x%02x%02x'%(d, e, f)
    color_1 = str(rgb_to_int(left_color))
    color_2 = str(rgb_to_int(right_color))
    base_text += '<g transform="translate(%s,%s)"\n>'%(-size_edge, -size_edge)
    base_text += '<defs>\n<linearGradient id="grad1" x1="0%%" y1="0%%" x2="100%%" y2="0%%">\n<stop offset="0%%" style="stop-color:rgb%s;stop-opacity:1" />\n<stop offset="100%%" style="stop-color:rgb%s;stop-opacity:1" />\n</linearGradient>\n</defs>\n'%(color_1, color_2)
    base_text += '<path id="rect" d="m %s,%s %s,0.0 0.0,%s %s,0.0 z" fill="url(#grad1)"/>'%(size_edge, size_edge, width, heigth, -width)
    print base_text
    for t in range(0, len(array)-n_columns):
        if t%n_columns != n_columns-1:
            offset_odd_row = (t/n_columns)%2
            vertices = [array[t], array[t+1], array[t+n_columns+offset_odd_row]]
            print add_path(vertices, hard_gradient_center(vertices, width, left_color, right_color, color_randomness, uniform_rgb_offset))
    for t in range(n_columns, len(array)-1):
        if t%n_columns != n_columns-1:
            offset_odd_row = (t/n_columns)%2
            vertices = [array[t], array[t+1], array[t-n_columns+offset_odd_row]]
            print add_path(vertices, hard_gradient_center(vertices, width, left_color, right_color, color_randomness, uniform_rgb_offset))
    print '</g>\n</svg>'
if __name__ == "__main__":
    main()
