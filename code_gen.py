def generate_request_segment(baseurl, requrl, params, headers):
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

    retval = 'import requests\n\nbaseurl = "' + baseurl + '"'
    if len(requrl) > 0 and requrl[0] == '/':
        requrl = requrl[1:]
    retval += '\nrequrl = "' + requrl + '"'

    #headers
    if len(headers) > 0:
        retval += '\n\nheaders = {' + '\n'
        for index, (key, value) in enumerate(headers.items()):
            retval += '    "' + key + '": "' + value + '"' + ',' * (index != len(headers) - 1) + '\n' #no comma on last item
        retval += '}\n'

    #params
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
    return retval
