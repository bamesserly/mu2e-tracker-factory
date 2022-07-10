"""
This file defines the SuppliesList class. This class handles the setup of the UI elements
for the supplies list and the mold release list, as well as handling reading and writing
to the files that track the status of which items have been checked off.

Author(s): Ben Hiltbrand
Date of Last Update: 4/15/19
"""

import csv, os, itertools
from PyQt5 import QtCore, QtGui, QtWidgets
from datetime import datetime
from PIL import Image
import string
from guis.common.gui_utils import generateBox


class SuppliesList:
    """
    __init__(self, Tools, Parts, Supplies, MoldRelease, pro, saveTPSMethod, saveMoldReleaseMethod)

        Description: Class initializer that sets up some class variables and calls the setup() method.

        Parameter: Tools - QGroupBox object corresponding to the tools box.
        Parameter: Parts - QGroupBox object corresponding to the parts box.
        Parameter: Supplies - QGroupBox object corresponding to the supplies box.
        Parameter: MoldRelease - QGroupBox object corresponding to the mold release box.
        Parameter: pro - Integer specifying the current panel pro to load tools, parts, and supplies.
        Parameter: saveTPSMethod - Function that save when when a Tool, Part, or Supply get checked off.
        Parameter: saveMoldReleaseMethod - Function that save when an item is mold released.
    """

    def __init__(
        self,
        Tools,
        Parts,
        Supplies,
        MoldRelease,
        pro=0,
        saveTPSMethod=None,
        saveMoldReleaseMethod=None,
    ):

        self.partsCheckboxes = []
        self.pro = pro
        self.saveTPSMethod = saveTPSMethod
        self.saveMoldReleaseMethod = saveMoldReleaseMethod

        self.moldReleasePage = MoldRelease.parentWidget()

        if Tools.layout() == None:
            self.toolBoxLayout = QtWidgets.QGridLayout(Tools)
        else:
            self.toolBoxLayout = Tools.layout()
        if Parts.layout() == None:
            self.partBoxLayout = QtWidgets.QGridLayout(Parts)
        else:
            self.partBoxLayout = Parts.layout()
        if Supplies.layout() == None:
            self.supplyBoxLayout = QtWidgets.QGridLayout(Supplies)
        else:
            self.supplyBoxLayout = Supplies.layout()
        if MoldRelease.layout() == None:
            self.moldBoxLayout = QtWidgets.QGridLayout(MoldRelease)
        else:
            self.moldBoxLayout = MoldRelease.layout()

        self.setupSupplies(Tools, Parts, Supplies)
        self.setupMoldRelease(MoldRelease)
        self.setupAcceptButton()

    """
    setupSupplies(self, Tools, Parts, Supplies)

        Description: Creates widgets and layouts for each groupbox and sets up the initial layout
                    for the tools, parts, and supplies lists.

        Parameter: Tools - QGroupBox object corresponding to the tools box.
        Parameter: Parts - QGroupBox object corresponding to the parts box.
        Parameter: Supplies - QGroupBox object corresponding to the supplies box.
    """

    def setupSupplies(self, Tools, Parts, Supplies):
        # Setup of tools area

        self.toolScrollArea = QtWidgets.QScrollArea(Tools)
        self.toolScrollArea.setWidgetResizable(True)
        self.toolScrollArea.setObjectName("toolScrollArea")
        self.toolScrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.toolWidget = QtWidgets.QWidget(self.toolScrollArea)
        self.toolWidget.setObjectName("toolWidget")

        self.toolsLayout = QtWidgets.QGridLayout(self.toolWidget)
        self.toolsLayout.setContentsMargins(0, 0, 5, 0)
        self.toolsLayout.setObjectName("toolsLayout")

        self.toolScrollArea.setWidget(self.toolWidget)
        self.toolBoxLayout.addWidget(self.toolScrollArea)

        # Setup of parts area

        self.partScrollArea = QtWidgets.QScrollArea(Parts)
        self.partScrollArea.setWidgetResizable(True)
        self.partScrollArea.setObjectName("partScrollArea")
        self.partScrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.partWidget = QtWidgets.QWidget(self.partScrollArea)
        self.partWidget.setObjectName("partWidget")

        self.partsLayout = QtWidgets.QGridLayout(self.partWidget)
        self.partsLayout.setContentsMargins(0, 0, 5, 0)
        self.partsLayout.setObjectName("partsLayout")

        self.partScrollArea.setWidget(self.partWidget)
        self.partBoxLayout.addWidget(self.partScrollArea)

        # Setup of supplies area

        self.supplyScrollArea = QtWidgets.QScrollArea(Supplies)
        self.supplyScrollArea.setWidgetResizable(True)
        self.supplyScrollArea.setObjectName("supplyScrollArea")
        self.supplyScrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.supplyWidget = QtWidgets.QWidget(self.supplyScrollArea)
        self.supplyWidget.setObjectName("supplyWidget")

        self.suppliesLayout = QtWidgets.QGridLayout(self.supplyWidget)
        self.suppliesLayout.setContentsMargins(0, 0, 5, 0)
        self.suppliesLayout.setObjectName("suppliesLayout")

        self.supplyScrollArea.setWidget(self.supplyWidget)
        self.supplyBoxLayout.addWidget(self.supplyScrollArea)

    """
    setupMoldRelease(self, MoldRelease)

        Description: Creates the layout and initial widget for the mold release list. Also creates
                    the titles for each of the columns.

        Parameter: MoldRelease - QGroupBox object corresponding to the mold release box.
    """

    def setupMoldRelease(self, MoldRelease):

        self.moldScrollArea = QtWidgets.QScrollArea(MoldRelease)
        self.moldScrollArea.setWidgetResizable(True)
        self.moldScrollArea.setObjectName("moldScrollArea")
        self.moldScrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        # self.moldScrollArea.setVerticalScrollBarPolicy(2)

        self.moldReleaseWidget = QtWidgets.QWidget(self.moldScrollArea)
        self.moldReleaseWidget.setObjectName("moldReleaseWidget")

        self.moldReleaseLayout = QtWidgets.QGridLayout(self.moldReleaseWidget)
        self.moldReleaseLayout.setContentsMargins(0, 0, 5, 0)
        self.moldReleaseLayout.setObjectName("moldReleaseLayout")

        self.partTitle = QtWidgets.QLabel(self.moldReleaseWidget)
        self.partTitle.setFont(self.getFont("huge"))
        self.partTitle.setAlignment(self.getCenterAlign())
        self.partTitle.setObjectName("partTitle")
        self.partTitle.setText("Part")
        self.partTitle.setFixedSize(100, 20)
        self.moldReleaseLayout.addWidget(self.partTitle, 0, 0, 1, 1)

        self.statusTitle = QtWidgets.QLabel(self.moldReleaseWidget)
        self.statusTitle.setFont(self.getFont("huge"))
        self.statusTitle.setAlignment(self.getLeftAlign())
        self.statusTitle.setObjectName("statusTitle")
        self.statusTitle.setText("Status")
        self.moldReleaseLayout.addWidget(self.statusTitle, 0, 1, 1, 1)

        self.workersTitle = QtWidgets.QLabel(self.moldReleaseWidget)
        self.workersTitle.setFont(self.getFont("huge"))
        self.workersTitle.setAlignment(self.getCenterAlign())
        self.workersTitle.setObjectName("workersTitle")
        self.workersTitle.setText("Worker")
        self.moldReleaseLayout.addWidget(self.workersTitle, 0, 2, 1, 1)

        self.dateTitle = QtWidgets.QLabel(self.moldReleaseWidget)
        self.dateTitle.setFont(self.getFont("huge"))
        self.dateTitle.setAlignment(self.getCenterAlign())
        self.dateTitle.setObjectName("dateTitle")
        self.dateTitle.setText("Date")
        self.moldReleaseLayout.addWidget(self.dateTitle, 0, 3, 1, 1)

        self.moldScrollArea.setWidget(self.moldReleaseWidget)
        self.moldBoxLayout.addWidget(self.moldScrollArea)

    """
    setupAcceptButton(self)

        Description: Creates the accept button for the mold release checklist. The checklist locks in changes, and saves
                 to the mold release file.
    """

    def setupAcceptButton(self):
        self.acceptButton = QtWidgets.QPushButton(self.moldReleasePage)
        # self.acceptButton.setGeometry(QtCore.QRect(610, 592, 151, 31))
        layout = self.moldReleasePage.layout().itemAtPosition(1, 0)

        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.acceptButton.setFont(font)

        self.acceptButton.setText("Accept")
        self.acceptButton.setObjectName("acceptButton")
        self.acceptButton.setDisabled(True)
        self.acceptButton.clicked.connect(self.writeMoldRelease)
        self.acceptButton.setSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred
        )
        layout.insertWidget(0, self.acceptButton, 0)

    """
    setWorker(self, workers)

        Description: Sets the current workers for the class to the specified value.

        Parameter: workers - String list specifying current panel workers.
    """

    def setWorkers(self, workers):
        self.workers = workers

    """
    setpro(self, pro)

        Description: Sets the current pro to the value specified.

        Parameter: pro - Integer specifying the current panel pro.
    """

    def setpro(self, pro):
        self.pro = pro

    """
    setMoldReleaseWidget(self, widget)

        Description: Sets the moldReleaseWidget class variable to the given widget.

        Parameter: widget - QWidget specifying the widget for the mold release layout
    """

    def setMoldReleaseWidget(self, widget):
        self.moldReleaseWidget = widget

    """
    setToolWidget(self, widget)

        Description: Sets the toolWidget class variable to the given widget.

        Parameter: widget - QWidget specifying the widget for the tools layout
    """

    def setToolWidget(self, widget):
        self.toolWidget = widget

    """
    setPartWidget(self, widget)

        Description: Sets the partWidget class variable to the given widget.

        Parameter: widget - QWidget specifying the widget for the parts layout
    """

    def setPartWidget(self, widget):
        self.partWidget = widget

    """
    setSupplyWidget(self, widget)

        Description: Sets the supplyWidget class variable to the given widget.

        Parameter: widget - QWidget specifying the widget for the supplies layout
    """

    def setSupplyWidget(self, widget):
        self.supplyWidget = widget

    """
    setDiagramPopup(self, function)

        Description: Sets the diagram_popup function

        Parameter: function - Function to display pop up images
    """

    def setDiagramPopup(self, function):
        self.diagram_popup = function

    """
    setSaveMoldReleaseMethod(self, function)

        Description: Sets the saveMoldReleaseMethod function

        Parameter: function - Function that takes the name of an item and saves (to txt file, sql, etc...) that it has been mold released.
    """

    def setSaveMoldReleaseMethod(self, function):
        self.saveMoldReleaseMethod = function

    """
    setSaveTPSMethod(self, function)

        Description: Sets the saveTPSMethod function

        Parameter: function -   Function that takes the name of an item, whether it is a tool, part or supply, and boolean as input, saves that 
                                it has been "checked-off" (or not), then returns the worker who checked it off and the timestamp it was saved.
    """

    def setSaveTPSMethod(self, function):
        self.saveTPSMethod = function

    """
    getMoldReleaseItems(self)

        Description: Returns all items on the mold release list to be mold released for the current pro.

        Returns: String list of all mold release items relevant to the current pro.
    """

    def getMoldReleaseItems(self):
        buttons = self.moldReleaseWidget.findChildren(QtWidgets.QPushButton)

        return [btn.text() for btn in buttons]

    """
    getUncheckedMoldReleaseItems(self)

        Description: Gets all items on the mold release list that have not been checked off for the current pro.

        Returns: String list of part names that have not been checked off.
    """

    def getUncheckedMoldReleaseItems(self):
        buttons = self.moldReleaseWidget.findChildren(QtWidgets.QPushButton)
        checkboxes = self.moldReleaseWidget.findChildren(QtWidgets.QCheckBox)

        btnText = [btn.text() for btn in buttons]
        boxes = [box for box in checkboxes]

        return [
            text
            for index, text in enumerate(btnText)
            if (not boxes[index].isChecked() or boxes[index].isEnabled())
        ]

    """
    getFont(self, size = 'large')

        Description: Gets the font to be used for all text elements. Currently only sets the text size,
                    but typeface could be changed here as well.

        Parameter: size - String specifying 'large' or 'small' corresponding to a font size of 12 or 8
                        respectively.

        Return: QFont specifying the desired font for the text object.
    """

    def getFont(self, size="large"):
        font = QtGui.QFont()

        if size == "large":
            font.setPointSize(12)
        elif size == "small":
            font.setPointSize(8)
        elif size == "huge":
            font.setPointSize(18)

        return font

    """
    getLeftAlign(self)

        Description: Gets an alignment object that has left horizontal alignment.

        Return: Alignment bit pattern with left horizontal alignment and center vertical alignment.
    """

    def getLeftAlign(self):
        return QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter

    """
    getCenterAlign(self)

        Description: Gets an alignment object that has centered horizontal alignment.

        Return: Alignment bit pattern with both horizontal and vertical alignment centered.
    """

    def getCenterAlign(self):
        return QtCore.Qt.AlignLeading | QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter

    """
    addLabel(self, num_elements, layout, widget, width, size, location, text, alignment, labelSuffix = '', resize = True, fixedWidth = 0)

        Description: Adds a new QLabel to a layout, in the correct position and with correct text, size, and alignment.

        Parameter: num_elements - Integer giving the number of widgers in a column (not including the one to be added). Also specifies
                                the index of the position of where to place this label.
        Parameter: layout - QGridLayout that specifies the layout where the label is to be placed.
        Parameter: widget - The QWidget that corresponds to the layout parameter.
        Parameter: width - Integer specifying the width of the QGroupBox that contains the layout.
        Parameter: size - Integer specifying the size (in units of cells) that the label should be.
        Parameter: location - Integer giving the cumulative size (in units of cells) of all other widgets in the current row, to the left of this
                            widget. Also specifies the index of the column position of where to place the label.
        Parameter: text - String specifying the text to be displayed on the label.
        Parameter: alignment - String specifying 'left' or 'center' for left or centered horizontal alignment, respectively.
        Parameter: labelSuffix - String specifying a suffix to be attached to the label object name, to differentiate when
                                there are multiple labels in one layout.
        Parameter: resize - Boolean specifying whether or not the widget corresponding to the current layout should be resized
                            when this label is added.
        Parameter: fixedWidth - Integer specifying a specific width (in pixels) that the label should occupy. A fixedWidth of 0
                                means the label is free to occupy as much space as it needs (and will dynamically change size).
        Parameter: textSize - String specifying the size of the text to be used in getFont().
    """

    def addLabel(
        self,
        num_elements,
        layout,
        widget,
        width,
        size,
        location,
        text,
        alignment,
        labelSuffix="",
        resize=True,
        fixedWidth=0,
        textSize="small",
    ):
        alignDict = {"left": self.getLeftAlign, "center": self.getCenterAlign}

        label = QtWidgets.QLabel(widget)
        label.setFont(self.getFont(textSize))
        label.setAlignment(alignDict[alignment]())
        label.setObjectName(
            f"{layout.objectName()}_label_{str(num_elements).zfill(2)}{labelSuffix}"
        )
        label.setText(text)

        if fixedWidth != 0:
            label.setFixedWidth(fixedWidth)

        layout.addWidget(label, num_elements, location, 1, size)
        widget.setLayout(layout)

    """
    addButtonToArea(self, num_elements, layout, widget, areaWidget, width, size, location, text, alignment)

        Description: Adds a new QPushButton to a layout in a QScrollArea, in the correct position and with 
                    correct text, size, and alignment.

        Parameter: num_elements - Integer giving the number of widgers in a column (not including the one to be added). Also specifies
                                the index of the position of where to place this button.
        Parameter: layout - QGridLayout that specifies the layout where the button is to be placed.
        Parameter: widget - The QWidget that corresponds to the layout parameter.
        Parameter: areaWidget - QWidget that corresponds to the QScrollArea that this button is being added to.
        Parameter: width - Integer specifying the width of the QGroupBox that contains the layout.
        Parameter: size - Integer specifying the size (in units of cells) that the button should be.
        Parameter: location - Integer giving the cumulative size (in units of cells) of all other widgets in the current row, to the left of this
                            widget. Also specifies the index of the column position of where to place the button.
        Parameter: text - String specifying the text to be displayed on the button.
        Parameter: alignment - String specifying 'left' or 'center' for left or centered horizontal alignment, respectively.
    """

    def addButtonToArea(
        self,
        num_elements,
        layout,
        widget,
        areaWidget,
        width,
        size,
        location,
        text,
        alignment,
    ):
        button = QtWidgets.QPushButton(widget)
        button.setFont(self.getFont("small"))
        button.setObjectName(
            f"{layout.objectName()}_button_{str(num_elements).zfill(2)}"
        )

        # Finds spaces in the name and adds a '\n' so that the text doesn't run off the button
        spaces = []
        start = 0
        try:
            while True:
                i = text.index(" ", start)
                spaces.append(i)
                start = i + 1
        except ValueError:
            pass
        if spaces != []:
            n = round(len(text) / 2)
            diff = [abs(n - i) for i in spaces]
            i = spaces[diff.index(min(diff))]
            text = text[:i] + "\n" + text[i + 1 :]

        button.setText(text)
        pictureName = self.fileName(text)
        button.clicked.connect(lambda: self.diagram_popup(f"{pictureName}.png"))

        layout.addWidget(button, num_elements, location, 1, size)
        widget.setLayout(layout)

    """
    addButton(self, num_elements, layout, widget, width, size, location, text, alignment)

        Description: Adds a new QPushButton to a layout, in the correct
        position and with correct text, size, and alignment.

        Parameter: num_elements - Integer giving the number of widgers in a
                   column (not including the one to be added). Also specifies
                   the index of the position of where to place this button.
        Parameter: layout - QGridLayout that specifies the layout where the button is to be placed.
        Parameter: widget - The QWidget that corresponds to the layout parameter.
        Parameter: width - Integer specifying the width of the QGroupBox that contains the layout.
        Parameter: size - Integer specifying the size (in units of cells) that the button should be.
        Parameter: location - Integer giving the cumulative size (in units of
                   cells) of all other widgets in the current row, to the left of this
                   widget. Also specifies the index of the column position of where to
                   place the button.
        Parameter: text - String specifying the text to be displayed on the button.
        Parameter: alignment - String specifying 'left' or 'center' for left or
                   centered horizontal alignment, respectively.
    """

    def addButton(
        self, num_elements, layout, widget, width, size, location, text, alignment
    ):
        button = QtWidgets.QPushButton(widget)
        button.setFont(self.getFont())
        button.setObjectName(
            f"{layout.objectName()}_button_{str(num_elements).zfill(2)}"
        )
        button.setText(text)
        pictureName = self.fileName(text)
        button.clicked.connect(lambda: self.diagram_popup(f"{pictureName}.png"))
        layout.addWidget(button, num_elements, location, 1, size)
        widget.setLayout(layout)

    """
    addCheckBox(self, index, layout, widget, location, text, state, setDisabledOnTrue = False)

        Description: Adds a new QCheckBox to a layout, in the correct position and with correct state, size, and alignment.
                    All checkboxes have a fixed width of 16 pixels. Checkboxes are added to their own horizontal layout in
                    each grid layout cell, to center them in the cell.

        Parameter: index - Integer giving the number of widgers in a column (not including the one to be added). Also specifies
                                the index of the position of where to place this checkbox.
        Parameter: layout - QGridLayout that specifies the layout where the checkbox is to be placed.
        Parameter: widget - The QWidget that corresponds to the layout parameter.
        Parameter: location - Integer giving the cumulative size (in units of cells) of all other widgets in the current row, to the left of this
                            widget. Also specifies the index of the column position of where to place the checkbox.
        Parameter: text - String specifying the text to be displayed on the checkbox.
        Parameter: state - Boolean specifying whether or not the checkbox should start checked.
        Parameter: setDisabledOnTrue - Boolean specifying if the checkbox should be disabled when checked.
    """

    def addCheckBox(
        self, index, layout, widget, location, text, state, setDisabledOnTrue=False
    ):
        horizontalLayout = QtWidgets.QHBoxLayout()
        horizontalLayout.setObjectName(f"horizontalLayout_{index}")

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)

        checkbox = QtWidgets.QCheckBox(widget)
        checkbox.setFont(self.getFont())
        checkbox.setText("")
        checkbox.setChecked(state)
        checkbox.setFixedWidth(14)
        checkbox.setFixedHeight(14)
        # checkbox.setStyleSheet("margin-left:90%; margin-right:10%;")
        checkbox.setObjectName(f"{layout.objectName()}_checkbox_{str(index).zfill(2)}")

        # sizePolicy.setHeightForWidth(checkbox.sizePolicy().hasHeightForWidth())
        # checkbox.setSizePolicy(sizePolicy)

        horizontalLayout.addWidget(checkbox)
        layout.addLayout(horizontalLayout, index, location, 1, 1)

        # layout.addWidget(checkbox, index, location, 1, 1)
        widget.setLayout(layout)

        if setDisabledOnTrue and state:
            checkbox.setDisabled(True)

        return checkbox

    """
    connectTPSCheckboxes(self)

        Description: Connects all checkbox clicked signals for the tools, parts, and supplies 
                 checkboxes to the self.writeTPS function.
    """

    def connectTPSCheckboxes(self):
        toolsLabels = self.toolWidget.findChildren(QtWidgets.QLabel)
        toolsWorkersLabels = list(
            filter(lambda obj: "_worker" in obj.objectName(), toolsLabels)
        )
        toolsDateLabels = list(
            filter(lambda obj: "_date" in obj.objectName(), toolsLabels)
        )
        toolsCheckboxes = self.toolWidget.findChildren(QtWidgets.QCheckBox)

        partsLabels = self.partWidget.findChildren(QtWidgets.QLabel)
        partsWorkersLabels = list(
            filter(lambda obj: "_worker" in obj.objectName(), partsLabels)
        )
        partsDateLabels = list(
            filter(lambda obj: "_date" in obj.objectName(), partsLabels)
        )
        partsCheckboxes = self.partWidget.findChildren(QtWidgets.QCheckBox)

        suppliesLabels = self.supplyWidget.findChildren(QtWidgets.QLabel)
        suppliesWorkersLabels = list(
            filter(lambda obj: "_worker" in obj.objectName(), suppliesLabels)
        )
        suppliesDateLabels = list(
            filter(lambda obj: "_date" in obj.objectName(), suppliesLabels)
        )
        suppliesCheckboxes = self.supplyWidget.findChildren(QtWidgets.QCheckBox)

        for index, checkbox in enumerate(toolsCheckboxes):
            checkbox.clicked.connect(
                lambda box=checkbox, workerLabel=toolsWorkersLabels[
                    index
                ], dateLabel=toolsDateLabels[index], i=index: self.writeTPS(
                    "tools", box, workerLabel, dateLabel, i
                )
            )

        for index, checkbox in enumerate(partsCheckboxes):
            checkbox.clicked.connect(
                lambda box=checkbox, workerLabel=partsWorkersLabels[
                    index
                ], dateLabel=partsDateLabels[index], i=index: self.writeTPS(
                    "parts", box, workerLabel, dateLabel, i
                )
            )

        for index, checkbox in enumerate(suppliesCheckboxes):
            checkbox.clicked.connect(
                lambda box=checkbox, workerLabel=suppliesWorkersLabels[
                    index
                ], dateLabel=suppliesDateLabels[index], i=index: self.writeTPS(
                    "supplies", box, workerLabel, dateLabel, i
                )
            )

    """
    connectMoldReleaseCheckboxes(self)

        Description: Connects the checkbox clicked signal for all mold release checkboxes. Updates the state changed for the checkbox
                 and checks if the accept button should be enabled.
    """

    def connectMoldReleaseCheckboxes(self):
        for checkbox in self.moldReleaseWidget.findChildren(QtWidgets.QCheckBox):
            index = int(checkbox.objectName()[-2:])
            checkbox.clicked.connect(
                lambda clicked, i=index: self.updateStateChanged(i - 1)
            )
            checkbox.clicked.connect(
                lambda: self.acceptButton.setDisabled(False)
                if any(self.moldReleaseStateChanged)
                else self.acceptButton.setDisabled(True)
            )

    """
    processList(self, list)

        Description: Handles extraneous commas in the list, that were not intended as delimiters.

        Parameter: list - String list to be processed.
    """

    def processList(self, list):
        for index, row in enumerate(list):
            list[index] = [",".join(row[:-3]), row[-3], row[-2], row[-1]]

    def updateStateChanged(self, index):
        self.moldReleaseStateChanged[index] = not self.moldReleaseStateChanged[index]

    """
    loadSuppliesList(self)

        Description: Loads the supplies list for the pro, and then generates the UI buttons, checkboxes, and labels.
    """

    def loadSuppliesList(self, tools, parts, supplies):
        # Save lists for local access
        self.tools = tools
        self.parts = parts
        self.supplies = supplies

        # Specifications for dimensions and allignment of supplies lists
        size = 5
        width = 469
        alignL = "left"
        alignC = "center"
        resize = False
        workerFixedWidth = 100
        dateFixedWidth = 100

        spacer = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )

        # Iterates through the tools list
        for index, tool in enumerate(self.tools):
            # Parses inner list into component parts
            name, state, worker, date = tool

            if state:
                date = date.strftime("%Y-%m-%d %H:%M")
            else:
                date = str()
                worker = str()

            # Generates a button, label, and checkbox for each item in the list
            self.addButtonToArea(
                index,
                self.toolsLayout,
                self.toolWidget,
                self.toolScrollArea,
                width,
                size,
                0,
                name,
                alignL,
            )
            self.addLabel(
                index,
                self.toolsLayout,
                self.toolWidget,
                width,
                1,
                size,
                worker,
                alignC,
                "_worker",
                resize,
                workerFixedWidth,
            )
            self.addLabel(
                index,
                self.toolsLayout,
                self.toolWidget,
                width,
                1,
                size + 1,
                date,
                alignC,
                "_date",
                resize,
                dateFixedWidth,
            )
            checkbox = self.addCheckBox(
                index, self.toolsLayout, self.toolWidget, size + 2, "", state
            )
            self.partsCheckboxes.append(checkbox)

            # Also add spacers to list
            self.toolsLayout.addItem(spacer, index + 1, 1, 1, 4)

        # Do the same for the parts and supplies lists...

        for index, part in enumerate(self.parts):
            # Parses inner list into component parts
            name, state, worker, date = part

            if state:
                date = date.strftime("%Y-%m-%d %H:%M")
            else:
                date = str()
                worker = str()

            self.addButtonToArea(
                index,
                self.partsLayout,
                self.partWidget,
                self.partScrollArea,
                width,
                size,
                0,
                name,
                alignL,
            )
            self.addLabel(
                index,
                self.partsLayout,
                self.partWidget,
                width,
                1,
                size,
                worker,
                alignC,
                "_worker",
                resize,
                workerFixedWidth,
            )
            self.addLabel(
                index,
                self.partsLayout,
                self.partWidget,
                width,
                1,
                size + 1,
                date,
                alignC,
                "_date",
                resize,
                dateFixedWidth,
            )
            checkbox = self.addCheckBox(
                index, self.partsLayout, self.partWidget, size + 2, "", state
            )
            self.partsCheckboxes.append(checkbox)

            self.partsLayout.addItem(spacer, index + 1, 1, 1, 4)

        for index, supply in enumerate(self.supplies):
            # Parses inner list into component parts
            name, state, worker, date = supply

            if state:
                date = date.strftime("%Y-%m-%d %H:%M")
            else:
                date = str()
                worker = str()

            self.addButtonToArea(
                index,
                self.suppliesLayout,
                self.supplyWidget,
                self.supplyScrollArea,
                width,
                size,
                0,
                name,
                alignL,
            )
            self.addLabel(
                index,
                self.suppliesLayout,
                self.supplyWidget,
                width,
                1,
                size,
                worker,
                alignC,
                "_worker",
                resize,
                workerFixedWidth,
            )
            self.addLabel(
                index,
                self.suppliesLayout,
                self.supplyWidget,
                width,
                1,
                size + 1,
                date,
                alignC,
                "_date",
                resize,
                dateFixedWidth,
            )
            checkbox = self.addCheckBox(
                index, self.suppliesLayout, self.supplyWidget, size + 2, "", state
            )
            self.partsCheckboxes.append(checkbox)

            self.suppliesLayout.addItem(spacer, index + 1, 1, 1, 4)
        self.connectTPSCheckboxes()

    # Check all checkboxes in TPS!
    def checkEmAll(self):
        toolsLabels = self.toolWidget.findChildren(QtWidgets.QLabel)
        toolsWorkersLabels = list(
            filter(lambda obj: "_worker" in obj.objectName(), toolsLabels)
        )
        toolsDateLabels = list(
            filter(lambda obj: "_date" in obj.objectName(), toolsLabels)
        )
        toolsCheckboxes = self.toolWidget.findChildren(QtWidgets.QCheckBox)

        partsLabels = self.partWidget.findChildren(QtWidgets.QLabel)
        partsWorkersLabels = list(
            filter(lambda obj: "_worker" in obj.objectName(), partsLabels)
        )
        partsDateLabels = list(
            filter(lambda obj: "_date" in obj.objectName(), partsLabels)
        )
        partsCheckboxes = self.partWidget.findChildren(QtWidgets.QCheckBox)

        suppliesLabels = self.supplyWidget.findChildren(QtWidgets.QLabel)
        suppliesWorkersLabels = list(
            filter(lambda obj: "_worker" in obj.objectName(), suppliesLabels)
        )
        suppliesDateLabels = list(
            filter(lambda obj: "_date" in obj.objectName(), suppliesLabels)
        )
        suppliesCheckboxes = self.supplyWidget.findChildren(QtWidgets.QCheckBox)

        for index, checkbox in enumerate(toolsCheckboxes):
            checkbox.setChecked(True)
            self.writeTPS(
                "tools", True, toolsWorkersLabels[index], toolsDateLabels[index], index
            )

        for index, checkbox in enumerate(partsCheckboxes):
            checkbox.setChecked(True)
            self.writeTPS(
                "parts", True, partsWorkersLabels[index], partsDateLabels[index], index
            )

        for index, checkbox in enumerate(suppliesCheckboxes):
            checkbox.setChecked(True)
            self.writeTPS(
                "supplies",
                True,
                suppliesWorkersLabels[index],
                suppliesDateLabels[index],
                index,
            )

    """
    loadMoldReleaseList(self, data)

        Description: Reads the mold release list, and generates the UI elements like buttons and checkboxes.

        Parameter: data - List of lists holding mold release data:
            - Inner list format:
                1. (str)        Item name 
                2. (bool)       Has item been mold released
                3. (str)        Worker id
                4. (datetime)   Time when item was mold released
    """

    def loadMoldReleaseList(self, data):
        width = 1000
        alignL = "left"
        alignC = "center"
        index = 0

        spacer = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )

        for index, row in enumerate(data):
            item, state, worker, timestamp = row

            if state:
                timestamp = timestamp.strftime("%Y-%m-%d %H:%M")
            else:
                worker = str()
                timestamp = str()

            self.addButton(
                index + 1,
                self.moldReleaseLayout,
                self.moldScrollArea,
                width,
                1,
                0,
                item,
                alignL,
            )
            self.addLabel(
                index + 1,
                self.moldReleaseLayout,
                self.moldReleaseWidget,
                width,
                1,
                2,
                worker,
                alignC,
                "_2",
            )
            self.addLabel(
                index + 1,
                self.moldReleaseLayout,
                self.moldReleaseWidget,
                width,
                1,
                3,
                timestamp,
                alignC,
                "_3",
            )
            self.addCheckBox(
                index + 1,
                self.moldReleaseLayout,
                self.moldReleaseWidget,
                1,
                "",
                state,
                True,
            )

            self.moldReleaseLayout.addItem(spacer, index + 2, 1, 1, 4)

            # self.moldReleaseStateChanged defaults to all False
            self.moldReleaseStateChanged = [False] * (index + 1)

        self.connectMoldReleaseCheckboxes()

    """
    writeMoldRelease(self)

        Description:    Function called when a the accept button is pressed. Iterates through all mold release checkboxes 
                        and, if the state has been changed, writes the changed value to the mold release file.
    """

    def writeMoldRelease(self):
        box = QtWidgets.QMessageBox(self.moldReleaseWidget.window())
        box.setStyleSheet("color: black; background-color: white;")
        box.setIcon(QtWidgets.QMessageBox.Question)
        box.setWindowTitle("Save Mold Release Data")
        box.setText("Are you sure that everything is correct?")
        box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        ok = box.exec_()

        self.acceptButton.setDisabled(True)

        if ok == QtWidgets.QMessageBox.Yes:
            self.saveMoldReleaseState()

    """
    saveMoldReleaseState

        Description:    For every checkbox who's state has changed, saves it with 'self.saveMoldReleaseMethod'
                        and displays worker, date, etc... 
    """

    def saveMoldReleaseState(self):
        # Iterate through each of the mold release checkboxes
        for button, check_box in zip(
            self.moldReleaseWidget.findChildren(QtWidgets.QPushButton),
            self.moldReleaseWidget.findChildren(QtWidgets.QCheckBox),
        ):

            # Get index by object name
            index = int(check_box.objectName()[-2:])

            # It item has been checked off, save and display it
            if self.moldReleaseStateChanged[index - 1]:
                self.moldReleaseStateChanged[index - 1] = False  # Reset state changed

                # Get item info
                item = button.text()
                status = check_box.isChecked()

                # Save info
                worker, timestamp = self.saveMoldReleaseMethod(item, status)

                # Display worker and timestamp
                workerLabel = self.moldReleaseWidget.findChild(
                    QtWidgets.QLabel, f"moldReleaseLayout_label_{str(index).zfill(2)}_2"
                )
                dateLabel = self.moldReleaseWidget.findChild(
                    QtWidgets.QLabel, f"moldReleaseLayout_label_{str(index).zfill(2)}_3"
                )

                if status:
                    workerLabel.setText(worker)
                    dateLabel.setText(timestamp.strftime("%Y-%m-%d %H:%M"))
                    check_box.setDisabled(True)
                else:
                    workerLabel.setText(str())
                    dateLabel.setText(str())

    """
    clearMoldRelease(self)

        Description: Resets the mold release list to default, with no items being checked off. Clears labels and re-enables checkboxes.
                 Called at the end of panel pro five.
    """

    def clearMoldRelease(self):
        # Re-enable accept button
        self.acceptButton.setEnabled(True)

        # Un-check all check boxes
        for check_box in self.moldReleaseWidget.findChildren(QtWidgets.QCheckBox):
            check_box.setChecked(False)

        # Save that all checkboxes have been changed
        if hasattr(self, "moldReleaseStateChanged"):
            self.moldReleaseStateChanged = [True for _ in self.moldReleaseStateChanged]

        # Save changes
        self.saveMoldReleaseState()

    """
    writeTPS(self, mode, state, workerLabel, dateLabel, index)

        Description: Function called when a tools, parts, or supplies checkbox is clicked. Updates labels
                    with worker and time checked off, and updates the list file accordingly.
                    
        Parameter: mode - String specifying which list to update 'tools', 'parts', or 'supplies'.
        Parameter: state - Boolean specifying checkbox check state, True for checked, False otherwise.
        Parameter: workerLabel - String specifying the label object name for the worker label corresponding
                                to the checkbox clicked.
        Parameter: dateLabel - String specifying the label object name for the date label corresponding
                            to the checkbox clicked.
        Parameter: index - Integer specifying the index of the checkbox that called the function.
    """

    def writeTPS(self, mode, state, workerLabel, dateLabel, index):
        # Get list to be editted
        modeDict = {"tools": self.tools, "parts": self.parts, "supplies": self.supplies}
        editList = modeDict[mode]

        # Get name of item
        item = editList[index][0]

        # Save with DP and get worker and timestamp
        worker, timestamp = self.saveTPSMethod(tps=mode, item=item, state=state)

        # Update local list
        editList[index] = [item, state, worker, timestamp]

        # Display text
        if state:
            workerLabel.setText(worker)
            dateLabel.setText(timestamp.strftime("%Y-%m-%d %H:%M"))
        else:
            workerLabel.setText(str())
            dateLabel.setText(str())

    """
    clearTPS(self)

        Description: Resets the tools, parts, and supplies list to the default state.
    """

    def clearTPS(self):

        # Inner method that finds the worker/date labels and checkboxes for a given widget
        # then sets the checkbox to 'False', and writes that it is unchecked.
        def resetWidget(widget, mode):
            labels = widget.findChildren(QtWidgets.QLabel)
            worker_labels = list(
                filter(lambda obj: "_worker" in obj.objectName(), labels)
            )
            date_labels = list(filter(lambda obj: "_date" in obj.objectName(), labels))
            checkboxes = widget.findChildren(QtWidgets.QCheckBox)
            for i in range(len(checkboxes)):
                checkboxes[i].setChecked(False)
                self.writeTPS(mode, False, worker_labels[i], date_labels[i], i)

        # Call method on TPS widgets with corresponding modes ('tools', etc...)
        resetWidget(self.toolWidget, "tools")
        resetWidget(self.partWidget, "parts")
        resetWidget(self.supplyWidget, "supplies")

    """
    allPartsChecked(self)

        Description: Checks if all the checkboxes for the tools, parts, and supplies lists are checked off.

        Return: Boolean True if they are all checked off, False otherwise.
    """

    def allPartsChecked(self):
        toolsCheckboxes = self.toolWidget.findChildren(QtWidgets.QCheckBox)
        partsCheckboxes = self.partWidget.findChildren(QtWidgets.QCheckBox)
        supplyCheckboxes = self.supplyWidget.findChildren(QtWidgets.QCheckBox)

        checked1 = [obj.isChecked() for obj in toolsCheckboxes]
        checked2 = [obj.isChecked() for obj in partsCheckboxes]
        checked3 = [obj.isChecked() for obj in supplyCheckboxes]

        return all(checked1) and all(checked2) and all(checked3)

    """
    moldReleaseChecked(self)

        Description: Checks that all relevant mold release items for the pro have been checked off.

        Returns: Boolean value, True if all items checked off, False otherwise.
    """

    def moldReleaseChecked(self):
        checkboxes = self.moldReleaseWidget.findChildren(QtWidgets.QCheckBox)

        return all([box.isChecked() for box in checkboxes])

    """
    deleteLists(self)

        Description: Deletes the supply and mold release lists. This is needed when the back to pro select button
                 is pressed, and a new supplies list is loaded. Without this, the new list is simply put on
                 top of the old list, resulting in it looking bad, and allowing for unintended behavior. Calls
                 to deleteLater() have been removed. Technically, this can result in memory leaks. The total memory
                 used is so small, and the number of times the button is expected to be pressed (1 or 2) means
                 this is not a huge deal. The deleteLater() calls were removed due to causing segmentation faults
                 when deleteLists() was called.
    """

    def deleteLists(self):
        try:
            self.toolScrollArea.setParent(None)
            # self.toolScrollArea.deleteLater()

            self.toolWidget.setParent(None)
            # self.toolWidget.deleteLater()

            # self.toolsLayout.setParent(None)   # crash in backtoproselect
            # self.toolsLayout.deleteLater()

            self.partScrollArea.setParent(None)
            # self.partScrollArea.deleteLater()

            self.partWidget.setParent(None)
            # self.partWidget.deleteLater()

            # self.partsLayout.setParent(None)     # crash in backtoproselect
            # self.partsLayout.deleteLater()

            self.supplyScrollArea.setParent(None)
            # self.supplyScrollArea.deleteLater()

            self.supplyWidget.setParent(None)
            # self.supplyWidget.deleteLater()

            # self.suppliesLayout.setParent(None)     # crash in backtoproselect
            # self.suppliesLayout.deleteLater()

            self.moldReleaseWidget.setParent(None)
            # self.moldReleaseWidget.deleteLater()

            self.moldScrollArea.setParent(None)
            # self.moldScrollArea.deleteLater()

            # self.moldReleaseLayout.setParent(None)   # crash in backtoproselect
            # self.moldReleaseLayout.deleteLater()

            self.acceptButton.setParent(None)
            # self.acceptButton.deleteLater()

        except Exception:
            print("Unable to delete supplies lists")

    """   
    fileName(self, string_input)

        Description: Removes punctuation so the GUI can find the files.

        Parameter: string_input - the string to be modified. 
    """

    def fileName(self, string_input):
        punctuations = """!;:'"\<>/?@$^*_~"""
        no_punct = ""
        for char in string_input:
            if char not in punctuations:
                no_punct = no_punct + char
        name = no_punct.replace("\n", " ")
        return name
