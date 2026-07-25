#!/usr/bin/env python3
"""
🚀 HYPERAI Framework - Interactive Quick Start Guide
Chạy script này để xem hướng dẫn sử dụng tương tác

Creator: Nguyễn Đức Cường (alpha_prime_omega)
Date: November 6, 2025
"""

import os
import subprocess
import sys
from pathlib import Path


class HYPERAIQuickStart:
    """Interactive guide cho DAIOF Framework"""

    def __init__(self):
        self.base_dir = Path("/Users/andy/DAIOF-Framework")
        self.menu_options = {
            "1": ("🚀 System Initialization", self.init_system),
            "2": ("📊 Run Basic Example", self.run_example_01),
            "3": ("🧬 Run Evolution Race", self.run_example_02),
            "4": ("📈 Check System Status", self.check_status),
            "5": ("📚 View Documentation", self.view_docs),
            "6": ("🔍 Run Tests", self.run_tests),
            "7": ("📝 Git Operations", self.git_menu),
            "8": ("🛠️ Python Tools", self.python_tools),
            "9": ("📋 View Command Checklist", self.view_checklist),
            "0": ("❌ Exit", self.exit_program),
        }

    def clear_screen(self):
        """Clear terminal screen"""
        os.system("clear" if os.name != "nt" else "cls")

    def print_header(self):
        """Print header"""
        print("\n" + "=" * 70)
        print("🎼 HYPERAI FRAMEWORK - DAIOF Quick Start Interactive Guide")
        print("=" * 70)
        print("Creator: Nguyễn Đức Cường (alpha_prime_omega)")
        print("Version: 1.0.0 | Date: November 6, 2025")
        print("=" * 70 + "\n")

    def print_menu(self):
        """Display main menu"""
        print("\n📋 MAIN MENU:\n")
        for key, (label, _) in sorted(self.menu_options.items()):
            print(f"  [{key}] {label}")
        print()

    def get_choice(self):
        """Get user choice"""
        return input("Select option (0-9): ").strip()

    def init_system(self):
        """Initialize DAIOF system"""
        print("\n🚀 Initializing DAIOF System...")
        print("-" * 70)
        cmd = "cd /Users/andy/DAIOF-Framework && python3 system_initializer.py"
        os.system(cmd)
        input("\nPress Enter to continue...")

    def run_example_01(self):
        """Run basic organism example"""
        print("\n📊 Running Basic Organism Example...")
        print("-" * 70)
        cmd = "cd /Users/andy/DAIOF-Framework && PYTHONPATH=/Users/andy/DAIOF-Framework python3 examples/01_basic_organism.py"
        os.system(cmd)
        input("\nPress Enter to continue...")

    def run_example_02(self):
        """Run evolution race example"""
        print("\n🧬 Running Evolution Race Example...")
        print("-" * 70)
        cmd = "cd /Users/andy/DAIOF-Framework && PYTHONPATH=/Users/andy/DAIOF-Framework python3 examples/02_evolution_race_fixed.py"
        os.system(cmd)
        input("\nPress Enter to continue...")

    def check_status(self):
        """Check system status"""
        print("\n📈 System Status Check...")
        print("-" * 70)

        # Check git status
        print("\n✅ GIT STATUS:")
        os.system("cd /Users/andy/DAIOF-Framework && git status")

        # Check Python
        print("\n✅ PYTHON VERSION:")
        os.system("python3 --version")

        # Check packages
        print("\n✅ KEY PACKAGES:")
        try:
            from digital_ai_organism_framework import DigitalOrganism

            print("  ✓ digital_ai_organism_framework: OK")
        except:
            print("  ✗ digital_ai_organism_framework: NOT FOUND")

        input("\nPress Enter to continue...")

    def view_docs(self):
        """View documentation"""
        print("\n📚 Documentation Menu:")
        print("  [1] Copilot Instructions")
        print("  [2] Activation Guide")
        print("  [3] System Stabilization Report")
        print("  [4] Command Checklist")

        choice = input("\nSelect (1-4): ").strip()

        docs = {
            "1": ".github/copilot-instructions.md",
            "2": ".github/ACTIVATION_GUIDE.md",
            "3": "SYSTEM_STABILIZATION_REPORT.md",
            "4": "COMMAND_CHECKLIST.md",
        }

        if choice in docs:
            doc_path = self.base_dir / docs[choice]
            if doc_path.exists():
                os.system(f"less {doc_path}")

        input("Press Enter to continue...")

    def run_tests(self):
        """Run tests"""
        print("\n🔍 Running Tests...")
        print("-" * 70)

        print("Available test options:")
        print("  [1] Run all tests")
        print("  [2] Run specific test")
        print("  [3] Run with coverage")

        choice = input("\nSelect (1-3): ").strip()

        if choice == "1":
            os.system("cd /Users/andy/DAIOF-Framework && python3 -m pytest")
        elif choice == "2":
            test_file = input("Enter test file path: ").strip()
            os.system(
                f"cd /Users/andy/DAIOF-Framework && python3 -m pytest {test_file}"
            )
        elif choice == "3":
            os.system(
                "cd /Users/andy/DAIOF-Framework && python3 -m pytest --cov=digital_ai_organism_framework"
            )

        input("\nPress Enter to continue...")

    def git_menu(self):
        """Git operations menu"""
        print("\n📝 Git Operations Menu:")
        print("  [1] Check status")
        print("  [2] Add all changes")
        print("  [3] Commit changes")
        print("  [4] Push to GitHub")
        print("  [5] Pull from GitHub")
        print("  [6] View log")
        print("  [0] Back to main menu")

        choice = input("\nSelect (0-6): ").strip()

        os.chdir(self.base_dir)

        if choice == "1":
            os.system("git status")
        elif choice == "2":
            os.system("git add .")
            print("✅ All changes staged")
        elif choice == "3":
            msg = input("Enter commit message: ").strip()
            os.system(f"git commit -m '{msg}'")
        elif choice == "4":
            os.system("git push origin main")
        elif choice == "5":
            os.system("git pull origin main --no-rebase")
        elif choice == "6":
            os.system("git log --oneline | head -20")

        input("\nPress Enter to continue...")

    def python_tools(self):
        """Python tools menu"""
        print("\n🛠️ Python Tools Menu:")
        print("  [1] Check Python version")
        print("  [2] List installed packages")
        print("  [3] Install requirements")
        print("  [4] Check syntax of file")
        print("  [5] Format code (black)")
        print("  [0] Back to main menu")

        choice = input("\nSelect (0-5): ").strip()

        if choice == "1":
            os.system("python3 --version")
        elif choice == "2":
            os.system("pip list")
        elif choice == "3":
            os.system(
                "cd /Users/andy/DAIOF-Framework && pip install -r requirements.txt"
            )
        elif choice == "4":
            file = input("Enter file path: ").strip()
            os.system(f"python3 -m py_compile {file}")
        elif choice == "5":
            file = input("Enter file path: ").strip()
            os.system(f"black {file}")

        input("\nPress Enter to continue...")

    def view_checklist(self):
        """View command checklist"""
        print("\n📋 Opening Command Checklist...")
        checklist_path = self.base_dir / "COMMAND_CHECKLIST.md"
        if checklist_path.exists():
            os.system(f"less {checklist_path}")
        else:
            print("❌ Checklist not found")

        input("Press Enter to continue...")

    def exit_program(self):
        """Exit program"""
        print("\n👋 Thank you for using HYPERAI Framework!")
        print("🎼 Powered by HYPERAI")
        print("👤 Creator: Nguyễn Đức Cường (alpha_prime_omega)")
        sys.exit(0)

    def run(self):
        """Main loop"""
        while True:
            self.clear_screen()
            self.print_header()
            self.print_menu()

            choice = self.get_choice()

            if choice in self.menu_options:
                _, action = self.menu_options[choice]
                action()
            else:
                print("❌ Invalid option! Please try again.")
                input("Press Enter to continue...")


def main():
    """Main entry point"""
    try:
        guide = HYPERAIQuickStart()
        guide.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
