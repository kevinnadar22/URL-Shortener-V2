my_list = [i for i in range(10123)]
for i in range(0, len(my_list), 100):
    print(my_list[i:i+100])
    