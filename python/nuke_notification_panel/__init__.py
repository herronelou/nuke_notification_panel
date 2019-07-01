"""
nuke_notification_panel

This module provides a simple notification panel for Nuke.
It is implemented for non-intrusive messages to the user (as opposed to a pop up dialogs).

In order to be consistent with the Nuke API and Qt (PySide2), class properties are made private and interaction is
made via setters and getters. PEP8 naming convention is ignored in favor of camelCase for class methods.
The rest of the code will be following PEP8 conventions.
"""

# imports
import nuke
from . import ui


def addNotificationPanel(menu=None):
    """

    :param menu:
    :return:
    """
    if not menu:
        menu = nuke.menu('Nuke')

    notification_menu = menu.addMenu('Notifications')
    notification_action = notification_menu.action()
    notification_qmenu = notification_action.parent()
    notification_qmenu.addAction(ui.NotificationDrawerAction(notification_action))


def info(title, message, details=None):
    """ Add an information level notification

    :param str title: Title of the notification
    :param str message: Content of the notification
    :param str details: Details of the notification, if required.
    :return:
    """
    _build_notification(title, message, details, ui.Notification.Information)


def warning(title, message, details=None):
    """ Add an information level notification

    :param str title: Title of the notification
    :param str message: Content of the notification
    :param str details: Details of the notification, if required.
    :return:
    """
    _build_notification(title, message, details, ui.Notification.Warning)


def error(title, message, details=None):
    """ Add an information level notification

    :param str title: Title of the notification
    :param str message: Content of the notification
    :param str details: Details of the notification, if required.
    :return:
    """
    _build_notification(title, message, details, ui.Notification.Critical)


def _build_notification(title, message, details, level):
    """ Build a notification widget and add it to the notification panel. """
    notification = ui.Notification(title, message, details, level)
    ui.NOTIFICATION_PANEL.notify(notification)
