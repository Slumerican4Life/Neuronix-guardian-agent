"""
Lyra Quantum Logic Processing Engine
===================================

Quantum-inspired decision making system that maintains superposition states
for unresolved ideas, enabling sophisticated uncertainty handling and
multi-hypothesis reasoning.
"""

import json
import math
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3

class QuantumGateType(Enum):
    HADAMARD = "hadamard"      # Creates superposition
    CNOT = "cnot"              # Creates entanglement
    MEASUREMENT = "measurement" # Collapses superposition
    PHASE = "phase"            # Adjusts amplitudes
    ROTATION = "rotation"      # Rotates state vector

class CollapseReason(Enum):
    USER_CONFIRMATION = "user_confirmation"
    EVIDENCE_THRESHOLD = "evidence_threshold"
    TIMEOUT = "timeout"
    ENTANGLEMENT_CASCADE = "entanglement_cascade"
    MANUAL_OVERRIDE = "manual_override"

@dataclass
class QuantumState:
    """Represents a quantum superposition of multiple possible states"""
    
    id: str
    states: List[str]                    # Possible states
    amplitudes: List[float]              # Probability amplitudes
    phases: List[float]                  # Quantum phases
    is_collapsed: bool = False
    collapsed_state: Optional[str] = None
    collapse_reason: Optional[CollapseReason] = None
    collapse_timestamp: Optional[str] = None
    entangled_with: List[str] = None     # IDs of entangled states
    confidence_threshold: float = 0.8    # Threshold for auto-collapse
    created_at: str = None
    last_modified: str = None
    
    def __post_init__(self):
        if self.entangled_with is None:
            self.entangled_with = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.last_modified is None:
            self.last_modified = self.created_at
        
        # Normalize amplitudes
        self._normalize_amplitudes()
    
    def _normalize_amplitudes(self):
        """Normalize probability amplitudes to ensure they sum to 1"""
        total = sum(abs(amp) ** 2 for amp in self.amplitudes)
        if total > 0:
            self.amplitudes = [amp / math.sqrt(total) for amp in self.amplitudes]
    
    def get_probabilities(self) -> List[float]:
        """Get probability distribution from amplitudes"""
        return [abs(amp) ** 2 for amp in self.amplitudes]
    
    def add_state(self, state: str, amplitude: float, phase: float = 0.0):
        """Add new state to superposition"""
        if self.is_collapsed:
            raise ValueError("Cannot add state to collapsed quantum state")
        
        if state not in self.states:
            self.states.append(state)
            self.amplitudes.append(amplitude)
            self.phases.append(phase)
            self._normalize_amplitudes()
            self.last_modified = datetime.now().isoformat()
    
    def adjust_amplitude(self, state: str, factor: float):
        """Adjust amplitude of specific state"""
        if self.is_collapsed:
            return
        
        try:
            index = self.states.index(state)
            self.amplitudes[index] *= factor
            self._normalize_amplitudes()
            self.last_modified = datetime.now().isoformat()
        except ValueError:
            pass  # State not found
    
    def apply_evidence(self, state: str, evidence_strength: float):
        """Apply evidence to strengthen or weaken a particular state"""
        if self.is_collapsed:
            return
        
        # Evidence strengthens the amplitude
        self.adjust_amplitude(state, 1 + evidence_strength)
        
        # Check if any state exceeds confidence threshold
        probabilities = self.get_probabilities()
        max_prob = max(probabilities)
        
        if max_prob >= self.confidence_threshold:
            max_index = probabilities.index(max_prob)
            self.collapse(self.states[max_index], CollapseReason.EVIDENCE_THRESHOLD)
    
    def collapse(self, chosen_state: Optional[str] = None, reason: CollapseReason = CollapseReason.MANUAL_OVERRIDE) -> str:
        """Collapse superposition to definite state"""
        if self.is_collapsed:
            return self.collapsed_state
        
        if chosen_state is None:
            # Probabilistic collapse based on amplitudes
            probabilities = self.get_probabilities()
            chosen_state = random.choices(self.states, weights=probabilities)[0]
        
        self.is_collapsed = True
        self.collapsed_state = chosen_state
        self.collapse_reason = reason
        self.collapse_timestamp = datetime.now().isoformat()
        self.last_modified = self.collapse_timestamp
        
        return chosen_state
    
    def get_dominant_state(self) -> Tuple[str, float]:
        """Get the most probable state without collapsing"""
        if self.is_collapsed:
            return self.collapsed_state, 1.0
        
        probabilities = self.get_probabilities()
        max_index = probabilities.index(max(probabilities))
        return self.states[max_index], probabilities[max_index]
    
    def get_entropy(self) -> float:
        """Calculate quantum entropy (uncertainty measure)"""
        if self.is_collapsed:
            return 0.0
        
        probabilities = self.get_probabilities()
        entropy = -sum(p * math.log2(p) for p in probabilities if p > 0)
        return entropy

