C = input()
N = int(input())
ways = ['В', 'С', 'З', 'Ю']
i = (ways.index(C) + N) % 4
print(ways[i])
