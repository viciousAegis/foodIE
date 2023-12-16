import numpy as np
import pandas as pd
import re
from unidecode import unidecode
import json
import spacy
import argparse

def clean_text(post):
    cleaned_post = re.sub(r'#\w+\s*', '', post)  # Remove words starting with #
    cleaned_post = re.sub(r'["“”]', '', cleaned_post)  # Remove double quotation marks
    cleaned_post = re.sub(r"(?<!\w)'|'(?!\w)", '', cleaned_post)  # Remove single quotation marks not part of words
    cleaned_post = re.sub(r'\s+', ' ', cleaned_post)
    
    transliterated_post = unidecode(cleaned_post)  # Transliterate to ASCII
    
    return transliterated_post

def get_docs(posts):
    docs = []
    for post in posts:
        cleaned_post = clean_text(post)
        doc = nlp(cleaned_post)
        docs.append(doc)
    return docs

# temporary
food_substitution_posts = [
    "Heat the Colby-jack white beef soup in the pan until it boils.",
    "Just tried using applesauce instead of 'oil' in my baking recipe and it turned out surprisingly moist! #HealthyBaking #FoodSubstitutions",
    "Swapped cauliflower for rice in my stir-fry and it's a game-changer! Low-carb and delicious. #FoodHacks #CauliflowerRice",
    'Replacing dairy with almond milk in my "morning" smoothie -    loving the nutty flavor! #DairyFree #HealthyChoices',
    '''Who knew mashed avocado coÜld replace butter   on toast? 
    Creamy goodness with a healthier twist. #AvocadoLove #HealthyEating''',
    "Used Greek yogurt instead of mayo in my 'potato' salad - lighter and tangier! #HealthySwaps #YogurtLove",
    "Trying out zucchini noodles instead of pasta for a low-carb dinner. Surprisingly satisfying! #Zoodles #HealthyEating",
    "Substituted maple syrup for sugar in my baking - adds a lovely depth of flavor! #NaturalSweeteners #BakingTips",
    "Made a veggie burger with black beans instead of meat - so hearty and packed with protein! #VegetarianLife #PlantBased",
    "Using quinoa instead of rice in my burrito bowl - a nuttier taste and loaded with nutrients! #QuinoaLove #HealthyChoices",
    "Discovering the wonders of using mashed bananas as an egg substitute in baking. Works like a charm! #EggSubstitutes #BakingTips"
]

class Rule1:
    # if true, tag as food object
    
    def __init__(self):
        self.condition1_tags = {
            'food_tags': ['F1', 'F2', 'F3', 'F4'],
            'living_tags': ['L2', 'L3'],
            'substance_tags': ['O1.1','O1.2']
        }
        self.condition2_tags = {
            'body_part_tags': ['B1'],
            'linear_order_tags': ['N4'],
            'location_and_direction_tags': ['M6'],
            'texture_tags': ['O4.5']
        }
        self.condition3_tags = {
            'general_object_tags': ['O2'],
            'quantities_tags': ['N5'],
            'clothing_tags': ['B5', 'AH.02'],
            'equipment_for_food_preparation_tags': ['AG.01.t.08'],
            'container_for_food_place_for_storing_food_tags': ['AG.01.u'],
        }
    
    def set_doc(self, doc):
        self.doc = doc
    
    def print_doc(self):
        print(f'Text\tLemma\tPOS\tUSAS Tags')
        for token in self.doc:
            print(f'{token.text}\t{token.lemma_}\t{token.pos_}\t{token._.pymusas_tags}')
    
    def condition1(self, token):
        # check semantic tag
        semantic_tags = token._.pymusas_tags
        
        # check condition 1 for all semantic tags
        for semantic_tag in semantic_tags:
            if semantic_tag in self.condition1_tags['food_tags'] or semantic_tag in self.condition1_tags['living_tags'] or semantic_tag in self.condition1_tags['substance_tags']:
                return True
        
        return False
        
    def condition2(self, token):
        # check semantic tag
        semantic_tags = token._.pymusas_tags
        
        # check condition 2 for all semantic tags
        if self.condition2_tags['body_part_tags'][0] in semantic_tags and self.condition2_tags['linear_order_tags'][0] not in semantic_tags and self.condition2_tags['location_and_direction_tags'][0] not in semantic_tags and self.condition2_tags['texture_tags'][0] not in semantic_tags:
            return True

        return False
    
    def condition3(self, token):
        semantic_tags = token._.pymusas_tags
        
        # check condition 3 for all semantic tags
        flag_1 = self.condition3_tags['general_object_tags'][0] not in semantic_tags
        flag_2 = self.condition3_tags['quantities_tags'][0] not in semantic_tags
        flag_3 = self.condition3_tags['clothing_tags'][0] not in semantic_tags and self.condition3_tags['clothing_tags'][1] not in semantic_tags
        flag_4 = self.condition3_tags['equipment_for_food_preparation_tags'][0] not in semantic_tags
        flag_5 = self.condition3_tags['container_for_food_place_for_storing_food_tags'][0] not in semantic_tags
        
        if flag_1 and flag_2 and flag_3 and flag_4 and flag_5:
            return True

        return False

    def apply_rule(self):
        # check if all conditions are satisfied
        for token in self.doc:
            if (self.condition1(token) or self.condition2(token)) and self.condition3(token):
                token._.food_tag = True
            else:
                token._.food_tag = False

