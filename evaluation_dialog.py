# evaluation_dialog.py

from PyQt6.QtWidgets import (QDialog, QTableWidget, QVBoxLayout,
                             QTableWidgetItem, QLabel, QHeaderView, QAbstractItemView)

class EvaluationDialog(QDialog):
    def __init__(self, edges, total_cost, node_cost, base_edge_cost, capacity_edge_cost,
                 max_delay, avg_delay, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Итоговая оценка проекта")
        self.setMinimumSize(800, 500)

        # Отображение итогов
        cost_details_text = (
            f"<b>Общая стоимость проекта: {total_cost:.2f} у.е.</b><br>"
            f"<i> - Стоимость узлов: {node_cost:.2f} у.е.</i><br>"
            f"<i> - Аренда каналов (от длины): {base_edge_cost:.2f} у.е.</i><br>"
            f"<i> - Оборудование (от проп. способности): {capacity_edge_cost:.2f} у.е.</i>"
        )
        total_cost_label = QLabel(cost_details_text)

        max_delay_text = f"{max_delay:.4f} мс" if max_delay != float('inf') else "∞ (сеть перегружена)"
        max_delay_label = QLabel(f"<b>Максимальная задержка в сети:</b> {max_delay_text}")

        # --- ИЗМЕНЕНИЕ 2: Создаем новый QLabel для средней задержки ---
        # Назовем его "Средняя задержка в сети"
        # Он будет находиться под максимальной задержкой.
        avg_delay_text = f"{avg_delay:.4f} мс" if avg_delay > 0 else "N/A"
        avg_delay_label = QLabel(f"<b>Средняя задержка в сети:</b> {avg_delay_text}")

        # Настройка таблицы (остается без изменений)
        self.table = QTableWidget()
        # ... (весь код настройки таблицы остается прежним) ...
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Откуда", "Куда", "Поток (Мбит/с)", "Проп. сп. (Мбит/с)",
            "Загрузка (%)", "Задержка (мс)", "Стоимость"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.populate_table(edges)

        # --- ИЗМЕНЕНИЕ 3: Добавляем новый QLabel в компоновку окна ---
        layout = QVBoxLayout(self)
        layout.addWidget(total_cost_label)
        layout.addWidget(max_delay_label)
        layout.addWidget(avg_delay_label)  # <-- ВОТ ОН
        layout.addWidget(self.table)

    def populate_table(self, edges):
        # Сортируем ребра, чтобы вывод был всегда одинаковым
        sorted_edges = sorted(edges, key=lambda e: (e.from_id, e.to_id))
        self.table.setRowCount(len(sorted_edges))

        for row, edge in enumerate(sorted_edges):
            utilization = (edge.flow / edge.capacity * 100) if edge.capacity > 0 else 0
            delay_text = f"{edge.delay:.4f}" if edge.delay != float('inf') else "∞ (Перегрузка)"

            self.table.setItem(row, 0, QTableWidgetItem(str(edge.from_id)))
            self.table.setItem(row, 1, QTableWidgetItem(str(edge.to_id)))
            self.table.setItem(row, 2, QTableWidgetItem(f"{edge.flow:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{edge.capacity:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{utilization:.2f} %"))
            self.table.setItem(row, 5, QTableWidgetItem(delay_text))
            self.table.setItem(row, 6, QTableWidgetItem(f"{edge.cost:.2f}"))
