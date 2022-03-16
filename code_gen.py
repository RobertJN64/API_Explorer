class CodeGenInfo:
    def __init__(self, baseurl, requrl, params, headers, data):
        self.baseurl = baseurl
        self.requrl = requrl
        self.params = params
        self.headers = headers
        self.data = data
        self.searchKey = None
        self.searchValue = None


def generate_request_segment(codeGenInfo: CodeGenInfo):
    """
    Generates a code segment for making a rest API request.
    """

    #EXAMPLE:
    """
    import requests
    baseurl = {baseurl}
    requrl = {requrl}
    paramAKey = paramAValue
    paramBKey = paramBValue
    headers = {
      headerAKey: headerAValue,
      headerBKey: headerBValue
    }
    response = requests.get(baseurl + '/' + requrl + '?' + paramAKey + '=' + paramAValue + '&' + paramBKey + '=' + paramBValue,
                     headers = headers)
    respJSON = repsonse.json()
    """

    requrl = codeGenInfo.requrl
    retval = 'import requests\n\nbaseurl = "' + codeGenInfo.baseurl + '"'
    if len(requrl) > 0 and requrl[0] == '/':
        requrl = requrl[1:]
    retval += '\nrequrl = "' + requrl + '"'

    #headers
    headers = codeGenInfo.headers
    if len(headers) > 0:
        retval += '\n\nheaders = {' + '\n'
        for index, (key, value) in enumerate(headers.items()):
            retval += '    "' + key + '": "' + value + '"' + ',' * (index != len(headers) - 1) + '\n' #no comma on last item
        retval += '}\n'

    #params
    params = codeGenInfo.params
    pstring = ""
    if len(params) > 0:
        retval += '\n'
        for index, key in enumerate(params):
            if "?" in pstring:
                pstring += "&" + key + '=" + ' + key + ' + "' * (index != len(params) - 1)
            else:
                pstring += "?" + key + '=" + ' + key + ' + "' * (index != len(params) - 1)

        for key, value in params.items():
            retval += key + " = " + '"' + value + '"\n'

        retval += '\npstring = "' + pstring

    retval += ('\nresponse = requests.get(baseurl + "/" + requrl' + ' + pstring' * (len(params) > 0) +
              ', headers=headers' * (len(headers) > 0) +
              ')')
    retval += '\ndata = response.json()'

    if codeGenInfo.searchKey is not None and codeGenInfo.searchValue is not None:
        itemName = 'item'
        sKey = codeGenInfo.searchKey
        items = [item.replace("]", "").replace('"', "").replace('"', "") for item in sKey.split('[')[1:]]
        for item in items:
            if not item.isnumeric():
                itemName = item
        retval += '\n' + itemName + ' = data' + sKey
    return retval
