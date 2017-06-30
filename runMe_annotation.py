'''
Copyright (C) 2016 Saeed Gholami Shahbandi. All rights reserved.

This program is free software: you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public License
as published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this program. If not, see
<http://www.gnu.org/licenses/>
'''

from __future__ import print_function

import sys
if sys.version_info[0] == 3:
    from importlib import reload
elif sys.version_info[0] == 2:
    pass

from PySide import QtGui

sys.path.append('gui/')
sys.path.append('lib/')
sys.path.append('../arrangement/')
sys.path.append('../dev/') # for svg parser

import myWindowLib_annotation

__version__ = '0.1'

# if ''name'' == "''main''":
app = QtGui.QApplication(sys.argv)
myGUI = myWindowLib_annotation.MainWindow()
myGUI.show()
app.exec_()
# sys.exit(app.exec_())
