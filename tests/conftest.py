"""Gemeinsame Fixtures: die Mini-Instanz, an der jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def mini():
    """Vier Verbände mit 900, 600, 300 und 100 Mitgliedern (Summe 1900). Handrechnung: bei 7 Sitzen gibt Hamilton [3, 2, 1, 1], bei 8 Sitzen [4, 3, 1, 0] (Alabama-Paradox)."""
    return [900, 600, 300, 100]
