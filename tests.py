import os

os.environ['CHANNELS'] = "True"
x = True if os.environ.get('CHANNELS') == 'True' else False
print(x)