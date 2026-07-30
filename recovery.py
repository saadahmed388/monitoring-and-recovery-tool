import os
import subprocess

input_dir = "Monitoring App\Daily Monitoring.exe_extracted"
output_dir = "Monitoring App\decompiled_output"

for root, dirs, files in os.walk(input_dir):
    for file in files:
        if file.endswith(".pyc"):
            input_file = os.path.join(root, file)
            output_file = os.path.join(output_dir, file.replace(".pyc", ".py"))
            
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            command = f'decompyle3 "{input_file}" > "{output_file}"'
            subprocess.run(command, shell=True)