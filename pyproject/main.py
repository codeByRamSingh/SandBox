import subprocess

print("Choose an option:")
print("1. Individual entry")
print("2. Admission")

choice = input("Enter your choice (1 or 2): ")

if choice == "1":
    subprocess.run(["python", "pyproject/individuals.py"])
elif choice == "2":
    print("Admission option selected. (Functionality not implemented yet)")
else:
    print("Invalid choice.")
