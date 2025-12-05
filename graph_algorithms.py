# graph_algorithms.py

import heapq
import math


def _calculate_distance(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def prim_mst(nodes: dict) -> list:
    if not nodes: return []
    mst_edges = []
    visited = set()
    edges_heap = []
    start_node_id = next(iter(nodes.keys()))
    visited.add(start_node_id)
    for other_id, other_node in nodes.items():
        if other_id != start_node_id:
            distance = _calculate_distance(nodes[start_node_id].position, other_node.position)
            heapq.heappush(edges_heap, (distance, start_node_id, other_id))
    while edges_heap and len(visited) < len(nodes):
        weight, u, v = heapq.heappop(edges_heap)
        if v in visited: continue
        visited.add(v)
        mst_edges.append((u, v))
        for next_id, next_node in nodes.items():
            if next_id not in visited:
                distance = _calculate_distance(nodes[v].position, next_node.position)
                heapq.heappush(edges_heap, (distance, v, next_id))
    return mst_edges


def dijkstra_all_pairs_hops(nodes: dict, edges: list) -> dict:
    if not nodes: return {}
    adj = {node_id: [] for node_id in nodes}
    for edge in edges:
        adj[edge.from_id].append(edge.to_id)
        adj[edge.to_id].append(edge.from_id)
    all_routes = {}
    node_ids = list(nodes.keys())
    for start_node in node_ids:
        distances = {node_id: float('inf') for node_id in node_ids}
        previous_nodes = {node_id: None for node_id in node_ids}
        distances[start_node] = 0
        pq = [(0, start_node)]
        while pq:
            dist, current_node = heapq.heappop(pq)
            if dist > distances[current_node]: continue
            for neighbor in adj[current_node]:
                if distances[current_node] + 1 < distances[neighbor]:
                    distances[neighbor] = distances[current_node] + 1
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(pq, (distances[neighbor], neighbor))
        for end_node in node_ids:
            if start_node == end_node or distances[end_node] == float('inf'): continue
            path = []
            current = end_node
            while current is not None:
                path.append(current)
                current = previous_nodes[current]
            path.reverse()
            all_routes[(start_node, end_node)] = path
    return all_routes


# --- ВОЗВРАЩАЕМ СТАРУЮ, ПРОСТУЮ ФУНКЦИЮ РАСЧЕТА ЗАДЕРЖЕК ---
def calculate_edge_delays(edges: list, avg_packet_size_bits: int):
    """Рассчитывает и обновляет задержку (delay) ТОЛЬКО для каждого ребра в мс."""
    if avg_packet_size_bits <= 0:
        avg_packet_size_bits = 12000  # 1500 байт по умолчанию
    for edge in edges:
        # Используем простую формулу M/M/1, как было раньше
        if edge.capacity <= 0 or edge.flow <= 0 or edge.flow >= edge.capacity:
            edge.delay = float('inf') if edge.flow >= edge.capacity else 0.0
            continue

        flow_mbps = edge.flow
        capacity_mbps = edge.capacity

        # Переводим Мбит/с в пакеты/сек
        flow_pps = (flow_mbps * 1_000_000) / avg_packet_size_bits
        capacity_pps = (capacity_mbps * 1_000_000) / avg_packet_size_bits

        # Формула для времени в системе
        delay_seconds = 1 / (capacity_pps - flow_pps)
        edge.delay = delay_seconds * 1000


# --- ВОЗВРАЩАЕМ СТАРЫЙ, ПРОСТОЙ ПОИСК МАКСИМАЛЬНОЙ ЗАДЕРЖКИ ---
def dijkstra_max_delay_path(nodes: dict, edges: list) -> float:
    """Находит путь с максимальной суммарной задержкой (только по ребрам)."""
    adj = {node_id: [] for node_id in nodes}
    for edge in edges:
        if edge.delay != float('inf'):
            adj[edge.from_id].append((edge.to_id, edge.delay))
            adj[edge.to_id].append((edge.from_id, edge.delay))

    max_delay_found = 0.0
    for start_node_id in nodes.keys():
        distances = {node_id: float('inf') for node_id in nodes.keys()}
        distances[start_node_id] = 0
        pq = [(0, start_node_id)]

        while pq:
            dist, u = heapq.heappop(pq)
            if dist > distances[u]: continue
            for v, weight in adj.get(u, []):
                if distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight
                    heapq.heappush(pq, (distances[v], v))

        valid_distances = [d for d in distances.values() if d != float('inf')]
        if not valid_distances: continue

        current_max = max(valid_distances)
        if current_max > max_delay_found:
            max_delay_found = current_max

    return max_delay_found