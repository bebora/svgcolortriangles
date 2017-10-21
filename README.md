# svgcolortriangles
Create svg images with triangles using python in linux
```
Usage:
  python triangle.py [ARGS] > yourfile.svg

-Arguments:
  The script loads the config.json settings if it doesn't receive any argument
  Otherwise you must write all the arguments needed in the following order:
  width height edgelen randomness_points randomness_colors left_color right_color uniform_mode
  
  width = Width of the image
  height = Heigth of the image
  edgelen = Lenght of the side of each equilateral triangle before being transformed
  randomness_points = The max percentage of randomness of each point. High values mess things up
  randomness_colors = The max difference between original colors and randomized colors for each RGB channel
  left_color = Color on the left, must be written as #xxxxxx or xxxxxx
  right_color = Color on the right, must be written as #xxxxxx or xxxxxx
  uniform_mode = Set it to 1 to make the color randomizer affect only brightness of each triangle
  For example:
  python triangle.py 1920 1080 35 20 #ff662a #22ffe3 1 > example.svg
```
