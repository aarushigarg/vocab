f = open("/Users/aarushi/Documents/Vocab website/Code/data.noun_partial")

dictionary = []

#going through all the lines
for line in f:
    dict_entry = []
    num_of_words = int(line[14:16], 16)
    words = ""
    start_ind = 17

    #finding all the words in a line
    for num in range(num_of_words):
        #seperating the words by a comma and space
        if num != 0:
            words += ", "
            start_ind += 3

        #adding each character of the word inividually
        for i in range(start_ind, len(line)):
            if line[i] != " ":
                if line[i] == "_":
                    words += " "
                else:
                    words += line[i]
                start_ind += 1
            else:
                break

    dict_entry.append(words)

    #finding the definitions
    start = False
    definitions = ""
    for i in range(start_ind, len(line)):
        if line[i] == "|":
            start = True

        if line[i] == ";" and line[i+1] == " " and line[i+2] == '"' or line[i] == "\n":
            start = False

        if start:
            definitions += line[i]
    
    #removing the bar and extra spaces
    real_def = ""
    if definitions[-1] == " ":
        for i in range(2, len(definitions)-2):
            real_def += definitions[i]
    else:
        for i in range(2, len(definitions)):
            real_def += definitions[i]
    

    dict_entry.append(real_def)

    dictionary.append(dict_entry)
print(dictionary)


f.close()