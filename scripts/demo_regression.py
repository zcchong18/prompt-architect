import os
import shutil
import tempfile
from prompt_architect.core.template import PromptTemplate
from prompt_architect.core.evaluator import Evaluator
from prompt_architect.core.storage import Storage

def run_demo():
    print("🚀 Starting 'Broken Prompt' Demo...")

    # 1. Setup temporary working directory
    demo_dir = tempfile.mkdtemp(prefix="demo_prompt_architect_")
    print(f"📂 Created demo directory: {demo_dir}")
    
    try:
        # 2. Initialize components
        storage = Storage(demo_dir)
        evaluator = Evaluator()

        # 3. Define our 'Gold Standard' Prompt
        # This prompt expects a {name} and {topic}
        gold_template_str = "Hello {name}, welcome to the world of {topic}!"
        gold_template = PromptTemplate(name="gold_standard", template_string=gold_template_str)
        
        # 4. Save the Gold Standard
        storage.save(gold_template)
        print("✅ Gold Standard template saved.")

        # 5. Define the Evaluation Case (The 'Test')
        # We want to see if the prompt handles 'Alice' and 'AI' correctly.
        test_case = {
            "name": "Alice",
            "topic": "AI"
        }
        expected_output = "Hello Alice, welcome to the world of AI!"

        # 6. THE "BROKEN" PROMPT
        # This version accidentally removed the space after the comma
        broken_template_str = "Hello {name},welcome to the world of {topic}!"
        broken_template = PromptTemplate(name="broken_version", template_string=broken_template_str)
        storage.save(broken_template)
        print("⚠️  Broken template (regression) saved.")

        # 7. Run Evaluation
        print("🔍 Running Evaluation...")
        
        # We evaluate the broken template against the expected output
        # Using the 'exact' metric
        results = []
        
        # Test Gold
        gold_output = gold_template.render(**test_case)
        gold_score = 1.0 if gold_output == expected_output else 0.0
        results.append({"template": "gold_standard", "score": gold_score})

        # Test Broken
        broken_output = broken_template.render(**test_case)
        broken_score = 1.0 if broken_output == expected_output else 0.0
        results.append({"template": "broken_version", "score": broken_score})

        # 8. Report Results
        print("\n--- 📊 Evaluation Report ---")
        for res in results:
            status = "✅ PASS" if res['score'] == 1.0 else "❌ FAIL"
            print(f"Template: {res['template']} | Score: {res['score']} | Status: {status}")
        
        if results[0]['score'] == 1.0 and results[1]['score'] == 0.0:
            print("\n🎯 DEMO SUCCESS: The system successfully caught the regression!")
        else:
            print("\n❌ DEMO FAILED: The system failed to detect the error.")
            exit(1)

    finally:
        # Cleanup
        print(f"\n🧹 Cleaning up {demo_dir}...")
        shutil.rmtree(demo_dir)

if __name__ == "__main__":
    run_demo()
