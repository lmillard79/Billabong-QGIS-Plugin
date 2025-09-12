import os

from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox, QPushButton, QDialog, QLineEdit, QTextEdit, QComboBox
from PyQt5 import uic
from qgis.core import QgsSettings
from qgis.gui import (
    QgsFileWidget,
    QgsOptionsPageWidget,
    QgsOptionsWidgetFactory,
)

DESIGNER, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "settings.ui")
)


class BillabongOptionsFactory(QgsOptionsWidgetFactory):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    def icon(self):
        return QIcon(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "img", "WRM_DROPLET.png")
        )

    def createWidget(self, parent):
        return ConfigOptionsPage(parent, self.plugin)


class ConfigOptionsPage(QgsOptionsPageWidget, DESIGNER):

    def __init__(self, parent, plugin):
        super().__init__(parent)
        self.plugin = plugin
        self.setupUi(self)
        self.file_widget = self.findChild(QgsFileWidget, "custom_qlr_file")
        self.feedback_button = self.findChild(QPushButton, "feedbackButton")

        # Connect the feedback button
        if self.feedback_button:
            self.feedback_button.clicked.connect(self.show_feedback_dialog)

        self.load_settings()

    def helpKey(self):
        return "settings"

    def load_settings(self):
        """Load the saved settings"""
        settings = QgsSettings()
        file_path = settings.value("custom_qlr_file", "", type=str)
        self.file_widget.setFilePath(file_path)

    def apply(self):
        """Save the current settings"""
        settings = QgsSettings()
        file_path = self.file_widget.filePath()
        settings.setValue("custom_qlr_file", file_path)

        self.plugin.reload_menu()
        return True

    def show_feedback_dialog(self):
        """Show a feedback dialog to the user."""
        try:
            # Load the feedback dialog UI
            feedback_dialog_ui_path = os.path.join(os.path.dirname(__file__), "feedback_dialog.ui")
            dialog = QDialog()
            uic.loadUi(feedback_dialog_ui_path, dialog)
            
            # Connect the OK button to submit feedback
            dialog.buttonBox.accepted.connect(lambda: self.submit_feedback(dialog))
            
            dialog.exec_()
        except Exception as e:
            # If UI file is not found, show a simple message box
            QMessageBox.information(
                self,
                "Billabong Feedback",
                "Thank you for using Billabong!\n\n"
                "To provide feedback, please create an issue on our GitHub repository at:\n"
                "https://github.com/lmillard79/Billabong/issues\n\n"
                
            )
    
    def submit_feedback(self, dialog):
        """Handle feedback submission."""
        # Get feedback data from dialog
        name = dialog.findChild(QLineEdit, "nameLineEdit").text()
        email = dialog.findChild(QLineEdit, "emailLineEdit").text()
        feedback_type = dialog.findChild(QComboBox, "feedbackTypeComboBox").currentText()
        feedback_text = dialog.findChild(QTextEdit, "feedbackTextEdit").toPlainText()
        
        # Check if feedback text is provided
        if not feedback_text.strip():
            QMessageBox.warning(dialog, "Feedback Submission", "Please enter your feedback before submitting.")
            return
        
        # Create feedback message
        feedback_message = f"""
Billabong Plugin Feedback

Name: {name or "Not provided"}
Email: {email or "Not provided"}
Type: {feedback_type}

Feedback:
{feedback_text}
        """
        
        # Show confirmation message
        QMessageBox.information(
            dialog,
            "Feedback Submitted",
            "Thank you for your feedback!\n\n"
            "To officially submit your feedback, please create an issue on our GitHub repository at:\n"
            "https://github.com/lmillard79/Billabong/issues\n\n"            
            "Your feedback:\n"
            f"{feedback_message}"
        )
