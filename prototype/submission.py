n = int(input())
chars = 0
for _ in range(n):
    chars += len(input().strip())
print('there are', chars, 'characters')
