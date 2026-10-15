from pathlib import Path
raw = Path('data/raw')
classes = ['battery','cfl_bulb','keyboard','mobile_phone','monitor_crt','pcb','other']
print('Class counts after ingest:')
print('-' * 35)
total = 0
for c in classes:
    d = raw / c
    n = len(list(d.glob('*.*'))) if d.exists() else 0
    flag = '  [LOW - need own photos]' if n < 80 else ''
    print(f'  {c:<20} {n:>5}{flag}')
    total += n
print(f'  {"TOTAL":<20} {total:>5}')
