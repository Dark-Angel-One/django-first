with open('requirements.txt', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    line = line.strip()
    if line.startswith('gunicorn'):
        new_lines.append('gunicorn>=21.0.0\n')
    elif line.startswith('whitenoise'):
        new_lines.append('whitenoise>=6.0.0\n')
    elif line:
        new_lines.append(line + '\n')

if not any(l.startswith('whitenoise') for l in new_lines):
    new_lines.append('whitenoise>=6.0.0\n')

with open('requirements.txt', 'w') as f:
    f.writelines(new_lines)
