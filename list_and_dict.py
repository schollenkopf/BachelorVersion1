import datetime
dicts = {"a": [1, 2, 3]}
a = dicts["a"]
a.append(4)

dicts["a"] = a

print(dicts["a"])
b = "2021-10-01T08:30:00.000000000"
print(b[0:26])
print(datetime.datetime.strptime(
    "2021-10-01T08:30:00.000000", "%Y-%m-%dT%H:%M:%S.%f").timestamp())


all_times = [[[] for i in range(3)] for j in range(3)]

all_times[0][0].append(2)



print(all_times)

