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


from __future__ import print_function

import sys, os, platform, time
import PySide

import numpy as np
import sympy as sym

import cv2
import yaml

from sklearn import mixture
from numpy.linalg import det

import skimage.transform
from skimage.feature import canny
# from skimage.feature import peak_local_max
# from skimage.transform import hough_circle
# from skimage.transform import hough_line
# from skimage.transform import hough_line_peaks
# from skimage.transform import probabilistic_hough_line

import myCanvasLib
import annotation_gui
import utilities
import arrangement.geometricTraits as trts
import my_svg_parser_dev as mSGVp

# ###### debug-mode
# import matplotlib.pyplot as plt
# ######

#####################################################################
#####################################################################
#####################################################################

class MainWindow(PySide.QtGui.QMainWindow, annotation_gui.Ui_MainWindow):
    
    def __init__(self, parent=None):
        ''' '''
        super(MainWindow, self).__init__(parent)
        self.ui = annotation_gui.Ui_MainWindow()
        self.ui.setupUi(self)

        # todo: store everything non-relevant to the gui in this dictionary
        self.annotation = []
        self.trait_buffer = []
        self.trait_list = []

        # image processing informations - these are mutable from GUI 
        self.img_prc = {'canny setting': [50,150,3],
                        'binary thresholding': [120, 255],
                        'sinogram peak detection': [10,15,.5]}

        
        self.data = {'image_name': '',
                     'image': None,
                     'edges': None,
                     'binary': None,
                     'dominant_orientation': [],
                     'traits': [] }

        #####################################################################
        ############################## connecting graphicsViews to mpl canvas
        #####################################################################

        # self.ui.graphicsView_traits_visualization
        traits_visualization_widget = self.ui.graphicsView_traits_visualization
        self.traits_visualization_canvas = myCanvasLib.MyMplCanvas(traits_visualization_widget)
        layout = PySide.QtGui.QVBoxLayout(traits_visualization_widget)
        layout.addWidget(self.traits_visualization_canvas)
        self.traits_visualization_canvas.mpl_connect('button_press_event', self.mouseClick_annotation)

        #####################################################################
        #####################################################################
        #####################################################################

        ########## no groupBox
        self.ui.pushButton_loading.clicked.connect(self.load_image)
        self.ui.pushButton_add_trait_buffer_to_list.clicked.connect(self.add_trait_buffer_to_trait_list)
        self.ui.pushButton_reset_trait_buffer.clicked.connect(self.reset_trait_buffer)

        ########## groupBox_load_traits
        self.ui.pushButton_load_traits.clicked.connect(self.load_traits_from_file)

        ########## groupBox_trait_list_modification
        self.ui.pushButton_reset_trait_list.clicked.connect(self.reset_trait_list)
        self.ui.pushButton_remove_selected_trait.clicked.connect(self.remove_selected_trait_from_list)
        self.ui.listWidget_traits_list.itemClicked.connect(self.highlight_selected_list_item)
        self.ui.listWidget_traits_list.currentRowChanged.connect(self.highlight_selected_list_item)        
        self.ui.pushButton_save_traits_to_file.clicked.connect(self.save_traits_to_file)

        ########## groupBox_trait_visualization
        self.ui.checkBox_visualize_lines.toggled.connect(self.plot_traits_visualization_canvas)
        self.ui.checkBox_visualize_segments.toggled.connect(self.plot_traits_visualization_canvas)
        self.ui.checkBox_visualize_rays.toggled.connect(self.plot_traits_visualization_canvas)
        self.ui.checkBox_visualize_circles.toggled.connect(self.plot_traits_visualization_canvas)
        self.ui.checkBox_visualize_arcs.toggled.connect(self.plot_traits_visualization_canvas)
        self.ui.comboBox_draw_list_vs_buffer.currentIndexChanged.connect(self.plot_traits_visualization_canvas)


        self.ui.radioButton_radiography_source_origin.toggled.connect(self.plot_traits_visualization_canvas)
        self.ui.radioButton_radiography_source_binary.toggled.connect(self.plot_traits_visualization_canvas)
        self.ui.radioButton_radiography_source_edge.toggled.connect(self.plot_traits_visualization_canvas)

        
        ########## groupBox_manual_trait_detection
        self.ui.pushButton_man_reset_trait.clicked.connect(self.reset_trait_annotation)

        self.ui.groupBox_manual_trait_detection.setEnabled(False)
        self.ui.groupBox_auto_trait_detection.setEnabled(False)

        
        ########## groupBox_auto_trait_detection

        ### dominant orientations:
        self.ui.pushButton_find_dominant_orientations.clicked.connect(self.find_dominant_orientations)
        self.ui.pushButton_orientations_update_from_text.clicked.connect(self.update_orientation_from_text)
        self.ui.pushButton_orientations_update_from_annotation.clicked.connect(self.update_orientation_from_annotation)

        ### radiography:
        self.ui.pushButton_auto_detect_lines_radiography.clicked.connect(self.find_lines_with_radiography)

        ### circle detection:
        # self.ui.pushButton_auto_detect_circles.clicked.connect(self.detect_circles_auto)


    #########################################################################
    #################################################### methods of the class
    #########################################################################


    ########################################
    ############## plotting over myCanvasLib
    ########################################

    def load_image(self):

        # opening a dialog to load image address and loading image (grayscale)
        image_name = PySide.QtGui.QFileDialog.getOpenFileName()[0]
        image = np.flipud( cv2.imread( image_name, cv2.IMREAD_GRAYSCALE) )

        self.data['image'] = image
        self.data['image_name'] = image_name
        
        # computing binary and edge image
        self.update_binary_image()
        self.update_edge_image()
                    
        # plotting the image:
        # Note that plot_traits_... is called instead of ..._canvas.plotImage()
        # this is because the former contains the latter.
        # it is useful if the trait list / buffer is filled before the image is loaded
        self.plot_traits_visualization_canvas()

        self.ui.groupBox_manual_trait_detection.setEnabled(True)
        self.ui.groupBox_auto_trait_detection.setEnabled(True)


    ########################################
    def update_binary_image(self):
        [thr1, thr2] = self.img_prc['binary thresholding']
        if self.ui.checkBox_radiography_thresholding_inverted.isChecked():
            ret, self.data['binary'] = cv2.threshold(self.data['image'] , thr1,thr2 , cv2.THRESH_BINARY_INV)
        else:
            ret, self.data['binary'] = cv2.threshold(self.data['image'] , thr1,thr2 , cv2.THRESH_BINARY)

    ########################################
    def update_edge_image(self):
        [thr1, thr2, apt_size] = self.img_prc['canny setting']
        self.data['edges'] = cv2.Canny(self.data['image'], thr1, thr2, apt_size)
        

    ########################################
    def plot_traits_visualization_canvas(self):
        '''
        this is like the starting point for visualization
        '''

        self.traits_visualization_canvas.clear_axes()

        lst = self.trait_list + self.trait_buffer
        
        # plot the map as the base
        if self.data['image'] is not None:
            if self.ui.radioButton_radiography_source_origin.isChecked():
                image = self.data['image']
            elif self.ui.radioButton_radiography_source_binary.isChecked():
                image = self.data['binary']    
            elif self.ui.radioButton_radiography_source_edge.isChecked():
                image = self.data['edges']
            self.traits_visualization_canvas.plotImage(image)
        elif len(lst)>0:
            # note that regardless of target list to be visualized,
            # border lines of the "traits_visualization_canvas" are initialized
            # with all available traits, in both buffer and main list
            self.traits_visualization_canvas.set_border(lst)

        # draw specified lists
        if self.ui.comboBox_draw_list_vs_buffer.currentText() == 'draw all (buffer and list)':
            self.draw_a_list_of_traits(self.trait_list, clr='b', line_style='-')
            self.draw_a_list_of_traits(self.trait_buffer, clr='r', line_style='--')
        elif self.ui.comboBox_draw_list_vs_buffer.currentText() == 'draw trait list':
            self.draw_a_list_of_traits(self.trait_list, clr='b', line_style='-')
        elif self.ui.comboBox_draw_list_vs_buffer.currentText() == 'draw trait buffer':
            self.draw_a_list_of_traits(self.trait_buffer, clr='r', line_style='--')

    ########################################
    def draw_a_list_of_traits(self, lst, clr, line_style):

        for trait in lst: 
            if isinstance(trait, trts.SegmentModified) and self.ui.checkBox_visualize_segments.isChecked():
                self.traits_visualization_canvas.draw_trait_segment(trait, clr, line_style)
            elif isinstance(trait, trts.RayModified) and self.ui.checkBox_visualize_rays.isChecked():
                self.traits_visualization_canvas.draw_trait_ray(trait, clr, line_style)
            elif isinstance(trait, trts.LineModified) and self.ui.checkBox_visualize_lines.isChecked():
                self.traits_visualization_canvas.draw_trait_line(trait, clr, line_style)
            elif isinstance(trait, trts.ArcModified) and self.ui.checkBox_visualize_arcs.isChecked():
                self.traits_visualization_canvas.draw_trait_arc(trait, clr, line_style)
            elif isinstance(trait, trts.CircleModified) and self.ui.checkBox_visualize_circles.isChecked():
                self.traits_visualization_canvas.draw_trait_circle(trait, clr, line_style)


    ########################################
    ##### trait buffer and list manipulation
    ########################################
    def add_trait_buffer_to_trait_list(self):
        self.trait_list.extend(self.trait_buffer)
        self.update_trait_list_listWidget()
        self.reset_trait_buffer() # includes: self.plot_traits_visualization_canvas()

    ########################################
    def remove_selected_trait_from_list(self):
        # important! assuming the indices in listWidget_traits_list corresponds to trait_list
        idx = self.ui.listWidget_traits_list.currentIndex().row()

        if idx!=-1:# and len(self.trait_list)>0:
            # only if an item is selected and the list is not empty
            self.trait_list.pop(idx)
            self.update_trait_list_listWidget()
            self.plot_traits_visualization_canvas()

    ########################################
    def highlight_selected_list_item(self):

        if len(self.trait_list)>0:
            idx = self.ui.listWidget_traits_list.currentIndex().row()
            trait = self.trait_list[idx]
        else:
            trait = None
        # todo: sometimes I get this error from the line above, not sure when exactly!
        # IndexError: list index out of range
        # add print (idx, len(self.trait_list)) to see what is going on

        if isinstance(trait, trts.SegmentModified):
            trait_plot = self.traits_visualization_canvas.draw_trait_segment(trait, clr = 'r')

        elif isinstance(trait, trts.RayModified):
            trait_plot = self.traits_visualization_canvas.draw_trait_ray(trait, clr = 'r')

        elif isinstance(trait, trts.LineModified):
            trait_plot = self.traits_visualization_canvas.draw_trait_line(trait, clr = 'r')
            
        elif isinstance(trait, trts.ArcModified):
            trait_plot = self.traits_visualization_canvas.draw_trait_arc(trait, clr = 'r')
            
        elif isinstance(trait, trts.CircleModified):
            trait_plot = self.traits_visualization_canvas.draw_trait_circle(trait, clr = 'r')

        # oops!
        # I don't know why it works better like this!
        # things get worse when I try to sleep(), remove() and draw() 
        # in this form, it just keeps it until next item is selected
        # time.sleep(.5)
        if 'trait_plot' in locals():
            trait_plot[0].remove()
        # self.traits_visualization_canvas.draw()
        

    ########################################
    def update_trait_list_listWidget(self):
        
        self.ui.listWidget_traits_list.clear()

        for trait in self.trait_list:
            if isinstance(trait, trts.SegmentModified):
                p1  = '(' + '{:.2f}'.format( float(trait.obj.p1.x) )
                p1 += ',' + '{:.2f}'.format( float(trait.obj.p1.y) ) + ')'
                p2  = '(' + '{:.2f}'.format( float(trait.obj.p2.x) )
                p2 += ',' + '{:.2f}'.format( float(trait.obj.p2.y) ) + ')'
                string = 'S: p1'+p1+', p2'+p2

            elif isinstance(trait, trts.RayModified):
                p1  = '(' + '{:.2f}'.format( float(trait.obj.p1.x) )
                p1 += ',' + '{:.2f}'.format( float(trait.obj.p1.y) ) + ')'
                p2  = '(' + '{:.2f}'.format( float(trait.obj.p2.x) )
                p2 += ',' + '{:.2f}'.format( float(trait.obj.p2.y) ) + ')'
                string = 'R: p1'+p1+', p2'+p2

            elif isinstance(trait, trts.LineModified):
                p1  = '(' + '{:.2f}'.format( float(trait.obj.p1.x) )
                p1 += ',' + '{:.2f}'.format( float(trait.obj.p1.y) ) + ')'
                p2  = '(' + '{:.2f}'.format( float(trait.obj.p2.x) )
                p2 += ',' + '{:.2f}'.format( float(trait.obj.p2.y) ) + ')'
                string = 'L: p1'+p1+', p2'+p2

            elif isinstance(trait, trts.ArcModified):
                c  = '(' + '{:.2f}'.format( float(trait.obj.center.x) )
                c += ',' + '{:.2f}'.format( float(trait.obj.center.y) ) + ')'
                r = '{:.2f}'.format( float(trait.obj.radius) )
                t = '(' + '{:.2f}'.format( float(trait.t1) ) + ',' + '{:.2f}'.format( float(trait.t2) ) + ')'
                string = 'A: c:'+c+', r:'+r , ', t:'+t

            elif isinstance(trait, trts.CircleModified):
                c  = '(' + '{:.2f}'.format( float(trait.obj.center.x) )
                c += ',' + '{:.2f}'.format( float(trait.obj.center.y) ) + ')'
                r = '{:.2f}'.format( float(trait.obj.radius) )
                string = 'C: c'+c+', r'+r

            idx = self.ui.listWidget_traits_list.count()
            self.ui.listWidget_traits_list.insertItem(idx, string)

    ########################################
    def reset_trait_annotation(self):
        self.annotation = []
        self.plot_traits_visualization_canvas()

    ########################################
    def reset_trait_buffer(self):
        self.trait_buffer = []
        self.plot_traits_visualization_canvas()

    ########################################
    def reset_trait_list(self):
        self.trait_list = []
        self.update_trait_list_listWidget()
        self.plot_traits_visualization_canvas()

    ########################################
    ################### auto trait detection
    ########################################

    def find_dominant_orientations(self):
        '''  '''

        # flipud: why? I'm sure it won't work otherwise, but dont know why
        # It should happen in both "find_dominant_orientations" & "find_grid_lines"
        image = np.flipud(self.data['image'])

        ### computing orientations
        if image is None:
            orientations = np.array([])

        else:
            ### smoothing
            image = cv2.blur(image, (9,9))
            image = cv2.GaussianBlur(image, (9,9),0)

            ### oriented gradient of the image
            # is it (dx - 1j*dy) or (dx + 1j*dy)
            # this is related to "flipud" problem mentioned above
            dx = cv2.Sobel(image, cv2.CV_64F, 1,0, ksize=9)
            dy = cv2.Sobel(image, cv2.CV_64F, 0,1, ksize=9)
            grd = dx - 1j*dy
            
            ### weighted histogram of oriented gradients (over the whole image)
            hist, binc = utilities.wHOG (grd, NumBin = 180*5)

            ### finding peaks in the histogram
            peak_idx = utilities.FindPeaks( hist,
                                      CWT=True, cwt_range=(5,50,5),
                                      Refine_win=20 , MinPeakDist = 30 , MinPeakVal=.2,
                                      Polar=False )

            # shrinking the range to [-pi/2, pi/2]
            orientations = list(binc[peak_idx])
            for idx in range(len(orientations)):
                if orientations[idx]< -np.pi/2:
                    orientations[idx] += np.pi
                elif np.pi/2 <= orientations[idx]:
                    orientations[idx] -= np.pi

            # removing similar angles
            for idx in range(len(orientations)-1,-1,-1):
                for jdx in range(idx):
                    if np.abs(orientations[idx] - orientations[jdx]) < np.spacing(10**10):
                        orientations.pop(idx)
                        break

        ### setting orientations into places
        self.data['dominant_orientation'] = np.array(orientations)

        # note: that the internal unit of the orientation angles is radian
        # it is converted to degree (and back) only for the user interaction
        string = ['{:.1f}'.format(a*180/np.pi) for a in self.data['dominant_orientation']]
        self.ui.textEdit_dominant_orientations.setText(', '.join(string))
   
    
    ########################################
    def update_orientation_from_text(self):
        '''
        note: that the internal unit of the orientation angles is radian
        it is converted to degree (and back) only for the user interaction
        '''
        string = self.ui.textEdit_dominant_orientations.toPlainText()
        orientations = [float(angle)
                        for angle in string.split(',')
                        if len(angle)>0 ] # check len() to reject empty strings ('')
        self.data['dominant_orientation'] = np.array(orientations) *np.pi/180
        print ('\t orientations corrected to: ', orientations)

    ########################################
    def update_orientation_from_annotation(self):
        '''
        '''
        # notifying the user about the situation
        if len(self.annotation) < 2:
            print ('\t WARNING: to estimate orientation needs two points.')
            return
        elif len(self.annotation) > 2:
            print ('\t WARNING: orientation estimated from last two points, others discarded.')

        # calculating the new orientation from annotation points
        [x1,y1], [x2,y2] = self.annotation[-2] , self.annotation[-1]
        new_orientation = np.arctan((y2-y1) / (x2-x1))

        # updating the internal and GUI list
        orientations = np.append(self.data['dominant_orientation'], new_orientation) 
        self.data['dominant_orientation'] = orientations
        print ('\t orientation {:.2f} (rad) appended'.format(new_orientation) )
        string = ['{:.1f}'.format(a*180/np.pi) for a in self.data['dominant_orientation']]
        self.ui.textEdit_dominant_orientations.setText(', '.join(string))

        # reseting trait annotation
        self.reset_trait_annotation()

    ########################################
    def find_lines_with_radiography(self):
        ''''''

        ### get the appropriate input image
        if self.ui.radioButton_radiography_source_origin.isChecked():
            # using original image
            image = self.data['image']

        elif self.ui.radioButton_radiography_source_binary.isChecked():
            # thresholding to binary
            string = self.ui.textEdit_binary_thresholding.toPlainText()
            [thr1, thr2] = [float(param) for param in string.split(',')]
            if [thr1, thr2] != self.img_prc['binary thresholding']:
                self.img_prc['binary thresholding'] = [thr1, thr2]
                self.update_binary_image()
            image = self.data['binary']
    
        elif self.ui.radioButton_radiography_source_edge.isChecked():
            # using edge image
            string = self.ui.textEdit_canny_setting.toPlainText()
            [thr1, thr2, apt_size] = [float(param) for param in string.split(',')]
            if [thr1, thr2, apt_size] != self.img_prc['canny setting']:
                self.update_edge_image()
            image = self.data['edges']

        if len(self.data['dominant_orientation'])>0:

            ### fetching setting for sinogram peak detection
            string = self.ui.textEdit_sinogram_peak_detection_setting.toPlainText()
            [refWin, minDist, minVal] = [float(param) for param in string.split(',')]

            ### radiography
            # flipud: why? I'm sure it won't work otherwise, but dont know why
            # It should happen in both "find_dominant_orientations" & "find_grid_lines"
            image = np.flipud(image)
            imgcenter = (image.shape[1]/2, # cols == x
                         image.shape[0]/2) # rows == y

            orientations = self.data['dominant_orientation']
            sinog_angles = orientations - np.pi/2 # in radian
            sinograms = skimage.transform.radon(image, theta=sinog_angles*180/np.pi )#, circle=True)
            sinogram_center = len(sinograms.T[0])/2


            # ########## debug-mode
            # row, col = 1,1
            # fig, axes = plt.subplots(row, col, figsize=(20,12))
            # for singo in sinograms.T:
            #     axes.plot(singo)
            # fig.show()
            # ########## 

            lines = []
            for (orientation, sinog_angle, sinogram) in zip(orientations, sinog_angles, sinograms.T):
                # Find peaks in sinogram:
                peakind = utilities.FindPeaks(sinogram ,
                                        CWT=False, cwt_range=(1,8,1),
                                        Refine_win = int(refWin),
                                        MinPeakDist = int(minDist),
                                        MinPeakVal = minVal,
                                        Polar=False)

                # line's distance to the center of the image
                dist = np.array(peakind) - sinogram_center
                
                pts_0 = [ ( imgcenter[0] + d*np.cos(sinog_angle),
                            imgcenter[1] + d*np.sin(sinog_angle) )
                          for d in dist]
                
                pts_1 = [ ( point[0] + np.cos(orientation) ,
                            point[1] + np.sin(orientation) )
                          for point in pts_0]
                
                lines += [trts.LineModified( args=( sym.Point(p0[0],p0[1]), sym.Point(p1[0],p1[1]) ) )
                          for (p0,p1) in zip(pts_0,pts_1)]

            self.trait_buffer = lines
            # self.trait_buffer += lines
            self.plot_traits_visualization_canvas()
            print ('\t found {:d} lines'.format(len(lines)))
        else:
            print ('\t WARNING: no dominant orientation is available, so... goodluck')
        
        
        
    ########################################
    ################# manual trait detection
    ########################################
    def mouseClick_annotation(self, event):
        ''' '''
        # print ( 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(
        #     event.button, event.x, event.y, event.xdata, event.ydata) )

        if event.button == 1:
            self.annotation.append([event.xdata, event.ydata])

            # drawing temp points
            self.traits_visualization_canvas.plot_points([[event.xdata, event.ydata]])
        
        elif event.button == 3:
            # print ( 'I could wrap up everything here, right?' )
            self.construct_trait_from_annotation()

    ########################################
    def construct_trait_from_annotation(self):
        ''' '''

        # not enough point for any trait, unless I add points as trait (later)
        if len(self.annotation) < 2:

            # if only one point, make a line from p0 and orientation
            if len(self.data['dominant_orientation']) == 1 :
                if self.ui.radioButton_man_annotate_line.isChecked():
                    
                    p0 = self.annotation[-1]
                    p1 = [p0[0]+np.cos(self.data['dominant_orientation'][0]),
                          p0[1]+np.sin(self.data['dominant_orientation'][0])]
                    # print (p0,self.data['dominant_orientation'][0],p1 )
                    l_trait = trts.LineModified( args=(sym.Point(p0[0],p0[1]), 
                                                       sym.Point(p1[0],p1[1])) )

                    self.trait_buffer.append(l_trait)
                    self.traits_visualization_canvas.draw_trait_line(l_trait,'r','--') 
                    self.reset_trait_annotation()
                   
            # print ('\t WARNING: not enough point for the selected trait class')
            return


        if self.ui.radioButton_man_annotate_line.isChecked():
            # considering only the last two elements of the annotation list
            p0, p1 = self.annotation[-2] , self.annotation[-1]
            l_trait = trts.LineModified( args=(sym.Point(p0[0],p0[1]), sym.Point(p1[0],p1[1])) )
            self.trait_buffer.append(l_trait)
            self.traits_visualization_canvas.draw_trait_line(l_trait)
            
        elif self.ui.radioButton_man_annotate_segment.isChecked():
            # considering only the last two elements of the annotation list
            p0, p1 = self.annotation[-2] , self.annotation[-1]
            s_trait = trts.SegmentModified( args=(sym.Point(p0[0],p0[1]), sym.Point(p1[0],p1[1])) )
            self.trait_buffer.append(s_trait)
            self.traits_visualization_canvas.draw_trait_segment(s_trait)

        elif self.ui.radioButton_man_annotate_ray.isChecked():
            # considering only the last two elements of the annotation list
            p0, p1 = self.annotation[-2] , self.annotation[-1]
            r_trait = trts.RayModified( args=(sym.Point(p0[0],p0[1]), sym.Point(p1[0],p1[1])) )
            self.trait_buffer.append(r_trait)
            self.traits_visualization_canvas.draw_trait_ray(r_trait)

        elif self.ui.radioButton_man_annotate_circle.isChecked():

            if len(self.annotation) == 2:
                # if 2 points are given, the 1st is the center and 2nd is on the perimeter
                [xc,yc] , [x1,y1] = self.annotation[0] , self.annotation[1]
                rc = np.sqrt( (xc-x1)**2 + (yc-y1)**2 )
            elif len(self.annotation) > 2:
                # if 3 points are given, they are all considered on the perimeter
                # http://mathworld.wolfram.com/Circle.html
                [x1,y1], [x2,y2], [x3,y3] = self.annotation[-3] , self.annotation[-2], self.annotation[-1]
                a = np.array([ [x1,y1,1], [x2,y2,1], [x3,y3,1] ])
                d = np.array([ [x1**2+y1**2,y1,1], [x2**2+y2**2,y2,1], [x3**2+y3**2,y3,1] ])
                e = np.array([ [x1**2+y1**2,x1,1], [x2**2+y2**2,x2,1], [x3**2+y3**2,x3,1] ])
                f = np.array([ [x1**2+y1**2,x1,y1], [x2**2+y2**2,x2,y2], [x3**2+y3**2,x3,y3] ])
                a,d,e,f = det(a), -det(d), det(e), -det(f)
                xc, yc = -d/(2*a) , -e/(2*a)
                rc = np.sqrt( ((d**2 + e**2)/ (4*(a**2))) - (f/a))
            
            c_trait = trts.CircleModified( args=(sym.Point(xc,yc), rc) )
            self.trait_buffer.append(c_trait)
            self.traits_visualization_canvas.draw_trait_circle(c_trait)

        elif self.ui.radioButton_man_annotate_arc.isChecked():

            if len(self.annotation) <= 2:
                print ('\t WARNING: need at least and only 3 points to estimate an arc')
            else:
                [x1,y1], [x2,y2], [x3,y3] = self.annotation[0] , self.annotation[1], self.annotation[2]
                a = np.array([ [x1,y1,1], [x2,y2,1], [x3,y3,1] ])
                d = np.array([ [x1**2+y1**2,y1,1], [x2**2+y2**2,y2,1], [x3**2+y3**2,y3,1] ])
                e = np.array([ [x1**2+y1**2,x1,1], [x2**2+y2**2,x2,1], [x3**2+y3**2,x3,1] ])
                f = np.array([ [x1**2+y1**2,x1,y1], [x2**2+y2**2,x2,y2], [x3**2+y3**2,x3,y3] ])
                a,d,e,f = det(a), -det(d), det(e), -det(f)
                xc, yc = -d/(2*a) , -e/(2*a)
                rc = np.sqrt( ((d**2 + e**2)/ (4*(a**2))) - (f/a))

                # screw_up : t1,t2 \in [-pi,pi] 
                # in CCW order, the 1st pt is start, 2nd pt is on the perimeter and 3rd pt is the end
                # but ArcModified will modify the theta values anyway, so a good chance of screw_up here
                # so I will impose the restriction on the user to maintain the order and I will correct
                # the values here so that t1< t2
                t1,t2 = np.arctan2(y1-yc, x1-xc), np.arctan2(y3-yc, x3-xc)
                if t1 > t2:
                    t2 += 2*np.pi # or t1 -= 2*np.pi ?

                a_trait = trts.ArcModified( args=(sym.Point(xc,yc), rc, (t1,t2)) )
                self.trait_buffer.append(a_trait)
                self.traits_visualization_canvas.draw_trait_circle(a_trait)


        self.reset_trait_annotation()

    ########################################
    ################## load/save trait files
    ########################################
    def load_traits_from_file(self):

        if self.data['image_name'] is not '':
            dir_suggestion = self.data['image_name'].split('.')[0]
            file_name = PySide.QtGui.QFileDialog.getOpenFileName(None, 'Open File',
                                                                 dir_suggestion)[0]
        else:
            file_name = PySide.QtGui.QFileDialog.getOpenFileName()[0]

        if file_name is u'':
            print ('\t WARNING: no file was selected. file load aborted...')
            return None

        
        file_ext = file_name.split('.')[-1]
        
        # method exits if the file extension is not supported
        if not (file_ext in ['yaml', 'YAML', 'yml', 'YML', 'svg', 'SVG'] ):
            print ( '\t WARNING: only yaml and svg files are supported' )
            return None
            
        # convert svg to yaml and load the yaml file
        if file_ext in ['svg', 'SVG']:
            file_name = mSGVp.svg_to_ymal(file_name, convert_segment_2_infinite_line=False)
            print ( '\t NOTE: svg file converted to yaml, and the yaml file will be loaded' )



        print ('todo: arrangement has a yaml loader, use that instead?')
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

        # updating trait list listWidget
        self.update_trait_list_listWidget()

        # updating the canvas
        self.traits_visualization_canvas.clear_axes()
        self.plot_traits_visualization_canvas()


    ########################################
    def save_traits_to_file(self):

        # converting traits to a dictionary
        data = {'segments':[], 'rays':[], 'lines':[], 'arcs':[], 'circles':[] }
        for trait in self.trait_list:        
            if isinstance(trait, trts.SegmentModified):
                s = [trait.obj.p1.x, trait.obj.p1.y, trait.obj.p2.x, trait.obj.p2.y]
                s = [np.float(i.evalf()) for i in s]
                data['segments'].append(s)
                
            elif isinstance(trait, trts.RayModified):
                r = [trait.obj.p1.x, trait.obj.p1.y, trait.obj.p2.x, trait.obj.p2.y]
                r = [np.float(i.evalf()) for i in r]
                data['rays'].append(r)
                
            elif isinstance(trait, trts.LineModified):
                l = [trait.obj.p1.x, trait.obj.p1.y, trait.obj.p2.x, trait.obj.p2.y]
                l = [np.float(i.evalf()) for i in l]
                data['lines'].append(l)
                
            elif isinstance(trait, trts.ArcModified):
                a = [trait.obj.center.x, trait.obj.center.y, trait.obj.radius, trait.t1, trait.t2]
                a = [np.float(i.evalf()) for i in a]
                data['arcs'].append(a)
                
            elif isinstance(trait, trts.CircleModified):
                c = [trait.obj.center.x, trait.obj.center.y, trait.obj.radius]
                c = [np.float(i.evalf()) for i in c]
                data['circles'].append(c)
            
        ### removing keys with empty fields from the dictionary
        for key in data.keys():
            if len(data[key])==0:
                data.pop(key)


        ### adding the boundary information
        ### will be used for bounding the arrangement of infinit line        
        # the min-mix of x/y are already computed in the canvas class
        # see: MyMplCanvas.set_border() and MyMplCanvas.plotImage
        margin = 1
        xMin = self.traits_visualization_canvas.xMin -margin 
        xMax = self.traits_visualization_canvas.xMax +margin
        yMin = self.traits_visualization_canvas.yMin -margin
        yMax = self.traits_visualization_canvas.yMax +margin

        data['boundary'] = [xMin, yMin, xMax, yMax]


        ### the radiography could happen with different orientations
        ### but a safer practice is to do one at a time, as a consequence,
        ### there is no ugarantee at the time of saving, all orientations
        ### be present in list, therefore pointless to save them along
        # data['orientations'] = self.data['dominant_orientation']


        ### saving to file
        if self.data['image_name'] is not '':
            name_suggestion = self.data['image_name'].split('.')[0]+'.yaml'
            trait_file_name = PySide.QtGui.QFileDialog.getSaveFileName(None, 'Save File',
                                                                       name_suggestion)[0]
        else:
            trait_file_name = PySide.QtGui.QFileDialog.getSaveFileName()[0]

        if trait_file_name is not u'':
            with open(trait_file_name, 'w') as yaml_file:
                yaml.dump(data, yaml_file)
        else:
            print ('\t WARNING: file was NOT saved, saving was aborted...')



    #########################################################################
    #################################################################### MISC
    #########################################################################
    def dummy(self, event=None):
        print ( 'dummy is running...' )
        
    ########################################
    def about(self):
        PySide.QtGui.QMessageBox.about(self, "Spatial Map Annotation With Basic Curves",
                                       """<b>Version</b> %s
                                       <p>Copyright &copy; 2016 Saeed Gholami Shahbandi.
                                       All rights reserved in accordance with
                                       BSD 3-clause - NO WARRANTIES!
                                       <p>This GUI ... 
                                       <p>Python %s - PySide version %s - Qt version %s on %s""" % (__version__,
                                                                                                    platform.python_version(), PySide.__version__, QtCore.__version__,
                                                                                                    platform.system()))
