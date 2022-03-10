def make_treeview(data, opendepth = 3, cdepth = 0):
    if isinstance(data, dict):
        out = []
        for key, value in data.items():
            retval = make_treeview(value, opendepth=opendepth, cdepth = cdepth + 1)
            if isinstance(value, dict):
                if len(value) == 0:
                    t = "Empty Dictionary"
                else:
                    t = "Dictionary"
                out.append({"key": key, "value": "", "type": t, "subentry": retval, 'open': cdepth < opendepth})

            elif isinstance(value, list):
                if len(value) == 0:
                    t = "Empty List"
                else:
                    t = "List"
                out.append({"key": key, 'type': t, "value": "", "subentry": retval, 'open': cdepth < opendepth})

            else:
                out.append({"key": key, 'type': type(retval).__name__, "value": retval})
        return out

    elif isinstance(data, list):
        out = []
        for index, item in enumerate(data):
            if index > 0:
                opendepth = 0
            retval = make_treeview(item, opendepth=opendepth, cdepth = cdepth + 1)
            if isinstance(item, dict):
                if len(item) == 0:
                    t = "Empty Dictionary"
                else:
                    t = "Dictionary"
                out.append({"key": str(index), "type": t, "value":'',
                            "subentry": retval, 'open': cdepth < opendepth})

            elif isinstance(item, list):
                if len(item) == 0:
                    t = "Empty List"
                else:
                    t = "List"
                out.append({"key": str(index), "type": t, "value":"",
                            "subentry": retval, 'open': cdepth < opendepth})

            else:
                out.append({"key": str(index), "value": retval, "type": type(retval).__name__})
        return out

    else:
        return data

def udpate_treeview(tkwidget, data):
    for item in tkwidget.get_children():
        tkwidget.delete(item)


    datacolumnnames = ['key', 'value', 'type']
    def traverse(p, t, iid):
        for obj in t:
            iid[0] += 1
            values = []
            for value in datacolumnnames[1:]:
                values.append(obj.get(value, ""))
            tkwidget.insert(p, index='end', iid=iid[0], text=obj[datacolumnnames[0]], values=values)
            if obj.get("subentry", []):
                tkwidget.item(iid[0], open=obj['open'])
            traverse(iid[0], obj.get('subentry', []), iid)

    traverse('', data, [0])