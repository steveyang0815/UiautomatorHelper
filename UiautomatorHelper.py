# -*- coding: utf-8 -*-
# File: UiautomatorHelper.py
# Author: Ronggao Yang
# Created Date: 2019/4/1 19:51
# Environment: Python3.6
# Description: A program like Android Uiautomator Viewer by Python pyqt5

import sys, os, time, subprocess, traceback

try:
    from PyQt5.QtWidgets import QDialog, QHeaderView, QAbstractItemView , QMenu, QFileDialog, QMainWindow, QMessageBox, \
        QAction, QToolBar,QTableWidget,QGroupBox,QLineEdit, QApplication, QWidget, QFrame, QHBoxLayout, QPushButton, \
        QTreeWidget, QSplitter, QLabel, QTableView, QTreeWidgetItem, QVBoxLayout, QBoxLayout
except:
    print("PyQt5 installing...")
    subprocess.run('pip install -U PyQt5')
    from PyQt5.QtWidgets import QDialog, QHeaderView, QAbstractItemView, QMenu, QFileDialog, QMainWindow, QMessageBox, \
        QAction, QToolBar, QTableWidget, QGroupBox, QLineEdit, QApplication, QWidget, QFrame, QHBoxLayout, QPushButton, \
        QTreeWidget, QSplitter, QLabel, QTableView, QTreeWidgetItem, QVBoxLayout, QBoxLayout

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QPixmap, QStandardItem, QIcon, QCursor

try:
    import uiautomator2 as u2
except:
    print("uiautomator2 installing...")
    subprocess.run('pip install -U uiautomator2')
    import uiautomator2 as u2

try:
    import pyperclip
except:
    subprocess.run('pip install pyperclip')
    import pyperclip



