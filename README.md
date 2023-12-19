## FoodIE Implementation

### Requirements
Create a virtual env and run the following command to install the required packages
```
pip3 install -r requirements.txt
pip install https://github.com/UCREL/pymusas-models/releases/download/en_dual_none_contextual-0.3.3/en_dual_none_contextual-0.3.3-py3-none-any.whl!
python -m spacy download en_core_web_sm`
```


### foodIE.py
usage: foodIE.py [-h] [-t] [-d DOC]

options:
  -h, --help         show this help message and exit
  -t, --tags         Prints the USAS tags for each token in the input text
  -d DOC, --doc DOC  Document/Text to be processed

Example:
```
>>> python3 foodIE.py -t -d "Heat the white beef soup in the pan until it boils."

DOCUMENT:
Heat the white beef soup in the pan until it boils.
Text    Lemma   POS     USAS Tags
Heat    heat    VERB    ['O4.6+']
the     the     DET     ['Z5']
white   white   ADJ     ['O4.3', 'G2.2+']
beef    beef    NOUN    ['F1']
soup    soup    NOUN    ['F1']
in      in      ADP     ['Z5']
the     the     DET     ['Z5']
pan     pan     NOUN    ['O2']
until   until   ADP     ['Z5']
it      it      PRON    ['Z8']
boils   boil    VERB    ['O4.6+', 'E3-']
.       .       PUNCT   ['PUNCT']


EXTRACTED FOOD ENTITIES:
['white beef soup', 'soup']
```