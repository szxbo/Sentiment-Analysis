"""
    NAME
        sentiment_analysis
    
    DESCRIPTION
        This program analyzes the sentiment of a given text file or user input.
        It uses the spaCy library to process the text and the Matcher class to match multiword expressions.
        The program uses several datasets to analyze the sentiment of the text, such as BoosterWordList, EmoticonLookupTable,
        EmotionLookupTable, IronyTerms, NegatingWordList, QuestionWords, SlangLookupTable and Sentilex.
        The program can analyze the sentiment of a book, splitting it into chapters and analyzing each chapter.
        The program can also analyze the sentiment of test sentences.
    
    OPTIONS
        [no options]    :   User input mode.
        -f <file_path>  :   Path to the book file to be analyzed.
        -t              :   Test mode.
    
    EXAMPLES
        sentiment-analysis
        sentiment-analysis -f HP.txt
        sentiment-analysis -t
        
    AUTHOR
        Francisca Barros, Rafael Correia, Robert Szabo
        (pg53816@uminho.pt, pg54162@uminho.pt, pg54194@uminho.pt)
    
    VERSION
        0.2.1
        
    DEPENDENCIES
        spacy
        matplotlib
        jjcli    
"""

import spacy
from spacy.matcher import Matcher
from jjcli import *
import matplotlib.pyplot as plt
import os
import subprocess

def init():
    # Load the language model   
    global nlp
    try:
        nlp = spacy.load('pt_core_news_lg')
    except OSError:
        print("Model not found. In order to work, the model 'pt_core_news_lg' (568.2 MB) must be downloaded.")
        print("Do you want to download it now? (y/n)")
        if input().lower() == 'y':
            subprocess.run(['python', '-m', 'spacy', 'download', 'pt_core_news_lg'])
            nlp = spacy.load('pt_core_news_lg')
        else:
            print("Exiting program.")
            exit(1)
    # Initialize the Matcher
    global matcher
    matcher = Matcher(nlp.vocab)
    # Carregar os datasets
    print("Loading datasets...")
    global booster_words
    booster_words = load_data('data/BoosterWordList.txt')
    global emoticons
    emoticons = load_data('data/EmoticonLookupTable.txt')
    global expressions, emotions
    expressions, emotions = load_data_sentilex('data/palavras.txt')
    global emotions2
    emotions2 = load_data('data/EmotionLookupTable.txt')
    emotions.update(emotions2)
    global irony_terms
    irony_terms = set(open('data/IronyTerms.txt', 'r', encoding='utf-8').read().splitlines())
    global negating_words
    negating_words = set(open('data/NegatingWordList.txt', 'r', encoding='utf-8').read().splitlines())
    global question_words
    question_words = set(open('data/QuestionWords.txt', 'r', encoding='utf-8').read().splitlines())
    global slang_lookup_table
    slang_lookup_table = load_data('data/SlangLookupTable.txt',0)

# Carregar os dados dos arquivos
def load_data(file_path,flag=1):
    data = {}
    with open(file_path, errors='ignore') as file:
        for line in file.readlines():
            word, value = line.strip().split('\t')
            if flag: data[word] = -1 if int(value)<0 else (0 if int(value)==0 else 1)
            else: data[word] = value
    return data

#avinhado.PoS=Adj;TG=HUM:N0;POL:N0=-1;ANOT=MAN
#bajular.PoS=V;TG=HUM:N0:N1;POL:N0=-1;POL:N1=0;ANOT=MAN
def load_data_sentilex(file_path,flag=1):
    data = {}
    expressions = set()
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            
            fields = line.strip().split(';')
            
            word,pos = fields[0].split('=')
            word = word.split(".")[0]
            
            polarity = int(fields[2].split('=')[1])
            data[word] = polarity #dps tratar o pos
            if pos=="IDIOM":
                expressions.add(word)
                pattern = []
                for pal in word.split(" "):
                    pattern.append({"LOWER":pal})    
                matcher.add(word, [pattern])
    return expressions,data

