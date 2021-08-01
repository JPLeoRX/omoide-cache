import time
from omoide_cache.examples.example_nlp_spacy.spacy_service import SpacyService

service = SpacyService()

def timed_tokenize_difference(text: str):
    t1 = time.time()
    service.tokenize(text)
    t2 = time.time()
    service.tokenize(text)
    t3 = time.time()
    d1 = round(t2 - t1, 3)
    d2 = round(t3 - t2, 3)
    print('Real tokenization took ' + str(d1) + ' s, while cached one took ' + str(d2))


def timed_similarity_difference(text1: str, text2: str):
    t1 = time.time()
    service.calculate_semantic_similarity(text1, text2)
    t2 = time.time()
    service.calculate_semantic_similarity(text1, text2)
    t3 = time.time()
    d1 = round(t2 - t1, 3)
    d2 = round(t3 - t2, 3)
    print('Real similarity took ' + str(d1) + ' s, while cached one took ' + str(d2))


text1 = 'While some of spaCy’s features work independently, others require trained pipelines to be loaded, which enable spaCy to predict linguistic annotations – for example, whether a word is a verb or a noun. A trained pipeline can consist of multiple components that use a statistical model trained on labeled data. spaCy currently offers trained pipelines for a variety of languages, which can be installed as individual Python modules. Pipeline packages can differ in size, speed, memory usage, accuracy and the data they include. The package you choose always depends on your use case and the texts you’re working with. For a general-purpose use case, the small, default packages are always a good start. They typically include the following components:'
text2 = 'spaCy provides a variety of linguistic annotations to give you insights into a text’s grammatical structure. This includes the word types, like the parts of speech, and how the words are related to each other. For example, if you’re analyzing text, it makes a huge difference whether a noun is the subject of a sentence, or the object – or whether “google” is used as a verb, or refers to the website or company in a specific context.'
timed_tokenize_difference(text1)
timed_tokenize_difference(text2)


text3 = 'The B12 was lowered slightly on shorter, stiffer springs, with the new ride height going nicely with those trademark 20-inch Alpina multi-spokes. The other typical Alpina additions - a low-hanging front splitter and side decals - were also present. A total of 202 E38 5.7 B12s were made, and only 59 of these were in long-wheelbase spec like this one. The stretched body looks especially classy daubed in Alpina Blue Metallic with gold stripes. Inside there’s Anthracite Buffalo leather with neat Alpina Rhomboid patterned stripes and a decent helping of birch trim on the dash and door cards. The seat bottoms seem a little tired, but otherwise, it’s all looking pretty tidy in the cabin. The B12 currently resides in Ontario, having made its way over to Canada from Japan. In its 22 or so years on (both sides of) Planet Earth, it’s clocked 85,600 kilometres (53,200 miles). Interested? The guide price is $50,000 - $60,000.'
text4 = 'Few BMWs from the last few decades have aged as well as the E38 7-series. As the years roll by it merely gets cooler and meaner looking, particularly compared to its gaudy modern equivalent with those gigantic, spangly nostrils. Arguably the coolest E38 of all wasn’t made by BMW, however. That honour, we reckon, goes to the Alpina B12. Proving our point nicely is this 1998 example of the fettled E38, available via an RM Sotheby’s online auction that runs from 28 July to 4 August. To create this version of the B12, Alpina took the 750i and tossed a great deal of its 5.4-litre ‘M73’ V12 aside. It was given fresh cylinder heads with bigger valves and new camshafts, Mahle pistons and electrically-heated catalytic converters. After Alpina was done fiddling, the displacement had grown to 5.7-litres. This yielded outputs of around 380bhp and 413lb ft of torque, up from 322bhp and 361lb ft. Later versions received an even pokier 6.0-litre V12. The standard five-speed automatic gearbox was retained, but with some software tweaks. Cogs could be changed manually with Alpina’s ‘SwitchTronic’ steering wheel shifters, back when such a setup was still very rare. '
timed_similarity_difference(text3, text4)

exit(-1)