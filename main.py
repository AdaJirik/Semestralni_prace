import sys
import os
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolButton, QFrame, QWidget, QHBoxLayout, QVBoxLayout, \
    QGridLayout, QGraphicsDropShadowEffect, QLabel, QSpacerItem, QSizePolicy, QGraphicsEllipseItem, QLineEdit, \
    QComboBox, QTableView, QSlider
from PyQt5.QtGui import QIcon, QCursor, QStandardItemModel, QStandardItem, QColor
from PyQt5.QtCore import Qt, QSize, QEvent, QThread, pyqtSignal
import pyqtgraph as pg
import asyncio
import websockets
import json
import csv
from datetime import timedelta, datetime



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CESA Floorball Analyzer DEMO")
        self.geom = self.setGeometry(480, 220, 960, 540)
        self.images = self.make_img_dict("img_Lib")
        self.setWindowIcon(QIcon(self.images["cesa.png"]))
        self.central_widget = None
        self.layout = None
        self.show_home_screen()
        self.dataRec = DataRecording()

    def make_img_dict(self, folder):
        images = {}
        for img in os.listdir(folder):
            img_path = os.path.join(folder, img)
            images[img] = img_path
        return images

        ###____________  BACKGROUND  ____________###

    def make_background(self):
        self.central_widget = QWidget(self)
        self.central_widget.setObjectName("background_widget")
        self.central_widget.setStyleSheet("""QWidget#background_widget{
                                                    background-image: url(img_Lib/background-blue.jpg);
                                                    background-repeat: no-repeat;
                                                    background-position: center;
                                            }""")
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        ###____________  HOME-SCREEN  ____________###

    def make_frame(self):
        frame = QFrame(self)
        frame.setFixedSize(800, 400)
        frame.setObjectName("frame_widget")
        frame.setStyleSheet("""QWidget#frame_widget{
                                    background-color: white;
                                    border: 4px solid lightgray;
                                    border-radius: 15px;
                            }""")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(8)
        shadow.setYOffset(8)
        frame.setGraphicsEffect(shadow)
        hbox = QHBoxLayout(frame)
        return frame, hbox

    def create_session_button(self):
        session_button = QToolButton(self)
        session_button.setText("Record New Session")
        session_icon = QIcon(self.images["record.png"])
        hov_session_icon = QIcon(self.images["hover-record.png"])
        session_button.setFixedSize(300, 250)
        session_button.setIconSize(QSize(120, 120))
        session_button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        session_button.setObjectName("session_button")
        session_button.setCursor(QCursor(Qt.PointingHandCursor))
        session_button.clicked.connect(self.show_session_screen)
        self.setup_hover_icon(session_button, session_icon, hov_session_icon)
        return session_button

    def create_analysis_button(self):
        analysis_button = QToolButton(self)
        analysis_button.setText("Analysis")
        analysis_icon = QIcon(self.images["analysis.png"])
        hov_analysis_icon = QIcon(self.images["hover-analysis.png"])
        analysis_button.setFixedSize(200, 220)
        analysis_button.setIconSize(QSize(120, 120))
        analysis_button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        analysis_button.setObjectName("analysis_button")
        analysis_button.setCursor(QCursor(Qt.PointingHandCursor))
        analysis_button.clicked.connect(self.show_analysis_screen)
        self.setup_hover_icon(analysis_button, analysis_icon, hov_analysis_icon)
        return analysis_button

    def create_setting_button(self):
        setting_button = QToolButton(self)
        setting_button.setText("Settings")
        setting_icon = QIcon(self.images["settings.png"])
        hov_setting_icon = QIcon(self.images["hover-settings.png"])
        setting_button.setFixedSize(200, 220)
        setting_button.setIconSize(QSize(100, 100))
        setting_button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        setting_button.setObjectName("setting_button")
        setting_button.setCursor(QCursor(Qt.PointingHandCursor))
        setting_button.clicked.connect(self.show_setting_screen)
        self.setup_hover_icon(setting_button, setting_icon, hov_setting_icon)
        return setting_button

    def style_button(self):
        self.setStyleSheet("""
                            QToolButton{
                                font-size: 25px;
                                font-family: Arial;
                                padding: 20px 0px;
                                margin: 10px;
                                border: 3px solid;
                                border-radius: 15px;
                                border-color: #009db1;
                                background-color: #bddade;
                                text-align: center;
                            }
                            QToolButton:hover{
                                background-color: #009db1;
                                color: 'white';
                                font-weight: bold;
                            }
                            QToolButton#session_button{
                                padding: 35px 0px;
                                border-radius: 25px;
                            }
                            QToolButton#home_button{
                                padding: 0px 0px;
                                margin: 0px;
                                border-radius: 25px;
                            }
                            QToolButton#small_session_button{
                                padding: 0px 0px;
                                margin: 0px;
                                border-radius: 25px;
                            }
                            QToolButton#small_analysis_button{
                                padding: 0px 0px;
                                margin: 0px;
                                border-radius: 25px;
                            }
                            QToolButton#small_setting_button{
                                padding: 0px 0px;
                                margin: 0px;
                                border-radius: 25px;
                            }
                            QToolButton#start_button{
                                font-size: 20px;
                                padding: 0px 0px;
                                border-radius: 35px;
                            }
                            QToolButton#pause_button{
                                padding: 0px 0px;
                                border-radius: 35px;
                            }
                            QToolButton#stop_button{
                                padding: 0px 0px;
                                border-radius: 35px;
                            }
                            QToolButton#continue_button{
                                padding: 0px 0px;
                                border-radius: 35px;
                            }
                            QToolButton#function_button{
                                padding: 0px 0px;
                                margin: 0px;
                                border-radius: 20px;
                            }
                            QToolButton#fake_button{
                                padding: 0px 0px;
                                margin: 0px;
                                border-radius: 20px;
                            }
                            QToolButton#fake_button:hover{
                                background-color: #bddade;
                            }
                            QToolButton#switch_button{
                                padding: 0px 0px;
                                margin: 0px;
                                border-radius: 20px;
                            }
                        """)

        ###____________  ALL-SCREENS  ____________###

    def create_home_button(self):
        home_button = QToolButton(self)
        home_button.setFixedSize(90, 90)
        home_icon = QIcon(self.images["home.png"])
        hov_home_icon = QIcon(self.images["hover-home.png"])
        home_button.setIconSize(QSize(70, 70))
        home_button.setObjectName("home_button")
        home_button.setCursor(QCursor(Qt.PointingHandCursor))
        home_button.clicked.connect(self.show_home_screen)
        self.setup_hover_icon(home_button, home_icon, hov_home_icon)
        return home_button

    def create_small_session_button(self):
        small_session_button = QToolButton(self)
        small_session_button.setFixedSize(90, 90)
        small_session_icon = QIcon(self.images["record.png"])
        hov_small_session_icon = QIcon(self.images["hover-record.png"])
        small_session_button.setIconSize(QSize(70, 70))
        small_session_button.setObjectName("small_session_button")
        small_session_button.setCursor(QCursor(Qt.PointingHandCursor))
        small_session_button.clicked.connect(self.show_session_screen)
        self.setup_hover_icon(small_session_button, small_session_icon, hov_small_session_icon)
        return small_session_button

    def create_small_analysis_button(self):
        small_analysis_button = QToolButton(self)
        small_analysis_button.setFixedSize(90, 90)
        small_analysis_icon = QIcon(self.images["analysis.png"])
        hov_small_analysis_icon = QIcon(self.images["hover-analysis.png"])
        small_analysis_button.setIconSize(QSize(70, 70))
        small_analysis_button.setObjectName("small_analysis_button")
        small_analysis_button.setCursor(QCursor(Qt.PointingHandCursor))
        small_analysis_button.clicked.connect(self.show_analysis_screen)
        self.setup_hover_icon(small_analysis_button, small_analysis_icon, hov_small_analysis_icon)
        return small_analysis_button

    def create_small_setting_button(self):
        small_setting_button = QToolButton(self)
        small_setting_button.setFixedSize(90, 90)
        small_setting_icon = QIcon(self.images["settings.png"])
        hov_small_setting_icon = QIcon(self.images["hover-settings.png"])
        small_setting_button.setIconSize(QSize(70, 70))
        small_setting_button.setObjectName("small_setting_button")
        small_setting_button.setCursor(QCursor(Qt.PointingHandCursor))
        small_setting_button.clicked.connect(self.show_setting_screen)
        self.setup_hover_icon(small_setting_button, small_setting_icon, hov_small_setting_icon)
        return small_setting_button

    def make_headline(self, text):
        headline = QLabel(text)
        headline.setFixedHeight(90)
        headline.setObjectName("headline")
        headline.setStyleSheet("""QLabel#headline{
                                font-size: 40px;
                                font-family: Arial;
                            }
                        """)
        return headline

    def spacer(self):
        spacer = QSpacerItem(0, 0, QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        return spacer

    def make_upper_panel(self):
        up_panel = QFrame(self)
        up_panel.setGeometry(0, 0, self.width(), 100)
        up_panel.setObjectName("upper_panel_widget")
        up_panel.setStyleSheet("""QWidget#upper_panel_widget{
                                            background-color: white;
                                            border: 4px solid lightgray;
                                            border-radius: 15px;
                                    }""")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(8)
        shadow.setYOffset(8)
        up_panel.setGraphicsEffect(shadow)
        hbox = QHBoxLayout(up_panel)
        return up_panel, hbox

        ###____________  SESSION-SCREEN  ____________###

    def create_start_button(self):
        start_button = QToolButton(self)
        start_button.setFixedSize(250, 90)
        start_button.setText("Start Recording")
        start_button.setObjectName("start_button")
        start_button.setCursor(QCursor(Qt.PointingHandCursor))
        start_button.clicked.connect(self.start_session_clicked)
        start_button.clicked.connect(lambda: self.clear_layout(self.session_button_box))
        start_button.clicked.connect(lambda: self.insert_button_in_box(self.session_button_box,
                                                                       [self.create_pause_button(),
                                                                        self.create_stop_button()]))
        return start_button

    def create_pause_button(self):
        pause_button = QToolButton(self)
        pause_button.setFixedSize(90, 90)
        pause_button_icon = QIcon(self.images["pause.png"])
        hov_pause_button_icon = QIcon(self.images["hover-pause.png"])
        pause_button.setIconSize(QSize(40, 40))
        pause_button.setObjectName("pause_button")
        pause_button.setCursor(QCursor(Qt.PointingHandCursor))
        pause_button.clicked.connect(lambda: self.pause_session_clicked())
        self.setup_hover_icon(pause_button, pause_button_icon, hov_pause_button_icon)
        return pause_button

    def create_stop_button(self):
        stop_button = QToolButton(self)
        stop_button.setFixedSize(90, 90)
        stop_button_icon = QIcon(self.images["stop.png"])
        hov_stop_button_icon = QIcon(self.images["hover-stop.png"])
        stop_button.setIconSize(QSize(40, 40))
        stop_button.setObjectName("stop_button")
        stop_button.setCursor(QCursor(Qt.PointingHandCursor))
        stop_button.clicked.connect(lambda: self.stop_session_clicked())
        self.setup_hover_icon(stop_button, stop_button_icon, hov_stop_button_icon)
        return stop_button

    def create_continue_button(self):
        continue_button = QToolButton(self)
        continue_button.setFixedSize(90, 90)
        continue_button_icon = QIcon(self.images["continue.png"])
        hov_continue_button_icon = QIcon(self.images["hover-continue.png"])
        continue_button.setIconSize(QSize(40, 40))
        continue_button.setObjectName("continue_button")
        continue_button.setCursor(QCursor(Qt.PointingHandCursor))
        continue_button.clicked.connect(lambda: self.continue_session_clicked())
        self.setup_hover_icon(continue_button, continue_button_icon, hov_continue_button_icon)
        return continue_button

    def make_session_frame(self):
        session_frame = QFrame(self)
        session_frame.setFixedSize(500, 680)
        session_frame.setObjectName("session_frame_widget")
        session_frame.setStyleSheet("""QWidget#session_frame_widget{
                                    background-color: white;
                                    border: 4px solid lightgray;
                                    border-radius: 15px;
                            }""")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(8)
        shadow.setYOffset(8)
        session_frame.setGraphicsEffect(shadow)
        vbox = QVBoxLayout(session_frame)
        return session_frame, vbox

    def make_preview_frame(self):
        preview_frame = QFrame(self)
        preview_frame.setFixedSize(1000, 680)
        preview_frame.setObjectName("preview_frame_widget")
        preview_frame.setStyleSheet("""QWidget#preview_frame_widget{
                                    background-color: white;
                                    border: 4px solid lightgray;
                                    border-radius: 15px;
                            }""")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(8)
        shadow.setYOffset(8)
        preview_frame.setGraphicsEffect(shadow)
        vbox = QVBoxLayout(preview_frame)
        return preview_frame, vbox


    def insert_button_in_box(self, box, buttons):
        for button in buttons:
            box.addWidget(button, alignment=Qt.AlignVCenter)

    def name_session(self):
        session_name = QLineEdit(self)
        session_name.setPlaceholderText("Name")
        session_name.setFixedSize(400, 50)
        session_name.setMaxLength(25)
        session_name.setAlignment(Qt.AlignCenter)
        session_name.setStyleSheet("""
                            QLineEdit {
                                font-size: 25px;
                                font-family: Arial;
                                border: 3px solid;
                                border-radius: 15px;
                                border-color: #009db1;
                                }
                                """)
        return session_name

    def make_court(self):
        self.canvas = FloorballCourt(self)
        self.hovered_point = None
        # self.canvas.scene().sigMouseMoved.connect(self.on_mouse_move)

        return self.canvas

    def websocket_connection(self):
        # Inicializace WebSocket klienta
        uri = "ws://147.229.116.29"
        api_key = "171555a8fe71148a165392904"
        self.websocket_client = WebSocketClient(uri, api_key)
        self.PoP = {}
        self.rec_status = False

        self.websocket_label = QLabel("Waiting for connection...")
        self.websocket_client.message_received.connect(lambda message: self.on_message_received(message))
        self.websocket_client.connection_established.connect(lambda: self.on_connection_established())
        self.websocket_client.start()

        return self.websocket_label

    def on_connection_established(self):
        self.websocket_label.setText("Connected!")

    def PoP_management(self, mess):
        x = mess["x"]
        y = mess["y"]
        tag_ID = mess["Tag_ID"]

        if (0 < x < 40) and (0 < y < 20):
            self.PoP[tag_ID] = mess
            self.activeness = True
        else:
            if tag_ID in list(self.PoP.keys()):
                self.PoP.pop(tag_ID)
                self.activeness = True
            else:
                self.activeness = False

        """if self.activeness:
            for player in self.PoP.values():
                player["Time"] = time
                player["Timestamp"] = timestamp"""

    def on_message_received(self, message):
        mess = self.dataRec.message_decoder(message)
        print(f"Received message: {mess}")
        time = mess["Time"]
        self.PoP_management(mess)
        if self.activeness:
            if self.rec_status:
                LoP = list(self.PoP.values())
                for i in range(len(LoP)):
                    LoP[i]["Period"] = self.period
                    LoP[i]["Timestamp"] = self.timestamp
                    LoP[i]["Time"] = time
                self.dataRec.edit_csv(self.text_name, LoP)
                self.timestamp += 1

            self.canvas.scatter_positions(self.PoP)

    def start_session_clicked(self):
        self.timestamp = 0
        self.period = 1
        self.text_name = self.session_name.text()
        self.dataRec.create_csv(self.text_name)
        self.rec_status = True
        self.session_name.setReadOnly(True)
        self.websocket_label.setText("Recording...")

    def pause_session_clicked(self):
        self.rec_status = False
        self.websocket_label.setText("Recording paused.")
        self.clear_layout(self.session_button_box)
        self.insert_button_in_box(self.session_button_box, [self.create_continue_button(), self.create_stop_button()])

    def continue_session_clicked(self):
        self.period += 1
        self.rec_status = True
        self.websocket_label.setText("Recording...")
        self.clear_layout(self.session_button_box)
        self.insert_button_in_box(self.session_button_box, [self.create_pause_button(), self.create_stop_button()])

    def stop_session_clicked(self):
        self.rec_status = False
        self.websocket_label.setText("Recording ended.")
        self.clear_layout(self.session_button_box)
        self.insert_button_in_box(self.session_button_box, [self.create_start_button()])
        self.session_name.setReadOnly(False)
        self.session_name.setText("")
        self.session_name.clearFocus()

        ###____________  ANALYSIS-SCREEN  ____________###

    def create_session_selector(self):
        selector = QComboBox(self)
        selector.setFixedSize(500, 100)
        selector.setObjectName("selector_widget")
        selector.setStyleSheet("""QComboBox#selector_widget::drop-down{
                                        border: none;
                                        margin-right: 20px;
                                    }
                                    QComboBox#selector_widget{
                                        font-size: 25px;
                                        font-family: Arial;
                                        padding: 20px;
                                        background-color: white;
                                        border: 4px solid lightgray;
                                        border-radius: 15px;
                                    }
                                    QComboBox#selector_widget::down-arrow {
                                        image: url(img_Lib/more.png);
                                        width: 16px;
                                        height: 16px;
                                        
                                    }
                                    QComboBox#selector_widget::down-arrow:hover {
                                        image: url(img_Lib/hover-more.png);
                                    }
                                    QComboBox#selector_widget QAbstractItemView {
                                        padding: 20px;
                                        selection-background-color: #009db1;
                                    }
                                    
                                """)
        selector.setCursor(QCursor(Qt.PointingHandCursor))
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(8)
        shadow.setYOffset(8)
        selector.setGraphicsEffect(shadow)
        selector.clear()
        selector.addItem("Select session file")
        selector.model().item(0).setEnabled(False)
        for file in os.listdir("Measurements"):
            if file.endswith(".csv"):
                file_name = file[:-4]
                selector.addItem(file_name)

        def setup_session():
            self.selected_file = self.session_selector.currentText()
            self.selected_data = self.dataRec.read_csv(self.selected_file)

        selector.currentIndexChanged.connect(
            lambda: setup_session()
        )

        return selector

    def make_configure_frame(self):
        configure_frame = QFrame(self)
        configure_frame.setFixedSize(500, 600)
        configure_frame.setObjectName("configure_frame_widget")
        configure_frame.setStyleSheet("""QWidget#configure_frame_widget{
                                    background-color: white;
                                    border: 4px solid lightgray;
                                    border-radius: 15px;
                            }""")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(8)
        shadow.setYOffset(8)
        configure_frame.setGraphicsEffect(shadow)
        box = QGridLayout(configure_frame)
        return configure_frame, box

    def make_select_analysis_frame(self):
        select_analysis_frame = QFrame(self)
        select_analysis_frame.setFixedSize(1000, 100)
        select_analysis_frame.setObjectName("select_analysis_frame_widget")
        select_analysis_frame.setStyleSheet("""QWidget#select_analysis_frame_widget{
                                    background-color: white;
                                    border: 4px solid lightgray;
                                    border-radius: 15px;
                            }""")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(8)
        shadow.setYOffset(8)
        select_analysis_frame.setGraphicsEffect(shadow)
        hbox = QHBoxLayout(select_analysis_frame)
        return select_analysis_frame, hbox

    def make_analysis_frame(self):
        analysis_frame = QFrame(self)
        analysis_frame.setFixedSize(1000, 600)
        analysis_frame.setObjectName("analysis_frame_widget")
        analysis_frame.setStyleSheet("""QWidget#analysis_frame_widget{
                                    background-color: white;
                                    border: 4px solid lightgray;
                                    border-radius: 15px;
                            }""")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(8)
        shadow.setYOffset(8)
        analysis_frame.setGraphicsEffect(shadow)
        vbox = QVBoxLayout(analysis_frame)
        return analysis_frame, vbox

    def create_function_button(self, icon_name):
        button = QToolButton(self)
        button.setFixedSize(70, 70)
        button.setEnabled(False)
        if icon_name:
            icon = QIcon(self.images[icon_name])
            hov_icon = QIcon(self.images[f"hover-{icon_name}"])
            button.setIconSize(QSize(68, 68))
            button.setObjectName("function_button")
            button.setCursor(QCursor(Qt.PointingHandCursor))
            self.setup_hover_icon(button, icon, icon)

            def button_clicked():
                buttons = [self.view_button, self.table_button]
                current_size = button.size()
                for butt in buttons:
                    butt.setFixedSize(70, 70)
                    butt.setStyleSheet("QToolButton#function_button { background-color: #bddade; }"
                                       "QToolButton#function_button:hover { background-color: #009db1; }")

                if current_size == QSize(70, 70):
                    button.setFixedSize(300, 70)
                    button.setStyleSheet("QToolButton#function_button { background-color: #009db1; }")
                    self.function_button_clicked(icon_name[:-4], False)
                else:
                    self.function_button_clicked(icon_name[:-4])

            button.clicked.connect(button_clicked)

            def on_session_selected(index):
                if index != 0:
                    button.setEnabled(True)
                    self.setup_hover_icon(button, icon, hov_icon)
                else:
                    button.setEnabled(False)

            self.session_selector.currentIndexChanged.connect(on_session_selected)

        else:
            button.setObjectName("fake_button")

        return button

    ###____________  ANALYSIS-FUNCTIONS  ____________###

    def function_button_clicked(self, name, only_clear=True):
        self.clear_layout(self.configure_box)
        self.clear_layout(self.analysis_vbox)

        if not only_clear:
            if name == 'table':
                self.table_function()
            if name == 'view':
                self.view_function()

    ###____________  VIEW-FUNCTION  ____________###
    def view_function(self):
        self.view_selector_box = QVBoxLayout()
        self.timestamp_slider_box = QVBoxLayout()
        self.time_label_box = QVBoxLayout()

        self.configure_box.addWidget(self.make_headline("Pitch view"), 0, 0, alignment=Qt.AlignHCenter)
        self.configure_box.setRowMinimumHeight(0, 100)
        self.configure_box.addLayout(self.view_selector_box, 1, 0)
        self.configure_box.setRowMinimumHeight(1, 220)
        self.configure_box.addItem(self.spacer(), 2, 0)
        self.configure_box.setRowMinimumHeight(2, 100)
        self.configure_box.addLayout(self.timestamp_slider_box, 3, 0)
        self.configure_box.setRowMinimumHeight(3, 220)
        self.configure_box.addLayout(self.time_label_box, 4, 0)
        self.configure_box.setRowMinimumHeight(4, 50)
        self.configure_box.addItem(self.spacer(), 5, 0)
        self.configure_box.setRowMinimumHeight(5, 200)

        self.view_selector = self.create_period_selector()
        self.view_selector_box.addWidget(self.view_selector, alignment=Qt.AlignHCenter)

        self.pitch_view = self.make_court()
        self.analysis_vbox.addWidget(self.pitch_view, alignment=Qt.AlignCenter)

        self.time_label = self.create_time_label()
        self.time_label_box.addWidget(self.time_label, alignment=Qt.AlignCenter)

    def create_period_selector(self):
        selector = QComboBox(self)
        selector.setFixedSize(450, 100)
        selector.setObjectName("period_selector_widget")
        selector.setStyleSheet("""QComboBox#period_selector_widget::drop-down{
                                                border: none;
                                                margin-right: 20px;
                                            }
                                            QComboBox#period_selector_widget{
                                                font-size: 25px;
                                                font-family: Arial;
                                                padding: 20px;
                                                background-color: white;
                                                border: 2px solid lightgray;
                                                border-radius: 15px;
                                            }
                                            QComboBox#period_selector_widget::down-arrow {
                                                image: url(img_Lib/more.png);
                                                width: 16px;
                                                height: 16px;

                                            }
                                            QComboBox#period_selector_widget::down-arrow:hover {
                                                image: url(img_Lib/hover-more.png);
                                            }
                                            QComboBox#period_selector_widget QAbstractItemView {
                                                padding: 20px;
                                                selection-background-color: #009db1;
                                            }
                                            QComboBox#period_selector_widget QAbstractItemView::item:selected {
                                                background-color: white;
                                            }
                                        """)
        selector.setCursor(QCursor(Qt.PointingHandCursor))

        def make_selection():
            selector.clear()
            selector.addItem("Select Period")
            selector.model().item(0).setEnabled(False)
            item_list = self.selected_data['Period'].unique()

            for item in item_list:
                selector.addItem(f"Period {item}")

        if not selector:
            make_selection()

        def session_changed(file):
            self.clear_layout(self.analysis_vbox)
            self.clear_layout(self.view_selector_box)
            self.clear_layout(self.timestamp_slider_box)

            self.pitch_view = self.make_court()
            self.analysis_vbox.addWidget(self.pitch_view, alignment=Qt.AlignCenter)
            self.view_selector = self.create_period_selector()
            self.view_selector_box.addWidget(self.view_selector, alignment=Qt.AlignHCenter)

        self.session_selector.currentTextChanged.connect(
            lambda text: session_changed(text)
        )

        def item_selected(text):
            self.clear_layout(self.analysis_vbox)
            self.clear_layout(self.timestamp_slider_box)
            self.pitch_view = self.make_court()
            self.analysis_vbox.addWidget(self.pitch_view, alignment=Qt.AlignCenter)

            self.timestamp_slider = self.create_timestamp_slider()
            self.timestamp_slider_box.addWidget(self.timestamp_slider, alignment=Qt.AlignHCenter)

        selector.currentTextChanged.connect(
            lambda text: item_selected(text)
        )

        return selector

    def create_timestamp_slider(self):
        time_slider = QSlider()
        time_slider.setOrientation(Qt.Horizontal)
        time_slider.setFixedSize(300, 40)
        period = int(self.view_selector.currentText()[7:])
        data = self.selected_data
        stamps = data.loc[data["Period"] == period, ["Timestamp", "Time"]]
        t0 = stamps["Time"].iloc[0][-12:]
        minimum = stamps["Timestamp"].min()
        maximum = stamps["Timestamp"].max()
        time_slider.setMinimum(minimum)
        time_slider.setMaximum(maximum)
        time_slider.setValue(minimum+(maximum-minimum)//2)
        time_slider.setCursor(QCursor(Qt.PointingHandCursor))
        time_slider.setStyleSheet("""QSlider::groove:horizontal {
                                        border: 2px solid lightgray;
                                        height: 10px;
                                        background: #white;
                                        margin: 2px 0;
                                        border-radius: 4px;
                                    }
                                    QSlider::handle:horizontal {
                                        background: #bddade;
                                        border: 1px solid #009db1;
                                        width: 16px;
                                        height: 48px;
                                        margin: -12px 0;
                                        border-radius: 8px;
                                    }
                                    QSlider::handle:horizontal:pressed {
                                        background: #009db1;
                                    }
                                """)
        def make_timelabel(t):
            time_format = "%H:%M:%S.%f"
            T0 = datetime.strptime(t0, time_format)
            T = datetime.strptime(t, time_format)

            delta_t = T - T0
            time = self.analysis.time2str(delta_t)
            return time

        def slider_moved(timestamp):
            on_pitch = data.loc[data["Timestamp"] == timestamp, ["Tag_ID", "x", "y", "Time"]]
            t = on_pitch["Time"].iloc[0][-12:]
            PoP = {}
            for index, player in on_pitch.iterrows():
                PoP[player["Tag_ID"]] = {"x": player["x"], "y": player["y"]}

            self.pitch_view.scatter_positions(PoP)
            time = make_timelabel(t)
            self.time_label.setText(time)

        slider_moved(time_slider.value())
        time_slider.valueChanged.connect(lambda value: slider_moved(value))

        return time_slider

    def create_time_label(self):
        time_label = QLabel()
        time_label.setFixedHeight(20)
        time_label.setObjectName("time_label")
        time_label.setStyleSheet("""QLabel#time_label{
                                        font-size: 25px;
                                        font-family: Arial;
                                    }
                                """)
        def session_changed(i):
            self.clear_layout(self.time_label_box)

            self.time_label = self.create_time_label()
            self.time_label_box.addWidget(self.time_label, alignment=Qt.AlignCenter)

        self.session_selector.currentIndexChanged.connect(lambda index: session_changed(index))
        return time_label


    ###____________  TABLE-FUNCTION  ____________###

    def table_function(self):
        self.table_setting = None
        switch_box = QHBoxLayout()
        self.filter_selector_box = QVBoxLayout()

        self.configure_box.addWidget(self.make_headline("Players activity overview"), 0, 0, alignment=Qt.AlignHCenter)
        self.configure_box.setRowMinimumHeight(0, 100)
        self.configure_box.addLayout(switch_box, 1, 0)
        self.configure_box.setRowMinimumHeight(1, 100)
        self.configure_box.addLayout(self.filter_selector_box, 2, 0)
        self.configure_box.setRowMinimumHeight(2, 220)
        self.configure_box.addItem(self.spacer(), 3, 0)
        self.configure_box.setRowMinimumHeight(3, 200)

        self.switch_button_player = self.table_by_button("Player")
        self.switch_button_period = self.table_by_button("Period")

        switch_box.addSpacerItem(self.spacer())
        switch_box.addWidget(self.switch_button_player)
        switch_box.addSpacerItem(self.spacer())
        switch_box.addWidget(self.switch_button_period)
        switch_box.addSpacerItem(self.spacer())

        def count_table_variables():
            self.dist_dict, self.time_dict = self.analysis.count_distances(self.selected_data)

        count_table_variables()
        self.session_selector.currentIndexChanged.connect(lambda: count_table_variables())

    def table_by_button(self, text):
        button = QToolButton(self)
        button.setFixedSize(100, 40)
        button.setObjectName("switch_button")
        button.setText(text)
        button.setCursor(QCursor(Qt.PointingHandCursor))

        def button_pressed():
            self.clear_layout(self.analysis_vbox)
            self.table_setting = text

            column_player = 'Tag_ID'
            column_period = 'Period'
            self.merged_data_by_player = self.analysis.merge_data(column_player, self.selected_data)
            self.item_list_by_player = self.analysis.merged_values(self.merged_data_by_player)
            self.merged_data_by_period = self.analysis.merge_data(column_period, self.selected_data)
            self.item_list_by_period = self.analysis.merged_values(self.merged_data_by_period)

            self.clear_layout(self.filter_selector_box)
            self.table_selector = self.create_table_selector(text)
            self.filter_selector_box.addWidget(self.table_selector, alignment=Qt.AlignHCenter)

            buttons = [self.switch_button_player, self.switch_button_period]
            for butt in buttons:
                butt.setStyleSheet("QToolButton#switch_button { background-color: #bddade; }"
                                   "QToolButton#switch_button:hover { background-color: #009db1; }")

            button.setStyleSheet("QToolButton#switch_button { background-color: #009db1; }"
                                 "QToolButton#switch_button { color: 'white'; }"
                                 "QToolButton#switch_button { font-weight: bold; }")

        button.clicked.connect(button_pressed)

        return button

    def create_table_selector(self, filter_name):
        selector = QComboBox(self)
        selector.setFixedSize(450, 100)
        selector.setObjectName("filter_selector_widget")
        selector.setStyleSheet("""QComboBox#filter_selector_widget::drop-down{
                                                border: none;
                                                margin-right: 20px;
                                            }
                                            QComboBox#filter_selector_widget{
                                                font-size: 25px;
                                                font-family: Arial;
                                                padding: 20px;
                                                background-color: white;
                                                border: 2px solid lightgray;
                                                border-radius: 15px;
                                            }
                                            QComboBox#filter_selector_widget::down-arrow {
                                                image: url(img_Lib/more.png);
                                                width: 16px;
                                                height: 16px;

                                            }
                                            QComboBox#filter_selector_widget::down-arrow:hover {
                                                image: url(img_Lib/hover-more.png);
                                            }
                                            QComboBox#filter_selector_widget QAbstractItemView {
                                                padding: 20px;
                                                selection-background-color: #009db1;
                                            }
                                            QComboBox#filter_selector_widget QAbstractItemView::item:selected {
                                                background-color: white;
                                            }
                                        """)
        selector.setCursor(QCursor(Qt.PointingHandCursor))

        def make_selection(name):
            selector.clear()
            selector.addItem(f"Select {name}")
            selector.model().item(0).setEnabled(False)
            if name == 'Player':
                item_list = self.item_list_by_player
            else:
                item_list = self.item_list_by_period

            for item in item_list:
                if name == 'Player':
                    selector.addItem(f"Player {item}")
                else:
                    selector.addItem(f"Period {item}")
            if name == 'Period':
                selector.addItem("Whole match")

        if not selector:
            make_selection(filter_name)

        def session_changed(file, name):
            self.clear_layout(self.analysis_vbox)
            self.clear_layout(self.filter_selector_box)

            column_player = 'Tag_ID'
            column_period = 'Period'
            self.merged_data_by_player = self.analysis.merge_data(column_player, self.selected_data)
            self.item_list_by_player = self.analysis.merged_values(self.merged_data_by_player)
            self.merged_data_by_period = self.analysis.merge_data(column_period, self.selected_data)
            self.item_list_by_period = self.analysis.merged_values(self.merged_data_by_period)

            self.table_selector = self.create_table_selector(name)
            self.filter_selector_box.addWidget(self.table_selector, alignment=Qt.AlignHCenter)

        self.session_selector.currentTextChanged.connect(
            lambda text: session_changed(text, filter_name)
        )

        def item_selected(text):
            self.clear_layout(self.analysis_vbox)
            table = self.setup_table()
            self.analysis_vbox.addWidget(table, alignment=Qt.AlignCenter)

        selector.currentTextChanged.connect(
            lambda text: item_selected(text)
        )

        return selector

    def setup_table(self):
        table_view = QTableView(self)
        table_view.verticalHeader().setVisible(False)
        if self.table_setting == 'Player':
            rows = len(self.item_list_by_period) + 1
            model = QStandardItemModel(rows, 3)
            model.setHorizontalHeaderLabels(["Period", "Distance\n[m]", "Game-time\n[min:sec]"])
            idx = self.table_selector.currentIndex() - 1
            player = self.item_list_by_player[idx]

            for row in range(rows - 1):
                period = self.item_list_by_period[row]
                item = QStandardItem(str(period))
                item.setTextAlignment(Qt.AlignCenter)
                model.setItem(row, 0, item)

                dist = self.dist_dict[period][player]
                dist_item = QStandardItem(f"{dist:,}".replace(",", " "))
                dist_item.setTextAlignment(Qt.AlignCenter)
                model.setItem(row, 1, dist_item)

                time = self.time_dict[period][player]
                time_item = QStandardItem(self.analysis.time2str(time))
                time_item.setTextAlignment(Qt.AlignCenter)
                model.setItem(row, 2, time_item)

            last_item = QStandardItem("Whole match")
            last_item.setTextAlignment(Qt.AlignCenter)
            model.setItem(rows - 1, 0, last_item)

            last_dist = self.dist_dict['Whole match'][player]
            last_dist_item = QStandardItem(f"{last_dist:,}".replace(",", " "))
            last_dist_item.setTextAlignment(Qt.AlignCenter)
            model.setItem(rows - 1, 1, last_dist_item)

            last_time = self.time_dict['Whole match'][player]
            last_time_item = QStandardItem(self.analysis.time2str(last_time))
            last_time_item.setTextAlignment(Qt.AlignCenter)
            model.setItem(rows - 1, 2, last_time_item)

        if self.table_setting == 'Period':
            rows = len(self.item_list_by_player)
            model = QStandardItemModel(rows, 3)
            model.setHorizontalHeaderLabels(["Player", "Distance\n[m]", "Game-time\n[min:sec]"])
            idx = self.table_selector.currentIndex() - 1
            if idx == len(self.item_list_by_period):
                period = "Whole match"
            else:
                period = self.item_list_by_period[idx]

            for row in range(rows):
                player = self.item_list_by_player[row]
                item = QStandardItem(str(player))
                item.setTextAlignment(Qt.AlignCenter)
                model.setItem(row, 0, item)

                dist = self.dist_dict[period][player]
                dist_item = QStandardItem(f"{dist:,}".replace(",", " "))
                dist_item.setTextAlignment(Qt.AlignCenter)
                model.setItem(row, 1, dist_item)

                time = self.time_dict[period][player]
                time_item = QStandardItem(self.analysis.time2str(time))
                time_item.setTextAlignment(Qt.AlignCenter)
                model.setItem(row, 2, time_item)

        table_view.setModel(model)
        header_height = table_view.horizontalHeader().height()
        row_height = table_view.rowHeight(0)
        height = header_height + rows * row_height
        table_view.setFixedSize(720, height)
        max_height = 432
        table_view.setMaximumHeight(max_height)
        if height <= max_height:
            table_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table_view.horizontalHeader().setSectionResizeMode(1)
        table_view.setEnabled(False)
        table_view.setAlternatingRowColors(True)
        table_view.setStyleSheet("""QHeaderView::section {
                                        background-color: #009db1;     
                                        color: white;   
                                        font-weight: bold;
                                        border: 1px solid #bddade;
                                    }
                                    QTableView {
                                        font-size: 16px;
                                        color: black;
                                        font-family: Arial;
                                        gridline-color: #009db1;
                                        background-color: white;
                                        alternate-background-color: #bddade;
                                        border: 2px solid #009db1;
                                    }
                                """)
        return table_view



    ###____________  OPENING SCREENS  ____________###___________________________________________________________________
    def show_home_screen(self):
        self.home_scrn = True
        self.sess_scrn = False
        self.anal_scrn = False
        self.sett_scrn = False

        self.clear_screen()
        self.showNormal()
        self.make_background()
        frame, home_hbox = self.make_frame()

        home_hbox.addWidget(self.create_analysis_button())
        home_hbox.addWidget(self.create_session_button())
        home_hbox.addWidget(self.create_setting_button())

        self.layout.addWidget(frame, alignment=Qt.AlignCenter)

        self.style_button()

    def show_session_screen(self):
        self.home_scrn = False
        self.sess_scrn = True
        self.anal_scrn = False
        self.sett_scrn = False

        self.clear_screen()
        self.showMaximized()
        self.make_background()
        up_panel, panel_hbox = self.make_upper_panel()
        session_frame, session_vbox = self.make_session_frame()
        preview_frame, preview_vbox = self.make_preview_frame()
        screen_hbox = QHBoxLayout()
        label = self.websocket_connection()
        self.session_name = self.name_session()
        self.session_button_box = QHBoxLayout()

        panel_hbox.addWidget(self.create_home_button())
        panel_hbox.addSpacerItem(self.spacer())
        panel_hbox.addWidget(self.make_headline("Record new session"))
        panel_hbox.addSpacerItem(self.spacer())
        panel_hbox.addWidget(self.create_small_analysis_button())
        panel_hbox.addWidget(self.create_small_setting_button())

        self.layout.addWidget(up_panel, alignment=Qt.AlignTop)
        self.layout.addSpacerItem(self.spacer())
        self.layout.addLayout(screen_hbox)
        self.layout.addSpacerItem(self.spacer())

        screen_hbox.addSpacerItem(self.spacer())
        screen_hbox.addWidget(session_frame)
        screen_hbox.addSpacerItem(self.spacer())
        screen_hbox.addWidget(preview_frame)
        screen_hbox.addSpacerItem(self.spacer())

        session_vbox.addWidget(self.make_headline("Record settings"), alignment=Qt.AlignTop | Qt.AlignHCenter)
        session_vbox.addSpacerItem(self.spacer())
        session_vbox.addWidget(self.session_name, alignment=Qt.AlignHCenter)
        session_vbox.addSpacerItem(self.spacer())
        session_vbox.addWidget(label, alignment=Qt.AlignHCenter)
        session_vbox.addSpacerItem(self.spacer())
        session_vbox.addLayout(self.session_button_box)

        self.insert_button_in_box(self.session_button_box, [self.create_start_button()])

        preview_vbox.addWidget(self.make_headline("Real-time court view"), alignment=Qt.AlignTop | Qt.AlignHCenter)
        preview_vbox.addSpacerItem(self.spacer())
        preview_vbox.addWidget(self.make_court(), alignment=Qt.AlignHCenter)
        preview_vbox.addSpacerItem(self.spacer())

        self.style_button()

    def show_analysis_screen(self):
        self.home_scrn = False
        self.sess_scrn = False
        self.anal_scrn = True
        self.sett_scrn = False

        self.analysis = Analysis()

        self.clear_screen()
        self.showMaximized()
        self.make_background()

        up_panel, panel_hbox = self.make_upper_panel()
        self.session_selector = self.create_session_selector()
        self.configure_frame, self.configure_box = self.make_configure_frame()
        self.sel_analysis_frame, self.sel_analysis_hbox = self.make_select_analysis_frame()
        self.analysis_frame, self.analysis_vbox = self.make_analysis_frame()
        screen_hbox = QHBoxLayout()
        left_vbox = QVBoxLayout()
        right_vbox = QVBoxLayout()

        panel_hbox.addWidget(self.create_home_button())
        panel_hbox.addSpacerItem(self.spacer())
        panel_hbox.addWidget(self.make_headline("Session analysis"))
        panel_hbox.addSpacerItem(self.spacer())
        panel_hbox.addWidget(self.create_small_session_button())
        panel_hbox.addWidget(self.create_small_setting_button())

        self.layout.addWidget(up_panel, alignment=Qt.AlignTop)
        self.layout.addSpacerItem(self.spacer())
        self.layout.addLayout(screen_hbox)
        self.layout.addSpacerItem(self.spacer())

        screen_hbox.addSpacerItem(self.spacer())
        screen_hbox.addLayout(left_vbox)
        screen_hbox.addSpacerItem(self.spacer())
        screen_hbox.addLayout(right_vbox)
        screen_hbox.addSpacerItem(self.spacer())

        left_vbox.addWidget(self.session_selector)
        left_vbox.addWidget(self.configure_frame)

        right_vbox.addWidget(self.sel_analysis_frame)
        right_vbox.addWidget(self.analysis_frame)

        self.table_button = self.create_function_button("table.png")
        self.view_button = self.create_function_button("view.png")

        self.sel_analysis_hbox.addSpacerItem(self.spacer())
        self.sel_analysis_hbox.addWidget(self.view_button)
        self.sel_analysis_hbox.addSpacerItem(self.spacer())
        self.sel_analysis_hbox.addWidget(self.table_button)
        self.sel_analysis_hbox.addSpacerItem(self.spacer())
        self.sel_analysis_hbox.addWidget(self.create_function_button(False))
        self.sel_analysis_hbox.addSpacerItem(self.spacer())
        self.sel_analysis_hbox.addWidget(self.create_function_button(False))
        self.sel_analysis_hbox.addSpacerItem(self.spacer())
        self.sel_analysis_hbox.addWidget(self.create_function_button(False))
        self.sel_analysis_hbox.addSpacerItem(self.spacer())
        self.sel_analysis_hbox.addWidget(self.create_function_button(False))
        self.sel_analysis_hbox.addSpacerItem(self.spacer())
        self.sel_analysis_hbox.addWidget(self.create_function_button(False))
        self.sel_analysis_hbox.addSpacerItem(self.spacer())
        self.sel_analysis_hbox.addWidget(self.create_function_button(False))
        self.sel_analysis_hbox.addSpacerItem(self.spacer())

        self.style_button()

    def show_setting_screen(self):
        self.home_scrn = False
        self.sess_scrn = False
        self.anal_scrn = False
        self.sett_scrn = True

        self.clear_screen()
        self.showMaximized()
        self.make_background()

        up_panel, panel_hbox = self.make_upper_panel()

        panel_hbox.addWidget(self.create_home_button())
        panel_hbox.addSpacerItem(self.spacer())
        panel_hbox.addWidget(self.make_headline("Settings"))
        panel_hbox.addSpacerItem(self.spacer())
        panel_hbox.addWidget(self.create_small_session_button())
        panel_hbox.addWidget(self.create_small_analysis_button())

        self.layout.addWidget(up_panel, alignment=Qt.AlignTop)

        self.style_button()

    ###____________  CLEARING-SCREEN  ____________###

    def clear_screen(self):
        self.setCentralWidget(None)
        self.setMinimumSize(0, 0)

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()  # Odstraní widget
            elif item.layout():
                self.clear_layout(item.layout())

    ###____________  ICON-SETTING  ____________###

    def setup_hover_icon(self, button, icon, hover_icon):
        button.setIcon(icon)
        button.setAttribute(Qt.WA_Hover, True)
        button.installEventFilter(self)

        button._icon = icon
        button._hover_icon = hover_icon

    def eventFilter(self, source, event):
        if isinstance(source, QToolButton):
            if event.type() == QEvent.Enter:
                source.setIcon(source._hover_icon)
            elif event.type() == QEvent.Leave:
                source.setIcon(source._icon)
        return super().eventFilter(source, event)

    def mousePressEvent(self, event):
        if self.sess_scrn:
            if self.session_name.hasFocus():
                self.session_name.clearFocus()

        if self.anal_scrn:
            if self.session_selector.hasFocus():
                self.session_selector.clearFocus()

        super().mousePressEvent(event)

    ###____________  MAIN  ____________###______________________________________________________________________________

    ####################################################################################################################

    def on_mouse_move(self, pos):
        mouse_point = self.canvas.plotItem.vb.mapSceneToView(pos)
        hovered_point = None
        hover_radius = 20
        min_distance = float('inf')

        scatter_data = self.canvas.points.data
        x_pos = scatter_data['x']
        y_pos = scatter_data['y']

        for i, point in enumerate(scatter_data):
            distance = ((mouse_point.x() - x_pos[i]) ** 2 + (mouse_point.y() - y_pos[i]) ** 2) ** 0.5
            if distance < min_distance and distance < hover_radius:
                min_distance = distance
                hovered_point = point

        if hovered_point != self.hovered_point:
            if self.hovered_point:
                self.canvas.reset_point(self.hovered_point)

            if hovered_point:
                tag_id = self.canvas.positions[hovered_point]
                self.canvas.highlight_point(hovered_point, tag_id)

            self.hovered_point = hovered_point


########################################################################################################################
#########################################  FLOORBALL-COURT PLOT  #######################################################
########################################################################################################################


class FloorballCourt(pg.PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackground('w')
        self.setXRange(0, 40)
        self.setYRange(0, 20)
        self.setAspectLocked(True)
        self.setMouseEnabled(x=False, y=False)
        self.hideAxis('left')
        self.hideAxis('bottom')
        self.setFixedSize(800, 400)
        self.disableAutoRange()
        self.draw_field()

        self.points = pg.ScatterPlotItem()
        self.addItem(self.points)
        self.positions = {}

    def draw_field(self):
        pen = pg.mkPen(color='grey', width=2)
        width = 20
        length = 40
        corner_radius = 3.5

        # Nakreslení obvodových čar (bez rohů)
        self.plot([corner_radius, length - corner_radius], [0, 0], pen=pen)  # Spodní čára
        self.plot([corner_radius, length - corner_radius], [width, width], pen=pen)  # Horní čára
        self.plot([0, 0], [corner_radius, width - corner_radius], pen=pen)  # Levá čára (s vynecháním rohů)
        self.plot([length, length], [corner_radius, width - corner_radius], pen=pen)  # Pravá čára (s vynecháním rohů)

        # Zaoblené rohy (čtvrtkruhy)
        theta = np.linspace(0, np.pi / 2, 50)

        # Levý spodní roh
        x_corner = corner_radius - corner_radius * np.cos(theta)
        y_corner = corner_radius - corner_radius * np.sin(theta)
        self.plot(x_corner, y_corner, pen=pen)

        # Pravý spodní roh
        x_corner = length - corner_radius + corner_radius * np.cos(theta)
        y_corner = corner_radius - corner_radius * np.sin(theta)
        self.plot(x_corner, y_corner, pen=pen)

        # Levý horní roh
        x_corner = corner_radius - corner_radius * np.cos(theta)
        y_corner = width - corner_radius + corner_radius * np.sin(theta)
        self.plot(x_corner, y_corner, pen=pen)

        # Pravý horní roh
        x_corner = length - corner_radius + corner_radius * np.cos(theta)
        y_corner = width - corner_radius + corner_radius * np.sin(theta)
        self.plot(x_corner, y_corner, pen=pen)

        # Středová čára
        self.plot([length / 2, length / 2], [0, width], pen=pen)

        # Středový kruh
        radius = 3
        circle = QGraphicsEllipseItem(length / 2 - radius, width / 2 - radius, 2 * radius, 2 * radius)
        circle.setPen(pen)
        self.addItem(circle)

        # Křížky
        x_offset = 3.5
        y_offset = 1.5
        self.draw_cross(x_offset, y_offset, pen)
        self.draw_cross(x_offset, width - y_offset, pen)
        self.draw_cross(length - x_offset, y_offset, pen)
        self.draw_cross(length - x_offset, width - y_offset, pen)

        self.draw_cross(length / 2, y_offset, pen, vertical=False)
        self.draw_cross(length / 2, width / 2, pen, vertical=False)
        self.draw_cross(length / 2, width - y_offset, pen, vertical=False)

        # Brankoviště
        self.draw_goal_areas(length, width, pen)

    def draw_cross(self, x, y, pen, vertical=True):
        length = 0.3
        self.plot([x - length, x + length], [y, y], pen=pen)  # horizontální čára
        if vertical == True:
            self.plot([x, x], [y - length, y + length], pen=pen)  # vertikální čára

    def draw_goal_areas(self, length, width, pen):
        # parameters
        x_small = 1
        y_small = 2.5
        x_large = 4
        y_large = 5
        x_small_offset = 3.5
        x_large_offset = 2.85
        goal_w = 1.6
        goal_mark_l = 0.2
        # home-side
        # large area
        self.plot([x_large_offset, x_large_offset + x_large], [width / 2 + y_large / 2, width / 2 + y_large / 2],
                  pen=pen)
        self.plot([x_large_offset, x_large_offset + x_large], [width / 2 - y_large / 2, width / 2 - y_large / 2],
                  pen=pen)
        self.plot([x_large_offset, x_large_offset], [width / 2 - y_large / 2, width / 2 + y_large / 2], pen=pen)
        self.plot([x_large_offset + x_large, x_large_offset + x_large],
                  [width / 2 - y_large / 2, width / 2 + y_large / 2], pen=pen)
        # small area
        self.plot([x_small_offset, x_small_offset + x_small], [width / 2 + y_small / 2, width / 2 + y_small / 2],
                  pen=pen)
        self.plot([x_small_offset, x_small_offset + x_small], [width / 2 - y_small / 2, width / 2 - y_small / 2],
                  pen=pen)
        self.plot([x_small_offset, x_small_offset], [width / 2 - y_small / 2, width / 2 + y_small / 2], pen=pen)
        self.plot([x_small_offset + x_small, x_small_offset + x_small],
                  [width / 2 - y_small / 2, width / 2 + y_small / 2], pen=pen)
        # goal-mark
        self.plot([x_small_offset - goal_mark_l, x_small_offset], [width / 2 + goal_w / 2, width / 2 + goal_w / 2],
                  pen=pen)
        self.plot([x_small_offset - goal_mark_l, x_small_offset], [width / 2 - goal_w / 2, width / 2 - goal_w / 2],
                  pen=pen)
        # away-side
        # large area
        self.plot([length - x_large_offset, length - x_large_offset - x_large],
                  [width / 2 + y_large / 2, width / 2 + y_large / 2], pen=pen)
        self.plot([length - x_large_offset, length - x_large_offset - x_large],
                  [width / 2 - y_large / 2, width / 2 - y_large / 2], pen=pen)
        self.plot([length - x_large_offset, length - x_large_offset],
                  [width / 2 - y_large / 2, width / 2 + y_large / 2], pen=pen)
        self.plot([length - x_large_offset - x_large, length - x_large_offset - x_large],
                  [width / 2 - y_large / 2, width / 2 + y_large / 2], pen=pen)
        # small area
        self.plot([length - x_small_offset, length - x_small_offset - x_small],
                  [width / 2 + y_small / 2, width / 2 + y_small / 2], pen=pen)
        self.plot([length - x_small_offset, length - x_small_offset - x_small],
                  [width / 2 - y_small / 2, width / 2 - y_small / 2], pen=pen)
        self.plot([length - x_small_offset, length - x_small_offset],
                  [width / 2 - y_small / 2, width / 2 + y_small / 2], pen=pen)
        self.plot([length - x_small_offset - x_small, length - x_small_offset - x_small],
                  [width / 2 - y_small / 2, width / 2 + y_small / 2], pen=pen)
        # goal-mark
        self.plot([length - x_small_offset + goal_mark_l, length - x_small_offset],
                  [width / 2 + goal_w / 2, width / 2 + goal_w / 2], pen=pen)
        self.plot([length - x_small_offset + goal_mark_l, length - x_small_offset],
                  [width / 2 - goal_w / 2, width / 2 - goal_w / 2], pen=pen)

    def scatter_positions(self, PoP):
        # self.points.setData()
        self.positions = {}
        x = []
        y = []
        for tag_id, info in PoP.items():
            x.append(info["x"])
            y.append(info["y"])

        self.points.setData(x=x, y=y, pen=None, symbol='o', brush=QColor("#009db1"), size=10)

        # Mapování tag_id na jednotlivé body (ScatterPlotItem)
        for i, tag_id in enumerate(PoP):
            self.positions[i] = tag_id

    def highlight_point(self, point, tag_id):
        point.setBrush('r')
        point.setSize(20)
        point.setToolTip(f"tag ID {tag_id}")

    def reset_point(self, point):
        point.setBrush('b')
        point.setSize(10)
        point.setToolTip("")


########################################################################################################################
###########################################  WEBSOCKET CLIENT  #########################################################
########################################################################################################################


class WebSocketClient(QThread):
    message_received = pyqtSignal(str)
    connection_established = pyqtSignal()

    def __init__(self, uri, api_key):
        super().__init__()
        self.uri = uri
        self.api_key = api_key
        self.loop = asyncio.new_event_loop()
        self.websocket = None

    async def connect(self):
        try:
            # Připojení k WebSocket serveru
            self.websocket = await websockets.connect(self.uri)
            self.connection_established.emit()
            print("Connection established!")

            subscribe_message = {
                "headers": {"X-ApiKey": self.api_key},
                "method": "subscribe",
                "resource": "/feeds/"
            }
            await self.websocket.send(json.dumps(subscribe_message))
            print("Subscription message sent!")
            # Zpracování zpráv od serveru
            while True:
                message = await self.websocket.recv()
                self.message_received.emit(message)
        except Exception as e:
            print(f"Error: {e}")

    def run(self):
        # Spuštění asynchronního WebSocket připojení v novém event loopu
        self.loop.run_until_complete(self.connect())

    def send_message(self, message):
        # Funkce pro odeslání zprávy na WebSocket server
        if self.websocket:
            asyncio.run_coroutine_threadsafe(self.websocket.send(message), self.loop)


########################################################################################################################
###########################################  DATA-PROCESSING  ##########################################################
########################################################################################################################


class DataRecording:
    def __init__(self):
        super().__init__()
        self.file = None
        self.writer = None

    def message_decoder(self, message):
        message = json.loads(message)
        body = message["body"]
        tagID = int(body["id"])
        tagVals = body["datastreams"]
        self.offset = {"x": 0.9, "y": -2}
        for i in range(len(tagVals)):
            if tagVals[i]["id"] == "posX":
                time = tagVals[i]["at"]
                x = float(tagVals[i]["current_value"]) - self.offset["x"]
                continue
            elif tagVals[i]["id"] == "posY":
                y = float(tagVals[i]["current_value"]) + self.offset["y"]
                break
        mess = {"Period": None, "Timestamp": None, "Tag_ID": tagID, "x": x, "y": 20 - y, "Time": time}
        return mess

    def create_csv(self, name):
        head = [["Period", "Timestamp", "Tag_ID", "x", "y", "Time"]]
        path = 'Measurements\\'
        name = name + '.csv'
        file_path = os.path.join(path, name)

        with open(file_path, mode="w", newline="", encoding="utf-8") as self.file:
            self.writer = csv.writer(self.file)
            self.writer.writerows(head)

    def open_csv(self, name, mode):
        path = 'Measurements\\'
        name = name + '.csv'
        file_path = os.path.join(path, name)
        self.file = open(file_path, mode=mode, newline="", encoding="utf-8")

    def edit_csv(self, name, new_data):
        self.open_csv(name, "a")
        columns = list(new_data[0].keys())
        with self.file:
            self.writer = csv.DictWriter(self.file, fieldnames=columns)
            self.writer.writerows(new_data)
        print(f'Počet zapsaných řádků do csv: {len(new_data)}')

    def read_csv(self, name):
        path = 'Measurements\\'
        name = name + '.csv'
        file_path = os.path.join(path, name)
        df = pd.read_csv(file_path)
        return df

    def close_csv(self):
        if self.file:
            self.file.close()
            self.file = None
            self.writer = None


########################################################################################################################
###########################################  ANALYSIS FUNCTIONS  #######################################################
########################################################################################################################


class Analysis:
    def __init__(self):
        super().__init__()
        self.dataRec = DataRecording()

    def merge_data(self, column, data):
        merged_data = data.groupby(column)
        return merged_data

    def merged_values(self, merged_data):
        values_list = list(merged_data.groups.keys())
        return values_list

    def count_distances(self, data):
        dist_dict = {}
        time_dict = {}
        match_dist_dict = {}
        match_time_dict = {}
        merged_data = data.groupby(['Period', 'Tag_ID'])

        for (period, player), group in merged_data:
            group = group.sort_values(by='Timestamp')
            group['distances'] = np.sqrt((group['x'].diff() ** 2) + (group['y'].diff() ** 2))

            group['time'] = pd.to_datetime(group['Time'].str[-12:], format="%H:%M:%S.%f")
            group['time_diffs'] = group['time'].diff()

            continuity_mask = group['Timestamp'].diff() == 1
            total_distance = int(round(group.loc[continuity_mask, 'distances'].sum()))
            total_time = group.loc[continuity_mask, 'time_diffs'].sum()

            if period not in dist_dict:
                dist_dict[period] = {}
                time_dict[period] = {}
            if player not in match_dist_dict:
                match_dist_dict[player] = 0
                match_time_dict[player] = timedelta()

            dist_dict[period][player] = total_distance
            time_dict[period][player] = total_time
            match_dist_dict[player] += total_distance
            match_time_dict[player] += total_time

        dist_dict['Whole match'] = match_dist_dict
        time_dict['Whole match'] = match_time_dict

        return dist_dict, time_dict

    def time2str(self, t):
        total_seconds = t.total_seconds()
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        milliseconds = float((total_seconds - minutes * 60 - seconds))
        if milliseconds >= 0.5:
            seconds += 1
            if seconds >= 60:
                minutes += 1
                seconds -= 60

        time = f"{minutes}:{seconds:02}"
        return time

########################################################################################################################
###########################################  MAIN SCRIPT RUNNER  #######################################################
########################################################################################################################


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
