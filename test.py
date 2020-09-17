for i in [1,2,3,4,3,3,2,1]:
    print(str(i)+':')
    try:
        print('1,2,3'.split(',')[i])
    except IndexError as err:
        print('Error on ', ':', err)
        continue
    print('end')


