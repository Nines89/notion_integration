import sys
import re
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox

class LinkSaver(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Save Notion Link")
        self.setGeometry(200, 200, 400, 120)

        layout = QVBoxLayout()

        # Campo per inserire il link
        self.link_input = QLineEdit(self)
        self.link_input.setPlaceholderText("Insert Notion Link...")
        layout.addWidget(self.link_input)

        # Bottone submit
        self.submit_button = QPushButton("Submit", self)
        self.submit_button.clicked.connect(self.save_link)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def save_link(self):
        link = self.link_input.text().strip()

        # Regex di controllo: link notion con ID (32 caratteri hex)
        pattern = r"^https:\/\/www\.notion\.so\/[A-Za-z0-9\-]+([a-f0-9]{32})(\?.*)?$"

        if re.match(pattern, link):
            try:
                # Svuota e scrive il file
                with open("link.txt", "w", encoding="utf-8") as f:
                    f.write(link + "\n")
                QMessageBox.information(self, "Success", "Link saved!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Impossible to save the link:\n{e}")
        else:
            QMessageBox.warning(self, "Not Valid Link", "Link is not valid.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LinkSaver()
    window.show()
    sys.exit(app.exec())
