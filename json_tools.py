from typing import List

def is_match(a: str, b:str, stage):
    """
    Returns true if items are equal enough
    :param a: Search value
    :param b: Match Value
    :param stage: 0 = exact and numeric, 1 = first characters, 2 = anywhere
    """
    a = str(a).lower()
    b = str(b).lower()
    if len(a) == 0 or len(b) == 0:
        return False
    if stage == 0:
        return a == b

    if stage == 1:
        if a.isnumeric() or b.isnumeric():
            return False
        return a == b[:len(a)]
    if stage == 2:
        if a.isnumeric() or b.isnumeric():
            return False
        return a in b

class SearchManager:
    def __init__(self, searchableItems):
        self.searchableItems: List[SearchableItem] = searchableItems
        self.keySearchIndex = 0
        self.valueSearchIndex = 0

    def set_index_by_keystring(self, keystring):
        for index, item in enumerate(self.searchableItems):
            if item.keystring == keystring:
                self.keySearchIndex = index
                self.valueSearchIndex = index

    def get_next_key_match(self, key):
        for stage in range(0, 3):
            for index, item in enumerate(self.searchableItems[self.keySearchIndex+1:]):
                if is_match(key, item.key, stage):
                    self.keySearchIndex += index + 1
                    return item
            for index, item in enumerate(self.searchableItems):
                if is_match(key, item.key, stage):
                    self.keySearchIndex = index
                    return item

    def get_next_value_match(self, value):
        for stage in range(0, 2):
            for index, item in enumerate(self.searchableItems[self.valueSearchIndex + 1:]):
                if is_match(value, item.value, stage):
                    self.valueSearchIndex += index + 1
                    return item
            for index, item in enumerate(self.searchableItems):
                if is_match(value, item.value, stage):
                    self.valueSearchIndex = index
                    return item


class SearchableItem:
    def __init__(self, value, key, keystring):
        self.value = value
        self.key = key
        self.keystring = keystring

    def __repr__(self):
        return "Value: " + str(self.value) + " Key: " + str(self.key) + " Key String: " + self.keystring

def make_treeview(data, opendepth = 3, cdepth = 0, keystring=''):
    if isinstance(data, dict):
        out = []
        for key, value in data.items():
            retval = make_treeview(value, opendepth=opendepth, cdepth = cdepth + 1,
                                   keystring = keystring+ '["' + key + '"]')
            if isinstance(value, dict):
                if len(value) == 0:
                    t = "Empty Dictionary"
                else:
                    t = "Dictionary"
                out.append({"key": key, "value": "", "type": t, "subentry": retval,
                            'open': cdepth < opendepth, 'keystring': keystring + '["' + key + '"]'})

            elif isinstance(value, list):
                if len(value) == 0:
                    t = "Empty List"
                else:
                    t = "List"
                out.append({"key": key, 'type': t, "value": "", "subentry": retval,
                            'open': cdepth < opendepth, 'keystring': keystring + '["' + key + '"]'})

            else:
                out.append({"key": key, 'type': type(retval).__name__, "value": retval,
                            'keystring': keystring + '["' + key + '"]'})
        return out

    elif isinstance(data, list):
        out = []
        for index, item in enumerate(data):
            if index > 0:
                opendepth = 0
            retval = make_treeview(item, opendepth=opendepth, cdepth = cdepth + 1,
                                   keystring = keystring+ '[' + str(index) + ']')
            if isinstance(item, dict):
                if len(item) == 0:
                    t = "Empty Dictionary"
                else:
                    t = "Dictionary"
                out.append({"key": str(index), "type": t, "value":'',
                            "subentry": retval, 'open': cdepth < opendepth,
                            'keystring': keystring + '[' + str(index) + ']'})

            elif isinstance(item, list):
                if len(item) == 0:
                    t = "Empty List"
                else:
                    t = "List"
                out.append({"key": str(index), "type": t, "value":"",
                            "subentry": retval, 'open': cdepth < opendepth,
                            'keystring': keystring + '[' + str(index) + ']'})

            else:
                out.append({"key": str(index), "value": retval, "type": type(retval).__name__,
                            'keystring': keystring + '[' + str(index) + ']'})
        return out

    else:
        return data

def update_treeview(tkwidget, data):
    for item in tkwidget.get_children():
        tkwidget.delete(item)


    datacolumnnames = ['key', 'value', 'type']
    searchableItems = []
    def traverse(p, t):
        for obj in t:
            values = []
            for value in datacolumnnames[1:]:
                values.append(obj.get(value, ""))
            tkwidget.insert(p, index='end', iid=obj['keystring'], text=obj[datacolumnnames[0]], values=values)
            if obj.get("subentry", []):
                tkwidget.item(obj['keystring'], open=obj['open'])
            traverse(obj['keystring'], obj.get('subentry', []))
            searchableItems.append(SearchableItem(obj['value'], obj['key'], obj['keystring']))

    traverse('', data)
    return SearchManager(searchableItems)