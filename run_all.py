"""Run the whole pipeline in order: python run_all.py"""
import importlib

STEPS = ["task1_cleaning", "task2_content_type", "task3_country",
         "task4_trends", "task5_rating_genre", "task6_business_report"]

for name in STEPS:
    print(f"\n>>> {name}")
    importlib.import_module(name).main()
print("\nAll tasks finished. See the output/ folder.")
