# drawing_canvas.py

import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor
from PyQt6.QtCore import Qt, QPoint, pyqtSignal



class DrawingCanvas(QWidget):
    # --- СИГНАЛЫ для общения с главным окном ---
    # Мы "объявляем" события, которые наш холст может отправлять
    nodeSelected = pyqtSignal(int)  # Отправляет ID выбранного узла
    edgeSelected = pyqtSignal(object)  # Отправляет сам объект ребра
    selectionCleared = pyqtSignal()  # Сообщает, что выделение снято

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = self.parent().parent().parent()

        # --- Переменные для отслеживания действий мышью ---
        self.dragging_node_id = None
        self.drag_offset = QPoint(0, 0)

        # Новые переменные для создания ребра
        self.is_drawing_edge = False
        self.edge_start_node_id = None
        self.edge_start_pos = QPoint(0, 0)
        self.edge_current_pos = QPoint(0, 0)

    # --- Хелпер: найти узел по координатам ---
    def _get_node_at(self, pos: QPoint):
        for node_id, node in self.main_window.nodes.items():
            node_pos = QPoint(*node.position)
            if (pos - node_pos).manhattanLength() < 20:  # Радиус захвата 20px
                return node_id
        return None

    # --- Хелпер: найти ребро по координатам ---
    def _get_edge_at(self, pos: QPoint):
        nodes = self.main_window.nodes
        for edge in self.main_window.edges:
            p1 = QPoint(*nodes[edge.from_id].position)
            p2 = QPoint(*nodes[edge.to_id].position)

            # Простое вычисление расстояния от точки до отрезка
            dx, dy = p2.x() - p1.x(), p2.y() - p1.y()
            if dx == 0 and dy == 0: continue
            t = ((pos.x() - p1.x()) * dx + (pos.y() - p1.y()) * dy) / (dx * dx + dy * dy)

            if 0 <= t <= 1:
                closest_point = p1 + t * (p2 - p1)
                if (pos - closest_point).manhattanLength() < 7:  # Радиус захвата ребра
                    return edge
        return None

    # --- Обработчики событий мыши ---

    def mousePressEvent(self, event: "QMouseEvent"):
        clicked_node_id = self._get_node_at(event.pos())

        if clicked_node_id is not None:
            # --- Кликнули по узлу ---
            self.nodeSelected.emit(clicked_node_id)  # Сообщаем главному окну

            if self.main_window.is_move_mode:
                # РЕЖИМ ПЕРЕМЕЩЕНИЯ
                self.dragging_node_id = clicked_node_id
                node_pos = QPoint(*self.main_window.nodes[clicked_node_id].position)
                self.drag_offset = node_pos - event.pos()
            else:
                # РЕЖИМ СОЗДАНИЯ РЕБРА
                self.is_drawing_edge = True
                self.edge_start_node_id = clicked_node_id
                self.edge_start_pos = QPoint(*self.main_window.nodes[clicked_node_id].position)
                self.edge_current_pos = event.pos()
        else:
            # --- Кликнули не по узлу ---
            clicked_edge = self._get_edge_at(event.pos())
            if clicked_edge:
                # Кликнули по ребру
                self.edgeSelected.emit(clicked_edge)
            else:
                # Кликнули по пустому месту
                self.selectionCleared.emit()

        self.update()  # Перерисоваться в любом случае

    def mouseMoveEvent(self, event: "QMouseEvent"):
        if self.dragging_node_id is not None:
            # Двигаем узел
            node = self.main_window.nodes[self.dragging_node_id]
            new_pos = event.pos() + self.drag_offset
            node.position = (new_pos.x(), new_pos.y())
            self.update()
        elif self.is_drawing_edge:
            # Рисуем временную линию
            self.edge_current_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event: "QMouseEvent"):
        if self.is_drawing_edge:
            self.is_drawing_edge = False
            end_node_id = self._get_node_at(event.pos())

            # Если мы отпустили мышку над другим узлом, создаем ребро
            if end_node_id is not None and end_node_id != self.edge_start_node_id:
                self.main_window.create_edge(self.edge_start_node_id, end_node_id)

            self.update()  # Убрать временную линию

        self.dragging_node_id = None  # В любом случае сбрасываем перетаскивание

    # --- Метод рисования ---

    def paintEvent(self, event):
        if not self.main_window: return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        high_threshold = self.main_window.high_load_threshold
        overload_threshold = self.main_window.overload_threshold

        # Получаем данные из главного окна
        nodes = self.main_window.nodes
        edges = self.main_window.edges

        # --- Создаем набор ID рёбер для быстрой проверки подсветки маршрута ---
        highlighted_edges = set()
        if self.main_window.highlighted_path:
            path = self.main_window.highlighted_path
            for i in range(len(path) - 1):
                highlighted_edges.add(tuple(sorted((path[i], path[i + 1]))))

        # --- 1. Рисуем временную линию для нового ребра ---
        if self.is_drawing_edge:
            pen = QPen(Qt.GlobalColor.gray, 2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawLine(self.edge_start_pos, self.edge_current_pos)

        # --- 2. Рисуем постоянные рёбра (ИСПРАВЛЕННАЯ ЛОГИКА) ---
        for edge in edges:
            # Сначала вычисляем все параметры для текущего ребра
            utilization = 0.0
            if edge.capacity > 0:
                utilization = edge.flow / edge.capacity

            edge_key = tuple(sorted((edge.from_id, edge.to_id)))

            # Затем выбираем "кисть" (pen) на основе этих параметров
            if edge_key in highlighted_edges:
                pen = QPen(QColor("#00FF00"), 5)  # Маршрут
            elif edge is self.main_window.selected_edge:
                pen = QPen(Qt.GlobalColor.red, 4)  # Выделенное ребро
            else:
                # Цветовая индикация загрузки
                if utilization >= overload_threshold:
                    pen = QPen(QColor(139, 0, 0), 3)  # Темно-красный
                elif utilization >= high_threshold:
                    pen = QPen(QColor(255, 165, 0), 2)  # Оранжевый
                else:
                    pen = QPen(Qt.GlobalColor.black, 2)  # Черный

            # И только потом передаем кисть художнику и рисуем
            painter.setPen(pen)

            try:
                p1 = QPoint(*nodes[edge.from_id].position)
                p2 = QPoint(*nodes[edge.to_id].position)

                # Рисуем линию
                painter.drawLine(p1, p2)

                # Рисуем текст (всегда черным цветом для читаемости)
                mid_point = QPoint(int((p1.x() + p2.x()) / 2), int((p1.y() + p2.y()) / 2))
                painter.setPen(QPen(Qt.GlobalColor.black))
                painter.drawText(mid_point, f"{edge.capacity:.0f}")
            except KeyError:
                continue

        # --- 3. Рисуем узлы поверх рёбер ---
        node_radius = 20
        for node_id, node in nodes.items():
            pos = QPoint(*node.position)

            if node is self.main_window.selected_node:
                pen = QPen(Qt.GlobalColor.red, 3)  # Выделенный узел
            else:
                pen = QPen(Qt.GlobalColor.black, 1)  # Обычный узел

            painter.setBrush(QBrush(Qt.GlobalColor.cyan))
            painter.setPen(pen)
            painter.drawEllipse(pos, node_radius, node_radius)

            painter.setPen(QPen(Qt.GlobalColor.black))  # Возвращаем черный для текста
            painter.drawText(pos.x() - 50, pos.y() + node_radius + 15, 100, 20,
                             Qt.AlignmentFlag.AlignCenter, f"{node.id}: {node.name}")

        # --- Рисуем узлы ---
        node_radius = 20
        for node_id, node in nodes.items():
            pos = QPoint(*node.position)

            if node is self.main_window.selected_node:
                pen = QPen(Qt.GlobalColor.red, 3)
            else:
                pen = QPen(Qt.GlobalColor.black, 1)

            painter.setBrush(QBrush(Qt.GlobalColor.cyan))
            painter.setPen(pen)
            painter.drawEllipse(pos, node_radius, node_radius)

            painter.setPen(QPen(Qt.GlobalColor.black))  # Возвращаем черный для текста
            painter.drawText(pos.x() - 50, pos.y() + node_radius + 15, 100, 20,
                             Qt.AlignmentFlag.AlignCenter, f"{node.id}: {node.name}")