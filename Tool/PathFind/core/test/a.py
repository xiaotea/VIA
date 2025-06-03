s_version = '10.2.3'
s_lenth = len(s_version)
print(s_version[:0])
for i in range(s_lenth, 0, -1):
    print(i)
    print(s_version[:i])