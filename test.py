import subprocess     #Popen
"""
proc = subprocess.Popen('E:\\MCServer\\bds1.17.10\\bedrock_server.exe > Temp/console.txt', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
for line in iter(proc.stdout.readline, 'r'):
    print(line)
    if not subprocess.Popen.poll(proc) is None:
        if line == "":
            break
proc.stdout.close()"""

p = subprocess.Popen('Library\index.bat', stdout=subprocess.PIPE, bufsize=1)
for line in iter(p.stdout.readline, b''):
    print(line.decode('utf-8')),
p.stdout.close()
p.wait()
