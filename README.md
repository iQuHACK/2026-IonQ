# iQuHack 2026 - Quantum Entanglement Distillation Game

A competitive quantum networking game where players build subgraphs by claiming edges through entanglement distillation.

## Quick Start

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start Playing

Open `demo.ipynb` in Jupyter or VS Code:

```bash
jupyter notebook demo.ipynb
```

The notebook walks you through registration, gameplay, and circuit design.

---

## Game Overview

**Objective**: Build a quantum network subgraph to maximize your score.

**How It Works**:
1. Register with a unique player ID
2. Select a starting node from candidates
3. Design distillation circuits to improve noisy Bell pair fidelity
4. Claim edges by beating fidelity thresholds
5. Earn points from nodes with utility qubits
6. Manage your limited bell pair budget

**Key Mechanics**:
- **Graph**: Quantum network with nodes (utility qubits) and edges (entanglement links)
- **Distillation**: Submit circuits to purify noisy Bell pairs
- **Thresholds**: Achieve fidelity >= threshold to claim an edge
- **Budget**: Limited bell pairs for distillation attempts
- **Scoring**: Sum of utility qubits from owned nodes

---

## Repository Structure

```
iQuHack2026/
├── demo.ipynb         # Interactive tutorial - START HERE
├── client.py          # GameClient class (API wrapper)
├── visualization.py   # GraphTool class (graph rendering)
├── game_handbook.md   # Detailed game rules
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

---

## SDK Usage

### GameClient

```python
from client import GameClient

client = GameClient()
result = client.register("player_id", "Name", location="remote")

# Select starting node
client.select_starting_node(node_id)

# Get claimable edges
claimable = client.get_claimable_edges()

# Claim an edge with a circuit
result = client.claim_edge(edge, circuit, flag_bit, num_bell_pairs)

# Check status
client.print_status()
```

### GraphTool

```python
from visualization import GraphTool

viz = GraphTool(client.get_cached_graph())
owned = set(status.get('owned_nodes', []))

# Render focused view (nodes within 2 hops)
viz.render(owned, radius=2)

# Text summary
viz.print_summary(owned)
```

---

## API Endpoints

Base URL: `https://demo-entanglement-distillation-qfhvrahfcq-uc.a.run.app`

**Public**:
- `GET /v1/graph` - Get graph structure
- `GET /v1/leaderboard` - Get player rankings

**Protected** (Bearer token required):
- `POST /v1/register` - Register player (returns api_token)
- `POST /v1/select_starting_node` - Choose starting node
- `POST /v1/claim_edge` - Submit distillation circuit
- `GET /v1/status/{player_id}` - Get player status
- `POST /v1/restart` - Reset progress

---

## Strategy Tips

1. **Starting Node**: Balance utility qubits vs. bonus bell pairs
2. **Edge Claiming**: Start with low-difficulty edges
3. **Circuit Design**: More bell pairs improve fidelity but cost more budget
4. **Budget**: Failed attempts are free - only successful claims cost bell pairs

---

## Troubleshooting

**"Module not found"**: Run `pip install -r requirements.txt`

**"Invalid token"**: Re-register or use saved session token

**Visualization not showing**: Install matplotlib: `pip install matplotlib`

---

## Support

See `demo.ipynb` for comprehensive examples. For issues, check the game handbook or ask the organizers.

Good luck!
