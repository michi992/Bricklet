# Requisite imports
import os.path
from os import path
from vector_store import VectorStore
import numpy as np
import locale
locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')  # Set locale to German for proper handling of umlauts and special characters

path = os.path.join("T:\Mitarbeiter\Dewald, Michael\Codes\API2.ps1")

vector_store = VectorStore()

sentences = [
    "Benutze Deo"
    "Ich habe gegessen"
    "Ich bin in die Schule geganngen"
    "Ich tanke mein Auto"
]

vocabulary = set()
for sentence in sentences:
    words = sentence.lower().split()
    vocabulary.update(words)
    
    word_to_index = {word: i for i, word in enumerate(vocabulary)}
    
sentence_vectors = {}
for sentence in sentences:
    tokens = sentence.lower().split()
    vector = np.zeros(len(vocabulary))
    for token in tokens:
        vector[word_to_index[token]] += 1
    sentence_vectors[sentence] = vector
    
for sentence, vector in sentence_vectors.items():
    vector_store.add_vectors(sentence, vector)
    
query_sentence = "Ich tanke mein Auto"
query_vector = np.zeros(len(vocabulary))
query_token = query_vector.lower().split()

for token in query_token:
    if token in word_to_index:
        query_vector[word_to_index[token]] += 1
        
similare_sentences = vector_store.similarity_search(query_vector, n=5)

print("Similar sentences to", query_sentence, "are:")
print("similare Sentences:")
for sentence, similarty in similare_sentences:
    print(f"{sentence}: {similarty:.4f}")