#!/usr/bin/env python3
"""
Basic Digital Organism Example
Demonstrates fundamental organism capabilities: genome, metabolism, decision-making

This is the SIMPLEST example to understand DAIOF Framework.
Perfect for: First-time users, tutorials, quick demos

Creator: Nguyễn Đức Cường (alpha_prime_omega)
Framework: DAIOF (Digital Autonomous Intelligent Organism Framework)
Original Creation: October 30, 2025
"""

from digital_ai_organism_framework import DigitalGenome, DigitalOrganism


def main():
    """
    Creates a basic digital organism and demonstrates its core functions.

    This example shows:
    1. How to create a genome (DNA)
    2. How to initialize an organism
    3. How metabolism works (energy management)
    4. How organisms make decisions
    5. How to check organism health
    """

    print("=" * 60)
    print("🧬 BASIC DIGITAL ORGANISM EXAMPLE")
    print("=" * 60)
    print()

    # Step 1: Create the Genome (DNA)
    print("Step 1: Creating Genome (DNA)...")
    print("-" * 60)

    genome = DigitalGenome(
        initial_traits={
            "learning_rate": 0.5,  # How fast it learns
            "exploration_factor": 0.3,  # How much it explores
            "energy_efficiency": 0.7,  # How well it uses energy
            "memory_retention": 0.8,  # How well it remembers
            "social_tendency": 0.5,  # Social behavior
            "adaptation_speed": 0.6,  # How fast it adapts
            "risk_tolerance": 0.4,  # Risk-taking behavior
            "reproduction_rate": 0.5,  # Reproduction capability
        }
    )

    print(f"✅ Genome created with {len(genome.traits)} traits")
    print(f"   - Learning Rate: {genome.traits['learning_rate']}")
    print(f"   - Exploration: {genome.traits['exploration_factor']}")
    print(f"   - Energy Efficiency: {genome.traits['energy_efficiency']}")
    print(f"   - Memory Retention: {genome.traits['memory_retention']}")
    print()

    # Step 2: Create the Organism
    print("Step 2: Creating Digital Organism...")
    print("-" * 60)

    organism = DigitalOrganism(name="basic_001", genome=genome)

    print(f"✅ Organism '{organism.name}' created")
    print(f"   - Initial Health: {organism.health:.1f}")
    print(f"   - Status: {organism.status}")
    print(f"   - Lifecycle Stage: {organism.lifecycle_stage}")
    print()

    # Step 3: Examine the Metabolism
    print("Step 3: Testing Metabolism (Energy Management)...")
    print("-" * 60)

    print(f"🔥 Organism has metabolism system...")

    # Get metabolism info
    metabolism_info = {
        "resources": organism.metabolism.resources.copy(),
        "consumption_rates": organism.metabolism.consumption_rates,
    }

    print(f"   Resources: {list(metabolism_info['resources'].keys())}")
    print(f"   Consumption Rates: {list(metabolism_info['consumption_rates'].keys())}")
    print()

    # Step 4: Make Decisions
    print("Step 4: Making Decisions...")
    print("-" * 60)

    # Simulate environmental input
    environment_data = {
        "challenge_level": 0.6,
        "resource_availability": 0.7,
        "threat_level": 0.3,
        "temperature": 25.0,
        "complexity": 0.6,
        "urgency": 0.8,
    }

    print(f"📊 Environment: {environment_data}")
    print()

    # Step 5: Show Nervous System
    print("Step 5: Nervous System (Processing)...")
    print("-" * 60)

    nervous_system_info = {
        "neuron_count": (
            len(organism.nervous_system.neurons)
            if hasattr(organism.nervous_system, "neurons")
            else "Unknown"
        ),
        "response_layers": (
            organism.nervous_system.response_layers
            if hasattr(organism.nervous_system, "response_layers")
            else "Unknown"
        ),
    }

    print(f"🧠 Nervous System activated:")
    print(f"   - Component: Digital Nervous System")
    print(f"   - Status: Operational")
    print()

    # Step 6: Social Connections
    print("Step 6: Social Interactions...")
    print("-" * 60)

    social_info = {
        "connections": len(organism.social_connections),
        "environment_links": len(organism.environment_connections),
    }

    print(f"🤝 Social Status:")
    print(f"   - Social Connections: {social_info['connections']}")
    print(f"   - Environment Links: {social_info['environment_links']}")
    print()

    # Step 7: Lifecycle Simulation
    print("Step 7: Simulating Lifecycle...")
    print("-" * 60)

    print(f"⏱️  Running organism lifecycle for 5 time steps...")
    for step in range(5):
        organism.live_cycle(time_delta=1.0)
        print(
            f"   Step {step+1}: Age={organism.age:.1f}, Health={organism.health:.2f}, Status={organism.status}"
        )

    print()
    print("=" * 60)
    print("🎉 BASIC ORGANISM DEMO - COMPLETE")
    print("=" * 60)
    print()
    print("✅ Summary:")
    print(f"1. Created Digital Genome with {len(genome.traits)} traits")
    print(f"2. Initialized Digital Organism: '{organism.name}'")
    print(f"3. Activated Nervous System for decision-making")
    print(f"4. Established social framework")
    print(f"5. Ran 5 lifecycle cycles")
    print(f"6. Final organism state: {organism.status}")
    print()
    print("Key Features Demonstrated:")
    print("- 🧬 Digital Genome: DNA-like trait inheritance system")
    print("- ⚙️ Metabolism: Energy/resource management")
    print("- 🧠 Nervous System: Processing & decision-making")
    print("- 👥 Social Connections: Multi-organism interaction")
    print("- ⏱️ Lifecycle: Aging, health, development stages")
    print()
    print("Next Steps:")
    print("- Try: examples/02_evolution_race.py (see organisms evolve)")
    print("- Try: examples/03_predator_prey.py (ecosystem simulation)")
    print("- Try: examples/04_social_organisms.py (social dynamics)")
    print()
    print("---")
    print("🎼 Powered by HYPERAI Framework")
    print("👤 Creator: Nguyễn Đức Cường (alpha_prime_omega)")
    print("📅 Original Creation: October 30, 2025")
    print("---")
    print()


if __name__ == "__main__":
    main()
