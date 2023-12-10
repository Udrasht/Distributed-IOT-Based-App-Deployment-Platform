def get_average(json_array):
    # Remove common field from each object
    for obj in json_array:
        obj.pop('timestamp', None)

    # Calculate averages
    averages = {}
    count = len(json_array)
    for obj in json_array:
        for key in obj:
            if key in averages:
                averages[key] += obj[key]
            else:
                averages[key] = obj[key]
    for key in averages:
        averages[key] = averages[key] / count
    return averages


# json_array = [
#     { "timestamp": 1, "temperature": 10, "humidity": 20, "tds": 30 },
#     { "timestamp": 2, "temperature": 20, "humidity": 30, "tds": 40 },
#     { "timestamp": 3, "temperature": 30, "humidity": 40, "tds": 50 }
# ]

json_array = [
    {  "humidity": 20},
    {  "humidity": 30},
    {  "humidity": 40}
]

avg_obj = get_average(json_array)

print(avg_obj)
