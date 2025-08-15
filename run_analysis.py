#!/usr/bin/env python3
"""
Quick Start Guide for LLM Analysis System

This script provides easy commands to run the modular analysis system.
"""

import os
import subprocess
import sys

def run_python_command(script_name, description):
    """Run a Python script with proper error handling"""
    python_exe = r"C:/Users/jsava/AppData/Local/Programs/Python/Python313/python.exe"
    
    print(f"\n🔍 {description}")
    print("=" * 50)
    
    try:
        result = subprocess.run([python_exe, script_name], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print(result.stdout)
            print(f"✅ {description} completed successfully!")
        else:
            print(f"❌ Error running {script_name}:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Failed to run {script_name}: {e}")
        return False
    
    return True

def open_dashboard():
    """Open the latest dashboard in browser"""
    dashboard_path = "enhanced_analysis_dashboard.html"
    if os.path.exists(dashboard_path):
        abs_path = os.path.abspath(dashboard_path)
        url = f"file:///{abs_path.replace(os.sep, '/')}"
        print(f"\n🌐 Opening dashboard: {url}")
        
        try:
            import webbrowser
            webbrowser.open(url)
            print("✅ Dashboard opened in browser!")
        except Exception as e:
            print(f"❌ Could not open browser: {e}")
            print(f"📍 Manual URL: {url}")
    else:
        print("❌ Dashboard not found. Run analysis first.")

def main():
    """Main menu for the analysis system"""
    
    print("🤖 LLM Analysis System - Quick Start")
    print("=" * 40)
    print()
    print("Available commands:")
    print("1. Run standard modular analysis")
    print("2. Run enhanced analysis with demo modules")
    print("3. Generate dashboard only")
    print("4. Open latest dashboard")
    print("5. Show all available files")
    print("0. Exit")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (0-5): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                if run_python_command("modular_analyzer.py", "Standard Modular Analysis"):
                    open_dashboard()
            elif choice == "2":
                if run_python_command("demo_modular_system.py", "Enhanced Analysis with Security Module"):
                    open_dashboard()
            elif choice == "3":
                run_python_command("dashboard_generator.py", "Dashboard Generation")
            elif choice == "4":
                open_dashboard()
            elif choice == "5":
                print("\n📁 Current workspace files:")
                for item in sorted(os.listdir(".")):
                    if os.path.isfile(item):
                        print(f"  📄 {item}")
                    elif os.path.isdir(item) and not item.startswith('.'):
                        print(f"  📁 {item}/")
            else:
                print("❌ Invalid choice. Please enter 0-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
