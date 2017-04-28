f_in = open("word_list","rb")
f_out = open("stopword.py","wb")

f_out.write("from sets import Set\n\n")
f_out.write("stopwords = Set([")

while True:
    line = f_in.readline()
    if not line:
        break
    f_out.write("\"%s\","%(line.replace("\n","")))

f_out.write("])\n")
