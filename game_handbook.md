# iQuHack2026 - Entanglement Distillation Game

A competitive quantum networking game where players build subgraphs by claiming edges through entanglement distillation.

## Game Overview

The game takes place on a graph G(V, E) representing a quantum network:
- **Vertices (V)**: Quantum computers, each hosting utility qubits (points) and bonus bell pairs (resources)
- **Edges (E)**: Potential entanglement links (Bell pairs) between connected nodes

**Objective**: Starting from a single node, build a connected subgraph to maximize total utility qubits while managing a limited budget of distillation bell pairs.

## Core Mechanics

### Claiming Edges
Raw Bell pairs on edges contain noise. To claim an edge, players must design circuits with only local operations and classical corrections (LOCC) to distill a few low-fidelity raw Bell pairs from their budget into a high-fidelity distilled Bell pair.

The following rules are applied:

1. Fidelity (F) of a Bell pair is measured with respect to the $\Phi^{+}$ state: $|\Phi^{+}\rangle = \frac{1}{\sqrt{2}} (|00\rangle + |11\rangle)$, where $F = |\langle \Phi^{+} | \psi \rangle|^2$. 
2. On each edge, all the raw Bell pairs are identical. 

3. On each edge, the initial fidelity of a raw Bell pair is determined by the game.  

4. On each edge, the fidelity threshold for a high-fidelity Bell pair is determined by the game. To claim an edge, players must achieve post-distillation fidelity above the edge's fidelity threshold.

5. Any player can claim any edge - edges have no capacity limit.

6. Players may request N raw Bell pairs from their budget, provided that $N \le 8$ and $ N \le B $.  

7. The game engine initializes these N noisy Bell pairs as an initial state across 2N qubits.

8. The initial state pairs the qubits from outside in:

    Pair 1: Qubit 0 and Qubit 2N-1
    Pair 2: Qubit 1 and Qubit 2N-2
    ...
    Pair N: Qubit N-1 and Qubit N

    Note that Qubit 0 to Qubit N-1 are on the source vertex (Alice's side), and Qubits N to Qubits 2N-1 are on the target vertex (Bob's side). 

9. Players submit a single OpenQASM 3.0 circuit for the full 2N-qubit system. The circuit must respect LOCC constraints:
   - **Local quantum operations only**: Two-qubit gates (CNOT, CZ, SWAP) can only act on qubits within the same side (Alice: 0 to N-1, Bob: N to 2N-1). No quantum gates across the Alice/Bob boundary.
   - **Classical communication allowed**: Feedforward gates can condition on measurement results from either side (e.g., Bob can apply X on his qubit if Alice's measurement result was 1).

10. **Flag-based post-selection**: Players specify a `flag_bit` index. The server simulates all measurement outcomes and keeps only those where the designated classical bit equals 0. This allows players to implement their own post-selection logic:
    - Students compute the flag value using feedforward in their circuit.
    - The server returns both the fidelity (on successful outcomes) and the success probability.

11. The final state after executing the circuit is expected to be a distilled Bell pair on Qubit N-1 (Alice's side) and Qubit N (Bob's side).

12. The maximum number of raw Bell pairs is 8.

13. **Budget is only spent on successful claims** (failed attempts don't cost bell pairs).

### Vertex Rewards & Competition
Vertices have a **capacity** that determines how many players can receive rewards:
- **Claim Strength**: A weighted sum of edge contributions. Each edge contributes: `fidelity × success_probability / sqrt(rank)`, where edges are ranked by fidelity (highest first). The sqrt decay gives: 1st edge gets full weight, 2nd gets 71%, 3rd gets 58%, 4th gets 50%, etc.
- **Success Probability Factor**: Higher success probability means stronger claims. A distillation with 90% fidelity and 50% success probability contributes less than one with 85% fidelity and 100% success probability.
- **Reward Distribution**: Only the top-capacity players (ranked by claim strength) receive the vertex's rewards.
- **Rewards**: Utility qubits (score) and bonus bell pairs.

### Losing Rewards
When a player's claim strength is overtaken by others and they fall outside the top-capacity:
- Their utility qubits (score) from that vertex are **deducted**.
- Their bonus bell pairs from that vertex are **deducted**.
- If a player's bell pair budget reaches zero or negative, **their game ends** (no more actions possible unless they restart).

### Node Properties
- **Utility Qubits** (visible) - Points gained when in top-capacity for this vertex.
- **Bonus Bell Pairs** (visible) - Additional budget granted when in top-capacity for this vertex.
- **Capacity** (visible) - Maximum number of players who can receive rewards from this vertex.

### Edge Properties
- **Noise Type & Probability** (secret) - X/Z flip probabilities on raw Bell pairs.
- **Base Threshold Fidelity** (visible) - Minimum fidelity required to claim.
- **Difficulty Rating** (visible) - Hint about distillation difficulty.

## Game Flow

1. **Registration**: Players register with their location (in-person or remote) and receive 4 candidate starting nodes. In-person players spawn in the Americas, remote players spawn in Europe/Asia/Africa.
2. **Node Selection**: Choose one starting node from candidates (initial budget: 75 bell pairs).
3. **Gameplay**: Claim edges to build your subgraph and strengthen connections to vertices.
4. **Competition**: Monitor your claim strength on vertices - other players may overtake you.
5. **Restart Option**: Players may restart (lose progress, keep same candidates).
6. **End Condition**: Game runs for duration of hackathon event; game ends early for players with zero/negative budget.
