def get_chart_dict(rows):
    labels = []
    values = []
    for row in rows:
        labels.append(row[0])
        values.append(row[1])

    return {"labels": labels, "values": values}