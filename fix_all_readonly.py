import re

with open("/home/ulugbek/Projects/epl/document_processor/forms.py", "r") as f:
    content = f.read()

# removing all readonly from forms.py
content = re.sub(r", widget=forms\.TextInput\(attrs=\{'readonly': 'readonly'\}\)", "", content)

with open("/home/ulugbek/Projects/epl/document_processor/forms.py", "w") as f:
    f.write(content)

print("forms updated")
