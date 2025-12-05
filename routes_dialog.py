from PyQt6.QtWidgets import (QWidget, QTableWidget, QVBoxLayout, QAbstractItemView,
                             QTableWidgetItem, QLineEdit, QFormLayout, QLabel)
from PyQt6.QtCore import pyqtSignal, Qt


class RoutesDialog(QWidget):
    routeSelected = pyqtSignal(list)
    finished = pyqtSignal()

    def __init__(self, nodes, routes, parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Window)

        self.setWindowTitle("Рассчитанные маршруты")
        self.setMinimumSize(700, 500)  # Немного увеличим окно

        self.full_paths = []

        # --- ШАГ 1: Создаем виджеты для поиска ---
        self.from_search_edit = QLineEdit(self)
        self.to_search_edit = QLineEdit(self)

        # Создаем удобную компоновку для полей поиска
        search_layout = QFormLayout()
        search_layout.addRow(QLabel("Поиск Откуда:"), self.from_search_edit)
        search_layout.addRow(QLabel("Поиск Куда:"), self.to_search_edit)

        # --- ШАГ 2: Настраиваем таблицу (как и раньше) ---
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Откуда", "Куда", "Хопов", "Маршрут"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.populate_table(nodes, routes)

        # --- ШАГ 3: Привязываем сигналы ---
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        # Сигнал textChanged срабатывает при каждом изменении текста в поле
        self.from_search_edit.textChanged.connect(self.filter_routes)
        self.to_search_edit.textChanged.connect(self.filter_routes)

        # --- ШАГ 4: Собираем основной layout ---
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(search_layout)  # Добавляем поля поиска сверху
        main_layout.addWidget(self.table)  # Добавляем таблицу под ними

    def populate_table(self, nodes, routes):
        # ... (этот метод остается БЕЗ ИЗМЕНЕНИЙ) ...
        sorted_routes = sorted(routes.items())
        for (from_id, to_id), path in sorted_routes:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.full_paths.append(path)
            from_node_name = nodes[from_id].name
            to_node_name = nodes[to_id].name
            hop_count = len(path) - 1
            path_str = " -> ".join(nodes[node_id].name for node_id in path)
            self.table.setItem(row_position, 0, QTableWidgetItem(from_node_name))
            self.table.setItem(row_position, 1, QTableWidgetItem(to_node_name))
            self.table.setItem(row_position, 2, QTableWidgetItem(str(hop_count)))
            self.table.setItem(row_position, 3, QTableWidgetItem(path_str))

    def on_selection_changed(self):
        # ... (этот метод остается БЕЗ ИЗМЕНЕНИЙ) ...
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows: return
        selected_row_index = selected_rows[0].row()
        selected_path = self.full_paths[selected_row_index]
        self.routeSelected.emit(selected_path)

    # --- НОВЫЙ МЕТОД ДЛЯ ФИЛЬТРАЦИИ ---
    def filter_routes(self):
        """Скрывает/показывает строки в таблице на основе текста в полях поиска."""
        # Получаем текст из полей, приводим к нижнему регистру для поиска без учета регистра
        from_filter = self.from_search_edit.text().lower()
        to_filter = self.to_search_edit.text().lower()

        # Проходим по каждой строке таблицы
        for row in range(self.table.rowCount()):
            # Получаем текст из ячеек "Откуда" и "Куда"
            from_item = self.table.item(row, 0)
            to_item = self.table.item(row, 1)

            # Проверяем, что ячейки существуют
            if not from_item or not to_item:
                continue

            # Проверяем, содержится ли текст из фильтра в тексте ячейки
            from_match = from_filter in from_item.text().lower()
            to_match = to_filter in to_item.text().lower()

            # Если оба фильтра совпадают (или фильтры пустые), показываем строку. Иначе - скрываем.
            if from_match and to_match:
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)

    def closeEvent(self, event):
        """Срабатывает, когда пользователь закрывает окно."""
        self.finished.emit()  # Отправляем сигнал, что мы закрылись
        super().closeEvent(event)  # Выполняем стандартное закрытие