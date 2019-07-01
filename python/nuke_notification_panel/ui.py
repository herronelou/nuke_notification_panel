"""
UI elements for nuke notification panel.
"""
import datetime
import nuke
from . import config
from PySide2 import QtWidgets, QtCore, QtGui


class Notification(QtWidgets.QFrame):
    Information = 0
    Warning = 1
    Critical = 2

    def __init__(self, title, message, details=None, mode=0):
        super(Notification, self).__init__()

        self.setObjectName('Notification')

        # Content - All init to None, letting the respective functions to initialize
        self._mode = None
        self._title = None
        self._message = None
        self._details = None
        self._time = datetime.datetime.now()

        # Set Horizontal Layout
        layout = QtWidgets.QHBoxLayout(self)

        # Icon
        self.notification_icon = QtWidgets.QLabel('icon', self)
        layout.addWidget(self.notification_icon)

        # Contents area
        contents = QtWidgets.QVBoxLayout()
        self.title_widget = QtWidgets.QLabel()
        contents.addWidget(self.title_widget)
        self.message_widget = QtWidgets.QLabel()
        contents.addWidget(self.message_widget)

        layout.addLayout(contents, stretch=1)

        dismiss_button = QtWidgets.QToolButton()
        dismiss_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_TitleBarCloseButton))
        dismiss_button.clicked.connect(self.dismiss)

        layout.addWidget(dismiss_button)

        # Initialize all the values
        self.setMode(mode)
        self.setTitle(title)
        self.setMessage(message)
        self.setDetails(details)

        self.setLayout(layout)

    def dismiss(self):
        self.setVisible(False)
        self.deleteLater()

    def popup(self):
        """ Display full content in a message box"""
        message_box = QtWidgets.QMessageBox()
        message_box.setWindowTitle(self.title())
        message_box.setText(self.title())
        message_box.setInformativeText(self.message())
        message_box.setDetailedText(self.details())
        if self.mode() == self.Information:
            message_box.setIcon(message_box.Information)
        elif self.mode() == self.Warning:
            message_box.setIcon(message_box.Warning)
        elif self.mode() == self.Critical:
            message_box.setIcon(message_box.Critical)

        message_box.addButton("Dismiss", message_box.DestructiveRole)
        message_box.addButton("Close", message_box.RejectRole)

        result = message_box.exec_()
        if result == 0:  # The roles defined above don't seem trustworthy, use 0 instead.
            self.dismiss()

    def mode(self):
        """ Get the notification mode"""
        return self._mode

    def setMode(self, mode):
        """Set Notification mode (Changes the icon)"""
        self._mode = mode
        if mode == self.Warning:
            icon = self.style().standardIcon(QtWidgets.QStyle.SP_MessageBoxWarning)
        elif mode == self.Critical:
            icon = self.style().standardIcon(QtWidgets.QStyle.SP_MessageBoxCritical)
        else:
            icon = self.style().standardIcon(QtWidgets.QStyle.SP_MessageBoxInformation)
        self.notification_icon.setPixmap(icon.pixmap(20, 20))

    def message(self):
        """ Get the notification message """
        return self._message

    def truncatedMessage(self):
        """ Get the truncated message"""
        return self._message[:145] + "[...]" if len(self._message) > 150 else self._message

    def setMessage(self, message):
        """ Set the notification message"""
        if isinstance(message, basestring):
            self._message = message
            self.message_widget.setWordWrap(True)
            self.message_widget.setText(self.truncatedMessage())

        else:
            raise TypeError("setMessage requires string argument")

    def title(self):
        """ Get the notification title """
        return self._title

    def setTitle(self, title):
        """ Set the notification message"""
        if isinstance(title, basestring):
            self._title = title
            time = self._time.strftime('%-H:%M')
            self.title_widget.setText("<b>{0}</b> ({1})".format(title, time))
        else:
            raise TypeError("setTitle requires string argument")

    def details(self):
        """ Get the notification details """
        return self._details

    def setDetails(self, details):
        """ Set the notification message"""
        if isinstance(details, basestring) or details is None:
            self._details = details
        else:
            raise TypeError("setDetails requires string or None argument")

    def enterEvent(self, event):
        color = get_nuke_color('UIHighlightColor')
        self.setStyleSheet("#Notification {background-color:rgb(%d, %d, %d);}" % color)

    def leaveEvent(self, event):
        self.setStyleSheet("#Notification {background-color:none;}")

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.popup()


