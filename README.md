Robot-Map-Abstraction
=====================

Dependencies and Download
-------------------------
Most dependencies are listed in `requirements.txt`, and will be installed by the following instructions.
But there are two more, namely [opencv](http://docs.opencv.org/trunk/d7/d9f/tutorial_linux_install.html) and [arrangement](https://github.com/saeedghsh/arrangement/), which should be installed separately.
```shell
# Download
git clone https://github.com/saeedghsh/Map-Abstraction-2D.git
cd Map-Abstraction-2D

# Install dependencies
pip install -r requirements.txt

# launch GUIs
python runMe_annotation.py
python runMe_arrangement.py
```

Annotation GUI
--------------
A simple GUI for map annotation with simple geometric traits.
This could be useful for fast manual annotation for "ground-truth".
The result also could be used by the Arrangement-GUI to creat an [arrangement](https://github.com/saeedghsh/arrangement) representation of the map.
![Annotation_GUI](https://github.com/saeedghsh/Map-Abstraction-2D/blob/master/docs/annotation_gui.png)
Read on how to use the GUI [here](https://github.com/saeedghsh/Map-Abstraction-2D/blob/master/docs/HOWTO_annotation_GUI.md).

Arrangement GUI
---------------
This GUI is for constructing an [arrangement](https://github.com/saeedghsh/arrangement), and visualizing the result.
![Arrangement_GUI](https://github.com/saeedghsh/Map-Abstraction-2D/blob/master/docs/arrangement_gui.png)
Read on how to use this GUI [here](https://github.com/saeedghsh/Map-Abstraction-2D/blob/master/docs/HOWTO_arrangement_GUI.md).

Laundry List
------------
- [ ] skimage seems unnecessary.
- [ ] (annotation) remove the perpendicular assumption of the automatic dominant orientation.
- [ ] (annotation)add automatice trait detection for circle.
- [ ] (arrangement) animating the arrangement.
- [ ] (arrangement) interactive face selection and attribute assignment.
- [ ] (arrangement) save arrangement result.

License
-------
Distributed with a GNU GENERAL PUBLIC LICENSE; see LICENSE.
```
Copyright (C) Saeed Gholami Shahbandi <saeed.gh.sh@gmail.com>
```

These GUIs have been made to facilitate the experimentation and developement of the methods of the following publications:
- S. G. Shahbandi, B. Åstrand and R. Philippsen, "Sensor based adaptive metric-topological cell decomposition method for semantic annotation of structured environments", ICARCV, Singapore, 2014, pp. 1771-1777. doi: 10.1109/ICARCV.2014.7064584 [URL](http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=7064584&isnumber=7064265).
- S. G. Shahbandi, B. Åstrand and R. Philippsen, "Semi-supervised semantic labeling of adaptive cell decomposition maps in well-structured environments", ECMR, Lincoln, 2015, pp. 1-8. doi: 10.1109/ECMR.2015.7324207 [URL](http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=7324207&isnumber=7324045).
- S. G. Shahbandi, ‘Semantic Mapping in Warehouses’, Licentiate dissertation, Halmstad University, 2016. [URL](http://urn.kb.se/resolve?urn=urn:nbn:se:hh:diva-32170)
- S. G. Shahbandi, M. Magnusson, "2D Map Alignment With Region Decomposition", submitted to Autonomous Robots, 2017.
