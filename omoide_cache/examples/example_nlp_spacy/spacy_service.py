import time
import spacy
from spacy.tokens import Doc, Token
nlp = spacy.load('en_core_web_lg')

from omoide_cache.cache_decorator import omoide_cache

class SpacyService:
    # Build spacy tokens from string
    @omoide_cache()
    def tokenize(self, text: str) -> Doc:
        t1 = time.time()
        doc = nlp(text)
        t2 = time.time()
        print('SpacyService.tokenize(): Took ' + str(round(t2 - t1, 3)) + ' seconds')
        return doc

    # Find semantic similarity between two strings
    @omoide_cache()
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        t1 = time.time()
        tokens1 = self.tokenize(text1)
        if len(tokens1) == 0:
            return 0.0
        tokens2 = self.tokenize(text2)
        if len(tokens2) == 0:
            return 0.0
        score = tokens1.similarity(tokens2)
        t2 = time.time()
        print('SpacyService.calculate_semantic_similarity(): Took ' + str(round(t2 - t1, 3)) + ' seconds')
        return score
