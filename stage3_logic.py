# python_project/stage3_logic.py

from typing import List, Dict, Tuple
from collections import defaultdict
# Предполагаем, что data_models.py лежит рядом
from data_models import Edge, TrafficDemand






def calculate_flows_and_capacity(
        edges: List[Edge],
        routes: Dict[Tuple[int, int], List[int]],
        demands: List[TrafficDemand]
):
    """
    Python-версия логики Этапа 3.
    1. Обнуляет старые потоки.
    2. Рассчитывает суммарный поток (flow) на каждом ребре.
    3. Подбирает подходящую пропускную способность (capacity).
    """
    # "Прайс-лист" тарифов, как у вас
    available_capacities = [10, 25, 50, 100, 250, 500, 1000]

    # Шаг 1: Обнуляем потоки на всех ребрах
    for edge in edges:
        edge.flow = 0.0

    # Шаг 2: Рассчитываем суммарные потоки
    # Прогоняем трафик по маршрутам
    for demand in demands:
        route_key = (demand.from_id, demand.to_id)
        if route_key in routes:
            path = routes[route_key]
            # Проходим по каждому сегменту пути
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]

                # Находим соответствующее ребро в нашем списке
                # (неэффективно для больших графов, но просто для примера)
                for edge in edges:
                    if (edge.from_id == u and edge.to_id == v) or \
                            (edge.from_id == v and edge.to_id == u):
                        edge.flow += demand.volume
                        break  # Нашли ребро, выходим из внутреннего цикла

    # Шаг 3: Подбираем пропускную способность для каждого ребра
    for edge in edges:
        required_flow = edge.flow

        # Ищем первый тариф, который больше или равен потоку
        selected_capacity = next((c for c in available_capacities if c >= required_flow), 0)

        if selected_capacity == 0 and required_flow > 0:
            # Если поток больше максимального тарифа, берем максимальный
            selected_capacity = available_capacities[-1]
        elif required_flow == 0:
            # Ставим минимальный тариф, если потока нет
            selected_capacity = available_capacities[0]

        edge.capacity = selected_capacity