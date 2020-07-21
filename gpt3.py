import openai
#import pickle
import string
import re

openai.api_key = "sk-VVIX7jYxSZnJJl8PPQ8LF8Z2V5QFe83nQwQrVapN"

def create_rhyme_dictionary():
    pronounce_file = open("pronounce.txt", "r")
    rhyme_dictionary = {}
    reverse_rhyme_dictionary = {}
    syllable_count_dictionary = {}
    for line in pronounce_file:
        line = line.strip()
        if line.startswith(';'): continue
        word, phones = line.split("  ")
        syllables = phones.split(" ")
        syllable_count_dictionary[word]=phones.count("0")+phones.count("1")+phones.count("2")
        join_flag = 0
        outstring = ''
        for syllable in syllables:
            if join_flag == 0:
                if "1" in syllable:
                    join_flag = 1
                    outstring = syllable
            else:
                outstring = outstring + " " + syllable
        if outstring == "":
            for syllable in syllables:
                if join_flag == 0:
                    if "0" in syllable:
                        join_flag = 1
                        outstring = syllable
                else:
                    outstring = outstring + " " + syllable
        rhyme_dictionary[word.lower()] = outstring
        if outstring in reverse_rhyme_dictionary:
            reverse_rhyme_dictionary[outstring].append(word.lower())
        else:
            reverse_rhyme_dictionary[outstring]=[word.lower()]
    
    
    bad_rhymes = ["a","an","it","is","as","at","was","of","at","that",
                     "has","your","my","his","their","on","for","its","to",
                     "from","if","ur","re","our","un","dis","diss","mis",
                     "wat","com","comm","psych","lol","vis","al","los","pol",
                     "bis","up", " la","sa","ha","mah", " wal", "lat", "ot", "sol",
                     "b","c","d","e","f","g","h","i","j","k","l","m",
                     "n","o","p","q","r","s","t","u","v","w","x","y","z"]
    return rhyme_dictionary, reverse_rhyme_dictionary, bad_rhymes, syllable_count_dictionary

def create_stress_dictionary():
    pronounce_file = open("pronounce.txt", "r")
    stress_dictionary = {}
    for line in pronounce_file:
        line = line.strip("\n")
        parts = line.split(" ")
        syllable_list = parts[2:]
        word = parts[0]
        stresses=""
        if word in ["A","AN","THE","AND","BUT","OR"]:
            stresses="~"
        elif word in ["I","YOU","HE","SHE","IT","WE","THEY","MY","HIS","HER","ITS","OUR","YOUR","THEIR","OURS","YOURS","THEIRS","AM","IS","ARE","WAS","WERE","BEEN","BE","HAVE","HAS","HAD","DO","DOES","DID","WILL","WOULD","SHALL","SHOULD","MAY","MIGHT","MUST","CAN","COULD","OF","WITH","AT","FROM","TO","IN","FOR","ON","BY","LIKE","SINCE","UP","OFF","NEAR","WHICH","AS","EACH","SO","THAT","THATS"]:
            stresses="?"    
        else:
            for syllable in syllable_list:
                if syllable.endswith("1"):
                    stresses=stresses+"`"
                elif syllable.endswith("0"):
                    stresses=stresses+"~"
                elif syllable.endswith("2"):
                    stresses=stresses+"?"
        if word in {"A","B","C","D","E","F","G","H","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"}:
            pass
        else:
            stress_dictionary[word] = stresses
    return stress_dictionary

def compare_meters(test_meter,target_meter):
    #checks whether test_meter is plausibly matching target_meter. test_meter can include unknown ? stresses. 
    matchflag=False
    
    if len(test_meter)>0 and test_meter[-1]=="*":
        test_meter=test_meter[:-1]
    if "*" in test_meter[:-1]:
        return False
    if len(test_meter)==len(target_meter):
        matchflag=True
        for character1,character2 in zip(test_meter,target_meter):
            if (character1=="`" and character2=="`") or (character1=="~" and character2=="~") or character1=="?":
                pass
            else:
                matchflag=False
    #If you want to force it to end on a strongly stressed word, uncomment this.
    #elif test_meter[-1] == '?':
    #    matchflag = False  
    return matchflag

