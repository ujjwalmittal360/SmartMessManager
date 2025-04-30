import subprocess

# Replace with your directory path
directory = r"C:\Users\ujjwa\Desktop\SmartMessManager"

# Run radon on all Python files in the directory
result = subprocess.run(
    ["radon", "cc", directory, "-a"],
    capture_output=True,
    text=True
)

# Print result to console
print(result.stdout)

# Optional: Save to file
with open("cc_report.txt", "w") as f:
    f.write(result.stdout)
