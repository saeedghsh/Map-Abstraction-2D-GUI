# Robot-Map-Abstraction

## Robot-Map-Annotation-GUI
A simple GUI for robot map annotation with simple curves 
This could be useful for fast creating "ground-truth".
The result also could be used by the Robot-Map-Arrangement-GUI to creat an "arrangement" representation of the map.


### Why buffer and list?
buffer is like a scrapbook where things are unstable, items could be added to it, but not selectively removed. it could be only reset or appended to the list. It has only graphical manifestation.

list is more stable. items in it could be selectively removed. it has a list widget in addition to graphical representation. selected items in the list widget will be highlighted to facilitate the selective removing process.

what is the difference between buffer and list?
list: in blue and solid line, also represented in the list widget
buffer: only represented graphically and in red dashed lines

appending the buffer to the list automatically resets the buffer.

### How to manually annotate?
annotation point (red points in the figure) could be added with left-click in the figure.
traits are created from the available annotation points with right-click in the figure.
after each trait construction, all available points are discarded

for line, ray and segmet only the last two annotation points are considered, the rest are ignored.
for ray, the first point is the starting point and the second point specifies the direction.
for segment, the two points are considered to be the ending points.

for the circle, if only two points are available, first is the center and the second one is considered to be on the perimeter of circle. if more than three points are available, the last three point are representing the perimeter of the circle.

for arc, only the first three points count, they are all considered to be on the perimeter of the arc, the first and third point define the ending points of the arc. the order of the first and last points are important, they should be CCW, passing through the body of arc.
Important note on Arc; it's not working well, I haven't fixed the "zero-crossing" problem of the radian for it.

### How to use radiography for automatic line ectraction?
First find the dominant orientations
Be aware that the GUI over-estimates the number of orientations and it is noisy.
The overestimates must be manually edited in the text widget.

Second, use radiography to find lines.
This also is very noisy (I still don't have a reliable peak-detection algorithm!).
It makes it much simpler work with if radiography is employ on single orientation.
Hey, that't what buffer and list are for.
Apply radiography in one direction, clean-up the mess, and append the desired traits from buffer to the list.
Continue with the other orientations.

### loading and saving traits to and fro file
supported: svg and yaml
important note on svg: see the known bugs


### visualization options
To have a clear vision of only traits in buffer, it's possible to only visualize traits in the buffer without loosing the list.
Also one can selectively visualize traits of a particular class.

### known bugs

for some reason (I'm not sure why myself!) I flip the image upside down after loading.
Of course it has something to do with opencv setting the origin of the image on top-left.
But this problem shows up while computing the gradient of the image (effecting the orientation estimation), and radiography (effecting the line extraction.)
The current order of flippings (I think three times, in 'myWindow.load_image', 'myWindow.find_dominant_orientations', and 'myWindow.find_lines_with_radiography') works fine for the GUI!
However, if inkscape is used for annotation of a map and the traits are saved as svg, then the GUI's frame of reference and the frame of SVG are fliped upside down relatively.
This problem started when I could not flip the image in the QT.graphiview connected to matplotlib, and the numpy.flipud was the quickest. Then the problem of opencv in gradient came about, and now I don't have hang of it!
The solution is to maintain the proper frame of reference for the GUI.
Start by jsut loading an image and not flipping it, then try to just plot it correctly.
Then make sure that the svg could be loaded and has the same frame of reference.
Finally find the correct places to adjust the frame of reference by flipping the image temporarily (maybe no-where, maybe only in gradient computation and radiography).
But, be careful not to screw up manual annotation's frame of reference!



## Robot-Map-Annotation-GUI


### TODO
- [ ] (arrangement) most importantly, is the visualization of the arrangement in here!
- [ ] (arrangement) fix the arrangement library to return the dual graphs (it might be actually there!)
- [ ] (arrangement) then, comes the question on how to convert arrangement's dual graphs to "adjacency map" and "connectivity map". This is not essentialy a problem to be solved in the arrangement library, so this is the place for it. Howeverm the answer to this question might require some though (on how to do it) rather than just coding!
(arrangement)