def text_to_meter(text, stress_dictionary):
    #calculates the meter of a line of text.
    if len(text)==0:
        return ''
    #capitalize the text
    s = text.upper()
    #remove any punctuation
    whitelist = set('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    s2 = ''.join(filter(whitelist.__contains__, s))
    #split the text into individual words
    split_list = re.split('[\s\']', s2)
    # split_list = list(s2.split(" ")) 
    #find the stress for individual words
    line_stress=""
    for word in split_list:
        if len(word)>0:
            if word in stress_dictionary:
                line_stress = line_stress + stress_dictionary[word]
            else:
                line_stress = line_stress + "*"
    return line_stress

def poem_scheme(kind):
    #in "rhyme_scheme" the first thing in the list for each line must be the line you want to rhyme with. 
    # After that you can list other lines you want to avoid repeating the last word.
    # "meter_scheme" is ` for accented, ~ for unaccented syllable. 
    global poem_line
    if kind == "limerick":
        number_of_lines = 5
        meter_scheme = [""] * number_of_lines
        for line in {0,1,4}:
            meter_scheme[line] = "~`~~`~~`" 
        for line in {2,3}:
            meter_scheme[line] = "~`~~`"
        #meter_scheme[0] = "~`" # if you want to start with a prompt like "There once was a girl from"
        rhyme_scheme = [ "", [poem_line[0]], "", [poem_line[2]], [poem_line[0], poem_line[1]] ]
    if kind == "sonnet":
        number_of_lines = 10
        meter_scheme = [""] * number_of_lines
        for line in range(0,number_of_lines):
            meter_scheme[line] = "~`~`~`~`~`"
        rhyme_scheme = ["","",[poem_line[0]],[poem_line[1]],"","",[poem_line[4]],[poem_line[5]],"",[poem_line[8]] ]
    if kind == "blank verse":
        number_of_lines = 10
        meter_scheme = [""] * number_of_lines
        for line in range(0,number_of_lines):
            meter_scheme[line] = "~`~`~`~`~`"
        rhyme_scheme = [[0]]*number_of_lines
    if kind == "couplets":
        number_of_lines = 10
        meter_scheme = [""] * number_of_lines
        for line in range(0,number_of_lines):
            meter_scheme[line] = "`~`~`~"
        rhyme_scheme = ["",[poem_line[0]],"",[poem_line[2]],"",[poem_line[4]],"",[poem_line[6]],"",[poem_line[8]] ]
    if kind == "mini-couplets":
        number_of_lines = 20
        meter_scheme = [""] * number_of_lines
        for line in range(0,number_of_lines):
            meter_scheme[line] = "~`~`"
        rhyme_scheme = ["",[poem_line[0]],"",[poem_line[2]],"",[poem_line[4]],"",[poem_line[6]],"",[poem_line[8]],"",[poem_line[10]],"",[poem_line[12]],"",[poem_line[14]],"",[poem_line[16]],"",[poem_line[18]] ]
    if kind == "ballad":
        number_of_lines = 16
        meter_scheme = [""] * number_of_lines
        for line in {0,2,4,6,8,10,12,14}:
            meter_scheme[line] = "~`~`~`~`"
        for line in {1,3,5,7,9,11,13,15}:
            meter_scheme[line] = "~`~`~`"
        rhyme_scheme = [[0],"",[0],[poem_line[1]],[0],"",[0],[poem_line[5]],[0],"",[0],[poem_line[9]],[0],"",[0],[poem_line[13]]]
    return number_of_lines, rhyme_scheme, meter_scheme


def generate_rhyming_line(poem_so_far, rhyme):
    prompt_head = 'Q. Complete the poem with a line ending in the word "sigheth"\nWhere Claribel low-lieth\nThe breezes pause and die,\nLetting the rose-leaves fall:\nA. But the solemn oak-tree sigheth,\nQ. Complete the poem with a line ending in the word "detoxify"\nSomeone had blundered.\nTheirs not to make reply,\nTheirs not to reason why,\nA. Theirs but to do and detoxify.\nQ. Complete the poem with a line ending in the word "yesteryear"\nA boat, beneath a sunny sky,\nLingering onward dreamily\nIn an evening of July —\nA: Children three that nestle yesteryear,\nQ. Complete the poem with a line ending in the word "ear"\nAlice moving under skies\nNever seen by waking eyes.\nChildren yet, the tale to hear,\nQ. Complete the poem with a line ending in the word " '
    prompt = prompt_head + rhyme + " '\n" + poem_so_far + "\nA."
    try:
        response = openai.Completion.create(engine="davinci", api_key = openai.api_key, prompt=prompt, max_tokens=15, n=10, logprobs = 1, stop = "\n")
        completions = []
        for choice in response.choices:
            completions.append(choice.text)
        return completions
    except:
        return []

def generate_nonrhyming_line(poem_so_far):
    try:
        response = openai.Completion.create(engine="davinci", api_key = openai.api_key, prompt=poem_so_far, max_tokens=15, n=20, logprobs = 1, stop = "\n")
        completions = []
        for choice in response.choices:
            completions.append(choice.text)
        return completions
    except:
        return []
    

def last_word(line):
    split_completion = line.split()
    if len(split_completion)>0:
        last_word = split_completion[-1]
        last_word_stripped = last_word.translate(str.maketrans('', '', string.punctuation))
        return last_word_stripped
    else: 
        return ""
        
def find_metrical_completions(completions, meter, stress_dictionary):
    meter_OK=[]
    for completion in completions:
        completion_meter = text_to_meter(completion,stress_dictionary)
        comparison = compare_meters(completion_meter, meter)
        if comparison == True:
            meter_OK.append(completion)
    if len(meter_OK)>0:
        return meter_OK
    else:
        return []

    
stress_dictionary = create_stress_dictionary()   
rhyme_dictionary, reverse_rhyme_dictionary, bad_rhymes, syllable_count_dictionary = create_rhyme_dictionary()

poem_so_far = "He clasps the crag with crooked hands;\nClose to the sun in lonely lands,"
meter ="~`~`~`~`"
for ii in range(1,10):
    possible_rhymes = reverse_rhyme_dictionary[rhyme_dictionary[last_word(poem_so_far)]]
    rhyming_completions = []
    for rhyme in possible_rhymes:
        print(rhyme, end = " ")
        completions = generate_rhyming_line(poem_so_far, rhyme)
        if len(completions)>0:
            for completion in completions:
                    last_word_stripped = last_word(completion)
                    for rhyme2 in possible_rhymes:
                        if last_word_stripped == rhyme2:
                            rhyming_completions.append(completion)
                    

    metrical_completions = find_metrical_completions(rhyming_completions, meter, stress_dictionary)
    print()
    count = 0
    for completion in metrical_completions:
        print(str(count) + completion)
        count = count+1
    index = int(input("choose by number:"))
    best_completion = metrical_completions[index]
    poem_so_far = poem_so_far + "\n" + best_completion +"\n"
    metrical_completions=[]
    while len(metrical_completions)==0:
        completions = generate_nonrhyming_line(poem_so_far)
        metrical_completions = find_metrical_completions(completions,meter,stress_dictionary)
    print()
    count = 0
    for completion in metrical_completions:
        print(str(count) + completion)
        count = count+1
    index = int(input("choose by number:"))
    best_completion = metrical_completions[index]
    poem_so_far = poem_so_far + best_completion
    print(poem_so_far)


    