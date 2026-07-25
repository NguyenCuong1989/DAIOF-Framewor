#!/usr/bin/env python3
"""
Social Organisms - Cooperation and Communication
Demonstrates how organisms work together for mutual benefit

This example demonstrates:
- Social behaviors
- Communication protocols
- Resource sharing
- Collective intelligence
- Altruism and cooperation
"""

import random
from typing import Dict, List

from daiof.core.digital_genome import DigitalGenome
from daiof.core.digital_organism import DigitalOrganism
from daiof.social.social_network import SocialNetwork


class SocialOrganism(DigitalOrganism):
    """Organism with social capabilities"""

    def __init__(self, organism_id: str, personality: str = "cooperative"):
        genome = DigitalGenome()

        # Social traits
        genome.set_gene("cooperation", random.uniform(0.5, 1.0))
        genome.set_gene("communication", random.uniform(0.4, 0.9))
        genome.set_gene("trust", random.uniform(0.3, 0.8))
        genome.set_gene("altruism", random.uniform(0.2, 0.7))

        # Personality affects traits
        if personality == "leader":
            genome.set_gene("cooperation", 0.9)
            genome.set_gene("communication", 0.95)
        elif personality == "loner":
            genome.set_gene("cooperation", 0.3)
            genome.set_gene("trust", 0.2)

        genome.set_immutable_gene("personality", personality)
        genome.set_immutable_gene("human_dependency_coefficient", 1.0)

        super().__init__(
            genome=genome, organism_id=organism_id, name=f"{personality}_{organism_id}"
        )

        self.resources = 50.0
        self.relationships: Dict[str, float] = {}  # organism_id -> trust level
        self.messages_received: List[str] = []

    def share_resources(self, other: "SocialOrganism", amount: float) -> bool:
        """Share resources with another organism"""
        altruism = self.genome.get_gene("altruism")
        trust_level = self.relationships.get(other.organism_id, 0.5)

        # Decide whether to share
        if self.resources > amount and random.random() < (altruism * trust_level):
            self.resources -= amount
            other.resources += amount
            # Strengthen relationship
            self.relationships[other.organism_id] = min(1.0, trust_level + 0.1)
            other.relationships[self.organism_id] = min(
                1.0, other.relationships.get(self.organism_id, 0.5) + 0.1
            )
            return True
        return False

    def send_message(self, other: "SocialOrganism", message: str):
        """Send message to another organism"""
        communication = self.genome.get_gene("communication")
        if random.random() < communication:
            other.messages_received.append(f"From {self.name}: {message}")

    def form_alliance(self, other: "SocialOrganism") -> bool:
        """Form alliance with another organism"""
        my_cooperation = self.genome.get_gene("cooperation")
        their_cooperation = other.genome.get_gene("cooperation")

        if my_cooperation > 0.6 and their_cooperation > 0.6:
            self.relationships[other.organism_id] = 0.8
            other.relationships[self.organism_id] = 0.8
            return True
        return False


def simulate_resource_crisis(population: List[SocialOrganism]):
    """Simulate crisis requiring cooperation"""
    print("\n   ⚠️  RESOURCE CRISIS! Some organisms in need...")

    # Identify organisms in need
    in_need = [org for org in population if org.resources < 30]
    helpers = [org for org in population if org.resources > 60]

    help_events = 0
    for needy in in_need:
        for helper in helpers:
            if helper.share_resources(needy, 15):
                print(f"   🤝 {helper.name} helped {needy.name} (shared 15 resources)")
                help_events += 1
                break

    return help_events