class Rule2:
    # if true, tag as general object
    
    def __init__(self):
        self.general_object_tag = 'O2'
        self.clothing_tag = 'B5'
        self.body_part_tag = 'B1'
        self.living_tags = ['L2', 'L3']
    
    def set_doc(self, doc):
        self.doc = doc
    
    def condition1(self, token):
        semantic_tags = token._.pymusas_tags
        
        flag1 = self.general_object_tag in semantic_tags
        flag2 = self.clothing_tag in semantic_tags
        
        if flag1 or flag2:
            return True
        return False
    
    def condition2(self, token):
        semantic_tags = token._.pymusas_tags
        
        flag1 = self.body_part_tag not in semantic_tags
        flag2 = self.living_tags[0] not in semantic_tags
        flag3 = self.living_tags[1] not in semantic_tags
        
        if flag1 and flag2 and flag3:
            return True
        return False
    
    def condition3(self,token):
        return not token._.food_tag
    
    def apply_rule(self):
        for token in self.doc:
            if self.condition1(token) and self.condition2(token) and self.condition3(token):
                token._.general_object_tag = True
            else:
                token._.general_object_tag = False

class Rule3:
    # color tag
    def __init__(self):
        self.color_tag = 'O4.3'
    
    def set_doc(self, doc):
        self.doc = doc
    
    def apply_rule(self):
        for token in self.doc:
            if self.color_tag in token._.pymusas_tags:
                token._.color_tag = True
            else:
                token._.color_tag = False

class Rule4:
    # constructed for defining what is explicitly disallowed to be the main token in a food entity
    
    def __init__(self):
        self.equipment_for_food_preparation_tag = 'AG.01.t.08'
        self.container_for_food_place_for_storing_food_tag = 'AG.01.u'
        self.clothing_tag = 'AH.02'
        self.temperature_tag = 'O4.6'
        self.measure_tag = 'N3'
    
    def set_doc(self, doc):
        self.doc = doc
    
    def apply_rule(self):
        for token in self.doc:
            flag1 = self.equipment_for_food_preparation_tag in token._.pymusas_tags
            flag2 = self.container_for_food_place_for_storing_food_tag in token._.pymusas_tags
            flag3 = self.clothing_tag in token._.pymusas_tags
            flag4 = self.temperature_tag in token._.pymusas_tags
            flag5 = self.measure_tag in token._.pymusas_tags
            
            if flag1 and flag2 and flag3 and flag4 and flag5:
                token._.not_allowed_tag = True
            else:
                token._.not_allowed_tag = False

