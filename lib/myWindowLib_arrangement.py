# "
# Copyright (C) 2015 Saeed Gholami Shahbandi. All rights reserved.

# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>
# "

# pushButton_auto_detect_lines_rays_segments

import sys, os, platform, time

# from sklearn import mixture
import numpy as np
from numpy.linalg import det
import sympy as sym
import cv2
import yaml
import PySide

import myCanvasLib
import arrangement_gui

import arrangement.arrangement as arr
import arrangement.geometricTraits as trts
# import arrangement.plotting as aplt

#####################################################################
#####################################################################
#####################################################################

class MainWindow(PySide.QtGui.QMainWindow, arrangement_gui.Ui_MainWindow):
    
    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent)
        self.ui = arrangement_gui.Ui_MainWindow()
        self.ui.setupUi(self)

        self.annotation = []
        self.trait_list = []
        self.selected_faces = []
        self.data = {'image_name':'',
                     'image':None,
                     'arrangement': None,
                     'arrang_config': {'multi_processing':4, 'end_point':False}}

        #####################################################################
        ############################## connecting graphicsViews to mpl canvas
        #####################################################################

        # self.ui.graphicsView_arrangement
        arrangement_widget = self.ui.graphicsView_arrangement
        self.arrangement_canvas = myCanvasLib.MyMplCanvas(arrangement_widget)
        layout = PySide.QtGui.QVBoxLayout(arrangement_widget)
        layout.addWidget(self.arrangement_canvas)
        self.arrangement_canvas.mpl_connect('button_press_event', self.mouseClick_face_selection)

        #####################################################################
        #####################################################################
        #####################################################################
        self.ui.pushButton_load_map.clicked.connect(self.load_image)
        self.ui.pushButton_load_traits.clicked.connect(self.load_traits_from_file)
        self.ui.checkBox_visualize_traits.toggled.connect(self.plot_traits)

        ###### groupBox_arrangement
        self.ui.pushButton_construct_arrangement.clicked.connect(self.construct_arrangement)

        ###### groupBox_merge_faces
        self.ui.pushButton_reset_face_selection.clicked.connect(self.reset_face_selection)
        self.ui.pushButton_merge_selected_faces.clicked.connect(self.merge_selected_faces)
        
        ###### groupBox_dual_graphs
        self.ui.pushButton_construct_dual_graphs
        self.ui.pushButton_plot_adjecency_graph
        self.ui.pushButton_plot_connectivity_graph

        ###### groupBox_store
        self.ui.pushButton_save_arrangement_to_pickle
        self.ui.pushButton_save_arrangement_to_IEEE
        
    #########################################################################
    ############################################################### functions
    #########################################################################

    ########################################
    def load_image(self):

        # opening a dialog to load image address
        image_name = PySide.QtGui.QFileDialog.getOpenFileName()[0]

        if len(image_name) > 3:

            # loading image: grayscale
            image = np.flipud( cv2.imread( image_name, cv2.IMREAD_GRAYSCALE) )
            
            # plotting the image
            self.arrangement_canvas.plotImage( image )

            if self.ui.checkBox_visualize_traits.isChecked():
                self.plot_traits()

            self.data['image'] = image
            self.data['image_name'] = image_name            


    ########################################
    def load_traits_from_file(self):

        file_name = PySide.QtGui.QFileDialog.getOpenFileName()[0]
        file_ext = file_name.split('.')[-1]
        
        # method exits if the file extension is not supported
        if not (file_ext in ['yaml', 'YAML', 'yml', 'YML', 'svg', 'SVG'] ):
            print ( '\t WARNING: only yaml and svg files are supported' )
            return None
            
        # convert svg to yaml and load the yaml file
        if file_ext in ['svg', 'SVG']:
            file_name = mSGVp.svg_to_ymal(file_name, convert_segment_2_infinite_line=False)
            print ( '\t NOTE: svg file converted to yaml, and the yaml file will be loaded' )
        
        stream = open(file_name, 'r')
        data = yaml.load(stream)

        traits = []
        
        if 'lines' in data.keys():
            for l in data['lines']:
                if len(l) == 4: #[x1,y1,x2,y2]
                    traits += [ trts.LineModified( args=( sym.Point(l[0],l[1]), sym.Point(l[2],l[3]) ) ) ]
                elif len(l) == 3: #[x1,y1,slope]
                    traits += [ trts.LineModified( args=( sym.Point(l[0],l[1]), l[2]) ) ]

        if 'segments' in data.keys():
            for s in data['segments']:
                traits += [ trts.SegmentModified( args=( sym.Point(s[0],s[1]), sym.Point(s[2],s[3]))) ]

        if 'rays' in data.keys():
            for r in data['rays']:
                traits += [ trts.RayModified( args=( sym.Point(r[0],r[1]), sym.Point(r[2],r[3]))) ]

        if 'circles' in data.keys():
            for c in data['circles']:
                traits += [ trts.CircleModified( args=( sym.Point(c[0],c[1]), c[2]) ) ]

        if 'arcs' in data.keys():
            for a in data['arcs']:
                traits += [ trts.ArcModified( args=( sym.Point(a[0],a[1]), a[2], (a[3],a[4])) ) ]

        # copying loaded data into self.trait_list
        if self.ui.radioButton_load_traits_overwrite.isChecked():
            self.trait_list = traits
        else:
            self.trait_list.extend(traits)

        # updating the canvas with traits
        self.plot_traits()
            

    ########################################
    def plot_traits(self):
        
        if self.ui.checkBox_visualize_traits.isChecked():
            for trait in self.trait_list:
                if isinstance(trait, trts.SegmentModified):
                    self.arrangement_canvas.draw_trait_segment(trait)
                elif isinstance(trait, trts.RayModified):
                    self.arrangement_canvas.draw_trait_ray(trait)
                elif isinstance(trait, trts.LineModified):
                    self.arrangement_canvas.draw_trait_line(trait)
                elif isinstance(trait, trts.ArcModified):
                    self.arrangement_canvas.draw_trait_arc(trait)
                elif isinstance(trait, trts.CircleModified):
                    self.arrangement_canvas.draw_trait_circle(trait)
        else:
            pass
            # for trait_plot in self.arrangement_canvas.trait_plots:
            #     trait_plot.remove()
            

    ########################################
    def construct_arrangement (self):

        if len(self.trait_list) >0:            
            arrang = arr.Arrangement(self.trait_list, self.data['arrang_config'])

            self.data['arrangement'] = arrang
            self.data['trait'] = self.trait_list

            self.set_textEdit_arrangment_attribute_count()
            self.arrangement_canvas.plot_arrangement(self.data['arrangement'])

        else:
            print 'trait list is empty'

    ########################################
    def set_textEdit_arrangment_attribute_count(self):
        n_faces = str(len(self.data['arrangement'].decomposition.faces))
        n_nodes = str(len(self.data['arrangement'].graph.nodes()))
        # len(arrang.graph.edges()) is the number of half-edges
        n_edges = str( len(self.data['arrangement'].graph.edges())/2 )
        n_subgraphs = str(len(self.data['arrangement']._subDecompositions))
        self.ui.textEdit_arrangement_num_faces.setText( n_faces )
        self.ui.textEdit_arrangement_num_nodes.setText( n_nodes )
        self.ui.textEdit_arrangement_num_edges.setText( n_edges )
        self.ui.textEdit_arrangement_num_subgraphs.setText( n_subgraphs )

    ########################################
    # todo
    # textEdit_face_semantic_label
    # pushButton_assign_label_to_selected_faces

    ########################################
    def mouseClick_face_selection(self, event):
        ''' '''
        # print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(
        #     event.button, event.x, event.y, event.xdata, event.ydata)

        if event.button == 1:

            if self.data['arrangement'] != None:
                point = sym.Point(event.xdata, event.ydata)
                face_idx = self.data['arrangement'].decomposition.find_face(point)

                if face_idx != None:                    
                    self.selected_faces.append(face_idx)
                    self.set_textEdit_face_selection_list()
                    self.arrangement_canvas.highlight_face(self.data['arrangement'],
                                                           face_idx)
                    

        elif event.button == 3:
            # print 'I could wrap up everything here, right?'
            pass

    ######################################## 
    def merge_selected_faces (self):
        self.data['arrangement'].merge_faces(self.selected_faces)

        self.reset_face_selection()
        self.set_textEdit_arrangment_attribute_count()

        self.arrangement_canvas.clear_axes()
        self.arrangement_canvas.plotImage( self.data['image'] )
        self.arrangement_canvas.plot_arrangement(self.data['arrangement'])
       
    ######################################## 
    def set_textEdit_face_selection_list (self):
        string = ['{:d}'.format(a) for a in self.selected_faces]
        self.ui.textEdit_selected_faces_list.setText(', '.join(string))

    ######################################## 
    def reset_face_selection (self):
        self.selected_faces = []
        self.set_textEdit_face_selection_list()

        # because faces are highlighted
        for f in self.arrangement_canvas.face_plot_instances:
            f.remove()
        self.arrangement_canvas.draw()

    #########################################################################
    #################################################################### MISC
    #########################################################################
    def dummy(self, event=None):
        print 'dummy is running...'
        
    ########################################
    def about(self):
        PySide.QtGui.QMessageBox.about(self, "Adaptive Cell Decomposition",
                                       """<b>Version</b> %s
                                       <p>Copyright &copy; 2016 Saeed Gholami Shahbandi.
                                       All rights reserved in accordance with
                                       BSD 3-clause - NO WARRANTIES!
                                       <p>This GUI ... 
                                       <p>Python %s - PySide version %s - Qt version %s on %s""" % (__version__,
                                                                                                    platform.python_version(), PySide.__version__, QtCore.__version__,
                                                                                                    platform.system()))