def main():
    print("=" * 70)
    print("🤝 SOCIAL ORGANISMS - Cooperation in Action")
    print("=" * 70)
    print()

    # Create diverse population
    print("👥 Creating social population...")
    print("-" * 70)

    population: List[SocialOrganism] = []

    # Different personalities
    population.extend([SocialOrganism(f"lead_{i}", "leader") for i in range(2)])
    population.extend([SocialOrganism(f"coop_{i}", "cooperative") for i in range(5)])
    population.extend([SocialOrganism(f"lone_{i}", "loner") for i in range(2)])

    print(f"✅ Created {len(population)} organisms:")
    print(f"   👑 Leaders: 2 (high cooperation & communication)")
    print(f"   🤝 Cooperators: 5 (balanced social traits)")
    print(f"   🚶 Loners: 2 (low cooperation & trust)")
    print()

    # Phase 1: Initial interactions
    print("🔄 PHASE 1: First Contact")
    print("-" * 70)

    print("Organisms meeting and forming initial relationships...")

    for i, org1 in enumerate(population):
        for org2 in population[i + 1 :]:
            # Try to form alliance
            if org1.form_alliance(org2):
                print(f"   ✅ Alliance formed: {org1.name} ↔ {org2.name}")

            # Exchange messages
            org1.send_message(org2, "Hello, seeking cooperation")
            org2.send_message(org1, "Greetings, fellow organism")

    # Count alliances
    total_alliances = sum(len(org.relationships) for org in population) // 2
    print(f"\n   📊 Total alliances formed: {total_alliances}")
    print()

    # Phase 2: Resource sharing
    print("🔄 PHASE 2: Resource Sharing Test")
    print("-" * 70)

    # Set unequal resources
    for org in population[:3]:
        org.resources = 80  # Rich
    for org in population[-3:]:
        org.resources = 20  # Poor

    print("Testing voluntary resource sharing...")
    share_events = 0

    rich = [org for org in population if org.resources > 60]
    poor = [org for org in population if org.resources < 40]

    for wealthy in rich:
        for needy in poor:
            if wealthy.share_resources(needy, 10):
                share_events += 1

    print(f"   🎁 Voluntary sharing events: {share_events}")

    avg_resources = sum(org.resources for org in population) / len(population)
    print(f"   💰 Average resources after sharing: {avg_resources:.1f}")
    print()

    # Phase 3: Crisis response
    print("🔄 PHASE 3: Crisis Response")
    print("-" * 70)

    help_events = simulate_resource_crisis(population)

    print(f"\n   📊 Crisis response: {help_events} organisms helped")
    print()

    # Phase 4: Communication network
    print("🔄 PHASE 4: Communication Network")
    print("-" * 70)

    print("Analyzing message exchange patterns...")

    total_messages = sum(len(org.messages_received) for org in population)
    print(f"   📬 Total messages exchanged: {total_messages}")

    # Most connected organism
    most_connected = max(population, key=lambda x: len(x.relationships))
    print(
        f"   🌟 Most connected: {most_connected.name} "
        f"({len(most_connected.relationships)} relationships)"
    )

    # Show sample messages
    if most_connected.messages_received:
        print(f"\n   Sample messages to {most_connected.name}:")
        for msg in most_connected.messages_received[:3]:
            print(f"      📨 {msg}")

    print()

    # Final analysis
    print("=" * 70)
    print("📊 SOCIAL ANALYSIS")
    print("=" * 70)
    print()

    print("🤝 Cooperation Metrics:")
    avg_cooperation = sum(
        org.genome.get_gene("cooperation") for org in population
    ) / len(population)
    avg_trust = sum(org.genome.get_gene("trust") for org in population) / len(
        population
    )

    print(f"   Average Cooperation: {avg_cooperation:.2f}")
    print(f"   Average Trust: {avg_trust:.2f}")
    print(
        f"   Network Density: {total_alliances / (len(population) * (len(population)-1) / 2):.2%}"
    )
    print()

    print("🏆 Top Cooperators:")
    cooperators = sorted(
        population, key=lambda x: x.genome.get_gene("cooperation"), reverse=True
    )[:3]
    for rank, org in enumerate(cooperators, 1):
        coop = org.genome.get_gene("cooperation")
        personality = org.genome.get_immutable_gene("personality")
        print(f"   #{rank} {org.name} - {personality}: {coop:.2f} cooperation")

    print()
    print("🔬 Key Insights:")
    print("   - Leaders facilitate cooperation through high communication")
    print("   - Trust builds through repeated positive interactions")
    print("   - Resource sharing creates stronger alliances")
    print("   - Collective action more effective than individual effort")
    print("   - Social networks emerge naturally from interactions")
    print()
    print("Next: Try examples/05_intelligence_evolution.py for learning AI")
    print()


if __name__ == "__main__":
    main()
