"""
FASE 3: Player Movement - A* Pathfinding + RVO Collision Avoidance

Implements realistic player movement with:
- A* pathfinding for goal-directed movement
- RVO (Reciprocal Velocity Obstacles) for collision avoidance
- Smooth animation between positions
- Integration with spatial grid for neighbor queries
"""

from math import sqrt, atan2, cos, sin, pi
from typing import List, Tuple, Optional, Dict, Set
from dataclasses import dataclass
from heapq import heappush, heappop


@dataclass(order=True)
class PathNode:
    """Node for A* pathfinding"""
    f_cost: float
    counter: int = 0  # Tie-breaker for priority queue
    pos: Tuple[float, float] = None
    g_cost: float = 0.0
    h_cost: float = 0.0
    parent: Optional['PathNode'] = None

    def __hash__(self):
        return hash(self.pos)


class AStarPathfinder:
    """
    A* pathfinding algorithm for football field navigation

    Finds shortest path avoiding obstacles (other players)
    """

    def __init__(self, width: float = 100.0, height: float = 70.0, grid_size: float = 2.0):
        self.width = width
        self.height = height
        self.grid_size = grid_size

    def heuristic(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """Euclidean distance heuristic"""
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        return (dx*dx + dy*dy) ** 0.5

    def get_neighbors(self, pos: Tuple[float, float]) -> List[Tuple[float, float]]:
        """Get 8 neighbor positions in grid"""
        x, y = pos
        neighbors = []
        for dx in [-self.grid_size, 0, self.grid_size]:
            for dy in [-self.grid_size, 0, self.grid_size]:
                if dx == 0 and dy == 0:
                    continue
                nx = x + dx
                ny = y + dy
                # Check bounds
                if 0 <= nx <= self.width and 0 <= ny <= self.height:
                    neighbors.append((nx, ny))
        return neighbors

    def find_path(self, start: Tuple[float, float], goal: Tuple[float, float],
                  obstacles: List[Tuple[float, float]] = None, obstacle_radius: float = 2.0) -> List[Tuple[float, float]]:
        """
        Find path from start to goal using A*

        Args:
            start: Starting position
            goal: Goal position
            obstacles: List of obstacle positions
            obstacle_radius: Radius around obstacles to avoid

        Returns: List of waypoints from start to goal
        """
        if obstacles is None:
            obstacles = []

        open_set: List[PathNode] = []
        closed_set: Set[Tuple[float, float]] = set()
        counter = 0

        start_node = PathNode(
            f_cost=self.heuristic(start, goal),
            counter=counter,
            pos=start,
            g_cost=0.0,
            h_cost=self.heuristic(start, goal)
        )
        counter += 1
        heappush(open_set, start_node)

        while open_set:
            current = heappop(open_set)

            if current.pos in closed_set:
                continue

            # Check if reached goal
            dist_to_goal = self.heuristic(current.pos, goal)
            if dist_to_goal < self.grid_size:
                # Reconstruct path
                path = []
                node = current
                while node is not None:
                    path.append(node.pos)
                    node = node.parent
                return list(reversed(path))

            closed_set.add(current.pos)

            # Process neighbors
            for neighbor_pos in self.get_neighbors(current.pos):
                if neighbor_pos in closed_set:
                    continue

                # Check if neighbor is in obstacle
                is_blocked = False
                for obs in obstacles:
                    dist_to_obs = self.heuristic(neighbor_pos, obs)
                    if dist_to_obs < obstacle_radius:
                        is_blocked = True
                        break

                if is_blocked:
                    continue

                # Calculate costs
                move_dist = self.heuristic(current.pos, neighbor_pos)
                g_cost = current.g_cost + move_dist
                h_cost = self.heuristic(neighbor_pos, goal)
                f_cost = g_cost + h_cost

                neighbor_node = PathNode(
                    f_cost=f_cost,
                    counter=counter,
                    pos=neighbor_pos,
                    g_cost=g_cost,
                    h_cost=h_cost,
                    parent=current
                )
                counter += 1
                heappush(open_set, neighbor_node)

        # No path found - return straight line to goal
        return [start, goal]


class RVOAvoidance:
    """
    Reciprocal Velocity Obstacles (RVO) for collision avoidance

    Calculates desired velocity to avoid collisions with other agents
    """

    def __init__(self, max_speed: float = 7.0, agent_radius: float = 0.5, time_horizon: float = 2.0):
        self.max_speed = max_speed
        self.agent_radius = agent_radius
        self.time_horizon = time_horizon

    def velocity_obstacle(self, agent_pos: Tuple[float, float], agent_vel: Tuple[float, float],
                         obstacle_pos: Tuple[float, float], obstacle_vel: Tuple[float, float]) -> Tuple[float, float]:
        """
        Calculate velocity obstacle for one obstacle

        Returns: Adjusted velocity to avoid collision
        """
        # Relative position and velocity
        rel_x = obstacle_pos[0] - agent_pos[0]
        rel_y = obstacle_pos[1] - agent_pos[1]
        rel_vx = obstacle_vel[0] - agent_vel[0]
        rel_vy = obstacle_vel[1] - agent_vel[1]

        # Distance between agents
        dist = (rel_x*rel_x + rel_y*rel_y) ** 0.5
        min_dist = 2 * self.agent_radius

        if dist == 0:
            return agent_vel

        # Time to collision
        dot = rel_x * rel_vx + rel_y * rel_vy
        if dot >= 0:
            # Moving away or parallel
            return agent_vel

        # Calculate collision avoidance
        # Simple approach: adjust velocity perpendicular to relative position
        if dist < min_dist * 2:
            # Close to obstacle - strong avoidance
            perp_x = -rel_y / dist
            perp_y = rel_x / dist

            speed = (agent_vel[0]**2 + agent_vel[1]**2) ** 0.5
            if speed == 0:
                speed = self.max_speed * 0.5

            new_vel = (perp_x * speed, perp_y * speed)
            return new_vel

        return agent_vel

    def calculate_avoidance_velocity(self, agent_pos: Tuple[float, float],
                                    desired_vel: Tuple[float, float],
                                    nearby_agents: List[Dict]) -> Tuple[float, float]:
        """
        Calculate final velocity accounting for nearby agents

        Args:
            agent_pos: Current position
            desired_vel: Desired velocity from pathfinding
            nearby_agents: List of nearby agent dicts with pos/vel

        Returns: Adjusted velocity
        """
        if not nearby_agents:
            return desired_vel

        adjusted_vel = list(desired_vel)

        for agent_data in nearby_agents[:3]:  # Only consider 3 closest
            obs_pos = agent_data.get('pos', agent_pos)
            obs_vel = agent_data.get('vel', (0, 0))

            # Calculate collision avoidance
            adj = self.velocity_obstacle(agent_pos, tuple(adjusted_vel), obs_pos, obs_vel)
            adjusted_vel = list(adj)

        # Limit speed
        speed = (adjusted_vel[0]**2 + adjusted_vel[1]**2) ** 0.5
        if speed > self.max_speed:
            adjusted_vel[0] = adjusted_vel[0] / speed * self.max_speed
            adjusted_vel[1] = adjusted_vel[1] / speed * self.max_speed

        return tuple(adjusted_vel)


class PlayerMovement:
    """
    Manages player movement with pathfinding and collision avoidance
    """

    def __init__(self, player: 'Player', spatial_grid: 'SpatialHashGrid', max_speed: float = 7.0):
        self.player = player
        self.spatial_grid = spatial_grid
        self.max_speed = max_speed

        self.pathfinder = AStarPathfinder(width=100, height=70)
        self.rvo = RVOAvoidance(max_speed=max_speed)

        self.target_pos: Optional[Tuple[float, float]] = None
        self.path: List[Tuple[float, float]] = []
        self.path_index = 0
        self.velocity = (0.0, 0.0)

    def set_target(self, target_pos: Tuple[float, float]) -> None:
        """Set movement target"""
        self.target_pos = target_pos
        self.path_index = 0
        self._recalculate_path()

    def _recalculate_path(self) -> None:
        """Recalculate path to target using A*"""
        if self.target_pos is None:
            return

        # Get all player positions as obstacles
        all_players = self.spatial_grid.get_all_agents()
        obstacles = [
            (p.x, p.y) for p in all_players
            if hasattr(p, 'id') and p.id != self.player.id
        ]

        # Find path
        start = (self.player.x, self.player.y)
        self.path = self.pathfinder.find_path(start, self.target_pos, obstacles, obstacle_radius=2.0)
        self.path_index = 0

    def _get_nearby_agents_data(self) -> List[Dict]:
        """Get data about nearby agents for collision avoidance"""
        nearby = self.spatial_grid.nearby_agents(self.player.x, self.player.y, radius=15)
        agent_data = []
        for agent in nearby:
            if hasattr(agent, 'id') and agent.id != self.player.id:
                agent_data.append({
                    'pos': (agent.x, agent.y),
                    'vel': getattr(agent, 'velocity', (0, 0)),
                    'id': agent.id
                })
        return agent_data

    def update(self, dt: float = 1/60.0) -> None:
        """
        Update player position for this frame

        Args:
            dt: Delta time (seconds)
        """
        if self.target_pos is None:
            self.velocity = (0, 0)
            return

        # Check if reached target
        dist_to_target = ((self.player.x - self.target_pos[0])**2 +
                         (self.player.y - self.target_pos[1])**2) ** 0.5
        if dist_to_target < 1.0:
            self.velocity = (0, 0)
            return

        # Recalculate path if too far from path
        if self.path_index < len(self.path):
            current_waypoint = self.path[self.path_index]
            dist_to_waypoint = ((self.player.x - current_waypoint[0])**2 +
                               (self.player.y - current_waypoint[1])**2) ** 0.5

            if dist_to_waypoint < 2.0:
                self.path_index += 1
            elif self.path_index == 0 and dist_to_waypoint > 10.0:
                self._recalculate_path()

        # Get next waypoint
        if self.path_index < len(self.path):
            waypoint = self.path[self.path_index]
        else:
            waypoint = self.target_pos

        # Calculate desired velocity toward waypoint
        dx = waypoint[0] - self.player.x
        dy = waypoint[1] - self.player.y
        dist = (dx*dx + dy*dy) ** 0.5

        if dist > 0:
            desired_vx = (dx / dist) * self.max_speed
            desired_vy = (dy / dist) * self.max_speed
        else:
            desired_vx, desired_vy = 0, 0

        # Apply collision avoidance
        nearby_agents = self._get_nearby_agents_data()
        self.velocity = self.rvo.calculate_avoidance_velocity(
            (self.player.x, self.player.y),
            (desired_vx, desired_vy),
            nearby_agents
        )

        # Update position
        new_x = self.player.x + self.velocity[0] * dt
        new_y = self.player.y + self.velocity[1] * dt

        # Clamp to field
        new_x = max(0, min(100, new_x))
        new_y = max(0, min(70, new_y))

        # Update in spatial grid
        self.spatial_grid.update_agent_position(self.player.id, new_x, new_y)
        self.player.x = new_x
        self.player.y = new_y
        self.player.current_velocity = self.velocity

    def get_desired_direction(self) -> Tuple[float, float]:
        """Get normalized direction vector"""
        speed = (self.velocity[0]**2 + self.velocity[1]**2) ** 0.5
        if speed == 0:
            return (0, 0)
        return (self.velocity[0] / speed, self.velocity[1] / speed)
