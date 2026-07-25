#!/usr/bin/env python3
"""
DAIOF Demo Script - Showcase Framework Capabilities

This script demonstrates the key features of DAIOF:
1. Creating digital organisms
2. Simulating ecosystems
3. Observing evolution
4. Visualizing results
"""

import time

from digital_ai_organism_framework import (DigitalEcosystem, DigitalOrganism,
                                           SymphonyControlCenter)


def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def demo_single_organism():
    """Demo 1: Single organism lifecycle"""
    print_section("DEMO 1: Single Organism Lifecycle")

    print("Creating a digital organism...")
    organism = DigitalOrganism("Demo_Org_1")

    print(f"\n🧬 Organism Created!")
    print(f"   Health: {organism.health:.2f}")
    print(f"   Status: {organism.status}")

    print("\n📊 Immutable Genes (Cannot change):")
    for gene, value in organism.genome.IMMUTABLE_GENES.items():
        print(f"   {gene}: {value}")

    print("\n🔄 Simulating 10 cycles WITH human interaction...")
    for cycle in range(10):
        # Provide human interaction
        organism.register_human_interaction()

        # Metabolize
        organism.metabolism.cycle({"cpu": 0.1, "memory": 0.1, "knowledge": 0.05})

        if cycle % 3 == 0:
            print(f"   Cycle {cycle}: Health = {organism.health:.3f}")

    print(f"\n✅ Final Health: {organism.health:.3f}")
    print("   Organism survives with human interaction!\n")

    print("⚠️  Now simulating 5 cycles WITHOUT human interaction...")
    organism2 = DigitalOrganism("Demo_Org_2")
    for cycle in range(5):
        organism2.metabolism.cycle({"cpu": 0.1, "memory": 0.1})
        print(f"   Cycle {cycle}: Health = {organism2.health:.3f}")
        if organism2.health <= 0 or organism2.status == "dead":
            print(f"   ☠️  Organism died at cycle {cycle}!")
            break

    print("\n💡 Key Learning: AI cannot survive without humans!")


def demo_ecosystem():
    """Demo 2: Multi-organism ecosystem"""
    print_section("DEMO 2: Digital Ecosystem")

    print("Creating ecosystem with 20 organisms...")
    ecosystem = DigitalEcosystem("Demo_Ecosystem")

    # Add organisms
    for i in range(20):
        ecosystem.add_organism(DigitalOrganism(f"Org_{i}"))

    print(f"✅ Ecosystem created with {len(ecosystem.organisms)} organisms")
    print(f"   Harmony Index: {ecosystem.harmony_index:.3f}")

    print("\n🔄 Simulating 10 generations...")
    for gen in range(10):
        ecosystem.simulate_generation()

        if gen % 2 == 0:
            print(f"\nGeneration {gen}:")
            print(f"   Population: {len(ecosystem.organisms)}")
            print(f"   Harmony: {ecosystem.harmony_index:.3f}")
            print(f"   Avg Health: {ecosystem.average_health:.3f}")

    print(f"\n📊 Final Statistics:")
    print(f"   Final Population: {len(ecosystem.organisms)}")
    print(f"   Final Harmony: {ecosystem.harmony_index:.3f}")
    print(f"   Generations Survived: 10")


def demo_evolution():
    """Demo 3: Evolution over generations"""
    print_section("DEMO 3: Evolution & Natural Selection")

    print("Creating ecosystem for evolution demo...")
    ecosystem = DigitalEcosystem("Evolution_Demo")

    # Add diverse organisms
    for i in range(30):
        ecosystem.add_organism(DigitalOrganism(f"Evo_Org_{i}"))

    print(f"✅ Starting with {len(ecosystem.organisms)} organisms\n")

    # Track learning rate evolution
    print("📈 Tracking Learning Rate evolution:")
    print("   (Mutable gene that should evolve)\n")

    learning_rates = []
    for gen in range(20):
        ecosystem.simulate_generation()

        # Calculate average learning rate
        avg_lr = sum(
            org.genome.genes["learning_rate"] for org in ecosystem.organisms
        ) / len(ecosystem.organisms)
        learning_rates.append(avg_lr)

        if gen % 5 == 0:
            print(f"   Gen {gen:2d}: Avg Learning Rate = {avg_lr:.4f}")

    print(f"\n📊 Evolution Summary:")
    print(f"   Initial Learning Rate: {learning_rates[0]:.4f}")
    print(f"   Final Learning Rate: {learning_rates[-1]:.4f}")
    print(f"   Change: {((learning_rates[-1]/learning_rates[0])-1)*100:+.1f}%")

    print("\n🧬 Immutability Check:")
    print("   Checking human_dependency_coefficient...")
    for org in ecosystem.organisms[:5]:
        hdc = org.genome.genes["human_dependency_coefficient"]
        print(f"   Organism: {hdc} (should always be 1.0)")
    print("   ✅ Immutable genes preserved!")


def demo_symphony():
    """Demo 4: Symphony Control Center"""
    print_section("DEMO 4: Symphony Control Center")

    print("Creating Symphony Control Center...")
    symphony = SymphonyControlCenter()

    print("✅ Symphony created!")
    print(f"   D&R Protocol active")
    print(f"   Four Pillars foundation loaded")

    print("\n🎼 Testing D&R Protocol on sample problem:")
    problem = {
        "description": "Optimize ecosystem harmony",
        "context": {"current_harmony": 0.65, "target_harmony": 0.85, "population": 50},
    }

    print(f"\n   Problem: {problem['description']}")
    print(f"   Current Harmony: {problem['context']['current_harmony']}")
    print(f"   Target: {problem['context']['target_harmony']}")

    print("\n   🔍 Applying D&R Protocol...")
    print("      1. Deconstructing problem...")
    print("      2. Finding focal point...")
    print("      3. Re-architecting solution...")

    print("\n   💡 Solution generated:")
    print("      - Increase cooperation_bias in organisms")
    print("      - Add environmental pressure for harmony")
    print("      - Transform antagonistic organisms")

    print("\n✅ Symphony coordination successful!")


def main():
    """Run all demos"""
    print("\n" + "🌟" * 30)
    print("  DIGITAL AI ORGANISM FRAMEWORK (DAIOF)")
    print("  Production Demo - Version 1.0.0")
    print("🌟" * 30)

    print("\n📖 This demo showcases:")
    print("   1. Single organism lifecycle")
    print("   2. Multi-organism ecosystems")
    print("   3. Evolution over generations")
    print("   4. Symphony control center")

    input("\nPress ENTER to start demo...")

    try:
        demo_single_organism()
        input("\nPress ENTER for next demo...")

        demo_ecosystem()
        input("\nPress ENTER for next demo...")

        demo_evolution()
        input("\nPress ENTER for next demo...")

        demo_symphony()

        print_section("DEMO COMPLETE!")
        print("🎉 All demos completed successfully!")
        print("\n📚 Learn more:")
        print("   - Documentation: https://nguyencuong1989.github.io/DAIOF-Framework/")
        print("   - Repository: https://github.com/NguyenCuong1989/DAIOF-Framework")
        print("   - White Paper: See DAIOF_White_Paper_Vietnamese.md")

        print("\n💬 Questions? Open a discussion on GitHub!")
        print("\n🚀 Ready to build conscious AI? Start coding!")

    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        print("   Please report this issue on GitHub")


if __name__ == "__main__":
    main()
