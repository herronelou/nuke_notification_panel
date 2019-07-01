"""
This file provides an example on how to implement the nuke_notification_panel.
The tool is not meant to be used as-is, but be customized per the user's needs.
This requires a basic understanding of Python, and some Qt knowledge if further customizations are required.
"""

import nuke
import nuke_notification_panel as nnp


nnp.addNotificationPanel()  # This adds the notification panel in the default location (main menu)
# nnp.addNotificationPanel(custom_menu=nuke.menu('Nodes'))  # This would add it in another Nuke menu.
# Alternatively, one could decide not to add the notification panel in a menu and implement their own panel.


# Create an example callback to trigger notifications
# Do not keep this in your code, it is only meant as an example implementation,
def node_created_callback():
    node = nuke.thisNode()
    if node.Class() == "Grade":
        nnp.info("Grade Node Created",
                 "Congratulations, you created a Grade node.")
    elif node.Class() == "ColorCorrect":
        nnp.warning("CC Node Created",
                    "Congratulations, you created a Color Correct node.",
                    "If you can see this notification, it probably means that you did not make your own implementation "
                    "of the Nuke notification panel. This tools needs to be customized for your needs.")
    elif node.Class() == "Blur":
        nnp.error("Blur Node Created",
                  "Congratulations, you created a Blur node.",
                  "If you can see this notification, it probably means that you did not make your own implementation "
                  "of the Nuke notification panel. This tools needs to be customized for your needs.")


nuke.addOnUserCreate(node_created_callback)
