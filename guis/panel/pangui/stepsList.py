"""
This file contains the class definitions for both Step and StepList. StepList is a list
of Steps used for generating the panel steps on the GUI, as well as associated checkboxes
and buttons. Previously, steps were hard coded into the GUI, meaning any kind of change
to the steps was tedious. In addition, the steps occupied a fixed area, meaning there
was a limit to the amount of step text that could be used. These classes fix these problems.
Steps are loaded from text files that are trivially easy to modify. In addition, the layout
is now handled by PyQt, giving a more consistent look.

Author(s): Ben Hiltbrand
Date of Last Update: 4/15/19
"""

from PyQt5 import QtCore, QtGui, QtWidgets
import os, csv
from pathlib import Path
import logging

logger = logging.getLogger("root")


"""
    The step class defines a single step in the production process. A step may or may not
    have an associated checkbox and picture. In addition, a step may have substeps, which
    are simply a list of steps. Setters and getters for this class are trivial, and will
    not be documented in detail.
"""


class Step:
    """
    __init__(self, number, name, checkbox, picture, pictureName, text, substeps = [])

        Description: The class initializer. Creates a new Step object.

        Parameter: number - Integer giving where in the production process this step resides.
        Parameter: name - String giving the step name that is to be recorded when step is checked off.
        Parameter: checkbox - Boolean specifying whether this step has an associated checkbox.
        Parameter: picture - Boolean specifying whether this step has an associated picture.
        Parameter: pictureName - String giving the filename and type of the associated picture
                (e.g. picture.png). Empty string if no picture.
        Parameter: text - String specifying the text to display on the GUI for that step
        Parameter: substeps - A Step list of the associated substeps for this step.
    """

    def __init__(self, number, name, checkbox, picture, pictureName, text, substeps=[]):
        self.hasCheckbox = checkbox
        self.hasPicture = picture
        self.pictureName = pictureName
        self.substeps = []
        self.number = number
        self.text = text
        self.name = name
        self.checkbox = None
        self.pictureButton = None
        self.next = None
        self.previous = None
        self.isSubstep = False

    def setHasCheckbox(self, box):
        self.hasCheckbox = box

    def setHasPicture(self, picture):
        self.hasPicture = picture

    def setPictureName(self, name):
        self.pictureName = name

    def setSubsteps(self, steps):
        self.substeps = steps

    def setNumber(self, n):
        self.number = n

    def setText(self, text):
        self.text = text

    def setName(self, name):
        self.name = name

    def setCheckbox(self, checkbox):
        self.checkbox = checkbox

    def setPictureButton(self, button):
        self.pictureButton = button

    def setNext(self, step):
        self.next = step

    def setPrevious(self, step):
        self.previous = step

    def setIsSubstep(self, bool):
        self.isSubstep = bool

    def getHasCheckbox(self):
        return self.hasCheckbox

    def getHasPicture(self):
        return self.hasPicture

    def getPictureName(self):
        return self.pictureName

    def getSubsteps(self):
        return self.substeps

    def getNumber(self):
        return self.number

    def getText(self):
        return self.text

    def getName(self):
        return self.name

    def getCheckbox(self):
        return self.checkbox

    def getPictureButton(self):
        return self.pictureButton

    def getNext(self):
        return self.next
    
    def getNextCheckbox(self):
        if self.next is None:
            return None
        next=self.next
        while next.hasCheckbox is False and next.next is not None:
            next=next.next
        return next
        
    def getPrevious(self):
        return self.previous

    """
    addSubstep(self, step)

        Description: Adds a new substep to this step. When a new substep is added, substeps are sorted
                    by step number. This means substeps do not have to be added in order.

        Parameter: step - A Step object for the substep to be added
    """

    def addSubstep(self, step):
        self.substeps.append(step)

        l = list(zip((k.getNumber() for k in self.substeps), self.substeps))
        l.sort()
        self.substeps = [j for i, j in l]


