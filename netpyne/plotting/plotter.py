"""
Module for plotting analyses

"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy
import pickle, json
import os
from .scalebars import add_scalebar


plt.ion()

try:
    basestring
except NameError:
    basestring = str


colorList = [[0.42, 0.67, 0.84], [0.90, 0.76, 0.00], [0.42, 0.83, 0.59], [0.90, 0.32, 0.00], [0.34, 0.67, 0.67], [0.90, 0.59, 0.00], [0.42, 0.82, 0.83], [1.00, 0.85, 0.00], [0.33, 0.67, 0.47], [1.00, 0.38, 0.60], [0.57, 0.67, 0.33], [0.50, 0.20, 0.00], [0.71, 0.82, 0.41], [0.00, 0.20, 0.50], [0.70, 0.32, 0.10]] * 3


class GeneralPlotter:
    """A class used for plotting"""

    def __init__(self, data, axis=None, sim=None, rcParams=None, **kwargs):
        """
        Parameters
        ----------
        data : dict, str

        axis : matplotlib axis
            The axis to plot into.  If axis is set to None, a new figure and axis are created and plotted into.  If plotting into an existing axis, more options are available: xtwin, ytwin,
        
        """

        if type(data) == str:
            if os.path.isfile(data):
                self.data = self.loadData(data)
            else:
                raise Exception('In Plotter, if data is a string, it must be the path to a data file.')
        else:
            self.data = data

        if not sim:
            from .. import sim
        
        self.sim = sim
        self.axis = axis

        # Make a copy of the current matplotlib rcParams and update them
        self.orig_rcParams = deepcopy(mpl.rcParams)

        if rcParams:
            for rcParam in rcParams:
                if rcParam in mpl.rcParams:
                    mpl.rcParams[rcParam] = rcParams[rcParam]
                else:
                    print(rcParam, 'not found in matplotlib.rcParams')
            self.rcParams = rcParams
        else:
            self.rcParams = self.orig_rcParams


        # If an axis is input, plot there; otherwise make a new figure and axis
        if self.axis is None:
            if 'figSize' in kwargs:
                figSize = kwargs['figSize']
            else:
                figSize = self.rcParams['figure.figsize']
            self.fig, self.axis = plt.subplots(figsize=figSize)
        else:
            self.fig = plt.gcf()


    def loadData(self, fileName, fileDir=None, sim=None):
        
        from ..analysis import loadData
        self.data = loadData(fileName=fileName, fileDir=fileDir, sim=None)
        


    def saveData(self, fileName=None, fileDesc=None, fileType=None, fileDir=None, sim=None, **kwargs):

        from ..analysis import saveData as saveFigData

        saveFigData(self.data, fileName=fileName, fileDesc=fileDesc, fileType=fileType, fileDir=fileDir, sim=sim, **kwargs)
    

    def formatAxis(self, **kwargs):
        
        if 'title' in kwargs:
            self.axis.set_title(kwargs['title'])

        if 'xlabel' in kwargs:
            self.axis.set_xlabel(kwargs['xlabel'])

        if 'ylabel' in kwargs:
            self.axis.set_ylabel(kwargs['ylabel'])

        if 'xlim' in kwargs:
            if kwargs['xlim'] is not None:
                self.axis.set_xlim(kwargs['xlim'])

        if 'ylim' in kwargs:
            if kwargs['ylim'] is not None:
                self.axis.set_ylim(kwargs['ylim'])

        if 'invert_yaxis' in kwargs:
            if kwargs['invert_yaxis'] is True:
                self.axis.invert_yaxis()



    def saveFig(self, fileName=None, fileDesc=None, fileType='png', fileDir=None, overwrite=True, **kwargs):
        """
        'eps': 'Encapsulated Postscript',
        'jpg': 'Joint Photographic Experts Group',
        'jpeg': 'Joint Photographic Experts Group',
        'pdf': 'Portable Document Format',
        'pgf': 'PGF code for LaTeX',
        'png': 'Portable Network Graphics',
        'ps': 'Postscript',
        'raw': 'Raw RGBA bitmap',
        'rgba': 'Raw RGBA bitmap',
        'svg': 'Scalable Vector Graphics',
        'svgz': 'Scalable Vector Graphics',
        'tif': 'Tagged Image File Format',
        'tiff': 'Tagged Image File Format'
        """

        if fileDesc is not None:
            fileDesc = '_' + str(fileDesc)
        else:
            fileDesc = '_' + self.type

        if fileType not in self.fig.canvas.get_supported_filetypes():
            raise Exception('fileType not recognized in saveFig')
        else:
            fileExt = '.' + fileType

        if not fileName or not isinstance(fileName, basestring):
            fileName = self.sim.cfg.filename + fileDesc + fileExt
        else:
            if fileName.endswith(fileExt):
                fileName = fileName.split(fileExt)[0] + fileDesc + fileExt
            else:
                fileName = fileName + fileDesc + fileExt

        if fileDir is not None:
            fileName = os.path.join(fileDir, fileName)

        if not overwrite:
            while os.path.isfile(fileName):
                try:
                    fileNumStr = fileName.split(fileExt)[0].split('_')[-1]
                    fileNumStrNew = str(int(fileNumStr) + 1).zfill(2)
                    fileName = fileName.split('_' + fileNumStr)[0]
                except:
                    fileNumStr = fileNumStrNew = '01'
                    fileName = fileName.split(fileExt)[0]
                
                fileName = fileName.split(fileNumStr)[0] + '_' + fileNumStrNew + fileExt   
        
        self.fig.savefig(fileName)
        self.fileName = fileName

        return fileName



    def showFig(self, **kwargs):

        plt.close(self.fig)
        dummy = plt.figure(figsize=self.rcParams['figure.figsize'])
        new_manager = dummy.canvas.manager
        new_manager.canvas.figure = self.fig
        self.fig.set_canvas(new_manager.canvas)
        self.fig.show()


    def addLegend(self, handles=None, labels=None, **kwargs):

        legendParams = ['loc', 'bbox_to_anchor', 'fontsize', 'numpoints', 'scatterpoints', 'scatteryoffsets', 'markerscale', 'markerfirst', 'frameon', 'fancybox', 'shadow', 'framealpha', 'facecolor', 'edgecolor', 'mode', 'bbox_transform', 'title', 'title_fontsize', 'borderpad', 'labelspacing', 'handlelength', 'handletextpad', 'borderaxespad', 'columnspacing', 'handler_map']

        legendKwargs = {}
        for kwarg in kwargs:
            if kwarg in legendParams:
                legendKwargs[kwarg] = kwargs[kwarg]

        cur_handles, cur_labels = self.axis.get_legend_handles_labels()

        if not handles:
            handles = cur_handles
        if not labels:
            labels = cur_labels

        self.axis.legend(handles, labels, **legendKwargs)


    def addScalebar(self):
       
        # calculate scalebar size and add scalebar

        round_to_n = lambda x, n, m: int(np.ceil(round(x, -int(np.floor(np.log10(abs(x)))) + (n - 1)) / m)) * m
        
        scaley = 1000.0  # values in mV but want to convert to uV
        m = 10.0
        sizey = 100/scaley
        
        # while sizey > 0.25*ydisp:
        #     try:
        #         sizey = round_to_n(0.2*ydisp*scaley, 1, m) / scaley
        #     except:
        #         sizey /= 10.0
        #     m /= 10.0
        
        labely = '%.3g $\mu$V'%(sizey*scaley)#)[1:]
        
        # if len(electrodes) > 1:
        #     add_scalebar(ax,hidey=True, matchy=False, hidex=False, matchx=False, sizex=0, sizey=-sizey, labely=labely, unitsy='$\mu$V', scaley=scaley, loc=3, pad=0.5, borderpad=0.5, sep=3, prop=None, barcolor="black", barwidth=2)
        # else:
        #     add_scalebar(ax, hidey=True, matchy=False, hidex=True, matchx=True, sizex=None, sizey=-sizey, labely=labely, unitsy='$\mu$V', scaley=scaley, unitsx='ms', loc=3, pad=0.5, borderpad=0.5, sep=3, prop=None, barcolor="black", barwidth=2)

        add_scalebar(self.axis, hidey=True, matchy=False, hidex=False, matchx=False, sizex=0, sizey=-sizey, labely=labely, loc=3, pad=0.5, borderpad=0.5, sep=3, prop=None, barcolor="black", barwidth=2)
        


    def finishFig(self, **kwargs):

        self.formatAxis(**kwargs)
        
        if 'saveData' in kwargs:
            if kwargs['saveData']:
                self.saveData(**kwargs)

        if 'legend' in kwargs:
            if kwargs['legend'] is True:
                self.addLegend()
            elif type(kwargs['legend']) == dict:
                self.addLegend(**kwargs['legend'])

        if 'scalebar' in kwargs:
            if kwargs['scalebar'] is True:
                self.addScalebar()
            elif type(kwargs['scalebar']) == dict:
                self.addScalebar(**kwargs['scalebar'])

        if 'saveFig' in kwargs:
            if kwargs['saveFig']:
                self.saveFig(**kwargs)
        
        if 'showFig' in kwargs:
            if kwargs['showFig']:   
                self.showFig(**kwargs)
        else:
            plt.close(self.fig)

        # Reset the matplotlib rcParams to their original settings
        mpl.style.use(self.orig_rcParams)
        
                

class ScatterPlotter(GeneralPlotter):
    """A class used for scatter plotting"""

    def __init__(self, data, axis=None, **kwargs):
        
        super().__init__(data=data, axis=axis, **kwargs)

        self.type       = 'scatter'
        self.x          = data.get('x')
        self.y          = data.get('y')
        self.s          = data.get('s')
        self.c          = data.get('c')
        self.marker     = data.get('marker')
        self.linewidth  = data.get('linewidth')
        self.cmap       = data.get('cmap')
        self.norm       = data.get('norm')
        self.alpha      = data.get('alpha')
        self.linewidths = data.get('linewidths')


    def plot(self, **kwargs):

        scatterPlot = self.axis.scatter(x=self.x, y=self.y, s=self.s, c=self.c, marker=self.marker, linewidth=self.linewidth, cmap=self.cmap, norm=self.norm, alpha=self.alpha, linewidths=self.linewidths)

        self.finishFig(**kwargs)

        return self.fig


class LinePlotter(GeneralPlotter):
    """A class used for plotting one line per subplot"""

    def __init__(self, data, axis=None, options={}, **kwargs):
        
        super().__init__(data=data, axis=axis, **kwargs)

        self.type       = 'line'
        self.x          = np.array(data.get('x'))
        self.y          = np.array(data.get('y'))
        self.color      = data.get('color')
        self.marker     = data.get('marker')
        self.markersize = data.get('markersize')
        self.linewidth  = data.get('linewidth')
        self.alpha      = data.get('alpha')


    def plot(self, **kwargs):

        linePlot = self.axis.plot(self.x, self.y, color=self.color, marker=self.marker, markersize=self.markersize, linewidth=self.linewidth, alpha=self.alpha)

        self.finishFig(**kwargs)

        return self.fig




class LinesPlotter(GeneralPlotter):
    """A class used for plotting multiple lines on the same axis"""

    def __init__(self, data, axis=None, options={}, **kwargs):
        
        super().__init__(data=data, axis=axis, **kwargs)

        self.type       = 'lines'
        self.x          = np.array(data.get('x'))
        self.y          = np.array(data.get('y'))
        self.color      = data.get('colors')
        self.marker     = data.get('markers')
        self.markersize = data.get('markersizes')
        self.linewidth  = data.get('linewidths')
        self.alpha      = data.get('alphas')

        self.label      = data.get('label')


    def plot(self, **kwargs):

        numLines = len(self.y)

        if type(self.color) != list:
            colors = [self.color for line in range(numLines)]
        else:
            colors = self.color

        if type(self.marker) != list:
            markers = [self.marker for line in range(numLines)]
        else:
            markers = self.marker

        if type(self.markersize) != list:
            markersizes = [self.markersize for line in range(numLines)]
        else:
            markersizes = self.markersize

        if type(self.linewidth) != list:
            linewidths = [self.linewidth for line in range(numLines)]
        else:
            linewidths = self.linewidth

        if type(self.alpha) != list:
            alphas = [self.alpha for line in range(numLines)]
        else:
            alphas = self.alpha

        if self.label is None:
            labels = [None for line in range(numLines)]
        else:
            labels = self.label

        for index, line in enumerate(self.y):
            self.axis.plot(
                self.x, 
                self.y[index], 
                color=colors[index], 
                marker=markers[index], 
                markersize=markersizes[index], 
                linewidth=linewidths[index], 
                alpha=alphas[index], 
                label=labels[index],
                )

        self.finishFig(**kwargs)

        return self.fig



class HistPlotter(GeneralPlotter):
    """A class used for histogram plotting"""

    def __init__(self, data, axis=None, options={}, **kwargs):
        
        super().__init__(data=data, axis=axis, **kwargs)

        self.type        = 'histogram'
        self.x           = data.get('x')
        self.bins        = data.get('bins', None) 
        self.range       = data.get('range', None) 
        self.density     = data.get('density', False) 
        self.weights     = data.get('weights', None) 
        self.cumulative  = data.get('cumulative', False) 
        self.bottom      = data.get('bottom', None) 
        self.histtype    = data.get('histtype', 'bar') 
        self.align       = data.get('align', 'mid')
        self.orientation = data.get('orientation', 'vertical') 
        self.rwidth      = data.get('rwidth', None)
        self.log         = data.get('log', False) 
        self.color       = data.get('color', None)
        self.alpha       = data.get('alpha', None)
        self.label       = data.get('label', None)
        self.stacked     = data.get('stacked', False)
        self.data        = data.get('data', None)

    def plot(self, **kwargs):

        histPlot = self.axis.hist(self.x, bins=self.bins, range=self.range, density=self.density, weights=self.weights, cumulative=self.cumulative, bottom=self.bottom, histtype=self.histtype, align=self.align, orientation=self.orientation, rwidth=self.rwidth, log=self.log, color=self.color, alpha=self.alpha, label=self.label, stacked=self.stacked, data=self.data)

        self.finishFig(**kwargs)

        return self.fig



    """

    Types of plot:
        line
        scatter
        matrix
        bar
        pie
        

    Plots:
        plot2Dnet                   scatter
        plotConn                    matrix, bar, pie
        plotCSD                         
        plotEPSPAmp                 
        plotfI
        plotLFP
        plotRaster                  scatter
        plotRatePSD                 
        plotRates                   
        plotRateSpectrogram         
        plotRxDConcentration        
        plotShape                   
        plotSpikeHist               
        plotSpikeStats              
        plotSyncs                   
        plotTraces                  line

    """