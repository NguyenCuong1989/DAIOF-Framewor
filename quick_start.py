#!/usr/bin/env python3
"""
DAIOF Quick Start - Your First Digital Organism in 30 Seconds
==============================================================

This script demonstrates the core concepts of DAIOF:
1. Creating a digital organism with genetic traits
2. Observing evolution through mutation
3. Running a simple ecosystem simulation

Just run: python quick_start.py

No configuration needed!
"""

import random

from src.digital_organism import DigitalGenome, DigitalOrganism


def print_separator(title=""):
    """Pretty print separator"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}\n")
    else:
        print(f"{'='*60}\n")


def main():
    print_separator("🧬 DAIOF FRAMEWORK - QUICK START DEMO")

    # ========================================================================
    # STEP 1: Create Your First Digital Organism
    # ========================================================================
    print_separator("STEP 1: Creating Your First Organism")

    # Define genetic traits (like DNA)
    genome = DigitalGenome(
        traits={
            "learning_rate": 0.05,  # How fast it learns
            "exploration_factor": 0.6,  # How adventurous it is
            "memory_retention": 0.85,  # How much it remembers
            "social_tendency": 0.5,  # How social it is
            "energy_efficiency": 0.75,  # How efficient it is
            "adaptation_speed": 0.4,  # How quickly it adapts
            "risk_tolerance": 0.3,  # How risky it behaves
            "reproduction_rate": 0.5,  # How fast it reproduces
        },
        mutation_rate=0.1,  # 10% chance of mutation
    )

    # Create the organism
    organism = DigitalOrganism(
        organism_id="Explorer_01",
        genome=genome,
        initial_resources={
            "cpu_cycles": 100,
            "memory_units": 50,
            "network_bandwidth": 30,
            "storage_space": 20,
            "knowledge_points": 10,
        },
    )

    print(f"✅ Created organism: {organism.organism_id}")
    print(f"⚡ Energy level: {organism.energy}")
    print(f"🧬 Genome traits:")
    for trait, value in genome.traits.items():
        print(f"   • {trait}: {value:.2f}")

    # ========================================================================
    # STEP 2: Watch Evolution in Action
    # ========================================================================
    print_separator("STEP 2: Evolution Through Mutation")

    print("Creating offspring through mutation...\n")

    # Create 3 offspring with mutations
    offspring = []
    for i in range(3):
        child_genome = genome.mutate()
        child = DigitalOrganism(
            organism_id=f"Explorer_01_Child_{i+1}", genome=child_genome
        )
        offspring.append((child, child_genome))

    # Show evolution
    print(f"👨 PARENT: {organism.organism_id}")
    print(f"   Exploration: {genome.traits['exploration_factor']:.3f}")
    print(f"   Learning:    {genome.traits['learning_rate']:.3f}")
    print(f"   Risk:        {genome.traits['risk_tolerance']:.3f}\n")

    for child, child_genome in offspring:
        print(f"👶 OFFSPRING: {child.organism_id}")
        print(
            f"   Exploration: {child_genome.traits['exploration_factor']:.3f} "
            f"({((child_genome.traits['exploration_factor'] - genome.traits['exploration_factor']) / genome.traits['exploration_factor'] * 100):+.1f}%)"
        )
        print(
            f"   Learning:    {child_genome.traits['learning_rate']:.3f} "
            f"({((child_genome.traits['learning_rate'] - genome.traits['learning_rate']) / genome.traits['learning_rate'] * 100):+.1f}%)"
        )
        print(
            f"   Risk:        {child_genome.traits['risk_tolerance']:.3f} "
            f"({((child_genome.traits['risk_tolerance'] - genome.traits['risk_tolerance']) / genome.traits['risk_tolerance'] * 100):+.1f}%)"
        )
        print()

    print("💡 Notice: Each offspring has slightly different traits!")
    print("   This is EVOLUTION - random mutations create diversity.\n")

    # ========================================================================
    # STEP 3: Organism Makes Decisions
    # ========================================================================
    print_separator("STEP 3: Intelligent Decision Making")

    # Simulate environmental challenges
    scenarios = [
        {
            "name": "Easy Environment",
            "data": {
                "challenge_level": 0.2,
                "resource_availability": 0.9,
                "threat_level": 0.1,
            },
        },
        {
            "name": "Moderate Environment",
            "data": {
                "challenge_level": 0.5,
                "resource_availability": 0.5,
                "threat_level": 0.3,
            },
        },
        {
            "name": "Harsh Environment",
            "data": {
                "challenge_level": 0.8,
                "resource_availability": 0.2,
                "threat_level": 0.7,
            },
        },
    ]

    print("Testing organism's decision-making in different environments:\n")

    for scenario in scenarios:
        decision = organism.perceive_and_decide(scenario["data"])
        print(f"🌍 {scenario['name']}:")
        print(
            f"   Challenge: {scenario['data']['challenge_level']:.1f} | "
            f"Resources: {scenario['data']['resource_availability']:.1f} | "
            f"Threat: {scenario['data']['threat_level']:.1f}"
        )
        print(f"   → Decision: {decision.get('action', 'evaluate')}")
        print(f"   → Confidence: {decision.get('confidence', 0):.2f}")
        print()

    print("💡 Notice: Same organism makes different decisions based on environment!\n")

    # ========================================================================
    # STEP 4: Natural Selection
    # ========================================================================
    print_separator("STEP 4: Natural Selection Simulation")

    print("Simulating 5 generations of evolution...\n")

    # Create a small population
    population = [organism] + [child for child, _ in offspring]

    for generation in range(5):
        # Simulate fitness evaluation
        for org in population:
            # Random fitness based on traits
            fitness = (
                org.genome.traits["energy_efficiency"] * 0.3
                + org.genome.traits["adaptation_speed"] * 0.3
                + org.genome.traits["learning_rate"] * 0.4
                + random.uniform(-0.1, 0.1)  # Environmental randomness
            )
            org.genome.fitness_score = max(0, fitness)

        # Show generation stats
        avg_fitness = sum(o.genome.fitness_score for o in population) / len(population)
        best = max(population, key=lambda o: o.genome.fitness_score)

        print(f"Generation {generation + 1}:")
        print(f"   Population: {len(population)} organisms")
        print(f"   Avg Fitness: {avg_fitness:.3f}")
        print(f"   Best: {best.organism_id} (fitness: {best.genome.fitness_score:.3f})")

        # Create next generation (simplified)
        if generation < 4:  # Don't create new gen on last iteration
            # Keep best performers
            population.sort(key=lambda o: o.genome.fitness_score, reverse=True)
            survivors = population[:2]  # Top 2 survive

            # Create offspring from survivors
            new_population = survivors.copy()
            for i in range(2):
                child_genome = survivors[0].genome.mutate()
                child = DigitalOrganism(
                    organism_id=f"Gen{generation+2}_Organism_{i+1}", genome=child_genome
                )
                new_population.append(child)

            population = new_population

    print("\n💡 Notice: Fitness improves over generations through selection!\n")

    # ========================================================================
    # CONCLUSION
    # ========================================================================
    print_separator("🎉 DEMO COMPLETE!")

    print("You just witnessed:")
    print("  ✅ Digital organism creation with genetic traits")
    print("  ✅ Evolution through mutation")
    print("  ✅ Intelligent decision-making")
    print("  ✅ Natural selection over generations")
    print()
    print("This is just the beginning! With DAIOF you can:")
    print("  🌍 Create complex ecosystems with 100s of organisms")
    print("  🧬 Design custom traits and behaviors")
    print("  📊 Track evolution over 1000s of generations")
    print("  🔬 Experiment with different selection pressures")
    print("  🎮 Build evolutionary games and simulations")
    print()
    print("Next steps:")
    print("  📖 Read the full documentation: docs/")
    print("  💻 Explore example organisms: examples/")
    print("  💬 Join our community: GitHub Discussions")
    print("  🚀 Build something amazing!")
    print()
    print("Happy evolving! 🧬✨")
    print_separator()


if __name__ == "__main__":
    main()
