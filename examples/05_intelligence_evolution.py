#!/usr/bin/env python3
"""
Intelligence Evolution - Learning and Adaptation
Watch organisms become smarter through experience and evolution

This example demonstrates:
- Reinforcement learning
- Knowledge accumulation
- Skill improvement
- Adaptive behavior
- Intelligence inheritance
"""

import random
from typing import Dict, List

from daiof.core.digital_genome import DigitalGenome
from daiof.core.digital_organism import DigitalOrganism
from daiof.learning.reinforcement_learner import ReinforcementLearner


class IntelligentOrganism(DigitalOrganism):
    """Organism with learning capabilities"""

    def __init__(self, organism_id: str, parent=None):
        genome = DigitalGenome()

        # Intelligence traits
        if parent:
            # Inherit from parent with mutation
            genome.set_gene(
                "learning_rate",
                min(
                    1.0,
                    max(
                        0.1,
                        parent.genome.get_gene("learning_rate")
                        + random.uniform(-0.1, 0.1),
                    ),
                ),
            )
            genome.set_gene(
                "memory_capacity",
                min(
                    1.0,
                    max(
                        0.3,
                        parent.genome.get_gene("memory_capacity")
                        + random.uniform(-0.1, 0.1),
                    ),
                ),
            )
            genome.set_gene(
                "problem_solving",
                min(
                    1.0,
                    max(
                        0.2,
                        parent.genome.get_gene("problem_solving")
                        + random.uniform(-0.1, 0.1),
                    ),
                ),
            )
        else:
            genome.set_gene("learning_rate", random.uniform(0.4, 0.8))
            genome.set_gene("memory_capacity", random.uniform(0.5, 0.9))
            genome.set_gene("problem_solving", random.uniform(0.3, 0.7))

        genome.set_gene("curiosity", random.uniform(0.5, 1.0))
        genome.set_immutable_gene("human_dependency_coefficient", 1.0)

        super().__init__(
            genome=genome, organism_id=organism_id, name=f"Brain_{organism_id}"
        )

        # Learning state
        self.knowledge: Dict[str, float] = {}  # skill -> proficiency
        self.experiences: List[str] = []
        self.learning_learner = ReinforcementLearner(
            learning_rate=self.genome.get_gene("learning_rate")
        )
        self.total_score = 0
        self.generation = 0 if not parent else parent.generation + 1

    def learn_skill(self, skill: str, difficulty: float) -> float:
        """Attempt to learn a skill, returns success level"""
        learning_rate = self.genome.get_gene("learning_rate")
        problem_solving = self.genome.get_gene("problem_solving")

        # Current proficiency
        current = self.knowledge.get(skill, 0.0)

        # Learning attempt
        learning_bonus = learning_rate * problem_solving
        new_level = current + (difficulty * learning_bonus * random.uniform(0.5, 1.5))
        new_level = min(1.0, new_level)  # Cap at mastery

        # Update knowledge
        old_level = current
        self.knowledge[skill] = new_level
        improvement = new_level - old_level

        # Record experience
        self.experiences.append(f"Learned {skill}: {old_level:.2f} → {new_level:.2f}")

        return improvement

    def solve_problem(self, problem_complexity: float) -> bool:
        """Attempt to solve a problem"""
        problem_solving = self.genome.get_gene("problem_solving")

        # Use relevant knowledge
        relevant_skills = list(self.knowledge.values())[-3:]  # Last 3 skills learned
        knowledge_bonus = (
            sum(relevant_skills) / len(relevant_skills) if relevant_skills else 0
        )

        success_chance = (problem_solving + knowledge_bonus * 0.5) / (
            1 + problem_complexity
        )

        if random.random() < success_chance:
            # Learn from success
            self.total_score += problem_complexity * 10
            return True
        else:
            # Learn from failure (smaller gain)
            self.total_score += problem_complexity * 2
            return False

    def get_intelligence_score(self) -> float:
        """Calculate overall intelligence"""
        learning = self.genome.get_gene("learning_rate")
        memory = self.genome.get_gene("memory_capacity")
        problem_solving = self.genome.get_gene("problem_solving")

        # Knowledge contribution
        knowledge_score = sum(self.knowledge.values()) / max(len(self.knowledge), 1)

        # Combined intelligence
        intelligence = (
            learning * 0.2
            + memory * 0.2
            + problem_solving * 0.3
            + knowledge_score * 0.3
        )

        return intelligence


def run_learning_trials(organism: IntelligentOrganism, num_trials: int = 5):
    """Run learning trials for an organism"""
    skills = [
        ("pattern_recognition", 0.3),
        ("logical_reasoning", 0.5),
        ("creative_thinking", 0.4),
        ("abstract_concepts", 0.6),
        ("meta_learning", 0.8),
    ]

    print(f"   🧠 {organism.name} (Gen {organism.generation}) learning...")

    for i in range(num_trials):
        skill, difficulty = random.choice(skills)
        improvement = organism.learn_skill(skill, difficulty)

        if improvement > 0.1:
            print(f"      ✅ Learned {skill}: +{improvement:.3f}")

    # Intelligence score
    intelligence = organism.get_intelligence_score()
    print(f"      📊 Intelligence Score: {intelligence:.3f}")

    return intelligence


