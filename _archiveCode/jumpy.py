number = 100
print(number)
count = 0
sum = 0
while count < 500:
    # convert number into an array of digit
    numArray_default = list(str(number))
    # make 3 copies for comparing
    numArray_asc = numArray_default.copy()
    numArray_desc = numArray_default.copy()
    # sort each array accordingly
    numArray_asc.sort()
    numArray_desc.sort(reverse=True)
    # print(count, number, numArray_default, numArray_asc)
    # print(numArray_asc == numArray_default)
    # print(numArray_desc == numArray_default)
    if(numArray_default == numArray_asc or numArray_default == numArray_desc):
        print("this is not jumpy", number)
    else:
        sum = sum + number
        count = count + 1
    number = number + 1
print(sum)