@dataclass
class QuantumDecision:
    """Represents a decision point with quantum superposition"""
    
    id: str
    question: str
    quantum_state: QuantumState
    context: Dict[str, Any]
    dependencies: List[str]              # IDs of decisions this depends on
    affects: List[str]                   # IDs of decisions this affects
    priority: float = 0.5                # 0-1 scale
    deadline: Optional[str] = None       # ISO timestamp
    created_by: str = "system"
    
    def is_ready_for_collapse(self) -> bool:
        """Check if decision is ready to be collapsed"""
        if self.quantum_state.is_collapsed:
            return False
        
        # Check if deadline has passed
        if self.deadline:
            deadline_dt = datetime.fromisoformat(self.deadline)
            if datetime.now() > deadline_dt:
                return True
        
        # Check confidence threshold
        _, confidence = self.quantum_state.get_dominant_state()
        return confidence >= self.quantum_state.confidence_threshold

class QuantumLogicEngine:
    """
    Main quantum logic processing engine for Lyra.
    Manages superposition states, entanglement, and decision collapse.
    """
    
    def __init__(self, db_path: str = "lyra_quantum.db"):
        self.db_path = db_path
        self.quantum_states: Dict[str, QuantumState] = {}
        self.quantum_decisions: Dict[str, QuantumDecision] = {}
        self.entanglement_graph: Dict[str, List[str]] = {}
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for quantum state storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quantum_states (
                id TEXT PRIMARY KEY,
                states TEXT NOT NULL,
                amplitudes TEXT NOT NULL,
                phases TEXT NOT NULL,
                is_collapsed BOOLEAN NOT NULL,
                collapsed_state TEXT,
                collapse_reason TEXT,
                collapse_timestamp TEXT,
                entangled_with TEXT NOT NULL,
                confidence_threshold REAL NOT NULL,
                created_at TEXT NOT NULL,
                last_modified TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quantum_decisions (
                id TEXT PRIMARY KEY,
                question TEXT NOT NULL,
                quantum_state_id TEXT NOT NULL,
                context TEXT NOT NULL,
                dependencies TEXT NOT NULL,
                affects TEXT NOT NULL,
                priority REAL NOT NULL,
                deadline TEXT,
                created_by TEXT NOT NULL,
                FOREIGN KEY (quantum_state_id) REFERENCES quantum_states (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_superposition(
        self,
        question: str,
        options: List[str],
        initial_weights: Optional[List[float]] = None,
        context: Optional[Dict[str, Any]] = None,
        priority: float = 0.5,
        deadline: Optional[str] = None
    ) -> str:
        """Create new quantum superposition for a decision"""
        
        decision_id = f"qd_{uuid.uuid4().hex[:12]}"
        state_id = f"qs_{uuid.uuid4().hex[:12]}"
        
        # Set equal weights if not provided
        if initial_weights is None:
            initial_weights = [1.0 / len(options)] * len(options)
        
        # Create quantum state
        quantum_state = QuantumState(
            id=state_id,
            states=options,
            amplitudes=[math.sqrt(w) for w in initial_weights],  # Convert to amplitudes
            phases=[0.0] * len(options)
        )
        
        # Create quantum decision
        quantum_decision = QuantumDecision(
            id=decision_id,
            question=question,
            quantum_state=quantum_state,
            context=context or {},
            dependencies=[],
            affects=[],
            priority=priority,
            deadline=deadline
        )
        
        # Store in memory and database
        self.quantum_states[state_id] = quantum_state
        self.quantum_decisions[decision_id] = quantum_decision
        self._store_quantum_state(quantum_state)
        self._store_quantum_decision(quantum_decision)
        
        print(f"⚛️ Quantum superposition created: '{question}' with {len(options)} states")
        print(f"   Options: {', '.join(options)}")
        print(f"   Entropy: {quantum_state.get_entropy():.3f}")
        
        return decision_id
    
    def apply_evidence(self, decision_id: str, option: str, evidence_strength: float):
        """Apply evidence to strengthen or weaken a particular option"""
        if decision_id not in self.quantum_decisions:
            return False
        
        decision = self.quantum_decisions[decision_id]
        decision.quantum_state.apply_evidence(option, evidence_strength)
        
        # Update in database
        self._store_quantum_state(decision.quantum_state)
        
        print(f"⚛️ Evidence applied to '{option}': strength {evidence_strength:.3f}")
        
        # Check if state collapsed due to evidence
        if decision.quantum_state.is_collapsed:
            print(f"⚛️ Quantum state collapsed to: '{decision.quantum_state.collapsed_state}'")
            self._handle_collapse_cascade(decision_id)
        
        return True
    
    def create_entanglement(self, decision_id1: str, decision_id2: str, correlation_strength: float = 1.0):
        """Create quantum entanglement between two decisions"""
        if decision_id1 not in self.quantum_decisions or decision_id2 not in self.quantum_decisions:
            return False
        
        decision1 = self.quantum_decisions[decision_id1]
        decision2 = self.quantum_decisions[decision_id2]
        
        # Add to entanglement graph
        if decision_id1 not in self.entanglement_graph:
            self.entanglement_graph[decision_id1] = []
        if decision_id2 not in self.entanglement_graph:
            self.entanglement_graph[decision_id2] = []
        
        self.entanglement_graph[decision_id1].append(decision_id2)
        self.entanglement_graph[decision_id2].append(decision_id1)
        
        # Update quantum states
        decision1.quantum_state.entangled_with.append(decision2.quantum_state.id)
        decision2.quantum_state.entangled_with.append(decision1.quantum_state.id)
        
        # Store updates
        self._store_quantum_state(decision1.quantum_state)
        self._store_quantum_state(decision2.quantum_state)
        
        print(f"⚛️ Quantum entanglement created between decisions")
        print(f"   Decision 1: {decision1.question}")
        print(f"   Decision 2: {decision2.question}")
        
        return True
    
    def collapse_decision(
        self,
        decision_id: str,
        chosen_option: Optional[str] = None,
        reason: CollapseReason = CollapseReason.USER_CONFIRMATION
    ) -> Optional[str]:
        """Collapse quantum decision to definite state"""
        if decision_id not in self.quantum_decisions:
            return None
        
        decision = self.quantum_decisions[decision_id]
        
        if decision.quantum_state.is_collapsed:
            return decision.quantum_state.collapsed_state
        
        # Collapse the quantum state
        result = decision.quantum_state.collapse(chosen_option, reason)
        
        # Update in database
        self._store_quantum_state(decision.quantum_state)
        
        print(f"⚛️ Quantum decision collapsed: '{decision.question}'")
        print(f"   Result: {result}")
        print(f"   Reason: {reason.value}")
        
        # Handle entanglement cascade
        self._handle_collapse_cascade(decision_id)
        
        return result
    
    def _handle_collapse_cascade(self, collapsed_decision_id: str):
        """Handle cascade effects when an entangled decision collapses"""
        if collapsed_decision_id not in self.entanglement_graph:
            return
        
        collapsed_decision = self.quantum_decisions[collapsed_decision_id]
        entangled_decisions = self.entanglement_graph[collapsed_decision_id]
        
        for entangled_id in entangled_decisions:
            if entangled_id in self.quantum_decisions:
                entangled_decision = self.quantum_decisions[entangled_id]
                
                if not entangled_decision.quantum_state.is_collapsed:
                    # Apply influence based on collapsed state
                    collapsed_state = collapsed_decision.quantum_state.collapsed_state
                    
                    # Simple correlation: strengthen similar options
                    for state in entangled_decision.quantum_state.states:
                        if self._states_are_similar(collapsed_state, state):
                            entangled_decision.quantum_state.apply_evidence(state, 0.3)
                    
                    print(f"⚛️ Entanglement cascade: influenced decision '{entangled_decision.question}'")
    
    def _states_are_similar(self, state1: str, state2: str) -> bool:
        """Simple similarity check between states"""
        # Basic keyword matching - could be enhanced with NLP
        words1 = set(state1.lower().split())
        words2 = set(state2.lower().split())
        
        if not words1 or not words2:
            return False
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        similarity = len(intersection) / len(union)
        return similarity > 0.3
    
    def get_pending_decisions(self) -> List[QuantumDecision]:
        """Get all decisions that haven't collapsed yet"""
        return [
            decision for decision in self.quantum_decisions.values()
            if not decision.quantum_state.is_collapsed
        ]
    
    def get_ready_decisions(self) -> List[QuantumDecision]:
        """Get decisions ready for collapse (high confidence or past deadline)"""
        return [
            decision for decision in self.get_pending_decisions()
            if decision.is_ready_for_collapse()
        ]
    
    def process_automatic_collapses(self):
        """Process decisions that are ready for automatic collapse"""
        ready_decisions = self.get_ready_decisions()
        
        for decision in ready_decisions:
            if decision.deadline:
                deadline_dt = datetime.fromisoformat(decision.deadline)
                if datetime.now() > deadline_dt:
                    self.collapse_decision(decision.id, reason=CollapseReason.TIMEOUT)
                    continue
            
            # Check confidence threshold
            dominant_state, confidence = decision.quantum_state.get_dominant_state()
            if confidence >= decision.quantum_state.confidence_threshold:
                self.collapse_decision(decision.id, dominant_state, CollapseReason.EVIDENCE_THRESHOLD)
    
    def get_system_uncertainty(self) -> float:
        """Calculate overall system uncertainty"""
        pending_decisions = self.get_pending_decisions()
        
        if not pending_decisions:
            return 0.0
        
        total_entropy = sum(decision.quantum_state.get_entropy() for decision in pending_decisions)
        weighted_entropy = sum(
            decision.quantum_state.get_entropy() * decision.priority
            for decision in pending_decisions
        )
        
        return weighted_entropy / len(pending_decisions)
    
    def _store_quantum_state(self, state: QuantumState):
        """Store quantum state in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO quantum_states VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            state.id,
            json.dumps(state.states),
            json.dumps(state.amplitudes),
            json.dumps(state.phases),
            state.is_collapsed,
            state.collapsed_state,
            state.collapse_reason.value if state.collapse_reason else None,
            state.collapse_timestamp,
            json.dumps(state.entangled_with),
            state.confidence_threshold,
            state.created_at,
            state.last_modified
        ))
        
        conn.commit()
        conn.close()
    
    def _store_quantum_decision(self, decision: QuantumDecision):
        """Store quantum decision in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO quantum_decisions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            decision.id,
            decision.question,
            decision.quantum_state.id,
            json.dumps(decision.context),
            json.dumps(decision.dependencies),
            json.dumps(decision.affects),
            decision.priority,
            decision.deadline,
            decision.created_by
        ))
        
        conn.commit()
        conn.close()
    
    def get_quantum_status(self) -> Dict[str, Any]:
        """Get comprehensive quantum system status"""
        pending = self.get_pending_decisions()
        ready = self.get_ready_decisions()
        
        return {
            "total_decisions": len(self.quantum_decisions),
            "pending_decisions": len(pending),
            "ready_for_collapse": len(ready),
            "system_uncertainty": self.get_system_uncertainty(),
            "entangled_pairs": len(self.entanglement_graph),
            "average_entropy": sum(d.quantum_state.get_entropy() for d in pending) / len(pending) if pending else 0
        }

# Global instance for Lyra system
lyra_quantum = QuantumLogicEngine()

