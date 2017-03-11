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

import numpy as np
import sympy as sym
import PySide

# the address to the arrangement package is added to sys.path
# by the gui script that imports this library, so no need to do it again

import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'
matplotlib.rcParams['text.usetex']=True
matplotlib.rcParams['text.latex.unicode']=True
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg

# there is conflict in importing matplotlib stuff both here and in arrangement.plotting
# so, instead of importing the whole arrangement.plotting, I just import what I need.
# import arrangement.plotting as aplt
from  arrangement.plotting import plot_edges, plot_nodes
import arrangement.geometricTraits as trts

################################################################################
################################################################################
################################################################################
class MyMplCanvas(FigureCanvasQTAgg):
    '''
    Ultimately, this is a QWidget (as well as a FigureCanvasQTAgg, etc.).
    I connect this to graphicsView in the ui
    '''

    ########################################
    def __init__(self, parent=None):#, width=5, height=4, dpi=100):
        ''' '''

        self.alpha = 1.0
        self.markers = [ 'ro','go','bo','ko',
                         'r*','g*','b*','k*',
                         'r^','g^','b^','k^',]
        
        self.fig, self.axes = plt.subplots(1, 1)#, figsize=(20,12))#, sharex=True, sharey=True)
        # self.axes.axis('off')
        self.axes.axis('equal')

        self.face_plot_instances = []
        self.edge_plot_instances = []
        self.node_plot_instances = []

        FigureCanvasQTAgg.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvasQTAgg.setSizePolicy(self, PySide.QtGui.QSizePolicy.Expanding, PySide.QtGui.QSizePolicy.Expanding)
        FigureCanvasQTAgg.updateGeometry(self)

        self.draw()

    ########################################
    def clear_axes(self):
        self.axes.cla()
        # self.axes.axis('off')
        self.axes.axis('equal')
        self.draw()

    ########################################
    def plot_arrangement(self, arrangement):

        # plot edges and nodes
        self.edge_plot_instances = plot_edges (self.axes, arrangement)
        self.node_plot_instances = plot_nodes (self.axes, arrangement)
        self.draw()

        # self.arrangement_canvas.fig.canvas.mpl_disconnect(self.cid_click)
        # del self.cid_click


    ########################################
    def highlight_face(self, arrangement, face_idx):
        # plot edges and nodes
        
        # drawing face via path-patch
        face = arrangement.decomposition.faces[ face_idx ]
        patch = mpatches.PathPatch(face.get_punched_path(),
                                   facecolor='g', edgecolor='g', alpha=0.7)
        # facecolor='r', edgecolor='k', alpha=0.5)
        self.face_plot_instances += [self.axes.add_patch(patch)]

        # print the face's index
        # self.axes.text(0, 0,
        #                'face #'+str(face_idx),
        #                fontdict={'color':'m', 'size': 25})

        self.draw()
        
        # self.arrangement_canvas.fig.canvas.mpl_disconnect(self.cid_click)
        # del self.cid_click

    ################################################################################
    def set_border(self, lst):
        '''
        in order to draw lines or rays, this class needs the border of the plot
        if the trait list is loaded before the image, this information is missing
        hence, in such a case, the list of traits to be visualized are passed to this method
        the "bLines" will be overwrittern if an image is loaded to gui and passed to this class
        this method is called only if the traits are visualized and an image is not available
        '''
          
        X, Y = [], []
        for trait in lst: 
            if isinstance(trait, trts.SegmentModified):
                X.append(trait.obj.p1.x)
                X.append(trait.obj.p2.x)
                Y.append(trait.obj.p1.y)
                Y.append(trait.obj.p2.y)
            elif isinstance(trait, trts.RayModified):
                X.append(trait.obj.p1.x)
                X.append(trait.obj.p2.x)
                Y.append(trait.obj.p1.y)
                Y.append(trait.obj.p2.y)
            elif isinstance(trait, trts.LineModified):
                X.append(trait.obj.p1.x)
                X.append(trait.obj.p2.x)
                Y.append(trait.obj.p1.y)
                Y.append(trait.obj.p2.y)
            elif isinstance(trait, trts.ArcModified):
                xc, yc, rc = trait.obj.center.x, trait.obj.center.y, trait.obj.radius
                X.append(xc+rc)
                X.append(xc-rc)
                Y.append(yc+rc)
                Y.append(yc+rc)
                
            elif isinstance(trait, trts.CircleModified):
                xc, yc, rc = trait.obj.center.x, trait.obj.center.y, trait.obj.radius
                X.append(xc+rc)
                X.append(xc-rc)
                Y.append(yc+rc)
                Y.append(yc+rc)

        self.xMin, self.xMax = np.min(X), np.max(X)
        self.yMin, self.yMax = np.min(Y), np.max(Y)

        self.bLines  = [ sym.Line( (self.xMin,self.yMin),(self.xMax,self.yMin) ),
                         sym.Line( (self.xMax,self.yMin),(self.xMax,self.yMax) ),
                         sym.Line( (self.xMax,self.yMax),(self.xMin,self.yMax) ),
                         sym.Line( (self.xMin,self.yMax),(self.xMin,self.yMin) ) ]


    ################################################################################
    def plotImage(self, image, oriented_gradients=None):
        '''
        '''

        self.xMin = 0
        self.xMax = image.shape[1]
        self.yMin = 0
        self.yMax = image.shape[0]
        self.bLines  = [ sym.Line( (self.xMin,self.yMin),(self.xMax,self.yMin) ),
                         sym.Line( (self.xMax,self.yMin),(self.xMax,self.yMax) ),
                         sym.Line( (self.xMax,self.yMax),(self.xMin,self.yMax) ),
                         sym.Line( (self.xMin,self.yMax),(self.xMin,self.yMin) ) ]

        self.axes.imshow(image, cmap = 'gray', interpolation='nearest')#, origin='lower')
        
        if oriented_gradients!=None:
            self.plot_oriented_gradients(image, oriented_gradients)
             
        self.axes.set_xlim([0, np.shape(image)[1]])
        self.axes.set_ylim([0, np.shape(image)[0]])

        self.draw()

    ################################################################################
    def plot_oriented_gradients(self, image, vecfield):
        ''' '''
        offset = (image.shape[0] - vecfield.shape[0]) /2

        ### Quiver of Oriented Gradient
        # "X" is from left to right and "Y" is from top to bottom (depends on origin, maybe bottom to top)
        X,Y = np.meshgrid( np.arange(offset, np.shape(vecfield)[1]+offset),
                           np.arange(offset, np.shape(vecfield)[0]+offset) )
        
        U = np.real(vecfield) # always from left to right!
        V = np.imag(vecfield) # always from bottom to top is positive, regardless of the origin! 
        A = np.angle(vecfield) # this will be passed to qiover to color the arrows based on their angle
        
        n_th = 5 # every n_th arrow will be plotted, not all of them
        #np.flipud(Y[::n_th, ::n_th])
        self.axes.quiver( X[::n_th, ::n_th], Y[::n_th, ::n_th],
                          U[::n_th, ::n_th], V[::n_th, ::n_th],
                          A[::n_th, ::n_th],
                          pivot= 'mid', units= 'xy', scale_units= 'xy',
                          scale = np.max(np.abs(vecfield))/10) # width=0.005, headwidth = 3, headlength=5

        

    ################################################################################
    def plot_points(self, points, idx=None, symbolID=1):
        ''' '''
        pts = np.array(points)
        self.axes.plot(pts[:,0],pts[:,1] , 'r.') 
        self.draw()

    ################################################################################
    def draw_trait_line(self, trait, clr='b', line_style='-'): 

        # find the ending points on the bLines
        ips = []
        
        for bl in self.bLines:
            ips.extend( sym.intersection(trait.obj, bl) )

        for i in range(len(ips)-1,-1,-1):
            if not isinstance(ips[i], sym.Point):
                ips.pop(i)
            elif not ( (self.xMin <= ips[i].x <= self.xMax) and (self.yMin <= ips[i].y <= self.yMax) ):
                ips.pop(i)
                
        # plot the Line
        x = [np.float(ip.x.evalf()) for ip in ips]
        y = [np.float(ip.y.evalf()) for ip in ips]
        line = self.axes.plot (x, y, color=clr, linestyle=line_style, alpha=self.alpha)
        # self.axes.plot([trait.obj.p1.x, trait.obj.p2.x], [trait.obj.p1.y, trait.obj.p2.y], 'r')
        self.draw()
        return line

    ########################################
    def draw_trait_ray(self, trait, clr='b', line_style='-'):

        # find the ending point on one of the bLines
        ips = []
        for bl in self.bLines:
            ips.extend( sym.intersection(trait.obj, bl) )

        for i in range(len(ips)-1,-1,-1):
            if not isinstance(ips[i], sym.Point):
                ips.pop(i)
            elif not ( (self.xMin <= ips[i].x <= self.xMax) and (self.yMin <= ips[i].y <= self.yMax) ):
                ips.pop(i)

        # plot the ray
        x = np.float(trait.obj.p1.x.evalf())
        y = np.float(trait.obj.p1.y.evalf())
        dx = np.float(ips[0].x.evalf()) - np.float(trait.obj.p1.x.evalf())
        dy = np.float(ips[0].y.evalf()) - np.float(trait.obj.p1.y.evalf())
        ray = self.axes.arrow( np.float(x),np.float(y),
                               np.float(dx),np.float(dy), # shape='right',
                               # linewidth = 1, head_width = 0.1, head_length = 0.2,
                               linestyle=line_style,
                               fc=clr, ec=clr, alpha=self.alpha)
        # self.axes.plot([trait.obj.p1.x, trait.obj.p2.x], [trait.obj.p1.y, trait.obj.p2.y], 'g')
        self.draw()
        return ray

    ########################################
    def draw_trait_segment(self, trait, clr='b', line_style='-'):
        segment = self.axes.plot([trait.obj.p1.x, trait.obj.p2.x],
                                 [trait.obj.p1.y, trait.obj.p2.y],
                                 color=clr, linestyle=line_style, alpha=self.alpha)

        self.draw()
        return segment

    ########################################
    def draw_trait_circle(self, trait, clr='b', line_style='-'):
        tStep = 90#360
        theta = np.linspace(0, 2*np.pi, tStep, endpoint=True)
        xc,yc,rc = trait.obj.center.x, trait.obj.center.y, trait.obj.radius
        x = xc + rc * np.cos(theta)
        y = yc + rc * np.sin(theta)
        circle = self.axes.plot (x, y, color=clr, linestyle=line_style, alpha=self.alpha)
        self.draw()
        return circle

    ########################################
    def draw_trait_arc(self, trait, clr='b', line_style='-'):
        t1,t2 = trait.t1 , trait.t2
        tStep = max( [np.float(np.abs(t2-t1)*(180/np.pi)) ,2])
        theta = np.linspace(np.float(t1), np.float(t2), tStep, endpoint=True)
        xc, yc, rc = trait.obj.center.x , trait.obj.center.y , trait.obj.radius
        x = xc + rc * np.cos(theta)
        y = yc + rc * np.sin(theta)
        arc = self.axes.plot (x, y, color=clr, linestyle=line_style, alpha=self.alpha)
        self.draw()
        return arc

    ################################################################################
    def plot_dominant_orientation_detection(self, X, Y, GMMx, GMMy, bincenter, l, peakind):
        ''' '''
        histCol = 'b'
        gmmCol = 'r'
        roiCol, roiAlpha = 'k',0.7

        xMin, xMax = X[0], X[-1]
        yMin, yMax = np.min([np.min(Y),np.min(GMMy)]) , np.max([np.max(Y),np.max(GMMy)])

        arrowHeadLength = 5#350
        arrowHeadWidth = (yMax-yMin)/30.

        # left side
        self.axes.plot(X[:l], Y[:l], histCol+'-.', alpha=self.alpha)
        self.axes.plot(GMMx[:l], GMMy[:l], gmmCol+'-.', alpha=self.alpha)
        # centeral
        self.axes.plot(X[l:-l], Y[l:-l], histCol, label='Original Histogram')
        self.axes.plot(GMMx[l:-l], GMMy[l:-l], gmmCol , label='GMM')
        # right side
        self.axes.plot(X[-l:], Y[-l:], histCol+'-.', alpha=self.alpha)
        self.axes.plot(GMMx[-l:], GMMy[-l:], gmmCol+'-.', alpha=self.alpha)
        # resulting peaks from CWT over MMG
        self.axes.plot(bincenter[peakind],GMMy[peakind], 'r^', label='Dominant Orientations')
        
        # region of interest
        self.axes.plot([X[l],X[l]]   , [yMin, yMax], roiCol+'-', alpha=roiAlpha, linewidth=2)
        self.axes.plot([X[-l],X[-l]] , [yMin, yMax], roiCol+'-', alpha=roiAlpha, linewidth=2)
        self.axes.arrow(X[int(3.5*l)], np.mean([yMin, yMax]),
                        X[int(1.5*l)]-X[0]-arrowHeadLength, 0,
                        head_width=arrowHeadWidth, head_length=arrowHeadLength,
                        alpha=roiAlpha, fc=roiCol,ec=roiCol)
        self.axes.arrow(X[int(-3.5*l)], np.mean([yMin, yMax]),
                        -(X[int(1.5*l)]-X[0]-arrowHeadLength), 0,
                        head_width=arrowHeadWidth, head_length=arrowHeadLength,
                        alpha=roiAlpha, fc=roiCol,ec=roiCol)

        # axes configuration
        self.axes.set_xlim([xMin, xMax])
        self.axes.set_ylim([yMin, yMax])
        # self.axes.spines['left'].set_visible(False)
        # self.axes.spines['right'].set_visible(False)
        # self.axes.spines['top'].set_visible(False)
        self.axes.set_xticks([X[l],X[3*l],X[-l]])

        self.axes.set_xticklabels(['$-\pi$/2', '0' ,'$\pi$/2'])
        self.axes.yaxis.set_ticks([])

        self.draw()
