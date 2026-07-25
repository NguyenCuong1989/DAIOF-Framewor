#!/usr/bin/env python3
"""
Predator-Prey Ecosystem Simulation
Simulates a balanced ecosystem with predators and prey

This example demonstrates:
- Multi-species interactions
- Population dynamics
- Energy transfer
- Ecosystem balance
- Survival strategies
"""

import random

from daiof.core.digital_genome import DigitalGenome
from daiof.core.digital_organism import DigitalOrganism
from daiof.ecosystem.ecosystem import Ecosystem


class Prey(DigitalOrganism):
    """Herbivore - eats resources, avoids predators"""

    def __init__(self, organism_id: str):
        genome = DigitalGenome()
        genome.set_gene("speed", random.uniform(0.6, 0.9))  # Fast to escape
        genome.set_gene("detection", random.uniform(0.5, 0.8))  # Detect danger
        genome.set_gene(
            "reproduction_rate", random.uniform(0.7, 0.9)
        )  # High reproduction
        genome.set_immutable_gene("species", "prey")
        genome.set_immutable_gene("human_dependency_coefficient", 1.0)

        super().__init__(
            genome=genome, organism_id=organism_id, name=f"Prey_{organism_id}"
        )
        self.energy = 50.0

    def can_reproduce(self) -> bool:
        return self.energy > 40 and self.age > 2

    def reproduce(self) -> "Prey":
        """Create offspring"""
        self.energy -= 20  # Reproduction cost
        offspring_id = f"{self.organism_id}_child"
        offspring = Prey(offspring_id)
        # Inherit some traits with mutation
        for gene in ["speed", "detection"]:
            value = self.genome.get_gene(gene)
            mutation = random.uniform(-0.1, 0.1)
            offspring.genome.set_gene(gene, max(0.1, min(1.0, value + mutation)))
        return offspring


class Predator(DigitalOrganism):
    """Carnivore - hunts prey"""

    def __init__(self, organism_id: str):
        genome = DigitalGenome()
        genome.set_gene("speed", random.uniform(0.7, 1.0))  # Fast hunter
        genome.set_gene("hunting_skill", random.uniform(0.5, 0.8))
        genome.set_gene("energy_efficiency", random.uniform(0.6, 0.9))
        genome.set_immutable_gene("species", "predator")
        genome.set_immutable_gene("human_dependency_coefficient", 1.0)

        super().__init__(
            genome=genome, organism_id=organism_id, name=f"Predator_{organism_id}"
        )
        self.energy = 60.0

    def hunt(self, prey: Prey) -> bool:
        """Attempt to catch prey"""
        predator_speed = self.genome.get_gene("speed")
        hunting_skill = self.genome.get_gene("hunting_skill")
        prey_speed = prey.genome.get_gene("speed")
        prey_detection = prey.genome.get_gene("detection")

        # Success probability
        hunt_success = (predator_speed + hunting_skill) / 2
        escape_chance = (prey_speed + prey_detection) / 2

        if random.random() < (hunt_success - escape_chance + 0.3):
            # Successful hunt
            self.energy += 30  # Energy from prey
            return True
        return False

    def can_reproduce(self) -> bool:
        return self.energy > 80 and self.age > 3