def analyze_sentiment_sentence(text):

    text = text.lower()
    doc = nlp(text)
    #transformar tudo nos seus lemmas
    texto_com_lemmas = " ".join([token.lemma_ if token.pos_ == "VERB" else token.text for token in doc])
    doc = nlp(texto_com_lemmas)
    
    
    matches = matcher(doc)
    
    #print(texto_com_lemmas,matches)
    # Juntar multiwords
    with doc.retokenize() as retokenizer:
        for _, start, end in matches:
            span = doc[start:end]
            retokenizer.merge(span)
            
            
    # remover pontuação
    doc = [token for token in doc if not token.is_punct]

    avaliacao = {}
    evidencias = {}
    evidencias['positivas'] = []
    evidencias['negativas'] = []
    evidencias['neutras'] = []
    evidencias['negadores'] = []
    evidencias['boosters'] = []
    evidencias['ironia'] = []
    evidencias['emotions'] = []
    
    num_palavras = doc.__len__()
    sentiment_score = 0
    boost = 1
    
    for token in doc:
        if len(text.split(" ")) > 1:
            lemma = token.text
        else:
            lemma = token.lemma_
        
        token_score = 0
        if lemma in booster_words:
            token_score = booster_words[lemma]
            evidencias['boosters'].append((lemma,token_score))
            boost += token_score
            token_score = 0
        elif lemma in emoticons:
            token_score = emoticons[lemma]
            evidencias['emotions'].append((lemma,token_score))
        elif lemma in emotions:
            token_score = emotions[lemma]
            evidencias['emotions'].append((lemma,token_score))
        
        sentiment_score += token_score
            
        if token_score > 0:
            evidencias['positivas'].append((lemma,token_score))
        elif token_score < 0:
            evidencias['negativas'].append((lemma,token_score))
        else:
            evidencias['neutras'].append(lemma)

    has_irony = any(term in text for term in irony_terms)
    evidencias['ironia'] += [term for term in irony_terms if term in text]
    
    has_negation = any(term in text for term in negating_words)
    evidencias['negadores'] += [term for term in negating_words if term in text]
    
    is_question = any(term in text for term in question_words)
    
    sentiment_score*=boost

    if has_irony:
        sentiment_score *= -1
    if has_negation:
        sentiment_score *= -1
    if is_question:
        sentiment_score *= 0.5
        
    avaliacao = {
        'texto': text,
        'evidencias': evidencias,
        'score': sentiment_score,
        'num_palavras': num_palavras
    }
    
    return avaliacao

def analyze_sentiment_book(book_path):
    print(f"Loading book {book_path}...")
    all_scores = []
    with open(book_path, 'r', encoding='utf-8') as file:
        text = file.read()
        print("Book loaded successfully!")
        # dividir livro em capítulos (denotados por #)
        chapters = text.split('#')
        print("There are ", len(chapters[1:]), "chapters.")
        
        # criar pasta para guardar os capítulos, se não existir
        if not os.path.exists('chapters'):
            print("Creating chapters folder...")
            os.makedirs('chapters')
        os.chdir('chapters')
        
        # analisar cada capítulo
        for i, chapter in enumerate(chapters[1:]):
            with open(f'chapter_{i+1}.txt', 'w') as chapter_file:
                # split por frases (\n) (primeira frase é o número do capítulo)
                sentences = chapter.split('\n')
                chapter_number = sentences.pop(0)                
                chapter_file.write(f"\nChapter {chapter_number}\n")
                chapter_score = 0
                # separar por frases (\n)
                # analisar cada frase
                for sentence in sentences:
                    if sentence:
                        avaliacao = analyze_sentiment_sentence(sentence)
                        chapter_file.write(f"\nPhrase: {sentence}\n")
                        chapter_file.write(f"Word count: {avaliacao['num_palavras']}\n")
                        chapter_file.write(f"Sentiment Score: {avaliacao['score']}\n")
                        chapter_score += avaliacao['score']
                        # imprimir evidencias
                        chapter_file.write("Evidences:\n")
                        for key in avaliacao['evidencias']:
                            chapter_file.write(f"\t{key}: {avaliacao['evidencias'][key]}\n")
                        chapter_file.write("\n")
                chapter_file.write(f"\nChapter Score: {chapter_score}\n")
                chapter_file.write("\n")
            print(f"Chapter {chapter_number} analysed -> sentiment score: {chapter_score}")
            all_scores.append(chapter_score)
        os.chdir('..')
    
    # all_scores = [-26, -4, -46.5, -30, 26.5, -6, -25, -26, -38, -32, -25, -16.5, -5.5, -15.5, -40, -45, -47.5]µ
    hist_sentiment(all_scores)
    book_score = sum(all_scores)
    return book_score

