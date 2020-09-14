def createEntry(type, name, data):
    return {'type':type,'name':name,'data':data}


def appendEntry(acc, type, name, data):
    # if not acc:
        # acc=[]
    acc.append(createEntry(type, name, data))
    return acc
