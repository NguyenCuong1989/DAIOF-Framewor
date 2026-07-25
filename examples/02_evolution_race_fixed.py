#!/usr/bin/env python3
"""
Evolution Race Example
Watch multiple organisms compete and evolve over generations

This example demonstrates:
- Population dynamics
- Natural selection
- Genetic mutation
- Survival of the fittest
- Multi-generation evolution

Creator: Nguyễn Đức Cường (alpha_prime_omega)
Framework: DAIOF (Digital Autonomous Intelligent Organism Framework)
Original Creation: October 30, 2025
"""

import random

from digital_ai_organism_framework import DigitalGenome, DigitalOrganism

# Configuration
POPULATION_SIZE = 5
GENERATIONS = 3
MUTATION_RATE = 0.1


def create_random_organism(organism_id: str) -> DigitalOrganism:
    """Create organism with random genome"""
    genome = DigitalGenome()
    organism = DigitalOrganism(name=organism_id, genome=genome)
    return organism


def fitness_function(organism: DigitalOrganism) -> float:
    """Calculate fitness based on organism traits"""
    # Higher learning_rate + exploration + health = better fitness
    traits = organism.genome.traits
    fitness = (
        traits.get("learning_rate", 0.5) * 0.3
        + traits.get("exploration_factor", 0.3) * 0.3
        + organism.health * 0.4
    )
    return fitness


def main():
    print("=" * 70)
    print("🧬 EVOLUTION RACE EXAMPLE")
    print("=" * 70)
    print()

    print("🧬 Creating initial population...")
    print("-" * 70)

    population = [create_random_organism(f"org_{i}") for i in range(POPULATION_SIZE)]

    print(f"✅ Created {len(population)} organisms with random genes")
    print()

    # Track best organism across generations
    best_organisms = []

    # Evolution loop
    for generation in range(GENERATIONS):
        print(f"🔄 GENERATION {generation + 1}")
        print("-" * 70)

        # Evaluate fitness
        fitness_scores = [(org, fitness_function(org)) for org in population]
        fitness_scores.sort(key=lambda x: x[1], reverse=True)

        # Show top 3
        print("🏆 Top 3 Organisms:")
        for rank, (org, fitness) in enumerate(fitness_scores[:3], 1):
            learning_rate = org.genome.traits.get("learning_rate", 0)
            print(
                f"   {rank}. {org.name}: Fitness={fitness:.3f}, Learning={learning_rate:.3f}, Health={org.health:.2f}"
            )

        # Keep best
        best_organisms.append(fitness_scores[0])

        # Selection: keep top 50%
        survivors = [org for org, _ in fitness_scores[: POPULATION_SIZE // 2]]

        # Reproduction: create new organisms from survivors
        new_population = survivors.copy()
        while len(new_population) < POPULATION_SIZE:
            parent = random.choice(survivors)

            # Create mutated offspring
            new_genome = parent.genome.mutate(mutation_rate=MUTATION_RATE)
            offspring = DigitalOrganism(
                name=f"gen_{generation}_offspring_{len(new_population)}",
                genome=new_genome,
            )
            new_population.append(offspring)

        population = new_population
        print(f"   ➜ New generation created ({len(new_population)} organisms)")
        print()

    # Summary
    print("=" * 70)
    print("🎉 EVOLUTION SUMMARY")
    print("=" * 70)
    print()

    print("🏆 Best Organisms by Generation:")
    for gen, (org, fitness) in enumerate(best_organisms, 1):
        print(f"   Gen {gen}: {org.name} (Fitness: {fitness:.3f})")

    if len(best_organisms) > 1:
        improvement = (
            (best_organisms[-1][1] - best_organisms[0][1]) / best_organisms[0][1]
        ) * 100
        print(f"\n📈 Overall Improvement: {improvement:+.1f}%")

    print()
    print("---")
    print("🎼 Powered by HYPERAI Framework")
    print("👤 Creator: Nguyễn Đức Cường (alpha_prime_omega)")
    print("📅 Original Creation: October 30, 2025")
    print("---")
    print()


if __name__ == "__main__":
    main()