"""
    The StepList class defines a list of Steps, and also methods for reading steps from a file, and
    displaying the steps on the GUI itself. For ease of use with existing GUI functions, steps with
    checkboxes are stored in a doubly linked list. Since steps may or may not have a checkbox, it is
    necessary to keep track of what step is being checked off next (since it may not be the next step
    in the list).
"""


class StepList:
    """
    __init__(self, box, steps, stepFunction, imageFunction)

        Description: Class initializer. Creates a new StepList object.

        Parameter: box - A tab from an associated QTabWidget. Specifies where to display the steps list.
        Parameter: steps - An ordered list of Step objets.
        Parameter: stepFunction - A function to be connected to the checkboxes.
        Parameter: imageFunction - A function to be connected to image buttons.
    """

    def __init__(self, box, steps, stepFunction, imageFunction):

        self.steps = steps

        self.stepFunction = stepFunction
        self.imageFunction = imageFunction

        if box.layout() == None:
            self.boxLayout = QtWidgets.QGridLayout(box)
            self.boxLayout.setObjectName("StepsBoxLayout")
        else:
            self.boxLayout = box.layout()

        self.Steps = QtWidgets.QScrollArea(box)
        self.Steps.setWidgetResizable(True)
        self.Steps.setObjectName("Steps")
        self.boxLayout.addWidget(self.Steps)

        self.stepsWidget = QtWidgets.QWidget()
        self.stepsWidget.setGeometry(QtCore.QRect(0, 0, 439, 609))
        self.stepsWidget.setObjectName("stepsWidget")

        self.Steps.setWidget(self.stepsWidget)

        self.layout = QtWidgets.QGridLayout(self.stepsWidget)
        self.layout.setObjectName("StepsLayout")
        self.layout.setContentsMargins(5, 5, 5, 5)

    def setDay(self, day):
        self.day = day

    def setStepsPath(self, path):
        self.stepsPath = path

    def getSteps(self):
        return self.steps

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
    readSteps(self)

        Description: Reads the steps file for the associated panel day. Creates a new step object for
                 each line in the file, and adds the Step object to the list. Also handles adding
                 substeps to the substep list for the corresponding Step. The step list is sorted
                 by step number at the end, meaning the order of the steps in the file is
                 irrelevant.
    """

    def readSteps(self):
        stepFile = Path(self.stepsPath / f"Day {self.day}.csv")

        if Path.exists(stepFile):
            with open(str(stepFile), "r") as f:
                reader = csv.reader(f, delimiter=";")
                names = []

                for index, row in enumerate(reader):
                    if len(row) == 6:
                        if row[0].isnumeric():
                            try:
                                self.steps.append(Step(*row))
                                names.append(row[0])
                            except Exception:
                                logger.info(f"Unable to read step at line {index}")
                        else:
                            i = 1
                            s = row[0][:i]

                            while s.isnumeric():
                                i += 1
                                s = row[0][:i]

                            major = row[0][: i - 1]

                            try:
                                self.steps[names.index(major)].addSubstep(Step(*row))
                            except Exception:
                                logger.info(
                                    f"Unable to find parent step for step {row[0]}"
                                )

            l = list(zip([n.getNumber().zfill(2) for n in self.steps], self.steps))
            l.sort()
            self.steps = [j for i, j in l]

    """
    associateSteps(self)

        Description: Links steps with checkboxes together into the doubly linked list. Calling
                 the getNext() or getPrevious() methods will return the next and previous
                 step with a checkbox, respectively. If there is no previous or next step,
                 or the step being considered does not have a checkbox, None is returned.
    """

    def associateSteps(self):
        for index1, step1 in enumerate(self.steps):
            nSubsteps = len(step1.getSubsteps())

            if nSubsteps != 0:
                step1.setNext(step1.getSubsteps()[0])

                for index2, step2 in enumerate(step1.getSubsteps()):
                    if index2 + 1 < nSubsteps:
                        step2.setNext(step1.getSubsteps()[index2 + 1])
                        step1.getSubsteps()[index2 + 1].setPrevious(step2)
                    else:
                        if index1 + 1 < len(self.steps):
                            step2.setNext(self.steps[index1 + 1])
                            self.steps[index1 + 1].setPrevious(step2)
            else:
                if index1 + 1 < len(self.steps):
                    step1.setNext(self.steps[index1 + 1])
                    self.steps[index1 + 1].setPrevious(step1)

    """
    addStep(self, step, widget, layout, row)

        Description: Adds a step to the GUI. If a step has a checkbox, that is added to
                    the first column, otherwise a dummy label with no text is added to
                    preserve spacing. If the step has a picture, a button is added to
                    the second column, with its text being the step number. If there is
                    no picture, a label with the step number is added. The third column
                    displays the step text.

        Parameter: step - Step object of the step to be added.
        Parameter: widget - QWidget associated with the layout the step is to be added.
        Parameter: layout - QGridLayout where the step is to be added.
        Parameter: row - Integer specifying the row in the layout where the step is to be added.
    """

    def addStep(self, step, widget, layout, row):
        if step.getHasCheckbox():
            horizontalLayout = QtWidgets.QHBoxLayout()
            horizontalLayout.setObjectName(f"horizontalLayout_{row}")

            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed
            )
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)

            checkbox = QtWidgets.QCheckBox(widget)
            checkbox.setText("")
            checkbox.setChecked(False)
            checkbox.setFixedWidth(14)
            checkbox.setFixedHeight(14)
            checkbox.setObjectName(
                f"{layout.objectName()}_checkbox_{str(row).zfill(2)}"
            )
            checkbox.setDisabled(True)
            checkbox.clicked.connect(self.stepFunction)

            horizontalLayout.addWidget(checkbox)
            layout.addLayout(horizontalLayout, row, 0, 1, 1)

            step.setCheckbox(checkbox)
        else:
            horizontalLayout = QtWidgets.QHBoxLayout()
            horizontalLayout.setObjectName(f"horizontalLayout_{row}")

            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed
            )
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)

            label = QtWidgets.QLabel(widget)
            label.setText("")
            label.setFixedWidth(16)

            sizePolicy.setHeightForWidth(label.sizePolicy().hasHeightForWidth())
            label.setSizePolicy(sizePolicy)

            horizontalLayout.addWidget(label)
            layout.addLayout(horizontalLayout, row, 0, 1, 1)

        if step.getHasPicture():
            button = QtWidgets.QPushButton(widget)
            button.setFont(self.getFont())
            button.setObjectName(f"{layout.objectName()}_button_{str(row).zfill(2)}")
            if step.isSubstep:
                button.setText(f"{step.getNumber()}")
            else:
                button.setText(f"{step.getNumber()}.")
            button.setFixedWidth(30)
            button.clicked.connect(lambda: self.imageFunction(step.getPictureName()))
            layout.addWidget(button, row, 1, 1, 1)
            widget.setLayout(layout)
            step.setPictureButton(button)
        else:
            label = QtWidgets.QLabel(widget)
            label.setFont(self.getFont())
            label.setObjectName(
                f"{layout.objectName()}_step_number_{str(row).zfill(2)}"
            )
            if step.isSubstep:
                label.setText(f"{step.getNumber()}")
            else:
                label.setText(f"{step.getNumber()}.")
            label.setFixedWidth(25)
            label.setAlignment(
                QtCore.Qt.AlignLeading | QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter
            )
            layout.addWidget(label, row, 1, 1, 1)
            widget.setLayout(layout)

        label = QtWidgets.QLabel(widget)
        label.setFont(self.getFont())
        label.setObjectName(f"{layout.objectName()}_step_text_{str(row).zfill(2)}")

        label.setText(step.getText())
        label.setWordWrap(True)

        layout.addWidget(label, row, 2, 1, 1)
        widget.setLayout(layout)

    """
    setupList(self)

        Description: The function used to create the steps list on the GUI. Reads steps from file, associates
                 them, then adds the steps (and substeps) to the GUI in order.
    """

    def setupList(self):
        try:
            self.associateSteps()

            self.currentStep = self.steps[0]

            if not self.currentStep.getHasCheckbox():
                self.getNextStep()

            row = 0

            for step in self.steps:
                self.addStep(step, self.stepsWidget, self.layout, row)
                row += 1

                substeps = step.getSubsteps()
                if len(substeps) > 0:
                    widget = QtWidgets.QWidget(self.stepsWidget)
                    widget.setObjectName(f"SubstepWidget_{row}")
                    layout = QtWidgets.QGridLayout(widget)
                    layout.setObjectName(f"SubstepLayout_{row}")
                    layout.setContentsMargins(5, 0, 5, 0)
                    layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
                    self.layout.addWidget(widget, row, 1, 1, 2)

                    for substep in substeps:
                        self.addStep(substep, widget, layout, row)
                        row += 1

            # verticalSpacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            # self.layout.addItem(verticalSpacer, 6, 0, QtCore.Qt.AlignTop)
        except Exception as e:
            logger.info("Unable to read steps list")

    """
    getStep(self, number)

        Description: Function to find the step with the given number.

        Parameter: number - Integer giving the step number to be found.

        Returns: Step object with the given step number.
    """

    def getStep(self, number):
        try:
            self.steps[int([step.getNumber() for step in self.steps].index(number))]
        except Exception:
            logger.info("Invalid step number")

    """
    getNextCheckbox(self)

        Description: Finds the next checkbox, if it exists.

        Returns: A QCheckBox object of the next checkbox in the linked list, or None
             if it is the last checkbox.
    """

    def getNextCheckbox(self):
        nextStep = self.currentStep.getNext()

        while nextStep != None:
            if nextStep.getHasCheckbox():
                return nextStep.getCheckbox()
            else:
                nextStep = nextStep.getNext()

        return None

    """
    getCurrentStep(self)

        Description: Gets the the current step. Technically, this is not the current step,
                    but the next step to be checked off (skipping steps without checkboxes).
        
        Returns: A Step object corresponding to the current step.
    """

    def getCurrentStep(self):
        return self.currentStep

    """
    getNextStep(self)

        Description: Gets the next step with a checkbox in the linked list.

        Returns: Step object corresponding to the next step with a checkbox,
             or None if no such object exists.
    """

    def getNextStep(self):
        nextStep = self.currentStep.getNext()

        while nextStep != None:
            if nextStep.getHasCheckbox():
                self.currentStep = nextStep
                return
            else:
                nextStep = nextStep.getNext()

        self.currentStep = None
    
    def setNextStep(self, step):
        self.currentStep = step
        return self.currentStep

    """
    allStepsChecked(self)

        Description: Function to test whether all step checkboxes have been checked off.
                    Used to toggle between pausing and finishing the GUI. Replaces the
                    old function in the panel GUI class.
        
        Returns: Boolean True if all steps are checked, False otherwise.
    """

    def allStepsChecked(self):
        # return if currently in a methane testing session
        if self.ui.submit_methane_session.text() != 'Start Testing Session':
            return
        
        checked = []

        step = self.steps[0]

        while step != None:
            if step.getHasCheckbox():
                checked.append(step.getCheckbox().isChecked())

            step = step.getNext()

        return all(checked)

    """
    deleteList(self)

        Description: Deletes the step list from the GUI, freeing the memory. Used when
                 the GUI is reset, so that a new day's steps can be shown without
                 issue.
    """

    def deleteList(self):
        self.Steps.setParent(None)
        # self.Steps.deleteLater()
