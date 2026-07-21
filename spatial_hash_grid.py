"""
Spatial Hash Grid - O(1) Spatial Indexing for 22 Football Players
Used for efficient nearby agent queries in match simulation

Reference: Game Programming Patterns - Spatial Partitioning
Performance: O(1) queries, O(n) updates
"""

from math import floor
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass


@dataclass
class Agent:
    """Represents a player in the spatial grid"""
    id: int
    name: str
    x: float
    y: float
    radius: float = 0.5  # Player collision radius in meters

    def distance_to(self, other: 'Agent') -> float:
        """Euclidean distance to another agent"""
        dx = self.x - other.x
        dy = self.y - other.y
        return (dx*dx + dy*dy) ** 0.5


class SpatialHashGrid:
    """
    O(1) spatial indexing using hash grid.

    Field dimensions:
    - Width: 100m (goal line to goal line)
    - Height: 70m (sideline to sideline)
    - Cell size: 5m (optimal for nearby queries)

    Usage:
    ------
    grid = SpatialHashGrid(cell_size=5, width=100, height=70)
    grid.add_agent(player, x=30, y=35)
    nearby = grid.nearby_agents(x=33, y=36, radius=10)
    """

    def __init__(self, cell_size: float = 5.0, width: float = 100.0, height: float = 70.0):
        """
        Initialize spatial hash grid.

        Args:
            cell_size: Size of each cell (meters). 5m is optimal for nearby queries.
            width: Field width (meters, goal line to goal line)
            height: Field height (meters, sideline to sideline)
        """
        self.cell_size = cell_size
        self.width = width
        self.height = height

        # Grid: {cell_key: [agents]}
        self.grid: Dict[Tuple[int, int], List[Agent]] = {}

        # Agent tracking: {agent_id: (cell_key, agent)}
        self.agent_map: Dict[int, Tuple[Tuple[int, int], Agent]] = {}

        # Pre-compute grid dimensions
        self.grid_width = int(width / cell_size) + 1
        self.grid_height = int(height / cell_size) + 1

        # Stats for profiling
        self.query_count = 0
        self.query_time_ms = 0.0

    def _get_key(self, x: float, y: float) -> Tuple[int, int]:
        """
        Get grid cell key for position (x, y).

        Clamps coordinates to field bounds before hashing.
        Returns: (cell_x, cell_y) tuple
        """
        # Clamp to field bounds
        x = max(0, min(x, self.width))
        y = max(0, min(y, self.height))

        # Get cell coordinates
        cell_x = int(floor(x / self.cell_size))
        cell_y = int(floor(y / self.cell_size))

        return (cell_x, cell_y)

    def add_agent(self, agent: Agent, x: float, y: float) -> None:
        """
        Add agent to grid at position (x, y).

        Args:
            agent: Agent object (must have unique id)
            x: X position (meters)
            y: Y position (meters)
        """
        # Update agent position
        agent.x = x
        agent.y = y

        # Get cell key
        key = self._get_key(x, y)

        # Add to grid
        if key not in self.grid:
            self.grid[key] = []
        self.grid[key].append(agent)

        # Track agent
        self.agent_map[agent.id] = (key, agent)

    def remove_agent(self, agent_id: int) -> bool:
        """
        Remove agent from grid by ID.

        Returns: True if removed, False if not found
        """
        if agent_id not in self.agent_map:
            return False

        key, agent = self.agent_map[agent_id]

        # Remove from grid cell
        if key in self.grid:
            self.grid[key].remove(agent)
            if not self.grid[key]:  # Remove empty cells
                del self.grid[key]

        # Remove from tracking
        del self.agent_map[agent_id]
        return True

    def update_agent_position(self, agent_id: int, new_x: float, new_y: float) -> bool:
        """
        Update agent position. Moves to new cell if necessary.

        Returns: True if cell changed, False otherwise
        """
        if agent_id not in self.agent_map:
            return False

        old_key, agent = self.agent_map[agent_id]
        new_key = self._get_key(new_x, new_y)

        # No cell change - just update position
        if old_key == new_key:
            agent.x = new_x
            agent.y = new_y
            return False

        # Cell changed - remove from old cell, add to new cell
        if old_key in self.grid:
            self.grid[old_key].remove(agent)
            if not self.grid[old_key]:
                del self.grid[old_key]

        # Add to new cell
        if new_key not in self.grid:
            self.grid[new_key] = []
        self.grid[new_key].append(agent)

        # Update agent and tracking
        agent.x = new_x
        agent.y = new_y
        self.agent_map[agent_id] = (new_key, agent)

        return True

    def nearby_agents(self, x: float, y: float, radius: float = 10.0) -> List[Agent]:
        """
        Get all agents within radius of position (x, y).

        This is the key query function. Returns agents in O(1) expected time
        because we only check a constant number of nearby cells.

        Args:
            x: Query X position
            y: Query Y position
            radius: Search radius (meters)

        Returns: List of nearby Agent objects
        """
        center_key = self._get_key(x, y)

        # Calculate how many cells to search based on radius
        # For radius=10 and cell_size=5, we need 2 cells in each direction
        cells_to_check = int(radius / self.cell_size) + 1

        nearby = []
        checked_cells = set()

        # Check all cells within the search radius
        for dx in range(-cells_to_check, cells_to_check + 1):
            for dy in range(-cells_to_check, cells_to_check + 1):
                check_key = (center_key[0] + dx, center_key[1] + dy)

                # Avoid checking same cell twice
                if check_key in checked_cells:
                    continue
                checked_cells.add(check_key)

                # Skip out-of-bounds cells
                if (check_key[0] < 0 or check_key[0] >= self.grid_width or
                    check_key[1] < 0 or check_key[1] >= self.grid_height):
                    continue

                # Add all agents in this cell if within radius
                if check_key in self.grid:
                    for agent in self.grid[check_key]:
                        dx_to_agent = x - agent.x
                        dy_to_agent = y - agent.y
                        dist = (dx_to_agent*dx_to_agent + dy_to_agent*dy_to_agent) ** 0.5
                        if dist <= radius:
                            nearby.append(agent)

        self.query_count += 1
        return nearby

    def get_all_agents(self) -> List[Agent]:
        """Get all agents in the grid"""
        all_agents = []
        for agents_in_cell in self.grid.values():
            all_agents.extend(agents_in_cell)
        return all_agents

    def clear(self) -> None:
        """Clear the grid and all tracking"""
        self.grid.clear()
        self.agent_map.clear()
        self.query_count = 0
        self.query_time_ms = 0.0

    def get_stats(self) -> Dict:
        """Get grid statistics for profiling"""
        return {
            'total_agents': len(self.agent_map),
            'occupied_cells': len(self.grid),
            'total_cells': self.grid_width * self.grid_height,
            'queries': self.query_count,
            'avg_cell_density': len(self.agent_map) / len(self.grid) if self.grid else 0,
        }

    def visualize(self, show_grid: bool = True) -> str:
        """
        ASCII visualization of grid state.

        Shows 22 players on a simplified field representation.
        Useful for debugging.
        """
        # Create 100x70 field
        field = [['.' for _ in range(20)] for _ in range(14)]

        # Plot agents (scaled to ASCII grid)
        for agent in self.get_all_agents():
            grid_x = int(agent.x / self.width * 20)
            grid_y = int(agent.y / self.height * 14)
            grid_x = max(0, min(grid_x, 19))
            grid_y = max(0, min(grid_y, 13))
            field[grid_y][grid_x] = str(agent.id % 10)

        # Render
        lines = []
        lines.append("Field visualization (22 players):")
        lines.append("+" + "=" * 20 + "+")
        for row in field:
            lines.append("|" + "".join(row) + "|")
        lines.append("+" + "=" * 20 + "+")

        return "\n".join(lines)