def main():
    print("=" * 70)
    print("🌿 PREDATOR-PREY ECOSYSTEM SIMULATION")
    print("=" * 70)
    print()

    # Configuration
    INITIAL_PREY = 20
    INITIAL_PREDATORS = 5
    CYCLES = 15

    print(f"⚙️  Ecosystem Configuration:")
    print(f"   Initial Prey: {INITIAL_PREY}")
    print(f"   Initial Predators: {INITIAL_PREDATORS}")
    print(f"   Simulation Cycles: {CYCLES}")
    print()

    # Create ecosystem
    print("🌱 Initializing ecosystem...")

    prey_population = [Prey(f"prey_{i}") for i in range(INITIAL_PREY)]
    predator_population = [Predator(f"pred_{i}") for i in range(INITIAL_PREDATORS)]

    print(f"✅ Ecosystem created:")
    print(f"   🐰 Prey: {len(prey_population)}")
    print(f"   🦁 Predators: {len(predator_population)}")
    print()

    # Track populations
    history = {"prey": [len(prey_population)], "predators": [len(predator_population)]}

    # Simulation loop
    for cycle in range(CYCLES):
        print(f"🔄 Cycle {cycle + 1}")
        print("-" * 70)

        # Prey actions
        new_prey = []
        for prey in prey_population[:]:
            # Age and metabolism
            prey.age += 1
            prey.energy -= 2  # Basic metabolism

            # Eat resources
            if random.random() < 0.7:  # Food availability
                prey.energy += 10

            # Reproduction
            if prey.can_reproduce():
                offspring = prey.reproduce()
                new_prey.append(offspring)

            # Death from starvation
            if prey.energy <= 0:
                prey_population.remove(prey)

        prey_population.extend(new_prey)

        # Predator actions
        new_predators = []
        for predator in predator_population[:]:
            # Age and metabolism
            predator.age += 1
            predator.energy -= 5  # Predators need more energy

            # Hunting
            if prey_population and predator.energy < 80:
                target = random.choice(prey_population)
                if predator.hunt(target):
                    prey_population.remove(target)
                    # Predator gains energy (already added in hunt method)

            # Reproduction
            if (
                predator.can_reproduce()
                and len(predator_population) < len(prey_population) / 2
            ):
                # Only reproduce if prey is abundant
                predator.energy -= 30
                offspring_id = f"{predator.organism_id}_child"
                new_predators.append(Predator(offspring_id))

            # Death from starvation
            if predator.energy <= 0:
                predator_population.remove(predator)

        predator_population.extend(new_predators)

        # Record populations
        history["prey"].append(len(prey_population))
        history["predators"].append(len(predator_population))

        # Display status
        print(
            f"   🐰 Prey: {len(prey_population)} (births: {len(new_prey)}, "
            f"avg energy: {sum(p.energy for p in prey_population)/len(prey_population) if prey_population else 0:.1f})"
        )
        print(
            f"   🦁 Predators: {len(predator_population)} (births: {len(new_predators)}, "
            f"avg energy: {sum(p.energy for p in predator_population)/len(predator_population) if predator_population else 0:.1f})"
        )

        # Check extinction
        if not prey_population:
            print("\n   ⚠️  PREY EXTINCT! Ecosystem collapsed.")
            break
        if not predator_population:
            print("\n   ⚠️  PREDATORS EXTINCT! Prey overpopulation.")
            break

        print()

    # Final analysis
    print("=" * 70)
    print("📊 ECOSYSTEM ANALYSIS")
    print("=" * 70)
    print()

    print("📈 Population Trends:")
    print(
        f"   Prey: {history['prey'][0]} → {history['prey'][-1]} "
        f"({(history['prey'][-1] - history['prey'][0])/history['prey'][0]*100:+.0f}%)"
    )
    print(
        f"   Predators: {history['predators'][0]} → {history['predators'][-1]} "
        f"({(history['predators'][-1] - history['predators'][0])/history['predators'][0]*100:+.0f}%)"
    )
    print()

    # Ecosystem health
    final_ratio = history["prey"][-1] / max(history["predators"][-1], 1)
    print(f"🌿 Ecosystem Health:")
    print(f"   Prey/Predator Ratio: {final_ratio:.1f}")

    if 3 <= final_ratio <= 6:
        print(f"   Status: ✅ BALANCED - Sustainable ecosystem")
    elif final_ratio > 6:
        print(f"   Status: ⚠️  PREY DOMINANT - Predators struggling")
    else:
        print(f"   Status: ⚠️  PREDATOR DOMINANT - Prey under pressure")

    print()
    print("🔬 Key Insights:")
    print("   - Predator-prey populations oscillate naturally")
    print("   - Energy flow maintains ecosystem balance")
    print("   - Overpopulation leads to resource depletion")
    print("   - Extinction risk when populations too small")
    print()
    print("Next: Try examples/04_social_organisms.py for cooperation")
    print()


if __name__ == "__main__":
    main()
