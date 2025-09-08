school_class = {}

while True:
    name = input("Enter the student's name: ")
    if name == '':
        break

    score = float(input("Enter the student's score (0-10): "))
    if score not in range(0, 11):
        break

    if name in school_class:
        school_class[name] += (score,)
    else:
        school_class[name] = (score,)
print(school_class)
for name in sorted(school_class.keys()):
    for score in school_class[name]:
        adding = sum(school_class[name])
        counter = len(school_class[name])
    print(name, ":", adding / counter)
    # adding and counter should be changed with the sum and len



