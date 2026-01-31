"""
GraphTool - Client-side visualization for the quantum network graph.
"""

from typing import Dict, List, Optional, Set, Tuple
import networkx as nx

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class GraphTool:
    """Visualization tool for the quantum network graph."""

    def __init__(self, graph_data: Optional[Dict] = None):
        self.graph: nx.Graph = nx.Graph()
        self.nodes: Dict[str, Dict] = {}
        self.edges: Dict[Tuple[str, str], Dict] = {}
        if graph_data:
            self.load_from_json(graph_data)

    def load_from_json(self, graph_data: Dict) -> None:
        """Load graph from server JSON response."""
        self.graph.clear()
        self.nodes.clear()
        self.edges.clear()

        for node in graph_data.get("nodes", []):
            node_id = node["node_id"]
            self.nodes[node_id] = node
            self.graph.add_node(node_id)

        for edge in graph_data.get("edges", []):
            edge_id = tuple(edge["edge_id"])
            self.edges[edge_id] = edge
            self.edges[(edge_id[1], edge_id[0])] = edge
            self.graph.add_edge(edge_id[0], edge_id[1])

    def get_node(self, node_id: str) -> Optional[Dict]:
        return self.nodes.get(node_id)

    def get_edge(self, node1: str, node2: str) -> Optional[Dict]:
        return self.edges.get((node1, node2))

    def get_neighbors(self, node_id: str) -> List[str]:
        if node_id not in self.graph:
            return []
        return list(self.graph.neighbors(node_id))

    def get_claimable_edges(self, owned_nodes: Set[str]) -> List[Tuple[str, str]]:
        """Get edges adjacent to owned nodes leading to unowned nodes."""
        claimable = []
        for node_id in owned_nodes:
            for neighbor in self.get_neighbors(node_id):
                if neighbor not in owned_nodes:
                    claimable.append((node_id, neighbor))
        return claimable

    def get_neighborhood(self, center_nodes: Set[str], radius: int = 1) -> Set[str]:
        """Get all nodes within N hops of center nodes."""
        if not center_nodes:
            return set()

        neighborhood = set(center_nodes)
        frontier = set(center_nodes)

        for _ in range(radius):
            next_frontier = set()
            for node_id in frontier:
                next_frontier.update(self.get_neighbors(node_id))
            neighborhood.update(next_frontier)
            frontier = next_frontier - neighborhood

        return neighborhood

    def render(
        self,
        owned_nodes: Optional[Set[str]] = None,
        radius: int = 2,
        figsize: Tuple[int, int] = (12, 8),
        save_path: Optional[str] = None,
    ) -> None:
        """
        Render the graph focused around owned nodes.

        Args:
            owned_nodes: Set of node IDs owned by player (highlighted green)
            radius: Show nodes within N hops of owned nodes (use -1 for full graph)
            figsize: Figure size
            save_path: If provided, save figure to this path
        """
        if not HAS_MATPLOTLIB:
            print("matplotlib not installed. Install with: pip install matplotlib")
            return

        owned_nodes = owned_nodes or set()

        # Create focused view if owned nodes exist
        if radius >= 0 and owned_nodes:
            visible_nodes = self.get_neighborhood(owned_nodes, radius)
            graph_to_render = self.graph.subgraph(visible_nodes)
        else:
            graph_to_render = self.graph
            visible_nodes = set(self.graph.nodes())

        claimable = set(self.get_claimable_edges(owned_nodes))

        fig, ax = plt.subplots(figsize=figsize)
        pos = nx.spring_layout(graph_to_render, seed=42)

        # Node colors and sizes
        node_colors = ["#4CAF50" if n in owned_nodes else "#2196F3" for n in graph_to_render.nodes()]
        node_sizes = [300 + self.nodes.get(n, {}).get("utility_qubits", 1) * 100 for n in graph_to_render.nodes()]

        nx.draw_networkx_nodes(graph_to_render, pos, node_color=node_colors, node_size=node_sizes, ax=ax)

        # Edge colors
        edge_colors = []
        edge_widths = []
        for u, v in graph_to_render.edges():
            if (u, v) in claimable or (v, u) in claimable:
                edge_colors.append("#FF9800")
                edge_widths.append(3)
            elif u in owned_nodes and v in owned_nodes:
                edge_colors.append("#4CAF50")
                edge_widths.append(2)
            else:
                edge_colors.append("#9E9E9E")
                edge_widths.append(1)

        nx.draw_networkx_edges(graph_to_render, pos, edge_color=edge_colors, width=edge_widths, ax=ax)

        # Labels
        labels = {n: f"{n}\n({self.nodes.get(n, {}).get('utility_qubits', '?')})" for n in graph_to_render.nodes()}
        nx.draw_networkx_labels(graph_to_render, pos, labels, font_size=8, ax=ax)

        edge_labels = {}
        for u, v in graph_to_render.edges():
            edge = self.get_edge(u, v)
            if edge:
                edge_labels[(u, v)] = f"D{edge.get('difficulty_rating', '?')}"
        nx.draw_networkx_edge_labels(graph_to_render, pos, edge_labels, font_size=7, ax=ax)

        title = f"Quantum Network ({len(visible_nodes)}/{len(self.nodes)} nodes)"
        if owned_nodes:
            title += f" - Focused (radius={radius})"
        ax.set_title(title)
        ax.axis("off")

        # Legend
        legend = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#4CAF50', markersize=10, label='Owned'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#2196F3', markersize=10, label='Unowned'),
            plt.Line2D([0], [0], color='#FF9800', linewidth=3, label='Claimable'),
            plt.Line2D([0], [0], color='#9E9E9E', linewidth=1, label='Other'),
        ]
        ax.legend(handles=legend, loc='upper left')

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved to {save_path}")
        else:
            plt.show()

    def print_summary(self, owned_nodes: Optional[Set[str]] = None, radius: int = 2) -> None:
        """Print a text summary of the graph focused around owned nodes."""
        owned_nodes = owned_nodes or set()

        if owned_nodes:
            visible = self.get_neighborhood(owned_nodes, radius)
            nodes_to_show = {k: v for k, v in self.nodes.items() if k in visible}
        else:
            visible = set(self.nodes.keys())
            nodes_to_show = self.nodes

        print("=" * 50)
        print(f"Graph: {len(nodes_to_show)}/{len(self.nodes)} nodes (radius={radius})")
        print(f"Owned: {len(owned_nodes)} nodes")
        print()

        for node_id, node in sorted(nodes_to_show.items()):
            mark = "*" if node_id in owned_nodes else " "
            print(f"  [{mark}] {node_id}: {node.get('utility_qubits', '?')} qubits")

        if owned_nodes:
            claimable = self.get_claimable_edges(owned_nodes)
            print(f"\nClaimable edges: {len(claimable)}")
            for u, v in claimable[:5]:
                edge = self.get_edge(u, v)
                if edge:
                    print(f"  {u} -- {v}: threshold={edge.get('base_threshold', '?'):.2f}")
            if len(claimable) > 5:
                print(f"  ... and {len(claimable) - 5} more")
        print("=" * 50)