def main():
    print("=" * 70)
    print("🧠 INTELLIGENCE EVOLUTION - From Simple to Smart")
    print("=" * 70)
    print()

    # Configuration
    GENERATIONS = 4
    POPULATION_PER_GEN = 5
    TRIALS_PER_ORGANISM = 8

    print(f"⚙️  Configuration:")
    print(f"   Generations: {GENERATIONS}")
    print(f"   Population per Generation: {POPULATION_PER_GEN}")
    print(f"   Learning Trials: {TRIALS_PER_ORGANISM}")
    print()

    # Track evolution
    generation_data = []

    # Generation 0: Founders
    print("🔄 GENERATION 0: Founders")
    print("-" * 70)

    population = [IntelligentOrganism(f"org_0_{i}") for i in range(POPULATION_PER_GEN)]

    intelligence_scores = []
    for org in population:
        score = run_learning_trials(org, TRIALS_PER_ORGANISM)
        intelligence_scores.append((org, score))

    avg_intelligence = sum(s for _, s in intelligence_scores) / len(intelligence_scores)
    generation_data.append((0, avg_intelligence, intelligence_scores))

    print(f"\n   📊 Gen 0 Average Intelligence: {avg_intelligence:.3f}")
    print()

    # Evolve through generations
    for gen in range(1, GENERATIONS):
        print(f"🔄 GENERATION {gen}")
        print("-" * 70)

        # Select best organisms as parents
        intelligence_scores.sort(key=lambda x: x[1], reverse=True)
        parents = [org for org, _ in intelligence_scores[:2]]  # Top 2

        print(f"   🏆 Parents selected:")
        for parent in parents:
            intel = parent.get_intelligence_score()
            print(
                f"      {parent.name}: Intelligence {intel:.3f}, "
                f"{len(parent.knowledge)} skills mastered"
            )

        print()
        print(f"   👶 Creating new generation...")

        # Create offspring
        new_population = []
        for i in range(POPULATION_PER_GEN):
            parent = random.choice(parents)
            offspring = IntelligentOrganism(f"org_{gen}_{i}", parent=parent)
            new_population.append(offspring)

        population = new_population

        # Learning phase
        intelligence_scores = []
        for org in population:
            score = run_learning_trials(org, TRIALS_PER_ORGANISM)
            intelligence_scores.append((org, score))

        avg_intelligence = sum(s for _, s in intelligence_scores) / len(
            intelligence_scores
        )
        generation_data.append((gen, avg_intelligence, intelligence_scores))

        print(f"\n   📊 Gen {gen} Average Intelligence: {avg_intelligence:.3f}")

        # Show improvement
        prev_avg = generation_data[-2][1]
        improvement = ((avg_intelligence - prev_avg) / prev_avg) * 100
        print(f"   📈 Improvement: {improvement:+.1f}% from previous generation")
        print()

    # Problem-solving challenge
    print("=" * 70)
    print("🎯 FINAL CHALLENGE: Problem Solving Test")
    print("=" * 70)
    print()

    print("Testing all organisms on complex problems...")

    final_population = generation_data[-1][2]
    challenge_results = []

    for org, _ in final_population:
        problems_solved = 0
        problems = [(0.3, "Simple"), (0.5, "Moderate"), (0.7, "Hard"), (0.9, "Expert")]

        for complexity, level in problems:
            if org.solve_problem(complexity):
                problems_solved += 1

        challenge_results.append((org, problems_solved, org.total_score))
        print(
            f"   {org.name} (Gen {org.generation}): Solved {problems_solved}/4 problems, "
            f"Score: {org.total_score:.0f}"
        )

    print()

    # Final analysis
    print("=" * 70)
    print("📊 EVOLUTION ANALYSIS")
    print("=" * 70)
    print()

    print("📈 Intelligence Growth Across Generations:")
    for gen, avg_intel, _ in generation_data:
        print(f"   Generation {gen}: {avg_intel:.3f}")

    print()
    first_gen = generation_data[0][1]
    last_gen = generation_data[-1][1]
    total_improvement = ((last_gen - first_gen) / first_gen) * 100

    print(f"🎓 Learning Outcomes:")
    print(f"   Initial Intelligence: {first_gen:.3f}")
    print(f"   Final Intelligence: {last_gen:.3f}")
    print(f"   Total Improvement: {total_improvement:+.1f}%")
    print()

    # Best organism
    challenge_results.sort(key=lambda x: (x[1], x[2]), reverse=True)
    best_org, problems_solved, score = challenge_results[0]

    print(f"🏆 Top Performer:")
    print(f"   {best_org.name} (Generation {best_org.generation})")
    print(f"   Problems Solved: {problems_solved}/4")
    print(f"   Total Score: {score:.0f}")
    print(f"   Skills Mastered: {len(best_org.knowledge)}")
    print(f"   Learning Rate: {best_org.genome.get_gene('learning_rate'):.2f}")
    print()

    print("🔬 Key Insights:")
    print("   - Intelligence increases through generations via inheritance")
    print("   - Learning rate and problem-solving ability are genetic")
    print("   - Knowledge accumulation improves performance")
    print("   - Natural selection favors higher intelligence")
    print("   - Experience + genetics = evolutionary advantage")
    print()
    print("🎉 Congratulations! You've mastered all DAIOF examples.")
    print("📚 Explore the framework documentation for advanced features.")
    print()


if __name__ == "__main__":
    main()