class NotificationDrawer(QtWidgets.QWidget):

    new_notification = QtCore.Signal(Notification)

    def __init__(self):
        super(NotificationDrawer, self).__init__()

        # UI
        self.setFixedSize(config.PANEL_WIDTH, config.PANEL_HEIGHT)

        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        self.header = QtWidgets.QHBoxLayout()
        vbox.addLayout(self.header)

        body_container = QtWidgets.QWidget()
        self.body = QtWidgets.QVBoxLayout()
        self.body.addStretch(1)
        body_container.setLayout(self.body)

        # Scroll Area Properties
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(body_container)

        vbox.addWidget(scroll)

        # Add dismiss all Button
        dismiss_button = QtWidgets.QPushButton('Dismiss All')
        dismiss_button.clicked.connect(self.dismissAll)
        self.header.addWidget(dismiss_button)

        self.setGeometry(300, 300, 400, 500)
        self.setWindowTitle('Notifications')

    def notify(self, notification):
        """ Add a notification to the notification panel"""
        self.body.insertWidget(0, notification)  # Insert before the stretch
        self.new_notification.emit(notification)

    def dismissAll(self):
        """ Dismiss all current notifications """
        widgets = (self.body.itemAt(i).widget() for i in range(self.body.count()))
        for widget in widgets:
            if isinstance(widget, Notification):
                widget.dismiss()


class NotificationDrawerAction(QtWidgets.QWidgetAction):
    def __init__(self, parent):
        super(NotificationDrawerAction, self).__init__(parent)
        drawer = NOTIFICATION_PANEL
        self.setDefaultWidget(drawer)

        if _TRAY:
            _TRAY.setContextMenu(parent.parent())
            drawer.new_notification.connect(_TRAY.showNotification)


class NotificationTray(QtWidgets.QSystemTrayIcon):
    """ A Notification icon that shows in the OS's task bar/system tray. """
    def __init__(self):
        super(NotificationTray, self).__init__()

        self._latest_notification = None

        self.setToolTip("Nuke Notification Panel")

        if config.SYSTEM_TRAY_ICON_PATH:
            self.setIcon(QtGui.QIcon(config.SYSTEM_TRAY_ICON_PATH))
        else:
            icon = QtWidgets.QApplication.windowIcon()
            self.setIcon(icon)

        self.messageClicked.connect(self.notificationClicked)

    def showNotification(self, notification):
        """ Accepts our custom notification class and shows a representation of it

        :type notification: Notification
        """
        self._latest_notification = notification
        title = notification.title()
        message = notification.truncatedMessage()
        # Can't pass the icon directly, added in Qt5.9, use the mode to mimic behavior.
        if notification.mode() == notification.Warning:
            icon = self.Warning
        elif notification.mode() == notification.Critical:
            icon = self.Critical
        else:
            icon = self.Information

        self.showMessage(title, message, icon)

    def notificationClicked(self):
        """ Notification Tray message was clicked by the user"""
        notification = self._latest_notification
        if notification:
            notification.popup()


def get_nuke_color(knob_name):
    """ Get a color tuple for a given nuke preference knob

    :param str knob_name: Name of the knob to extract the color from
    :retrun: A tuple (int, int, int) with 8bit color values, ie. (255, 255, 0)"""
    prefs = nuke.toNode("preferences")
    color_int = prefs[knob_name].value()
    hex_value = '%08x' % color_int
    r = int(hex_value[0:2], 16)
    g = int(hex_value[2:4], 16)
    b = int(hex_value[4:6], 16)

    return r, g, b


# For convenience, keep a global reference to the notification panel and system tray
NOTIFICATION_PANEL = NotificationDrawer()

if config.USE_SYSTEM_TRAY:
    _TRAY = NotificationTray()
    _TRAY.show()
else:
    _TRAY = None