def hist_sentiment(scores):
    # histograma com a pontuação de cada capítulo usando o matplotlib
    # x -> pontuação (pode ser positiva ou negativa)
    # y -> número de capítulos (17 capítulos)
    capitulos = [i for i in range(17)]
    # quero valores do score em cima das barras se forem positivos, em baixo se forem negativos
    for i, score in enumerate(scores):
        if score > 0:
            plt.text(i, score, score, ha='center', va='bottom')
        else:
            plt.text(i, score, score, ha='center', va='top')
    plt.bar(capitulos, scores)
    plt.title('Score per chapter')
    plt.xlabel('Score')
    plt.ylabel('Number of chapters')
    plt.show()
    
def user_input():
    try:
        while(text:=input("\nInsira frase: ")):
            # guardar valores de avaliação num dicionario com a frase, evidencias e score
            avaliacao = analyze_sentiment_sentence(text)
            print("Word count:", avaliacao['num_palavras'])
            print("Sentiment Score:", avaliacao['score'])
            # imprimir evidencias
            print("Evidences:")
            for key in avaliacao['evidencias']:
                print("\t", key,":",avaliacao['evidencias'][key]) 
    except KeyboardInterrupt:
        print("\nExiting... See you next time!")
    
def frases_teste():
    frases = """
O café muito quente queimou-me a minha língua, mas eu gosto da sensação.
Música alta sabe-me bem, mas os vizinhos queixam-se.
Estes gatos só deixam pelos por todo o lado.
Tenho um teclado novo, mas não funciona.
Que bom é acordar pela manhã e não ter preocupações.
Amanhã vou sair com os meus amigos, nunca me diverti tanto.
Amor e ódio são sentimentos opostos.
Quando é que vais embora?
Não quero que fiques, mas vais-me fazer falta.
O stress causado pelo trabalho é insuportável.
"""
    
    # separar frases por \n
    frases = frases.split('\n')
    for frase in frases:
        if frase:
            print(frase)
            avaliacao = analyze_sentiment_sentence(frase)
            print("Word count:", avaliacao['num_palavras'])
            print("Sentiment Score:", avaliacao['score'])
            # imprimir evidencias
            print("Evidences:")
            for key in avaliacao['evidencias']:
                print("\t", key,":",avaliacao['evidencias'][key])
            print("\n")
    
def main():
    cl = clfilter("f:it", doc=__doc__)     ## option values in cl.opt dictionary
    
    if '-f' in cl.opt:
        init()
        file_path = cl.opt['-f']
        if file_path.endswith('.txt'):
            if os.path.exists(file_path):
                # analisar sentimento do livro
                book_score = analyze_sentiment_book(file_path)
                print(f"\nBook Score: {book_score}")
            else:
                print("File not found.")
        else:
            print("File not supported.")
        
    elif '-t' in cl.opt:
        init()
        frases_teste()
        
    else:
        # default: user input mode
        init()
        user_input()
    
if __name__ == '__main__':
    main()

# Ideias:
    """
    Se um verbo for conjugado no passado e a frase for negativa,
    serve como um booster para a negatividade, e vice-versa.
    Se a frase for negativa e tiver um verbo no futuro, serve como um unbooster para a negatividade.
        Ex: eu matei alguém -> negativo
        Ex: eu vou matar alguém -> menos negativo
        
    Se a frase for positiva e tiver um verbo no passado, serve como um booster para a positividade.
        Ex: eu ganhei ontem -> mais positivo
        Ex: eu vou ganhar -> menos positivo
    """
