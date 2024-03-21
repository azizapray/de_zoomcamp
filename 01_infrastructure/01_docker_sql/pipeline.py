import sys 
import pandas as pd

# print argumen
print(sys.argv)

# argumen 0 adalah nama file
# argumen 1 berisi argumen pertama yang sebenarnya kita perlukan
day = sys.argv[1]

# tampilkan kalimat dengan argumen
print(f'job finisihed successfully for day = {day}')