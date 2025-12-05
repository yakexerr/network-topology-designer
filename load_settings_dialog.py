from PyQt6.QtWidgets import QDialog
from settings_dialog import Ui_SettingsDialog # Импортируем сгенерированный UI

class LoadSettingsDialog(QDialog, Ui_SettingsDialog):
    def __init__(self, high_load_val, overload_val, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Устанавливаем начальные значения, полученные из главного окна
        self.highLoadSpinBox.setValue(high_load_val * 100) # Переводим 0.6 в 60%
        self.overloadSpinBox.setValue(overload_val * 100)

    def get_values(self):
        """Возвращает новые значения, выбранные пользователем."""
        # Возвращаем значения, переведенные обратно в доли (60% -> 0.6)
        return {
            "high": self.highLoadSpinBox.value() / 100.0,
            "overload": self.overloadSpinBox.value() / 100.0
        }