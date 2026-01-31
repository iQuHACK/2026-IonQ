"""
GameClient - Player interface for the quantum networking game server.
"""

from typing import Any, Dict, List, Optional, Tuple
import requests
from qiskit import QuantumCircuit, qasm3


class GameClient:
    """Client for interacting with the game server API."""

    def __init__(self, base_url: str = "https://demo-entanglement-distillation-qfhvrahfcq-uc.a.run.app", api_token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.player_id: Optional[str] = None
        self.name: Optional[str] = None
        self._cached_graph: Optional[Dict[str, Any]] = None

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        return headers

    def _get(self, path: str) -> Dict[str, Any]:
        r = requests.get(f"{self.base_url}{path}", headers=self._headers(), timeout=120)
        r.raise_for_status()
        return r.json().get("data", {})

    def _post(self, path: str, payload: Dict[str, Any], require_auth: bool = True) -> Dict[str, Any]:
        if require_auth and not self.api_token:
            return {"ok": False, "error": {"code": "NO_TOKEN", "message": "No API token. Register first."}}
        r = requests.post(f"{self.base_url}{path}", json=payload, headers=self._headers(), timeout=30)
        r.raise_for_status()
        return r.json()

    # ---- Core API Methods ----

    def register(self, player_id: str, name: str, location: str = "remote") -> Dict[str, Any]:
        """Register a new player. Location: "in_person" (Americas) or "remote" (AfroEuroAsia)."""
        resp = self._post("/v1/register", {"player_id": player_id, "name": name, "location": location}, require_auth=False)
        if resp.get("ok"):
            self.player_id = player_id
            self.name = name
            if "data" in resp and "api_token" in resp["data"]:
                self.api_token = resp["data"]["api_token"]
        elif resp.get("error", {}).get("code") == "PLAYER_EXISTS":
            self.player_id = player_id
            self.name = name
        return resp

    def select_starting_node(self, node_id: str) -> Dict[str, Any]:
        """Select a starting node from the candidates provided at registration."""
        if not self.player_id:
            return {"ok": False, "error": {"code": "NOT_REGISTERED", "message": "Not registered"}}
        return self._post("/v1/select_starting_node", {"player_id": self.player_id, "node_id": node_id})

    def restart(self) -> Dict[str, Any]:
        """Reset game progress (keeps player, resets starting node)."""
        if not self.player_id:
            return {"ok": False, "error": {"code": "NOT_REGISTERED", "message": "Not registered"}}
        return self._post("/v1/restart", {"player_id": self.player_id})

    def get_status(self) -> Dict[str, Any]:
        """Get current player status including score, budget, owned nodes/edges."""
        if not self.player_id:
            return {}
        return self._get(f"/v1/status/{self.player_id}")

    def get_graph(self) -> Dict[str, Any]:
        """Get the quantum network graph structure."""
        return self._get("/v1/graph")

    def get_leaderboard(self) -> List[Dict[str, Any]]:
        """Get the current leaderboard."""
        return self._get("/v1/leaderboard")

    def claim_edge(
        self,
        edge: Tuple[str, str],
        circuit: QuantumCircuit,
        flag_bit: int,
        num_bell_pairs: int,
    ) -> Dict[str, Any]:
        """
        Claim an edge by submitting a distillation circuit.

        Args:
            edge: Tuple of (node_a, node_b)
            circuit: 2N-qubit QuantumCircuit with LOCC operations
            flag_bit: Classical bit index for post-selection (0 = success)
            num_bell_pairs: Number of raw Bell pairs (1-8)

        Returns:
            Response with fidelity, success_probability, threshold, and success status.
        """
        if not self.player_id:
            return {"ok": False, "error": {"code": "NOT_REGISTERED", "message": "Not registered"}}

        payload = {
            "player_id": self.player_id,
            "edge": [edge[0], edge[1]],
            "num_bell_pairs": int(num_bell_pairs),
            "circuit_qasm": qasm3.dumps(circuit),
            "flag_bit": int(flag_bit),
        }
        return self._post("/v1/claim_edge", payload)

    # ---- Convenience Methods ----

    def get_cached_graph(self, force: bool = False) -> Dict[str, Any]:
        """Get graph with caching (graph doesn't change during game)."""
        if force or self._cached_graph is None:
            self._cached_graph = self.get_graph()
        return self._cached_graph

    def get_claimable_edges(self) -> List[Dict[str, Any]]:
        """Get edges adjacent to owned nodes that can be claimed."""
        status = self.get_status()
        owned = set(status.get('owned_nodes', []))
        if not owned:
            return []

        graph = self.get_cached_graph()
        claimable = []
        for edge in graph.get('edges', []):
            n1, n2 = edge['edge_id']
            if (n1 in owned) != (n2 in owned):
                claimable.append(edge)
        return claimable

    def get_node_info(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific node."""
        graph = self.get_cached_graph()
        for node in graph.get('nodes', []):
            if node['node_id'] == node_id:
                return node
        return None

    def get_edge_info(self, node_a: str, node_b: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific edge."""
        graph = self.get_cached_graph()
        edge_id = tuple(sorted([node_a, node_b]))
        for edge in graph.get('edges', []):
            if tuple(sorted(edge['edge_id'])) == edge_id:
                return edge
        return None

    def print_status(self):
        """Print a formatted summary of player status."""
        status = self.get_status()
        if not status:
            print("Not registered or no status available.")
            return

        print("=" * 50)
        print(f"Player: {status.get('player_id', 'Unknown')} ({status.get('name', '')})")
        print(f"Score: {status.get('score', 0)} | Budget: {status.get('budget', 0)} bell pairs")
        print(f"Active: {'Yes' if status.get('is_active', False) else 'No'}")
        print(f"Starting node: {status.get('starting_node', 'Not selected')}")

        owned_nodes = status.get('owned_nodes', [])
        owned_edges = status.get('owned_edges', [])
        print(f"Owned: {len(owned_nodes)} nodes, {len(owned_edges)} edges")

        claimable = self.get_claimable_edges()
        print(f"Claimable edges: {len(claimable)}")
        for edge in claimable[:3]:
            print(f"  - {edge['edge_id']}: threshold={edge['base_threshold']:.2f}, difficulty={edge['difficulty_rating']}")
        if len(claimable) > 3:
            print(f"  ... and {len(claimable) - 3} more")
        print("=" * 50)
