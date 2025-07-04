from PyQt5.QtWidgets import (QLabel, QHBoxLayout)

class StatusLayout(QHBoxLayout):

    def __init__(self):
        super().__init__()

        self.tx_label = QLabel('TX: OFF')
        self.rx_label = QLabel('RX: OFF')

        self.addWidget(self.tx_label)
        self.addWidget(self.rx_label)

    def set_tx(self, state: bool):
        state_info = self.state_info(state)
        self.tx_label.setText(f"TX: {state_info['text']}")
        self.tx_label.setStyleSheet(f"color: {state_info['color']}")

    def set_rx(self, state: bool):
        state_info = self.state_info(state)
        self.rx_label.setText(f"RX: {state_info['text']}")
        # self.rx_label.setStyleSheet(f"color: {state_info['color']}")

    def state_info(self, state: bool) -> dict[str, str]:
        return {
            "text": "ON" if state else "OFF",
            "color": "green" if state else "red"
        }