# python_project/stage4_logic.py

import math
import heapq
from typing import List, Dict
# Снова импортируем наши модели
from data_models import Node, Edge

# Средний размер пакета в битах (1500 байт) для формулы M/M/1
AVG_PACKET_SIZE_BITS = 1500 * 8


def calculate_edge_delays(edges: List[Edge]):
    """
    Рассчитывает и обновляет задержку (delay) для каждого ребра в миллисекундах.
    Использует формулу из теории массового обслуживания (M/M/1).
    """
    for edge in edges:
        if edge.capacity <= 0 or edge.flow <= 0:
            edge.delay = 0.0
            continue

        # Ключевая проверка: если поток равен или превышает пропускную способность,
        # канал перегружен, задержка стремится к бесконечности.
        if edge.flow >= edge.capacity:
            edge.delay = float('inf')
            continue

        # Переводим Мбит/с в пакеты/сек
        flow_pps = (edge.flow * 1_000_000) / AVG_PACKET_SIZE_BITS
        capacity_pps = (edge.capacity * 1_000_000) / AVG_PACKET_SIZE_BITS

        # Формула для времени в системе (очередь + обслуживание)
        delay_seconds = 1 / (capacity_pps - flow_pps)

        # Переводим в миллисекунды
        edge.delay = delay_seconds * 1000


def calculate_total_cost(nodes: Dict[int, Node], edges: List[Edge]) -> float:
    """Рассчитывает общую стоимость проекта: сумма стоимостей узлов и ребер."""
    node_costs = sum(node.cost for node in nodes.values())
    edge_costs = sum(edge.cost for edge in edges)
    return node_costs + edge_costs


def find_max_delay(nodes: Dict[int, Node], edges: List[Edge]) -> float:
    """
    Находит максимальную суммарную задержку между любой парой узлов в сети.
    Использует алгоритм Дейкстры, где весом ребер является их 'delay'.
    """
    if not nodes or not edges:
        return 0.0

    # Создаем удобное представление графа (список смежности)
    adj = {node_id: [] for node_id in nodes.keys()}
    for edge in edges:
        # Пропускаем перегруженные ребра
        if edge.delay == float('inf'):
            continue
        adj[edge.from_id].append((edge.to_id, edge.delay))
        adj[edge.to_id].append((edge.from_id, edge.delay))

    max_delay_found = 0.0

    # Запускаем Дейкстру от каждого узла
    for start_node_id in nodes.keys():
        distances = {node_id: float('inf') for node_id in nodes.keys()}
        distances[start_node_id] = 0
        pq = [(0, start_node_id)]  # (distance, node_id)

        while pq:
            current_dist, u = heapq.heappop(pq)
            if current_dist > distances[u]:
                continue
            for v, weight in adj.get(u, []):
                if distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight
                    heapq.heappush(pq, (distances[v], v))

        # Находим максимальную задержку от start_node до любого другого узла
        current_max = max(d for d in distances.values() if d != float('inf'))
        if current_max > max_delay_found:
            max_delay_found = current_max

    return max_delay_found