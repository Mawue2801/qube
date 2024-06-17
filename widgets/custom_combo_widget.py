from PyQt5.QtWidgets import QComboBox

class CustomComboBox(QComboBox):
    def __init__(self, parent=None):
        super(CustomComboBox, self).__init__(parent)

        self.setStyleSheet("""
            QComboBox {
                border: 2px solid grey;
                border-radius: 5px;
                padding: 3px;
                min-width: 6em;
                padding-right: 20px; /* Add space for the default arrow */
                margin: 5px;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 0px;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
                background-color: lightgrey;
            }
            
            QComboBox:on {
                border: 2px solid purple;
            }
        """)