class myApp(QMainWindow):


    def __init__(self):
        """Init Application"""
        super(myApp, self).__init__()
        self.initUI()

    def initUI(self):
        """Init UI widgets"""

        # set window title
        self.setWindowTitle("Uiautomator Helper")

        # Add toolbar
        self.toolbar = self.addToolBar("toolbar")

        # Add icon and action: open
        openAction = QAction(QIcon('open.png'), 'Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.triggered.connect(self.load_files) # Load local UI screenshot and UI xml
        self.toolbar.addAction(openAction)

        # Add icon and action: Device Screenshot
        dumpAction = QAction(QIcon('dump.png'), 'Device Screenshot', self)
        dumpAction.setShortcut('Ctrl+D')
        dumpAction.triggered.connect(self.dump_files) # Get screenshot and uiautomator dump from device
        self.toolbar.addAction(dumpAction)

        # Add icon and action: save screenshot and uiautomator dump
        saveAction = QAction(QIcon('save.jpg'), 'Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.triggered.connect(self.save_files) # Save screenshot and uiautomator dump
        self.toolbar.addAction(saveAction)

        # Main application screen
        cw = QWidget()
        hbox = QHBoxLayout()

        # Screen layout: left and right,  top and bottom for right part
        self.leftFrame = QFrame()
        self.leftFrame.resize(200,400)
        self.leftFrame.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.rightTop = QFrame()
        self.rightTop.resize(200, 200)
        self.rightTop.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.rightBottom = QFrame()
        self.rightBottom.resize(200, 200)
        self.rightBottom.setFrameStyle(QFrame.Box | QFrame.Raised)

        # Use QSplitter to seperate right part
        splitter1 = QSplitter(Qt.Vertical)
        splitter1.addWidget(self.rightTop)
        splitter1.addWidget(self.rightBottom)

        # Use QSplitter to seperate to left and right
        splitter2 = QSplitter(Qt.Horizontal)
        splitter2.addWidget(self.leftFrame)
        splitter2.addWidget(splitter1)

        # Add to main application layout
        hbox.addWidget(splitter2)
        splitter1.resize(200, 400)
        splitter2.resize(400, 400)

        # Add label to left frame for screenshot display
        self.img = QLabel(self.leftFrame)  # Use to show screenshot
        self.mark = QLabel(self.leftFrame)  # Use to mark clicked element
        self.leftFrame.setMinimumSize(120,160)

        # Add layout for label
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.img)

        # Set central widget for application
        cw.setLayout(hbox)
        self.setCentralWidget(cw)

        # load_first_time == True, not load XML
        self.load_first_time = True
        # Display default image
        self.uipng = 'dump.png'
        # Display default image
        self.display_img()

        # Add buttons, lineEdit, point info label to right top frame
        # Expand All button
        self.expandAllBtn = QPushButton()
        self.expandAllBtn.setText("+")
        self.expandAllBtn.setFixedWidth(30)
        self.expandAllBtn.setToolTip("Expand All")

        # Previous button
        self.preBtn = QPushButton()
        self.preBtn.setFixedWidth(30)
        self.preBtn.setText("<")
        self.preBtn.setToolTip("Previous Node")

        # Next button
        self.nextBtn = QPushButton()
        self.nextBtn.setFixedWidth(30)
        self.nextBtn.setText(">")
        self.nextBtn.setToolTip("Next Node")

        # Mouse point location information
        self.pointInfo = QLabel()
        self.pointInfo.resize(200, 10)
        self.pointInfo.setText("(0,0)")

        # Add widgets to layout
        oprBox = QHBoxLayout()
        oprBox.setContentsMargins(0, 5, 5, 0)
        oprBox.addWidget(self.expandAllBtn)
        oprBox.addWidget(self.preBtn)
        oprBox.addWidget(self.nextBtn)
        oprBox.addWidget(self.pointInfo)
        oprBox.addStretch()

        # Use operation frame to contain operation layout
        operation = QFrame()
        operation.setLayout(oprBox)

        # Add treewidget for all Nodes
        self.tree = QTreeWidget()
        self.tree.header().setVisible(False)

        # Use QVBoxLayout to contain operation frame and tree widget
        vbox = QVBoxLayout()
        vbox.setContentsMargins(10, 5, 5, 5)
        vbox.addWidget(operation)
        vbox.addWidget(self.tree)

        # Set as right top frame layout
        self.rightTop.setLayout(vbox)

        # Add groupbox widget to right bottom frame
        groupBox = QGroupBox()
        groupBox.setTitle("Node Detail")
        groupBox.setContentsMargins(0, 5, 0, 0)

        # Add TableView
        self.props = QTableView()

        # Add tableView to layout
        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.props)

        # Set groupBox layout
        groupBox.setLayout(hbox2)

        # Add groupBox to layout
        vbox2 = QVBoxLayout()
        vbox2.setContentsMargins(5, 5, 5, 5)
        vbox2.addWidget(groupBox)

        # Set layout for right bottom frame
        self.rightBottom.setLayout(vbox2)

        # Set signal for botton
        self.expandAllBtn.clicked.connect(self.tree.expandAll)
        self.preBtn.clicked.connect(self.pre_node)
        self.nextBtn.clicked.connect(self.next_node)

        # Init focus index for treeview
        self.focus_index = None
        self.resize(700, 500)


    def load_files(self):
        """Dialog to load existed screenshot and uiautomator dump"""
        self.dialog = QDialog()
        self.dialog.setWindowTitle("Open UI Dump Files")
        self.dialog.setFixedSize(350, 200)

        vbox = QVBoxLayout()

        gb1 = QGroupBox()
        gb1.setTitle("Screenshot")

        hb1 = QHBoxLayout()
        self.le1 = QLineEdit()  # To save screenshot path
        self.le1.setFixedHeight(22)
        self.le1.setEnabled(False)
        bt1 = QPushButton()
        bt1.setFixedSize(30, 20)
        bt1.setText("...")
        hb1.addWidget(self.le1)
        hb1.addWidget(bt1)
        gb1.setLayout(hb1)

        gb2 = QGroupBox()
        gb2.setTitle("UI XML Dunp")

        hb2 = QHBoxLayout()
        self.le2 = QLineEdit()  # To save uiautomator dump path
        self.le2.setFixedHeight(22)
        self.le2.setEnabled(False)
        bt2 = QPushButton()
        bt2.setFixedSize(30, 20)
        bt2.setText("...")
        hb2.addWidget(self.le2)
        hb2.addWidget(bt2)
        gb2.setLayout(hb2)

        vbox.addWidget(gb1)
        vbox.addWidget(gb2)

        f = QFrame()

        hb3 = QHBoxLayout()
        self.okbtn = QPushButton()
        self.okbtn.setText("OK")
        self.cancelbtn = QPushButton()
        self.cancelbtn.setText('Cancel')

        self.okbtn.setEnabled(False)

        self.okbtn.setFixedSize(100, 25)
        self.cancelbtn.setFixedSize(100, 25)

        hb3.addStretch()
        hb3.addWidget(self.okbtn)
        hb3.addWidget(self.cancelbtn)

        f.setLayout(hb3)
        vbox.addWidget(f)
        self.dialog.setLayout(vbox)

        # Set button signal
        bt1.clicked.connect(self.select_screenshot)
        bt2.clicked.connect(self.select_dump)
        self.okbtn.clicked.connect(self.open_files)
        self.cancelbtn.clicked.connect(self.dialog.close)

        self.dialog.resize(400, 200)
        self.dialog.exec_()

    def select_screenshot(self):
        """Select screenshot"""
        if len(self.le1.text()) > 0:
            path = os.path.split(self.le1.text())[0]
        elif len(self.le2.text()) > 0:
            path = os.path.split(self.le2.text())[0]
        else:
            path = "/"
        fname = QFileDialog.getOpenFileName(self, caption='Open File', directory=path, filter="*.png;*.jpg;*.jpeg;*.bmp")
        if fname[0]:
            self.le1.setText(fname[0])
        if len(self.le1.text())>0 and len(self.le2.text())>0:
            self.okbtn.setEnabled(True)

    def select_dump(self):
        """Select uiautomator dump"""
        if len(self.le1.text()) > 0:
            path = os.path.split(self.le1.text())[0]
        elif len(self.le2.text()) > 0:
            path = os.path.split(self.le2.text())[0]
        else:
            path = "/"
        fname = QFileDialog.getOpenFileName(self, caption='Open File', directory=path, filter="*.xml;*.uix")
        if fname[0]:
            self.le2.setText(fname[0])
        if len(self.le1.text())>0 and len(self.le2.text())>0:
            self.okbtn.setEnabled(True)

    def open_files(self):
        """Open and load files from existed screenshot and uiautomator dump"""
        self.device = None
        try:
            self.dialog.close()
            self.load_first_time = False
            self.uipng = None
            self.uipng = QPixmap(self.le1.text())  # Set current screenshot file
            self.display_img()  # Display screenshot
            self.uix_update(self.le2.text())  # Update uiautomator dump file
            self.get_all_elements(self.le2.text())  # Get all elements from uiautomator dump
        except:
            QMessageBox.critical(self, "Exception",
                                 "Load files error:\n" + traceback.format_exc(),
                                 QMessageBox.Ok)

    def dump_files(self):
        """Load screenshot and uiautomator dump from device"""
        try:
            self.device = u2.connect()
            subprocess.run("adb shell screencap /sdcard/ui.png")
            # subprocess.run("adb shell uiautomator dump /sdcard/ui.uix")
            subprocess.run("adb pull /sdcard/ui.png ui.png")
            # subprocess.run("adb pull /sdcard/ui.uix ui.uix")
            with open('ui.uix', 'w', encoding='utf-8') as f:
                self.xml = self.device.dump_hierarchy()
                f.write(self.xml)
            self.uix_update()
            if os.path.exists('ui.png') and os.path.exists('ui.uix'):
                self.uipng = 'ui.png' # Set current screenshot file
                self.load_first_time = False
                self.display_img() # Display screenshot
                self.get_all_elements('ui.uix') # Get all elements from uiautomator dump
            else:
                QMessageBox.critical(self, "Exception", "Load screenshot and uiautomator dump failed.\n"+traceback.format_exc(), QMessageBox.Ok)
        except Exception as e:
            print(traceback.format_exc())
            QMessageBox.critical(self, "Exception", "Get screenshot and uiautomator dump error, need connect only "
                                                    "one device to computer.\n"+traceback.format_exc()
                                                    , QMessageBox.Ok)

    def save_files(self):
        """Save screenshot and uiautomator dump"""
        try:
            self.device = u2.connect()
            dir_path = QFileDialog.getExistingDirectory(self, "Choose Directory", '/')
            if len(dir_path) == 0:
                print("No dir path selected")
                return
            tmp = time.strftime("%Y%m%d%H%M%S",time.localtime())  # Generate time stamp for file name

            # Save screenshot
            subprocess.run("adb shell screencap /sdcard/ui.png")  # Capture screenshot and save to phone
            subprocess.run("adb pull /sdcard/ui.png " + dir_path + "/dump_" + str(tmp) + ".png")  # Pull in screenshot

            # Save uiautomator dump  ----Methor 1
            # subprocess.run("adb shell uiautomator dump /sdcard/ui.uix")
            # subprocess.run("adb pull /sdcard/ui.uix " + dir_path + "/dump_" + str(tmp) + ".uix")
            # self.uix_update(dir_path + "/dump_" + str(tmp) + ".uix")

            # Save uiautomator dump  ----Methor 2 , this methor contains much more elements than Methor 1
            with open(dir_path + "/dump_" + str(tmp) + ".uix", 'w', encoding='utf-8') as f:
                self.xml = self.device.dump_hierarchy()  # Get uiautomator dump
                f.write(self.xml)

            QMessageBox.information(self, "Saved", "Save screenshot and uiautomator dump successfully:\n" +
                                    dir_path + "/dump_" + str(tmp) + ".png\n" + dir_path + "/dump_" + str(tmp) + ".uix"
                                 , QMessageBox.Ok)
        except:
            QMessageBox.critical(self, "Exception", "Save screenshot and uiautomator dump failed.\n" +
                                 traceback.format_exc(), QMessageBox.Ok)

    def mousePressEvent(self, event):
        """Get clicked point information"""
        if self.load_first_time: # Not load image yet
            return
        # Ajust point location according screenshot location
        x = event.x() - 10
        y = event.y() - 43
        if x < self.w and y < self.h:
            # Map to point in screenshot original size
            m = int(x * self.rate)
            n = int(y * self.rate)
            self.pointInfo.setText("({},{})".format(m,n))
            self.get_point_info(m,n)

    def resizeEvent(self, event):
        """Window resize event"""
        self.display_img()  # Update screenshot display
        self.draw_rect(self.focus_index)  # update marked rect

    def display_img(self):
        """Load and display screenshot"""
        try:
            self.pic = QPixmap(self.uipng)
            if self.load_first_time: # Load application first time, display default image
                self.img.setPixmap(self.pic)
                self.img.resize(self.pic.size())
                self.img.setScaledContents(True)
                self.img.update()
                return
            self.pic_h = self.pic.height()
            self.pic_w = self.pic.width()
            # Get zoom out/in rate for screenshot to fit for left frame
            if self.pic_h >= self.pic_w:
                self.rate = self.pic_h / self.leftFrame.height()
            else:
                self.rate = self.pic_w / self.leftFrame.width()
            self.h = self.pic_h / self.rate
            self.w = self.pic_w / self.rate
            self.img.setPixmap(self.pic)
            self.img.resize(self.w,self.h)  # Set screenshot size to fit for left frame
            self.img.setScaledContents(True)
            self.img.update()
        except Exception as e:
            print(e)
            print(traceback.format_exc())


    def get_all_elements(self, uix='ui.uix'):
        """Get all elements"""

        if self.load_first_time:
            return
        try:
            print('Get all elements')
            with open(uix,'r',encoding='utf-8') as f:
                self.uix = f.read()
            xml = self.uix

            self.elements = []
            i = xml.count("<node ")
            start = xml.find("<node ") + 6
            end = xml.find(">", start)
            while i > 0:
                d = {}
                if xml[end - 1] != "/":
                    s = xml[start:end]
                else:
                    s = xml[start:end - 1]
                s = s.strip()
                t = s.split('" ')
                for item in t:
                    p = item.split("=")
                    k = p[0]
                    v = p[1].strip('"').replace("&amp;","&") 
                    d[k] = v  # Add element's properties to dict
                d['xpath'] = ""
                d['fullIndexXpath'] = ""
                d['uiaSelector'] = ""
                d['indicator'] = ""
                self.elements.append(d)
                start = xml.find("<node ", end) + 6
                end = xml.find(">", start)
                i -= 1

            for ele in self.elements:
                flag = [False,False,False,False]
                # Get uiautomator indicator: description < text < className < resourceId
                # uiautomator indicator: for example self.device(indicator) can locate to single element
                if len(ele['content-desc']) > 0:
                    found_item = 0
                    for item in self.elements:
                        if item['content-desc'] == ele['content-desc']:
                            found_item += 1
                    if found_item == 1:
                        flag[0] = True
                        ele['indicator'] = 'description=\"{}\"'.format(ele['content-desc'])
                        ele['uiaSelector'] = 'new UiSelector().description(\"{}\")'.format(ele['content-desc'])
                if len(ele['text']) > 0:
                    found_item = 0
                    for item in self.elements:
                        if item['text'] == ele['text']:
                            found_item += 1
                    if found_item == 1:
                        flag[1] = True
                        ele['indicator'] = 'text=\"{}\"'.format(ele['text'])
                        ele['uiaSelector'] = 'new UiSelector().textContains(\"{}\")'.format(ele['text'])
                if len(ele['class']) > 0:
                    found_item = 0
                    for item in self.elements:
                        if item['class'] == ele['class']:
                            found_item += 1
                    if found_item == 1:
                        flag[2] = True
                        ele['indicator'] = 'className=\"{}\"'.format(ele['class'])
                        ele['uiaSelector'] = 'new UiSelector().className(\"{}\")'.format(ele['class'])
                if len(ele["resource-id"]) > 0:
                    found_item = 0
                    for item in self.elements:
                        if item['resource-id'] == ele['resource-id']:
                            found_item += 1
                    if found_item == 1:
                        flag[3] = True
                        ele['indicator'] = 'resourceId=\"{}\"'.format(ele['resource-id'])
                        ele['uiaSelector'] = 'new UiSelector().resourceId(\"{}\")'.format(ele['resource-id'])

                # Get xpath
                if flag[3]: # resourceId is indicator
                    ele['xpath'] = '//' + ele['class'] + '[@resource-id=\"{}\"]'.format(ele['resource-id'])
                elif flag[2]: # className is indicator
                    ele['xpath'] = '//' + ele['class']
                else:
                    if len(ele['text']) > 0 and len(ele['content-desc']) > 0:
                        ele['xpath'] = '//' + ele['class'] + '[@text=\"{}\" and @content-desc=\"{}\"]'.format(
                            ele['text'],ele['content-desc'])
                    if len(ele['text']) > 0 and len(ele['content-desc']) == 0:
                        ele['xpath'] = '//' + ele['class'] + '[@text=\"{}\"]'.format(ele['text'])
                    if len(ele['text']) == 0 and len(ele['content-desc']) > 0:
                        ele['xpath'] = '//' + ele['class'] + '[@content-desc=\"{}\"]'.format(ele['content-desc'])

                # Get uiaSelector
                if ele['indicator'] == "":
                    if len(ele['resource-id']) > 0:
                        if len(ele['text']) > 0:
                            ele['uiaSelector'] = 'new UiSelector().className(\"{}\").textContains(\"{}\").resourceId(' \
                                                 '\"{}\")'.format(ele['class'], ele['text'], ele['resource-id'])
                        else:
                            ele['uiaSelector'] = 'new UiSelector().className(\"{}\").resourceId(' \
                                                 '\"{}\")'.format(ele['class'], ele['resource-id'])
                    else:
                        if len(ele['text']) > 0:
                            ele['uiaSelector'] = 'new UiSelector().className(\"{}\").textContains(\"{}\")'.format(
                                ele['class'], ele['text'])

            print("Get all elements done ", len(self.elements))
        except Exception as e:
            print(e)
            print(traceback.format_exc())
        self.get_nodes()

    def get_point_info(self, x, y):
        """Get element index according to clicked point location"""
        i = 0
        self.focus_index = -1
        s = self.pic_h * self.pic_w
        found_index = None
        for item in self.elements:
            bounds = item['bounds']
            left = int(bounds[bounds.find("[") + 1:bounds.find(",")])
            top = int(bounds[bounds.find(",") + 1:bounds.find("][")])
            right = int(bounds[bounds.find("][") + 2:bounds.find(",", bounds.find("]["))])
            bottom = int(bounds[bounds.find(",", bounds.find("]["))+1:bounds.find("]", bounds.find("][") + 3)])
            # Check whether clicked point is internal point of element
            if left <= x <= right and top <= y <= bottom:
                new_s = (right - left) * (bottom - top)  # Area
                if new_s <= s:  # Check whether minimum area
                    s = new_s
                    found_index = i
                    self.focus_index = i
            i += 1
        # print("found:",found_index)
        self.draw_rect(found_index)
        self.setItemSelected(found_index)

    def draw_rect(self,i):
        """Draw rectangle by element index"""
        print('Draw found item ', i)
        if i is not None:
            self.mark.setVisible(True)
        else:
            # print('Not found item')
            return
        # print(self.elements)
        # print(self.elements[i]['bounds'])
        bounds = self.elements[i]['bounds']
        left = int(bounds[bounds.find("[") + 1:bounds.find(",")])-2
        top = int(bounds[bounds.find(",") + 1:bounds.find("][")])-2
        right = int(bounds[bounds.find("][") + 2:bounds.find(",", bounds.find("]["))])+2
        bottom = int(bounds[bounds.find(",", bounds.find("][")) + 1:bounds.find("]", bounds.find("][") + 3)])+2
        if left < 0:
            left = 0
        if top < 0:
            top = 0
        if right > self.pic_w:
            right = self.pic_w
        if bottom > self.pic_h:
            bottom = self.pic_h
        # print(left,right,top,bottom)
        self.mark.setFrameShape(QFrame.Box)
        self.mark.setGeometry(left / self.rate, top / self.rate, right / self.rate - left / self.rate, bottom / self.rate - top / self.rate)
        self.mark.setLineWidth(2)
        self.mark.setStyleSheet('color: rgb(255, 0, 0)')
        self.mark.show()
        self.mark.update()
        # Set table widget layout
        self.props.horizontalHeader().setStretchLastSection(True)
        self.get_props(i)

    def setItemSelected(self,i):
        """Set item selected by index"""
        if i is not None:
            self.tree.setCurrentItem(self.item_list[i])


    def get_props(self,i):
        """Get element properties by element index and display in table widget"""
        ele = self.elements[i]
        print(ele)
        self.prolist = []
        for item in ele:
            self.prolist.append(item)
        self.model = QStandardItemModel(len(self.prolist), 2)
        self.model.setHorizontalHeaderLabels(['Property', 'Value'])
        for row in range(len(self.prolist)):
            for column in range(2):
                if column == 0:
                    item = QStandardItem(self.prolist[row])
                    # Set first column as properties name
                    self.model.setItem(row, column, item)
                    item.setEditable(False)
                if column == 1:
                    item =QStandardItem(ele[self.prolist[row]])
                    # Set second column as properties value
                    self.model.setItem(row, column, item)
        self.props.setModel(self.model)
        for k in range(len(self.prolist)):
	    if k != len(self.prolist) - 3:
                self.props.setRowHeight(k, 3)
	    else:
		self.props.setRowHeight(k, 50)
        self.props.update()


    def get_nodes(self):
        """Get nodes information"""
        if self.tree.topLevelItemCount() > 0:
            self.tree.clearSelection()
            self.tree.clear()
        self.tree.setColumnCount(1)
        root = QTreeWidgetItem(self.tree)
        self.eles = []
        self.item_list = []
        i = 0
        self.top = [] # Save top node class
		self.topn = {} # Save top node index
        # Get nodes information
        for line in self.uix.split("\n"):
            if line.find("<node ") != -1:
                if line.find("android.widget.TextView") != -1:
                    sp = ":"
                else:
                    sp=" "
                if line.find("checkable")-line.find("content-desc") > 16:
                    cd = " {" + self.elements[i]["content-desc"] + "} "
                else:
                    cd = ""
                #  Get node index, node level, node information to display
                self.eles.append([i, line.find("<node ")/2, "(" + self.elements[i]['index']+") "+ \
                             self.elements[i]['class'].split("android.widget.")[-1] + sp + self.elements[i]['text'] + \
                                  cd + " " + self.elements[i]['bounds']])
                if line.find("<node ")/2 == 1: # Top node				
                    self.top.append(self.elements[i]['class'])
                    c = self.top.count(self.elements[i]['class'])
                    self.topn[str(i)] = str(c) # Add top node index
                i+=1

        # Add nodes to tree
        for n in range(len(self.eles)):
            if self.eles[n][1] == 1:
                child1 = QTreeWidgetItem(root)
                child1.setText(0,self.eles[n][2])  # use for item string
                child1.setText(1,str(n))  # use for item indicator
                self.item_list.append(child1)
            elif self.eles[n][1] == 2:
                child2 = QTreeWidgetItem(child1)
                child2.setText(0, self.eles[n][2])
                child2.setText(1, str(n))
                self.item_list.append(child2)
            elif self.eles[n][1] == 3:
                child3 = QTreeWidgetItem(child2)
                child3.setText(0, self.eles[n][2])
                child3.setText(1, str(n))
                self.item_list.append(child3)
            elif self.eles[n][1] == 4:
                child4 = QTreeWidgetItem(child3)
                child4.setText(0, self.eles[n][2])
                child4.setText(1, str(n))
                self.item_list.append(child4)
            elif self.eles[n][1] == 5:
                child5 = QTreeWidgetItem(child4)
                child5.setText(0, self.eles[n][2])
                child5.setText(1, str(n))
                self.item_list.append(child5)
            elif self.eles[n][1] == 6:
                child6 = QTreeWidgetItem(child5)
                child6.setText(0, self.eles[n][2])
                child6.setText(1, str(n))
                self.item_list.append(child6)
            elif self.eles[n][1] == 7:
                child7 = QTreeWidgetItem(child6)
                child7.setText(0, self.eles[n][2])
                child7.setText(1, str(n))
                self.item_list.append(child7)
            elif self.eles[n][1] == 8:
                child8 = QTreeWidgetItem(child7)
                child8.setText(0, self.eles[n][2])
                child8.setText(1, str(n))
                self.item_list.append(child8)
            elif self.eles[n][1] == 9:
                child9 = QTreeWidgetItem(child8)
                child9.setText(0, self.eles[n][2])
                child9.setText(1, str(n))
                self.item_list.append(child9)
            elif self.eles[n][1] == 10:
                child10 = QTreeWidgetItem(child9)
                child10.setText(0, self.eles[n][2])
                child10.setText(1, str(n))
                self.item_list.append(child10)
            elif self.eles[n][1] == 11:
                child11 = QTreeWidgetItem(child10)
                child11.setText(0, self.eles[n][2])
                child11.setText(1, str(n))
                self.item_list.append(child11)
            elif self.eles[n][1] == 12:
                child12 = QTreeWidgetItem(child11)
                child12.setText(0, self.eles[n][2])
                child12.setText(1, str(n))
                self.item_list.append(child12)
            elif self.eles[n][1] == 13:
                child13 = QTreeWidgetItem(child12)
                child13.setText(0, self.eles[n][2])
                child13.setText(1, str(n))
                self.item_list.append(child13)
            elif self.eles[n][1] == 14:
                child14 = QTreeWidgetItem(child13)
                child14.setText(0, self.eles[n][2])
                child14.setText(1, str(n))
                self.item_list.append(child14)
            elif self.eles[n][1] == 15:
                child15 = QTreeWidgetItem(child14)
                child15.setText(0, self.eles[n][2])
                child15.setText(1, str(n))
                self.item_list.append(child15)
            elif self.eles[n][1] == 16:
                child16 = QTreeWidgetItem(child15)
                child16.setText(0, self.eles[n][2])
                child16.setText(1, str(n))
                self.item_list.append(child16)
            elif self.eles[n][1] == 17:
                child17 = QTreeWidgetItem(child16)
                child17.setText(0, self.eles[n][2])
                child17.setText(1, str(n))
                self.item_list.append(child17)
            elif self.eles[n][1] == 18:
                child18 = QTreeWidgetItem(child17)
                child18.setText(0, self.eles[n][2])
                child18.setText(1, str(n))
                self.item_list.append(child18)
            elif self.eles[n][1] == 19:
                child19 = QTreeWidgetItem(child18)
                child19.setText(0, self.eles[n][2])
                child19.setText(1, str(n))
                self.item_list.append(child19)
            elif self.eles[n][1] == 20:
                child20 = QTreeWidgetItem(child19)
                child20.setText(0, self.eles[n][2])
                child20.setText(1, str(n))
                self.item_list.append(child20)
            elif self.eles[n][1] == 21:
                child21 = QTreeWidgetItem(child20)
                child21.setText(0, self.eles[n][2])
                child21.setText(1, str(n))
                self.item_list.append(child21)
            elif self.eles[n][1] == 22:
                child22 = QTreeWidgetItem(child21)
                child22.setText(0, self.eles[n][2])
                child22.setText(1, str(n))
                self.item_list.append(child22)
            elif self.eles[n][1] == 23:
                child23 = QTreeWidgetItem(child22)
                child23.setText(0, self.eles[n][2])
                child23.setText(1, str(n))
                self.item_list.append(child22)
            elif self.eles[n][1] == 24:
                child24 = QTreeWidgetItem(child23)
                child24.setText(0, self.eles[n][2])
                child24.setText(1, str(n))
                self.item_list.append(child22)
            elif self.eles[n][1] == 25:
                child25 = QTreeWidgetItem(child24)
                child25.setText(0, self.eles[n][2])
                child25.setText(1, str(n))
                self.item_list.append(child22)
            elif self.eles[n][1] == 26:
                child26 = QTreeWidgetItem(child25)
                child26.setText(0, self.eles[n][2])
                child26.setText(1, str(n))
                self.item_list.append(child22)
            elif self.eles[n][1] == 27:
                child27 = QTreeWidgetItem(child26)
                child27.setText(0, self.eles[n][2])
                child27.setText(1, str(n))
                self.item_list.append(child22)
            elif self.eles[n][1] == 28:
                child28 = QTreeWidgetItem(child27)
                child28.setText(0, self.eles[n][2])
                child28.setText(1, str(n))
                self.item_list.append(child22)
            elif self.eles[n][1] == 29:
                child29 = QTreeWidgetItem(child28)
                child29.setText(0, self.eles[n][2])
                child29.setText(1, str(n))
                self.item_list.append(child22)
            elif self.eles[n][1] == 30:
                child30 = QTreeWidgetItem(child29)
                child30.setText(0, self.eles[n][2])
                child30.setText(1, str(n))
                self.item_list.append(child22)
            elif self.eles[n][1] == 31:
                child31 = QTreeWidgetItem(child30)
                child31.setText(0, self.eles[n][2])
                child31.setText(1, str(n))
                self.item_list.append(child22)

        self.tree.show()
        self.tree.itemClicked.connect(self.itemClick)
        self.tree.update()

        # Get fullIndexXpath
        for i in range(len(self.item_list)):
            item = self.item_list[i]
            # print(item.text(1),item.text(0))
            xp = []
            idx = []
            while (item is not None):
                xp.append(item.text(1))
                idx.append(item.text(0))
                item = item.parent()

            self.elements[i]['fullIndexXpath'] = "/"
            xp.pop()
            idx.pop()
            # print(xp,idx)
            j = int(xp[0])
            k = int(xp.pop())
            v = self.topn[str(k)]  # Get the top node index
            self.elements[j]['fullIndexXpath'] = self.elements[j]['fullIndexXpath'] + "/" + self.elements[k]['class'] + "[" + v + "]"
            while (len(xp) > 0):
                k = int(xp.pop())
                # print(k)
                x = idx.pop()
                v = x[1:x.find(")")]
                v = int(v) + 1
                self.elements[j]['fullIndexXpath'] = self.elements[j]['fullIndexXpath'] + "/" + self.elements[k]['class'] + "[" + str(v) + "]"


    def itemClick(self, item):
        """Table Widget item click event"""
        i = int(item.text(1))
        # print("index ", i)
        # print("text ", item.text(0))
        self.focus_index = i
        self.draw_rect(i)

    def pre_node(self):
        """Switch to previous node/element"""
        try:
            print('Previous node')
            if self.load_first_time:
                return
            if self.focus_index is None:
                self.focus_index = 1

            self.focus_index = self.focus_index - 1
            if self.focus_index < 0:
                self.focus_index = len(self.elements) - 1

            i = self.focus_index
            self.draw_rect(i)
            self.setItemSelected(i)
        except Exception as e:
            print(e)
            print(traceback.format_exc())

    def next_node(self):
        """Switch to next node/element"""
        try:
            print('Next node')
            if self.load_first_time:
                return
            if self.focus_index is None:
                self.focus_index = -1
            self.focus_index = self.focus_index + 1
            if self.focus_index >= len(self.elements):
                self.focus_index = 0
            i = self.focus_index
            self.draw_rect(i)
            self.setItemSelected(i)
        except Exception as e:
            print(e)
            print(traceback.format_exc())

    def uix_update(self, uix='ui.uix'):
        """Update uiautomator dump file, add enter and necessary spaces"""
        with open(uix, 'r', encoding='utf-8') as f:
            xml = f.readlines()
        if len(xml) < 3: # only one or two lines, if use 'adb shell uiautomator dump /sdcard/ui.uix' then pull in ui.uix, need check uix
            x = xml[0].replace(">", ">\n")
            os.remove(uix)
            with open(uix, 'w', encoding='utf-8') as f:
                f.write(x)
            with open(uix, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            with open(uix, 'w', encoding='utf-8') as f:
                i = 0
                s = False
                for line in lines:
                    if line.find("<node") != -1:
                        if s:
                            line = " " * i + line
                            s = False
                        else:
                            i = i + 2
                            line = " " * i + line
                        if line[-3:-2] == "/":
                            s = True
                    if line.find("</node>") != -1:
                        i = i - 2
                        line = " " * i + line
                    f.write(line + "\n")

if __name__ == '__main__':
    app=QApplication(sys.argv)
    demo=myApp()
    demo.show()
    sys.exit(app.exec_())
