import re
import regex
# re.search returns either a re.Match object (if it matches) or None (if it
# does not match)

sentence = "This is a sample string."
t1 = "is"
t2 = "xyz"

print (bool(re.search(r'is', sentence)))
print (bool(re.search(r'xyz', sentence)))

if re.search(t1, sentence):
    print ('There was a match')

if not re.search(t2, sentence):
    print ('There was a not a match for:' + t2)

words = ['cat', 'attempt', 'tattle']

x = [w for w in words if re.search(r'tt', w)]
print(x)

pet = re.compile(r'dog')

print(bool(pet.search('They bought a dog')))
print(bool(pet.search('A cat crossed their path')))



