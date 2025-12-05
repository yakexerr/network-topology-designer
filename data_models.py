# python_project/data_models.py

from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class Node:
    """Точное соответствие вашему C# классу Node."""
    id: int
    name: str
    position: Tuple[int, int]  # В Python кортеж (x, y) удобнее, чем отдельный класс Point
    cost: float



# Это аналог вашего C# класса TrafficDemand
@dataclass
class TrafficDemand:
    from_id: int
    to_id: int
    volume: float

@dataclass
class Edge:
    from_id: int  # В C# у вас 'From', в Python принято from_id (snake_case)
    to_id: int  # Аналогично 'To' -> to_id

    # Свойства, задаваемые на Этапе 3
    capacity: float = 0.0

    # Свойства, вычисляемые при создании или перемещении
    length: float = 0.0  # В C# у вас 'Leght'
    cost: float = 0.0

    # Расчетные свойства для Этапа 4
    delay: float = 0.0

    # Это свойство вычисляется на Этапе 3, сохраним его здесь
    flow: float = 0.0