class FoodIE:
    def __init__(self):
        self.rule1 = Rule1()
        self.rule2 = Rule2()
        self.rule3 = Rule3()
        self.rule4 = Rule4()
        # nouns, adjectives, proper nouns, genetive, and unknown tags are allowed to be on the left of a food entity
        self.valid_chain_POS = ['NOUN', 'PROPN', 'ADJ']
    
    def set_doc(self, doc):
        self.doc = doc
        for token in self.doc:
            token._.used = False
    
    def print_doc(self):
        print(f'Text\tLemma\tPOS\tUSAS Tags')
        for token in self.doc:
            print(f'{token.text}\t{token.lemma_}\t{token.pos_}\t{token._.pymusas_tags}')
    
    def apply_rules(self):
        self.rule1.set_doc(self.doc)
        self.rule1.apply_rule()
        
        self.rule2.set_doc(self.doc)
        self.rule2.apply_rule()
        
        self.rule3.set_doc(self.doc)
        self.rule3.apply_rule()
        
        self.rule4.set_doc(self.doc)
        self.rule4.apply_rule()
    
    def get_food_tokens(self):
        food_tokens = []
        for token in self.doc:
            if token._.food_tag:
                food_tokens.append(token)
        print(food_tokens)
    
    def chain_left(self, token):
        index = token.i
        # start from left of token and check if chain is valid
        food_chunk = []
        for i in range(index-1, -1, -1):
            if self.doc[i].pos_ in self.valid_chain_POS and not self.doc[i]._.used:
                food_chunk.append(self.doc[i])
                self.doc[i]._.used = True
            else:
                break
        
        # reverse the list to get the correct order
        food_chunk.reverse()
        return food_chunk
    
    def chain_right(self, token):
        index = token.i
        # start from right of token and check if chain is valid
        food_chunk = []
        for i in range(index+1, len(self.doc)):
            if self.doc[i].pos_ in self.valid_chain_POS and not self.doc[i]._.used:
                food_chunk.append(self.doc[i])
                self.doc[i]._.used = True
            elif (self.doc[i]._.general_object_tag or self.doc[i]._.color_tag) and not self.doc[i]._.used:
                food_chunk.append(self.doc[i])
                self.doc[i]._.used = True
            else:
                break
        
        return food_chunk
    
    def get_food_chunk(self, food_token):
        if food_token._.used:
            return []
        left_chunk = self.chain_left(food_token)
        right_chunk = self.chain_right(food_token)
        food_chunk = left_chunk + [food_token] + right_chunk
        return food_chunk
    
    def check_food_chunk(self, food_chunk):
        # check if food chunk is valid
        if len(food_chunk) == 0:
            return False
        # check if last token is a noun and a general object
        if food_chunk[-1].pos_ == 'NOUN' and food_chunk[-1]._.general_object_tag:
            return False
        
        # check if last token is disallowed
        if food_chunk[-1]._.not_allowed_tag:
            return False
        
        return True

    def get_food_entities(self):
        
        self.apply_rules()
        
        food_entities = []
        for token in self.doc:
            if token._.food_tag:
                food_chunk = self.get_food_chunk(token)
                if self.check_food_chunk(food_chunk):
                    food_entities.append(" ".join([token.text for token in food_chunk]))
                else:
                    food_entities.append(token.text)
        return food_entities

if __name__ == '__main__':
    
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-t', '--tags', help='Prints the USAS tags for each token in the input text', action='store_true', dest='print_tags')
    argparser.add_argument('-d', '--doc', help='Document/Text to be processed', action='store', dest='doc')
    
    args = argparser.parse_args()
    
    nlp = spacy.load('en_core_web_sm', exclude=['parser', 'ner'])

    # define custom extension for spaCy tokens
    spacy.tokens.Token.set_extension("food_tag", default=False, force=True)
    spacy.tokens.Token.set_extension("general_object_tag", default=False, force=True)
    spacy.tokens.Token.set_extension("color_tag", default=False, force=True)
    spacy.tokens.Token.set_extension("not_allowed_tag", default=False, force=True)
    spacy.tokens.Token.set_extension("used", default=False, force=True)

    # Load the English PyMUSAS rule-based tagger in a separate spaCy pipeline
    english_tagger_pipeline = spacy.load('en_dual_none_contextual')
    # Adds the English PyMUSAS rule-based tagger to the main spaCy pipeline
    nlp.add_pipe('pymusas_rule_based_tagger', source=english_tagger_pipeline)
    
    foodIE = FoodIE()
    
    if args.doc:
        docs = get_docs([args.doc])
    else:
        docs = get_docs(food_substitution_posts)
    
    for doc in docs:
        foodIE.set_doc(doc)
        print("DOCUMENT:")
        print(doc)
        
        if args.print_tags:
            foodIE.print_doc()
            print('\n')
        
        food_entities = foodIE.get_food_entities()
        print("EXTRACTED FOOD ENTITIES:")
        print(food_entities)
        print('\n')