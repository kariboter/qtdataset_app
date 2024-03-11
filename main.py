import sys
import cv2
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QApplication, QLabel, QGridLayout, QWidget, QPushButton
from pyzbar.pyzbar import decode
import uuid

class VideoWidget(QWidget):
    def __init__(self, camera_index):
        super().__init__()

        self.video_label = QLabel()
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(self.camera_index)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(50)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_qimg = QImage(frame_rgb, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(frame_qimg))

    def take_photo(self, code):


        ret, frame = self.cap.read()
        if ret:
            filename = f"Dataset/{code}/{self.camera_index}_{uuid.uuid1()}.jpg"
            cv2.imwrite(filename, frame)

    def read_barcode(self):
        ret, frame = self.cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            barcodes = decode(frame_rgb)
            for barcode in barcodes:
                barcode_data = barcode.data.decode('utf-8')
                return barcode_data
class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QGridLayout()
        self.folder_code = None
        self.camera_widget1 = VideoWidget(0) # Camera 1
        self.camera_widget2 = VideoWidget(4) # Camera 2

        self.take_photo_button = QPushButton("Take Photo")
        self.take_photo_button.clicked.connect(self.take_photo)

        self.animation = QPropertyAnimation(self.take_photo_button, b"color")

        self.scan_button = QPushButton('Scan Barcode')
        self.scan_button.clicked.connect(self.read_barcode)

        self.code_label = QLabel("Barcode:")

        self.layout.addWidget(self.camera_widget1.video_label, 0, 0)
        self.layout.addWidget(self.camera_widget2.video_label, 0, 1)
        self.layout.addWidget(self.code_label, 3, 0, 1, 2, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.take_photo_button, 1, 0, 1, 2, )
        self.layout.addWidget(self.scan_button, 2, 0, 1, 2)
        self.setLayout(self.layout)

    def take_photo(self):
        if self.folder_code is not None:
            self.animation.setEndValue(Qt.black)
            self.animation.setDuration(200)
            self.animation.start()
            Path(f"Dataset/{self.folder_code}").mkdir(parents=True, exist_ok=True)
            for camera_widget in [self.camera_widget1, self.camera_widget2]:
                camera_widget.take_photo(self.folder_code)
        else:
            self.code_label.setText("Сначала простканируйте штрихкод товара")

    def read_barcode(self):

        for camera_widget in [self.camera_widget1, self.camera_widget2]:
            code = camera_widget.read_barcode()
            self.animation.setStartValue(Qt.red)

            self.folder_code = code
            self.code_label.setText("Barcode: " + str(code))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec())
