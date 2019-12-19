def typecast_dict(dict1):
    for key in dict1:
        try:
            dict1[key] = float(dict1[key])
        except:
            continue
    return dict1
