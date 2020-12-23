def remove_newlines(fname):
    text_file = open(fname, "r")
    lines = text_file.readlines()
    result = filter(lambda x: x != '', lines)
    result = filter(lambda x: "am" not in x, result)
    result = filter(lambda x: "pm" not in x, result)
    result = filter(lambda x: x != '\n', result)
    text_file.close()
    print(list(result))

# flist = open(fname).readlines()
# text = [s.rstrip('\n') for s in flist]
# for index, letter in enumerate(text):
#     print(index)
#     if letter == '':
#         text.pop(index)
