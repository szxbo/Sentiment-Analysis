"""
    NAME
        sentiment-analysis.py
        
    This script performs sentiment analysis on text data. It uses a combination of
    dictionaries and rules to determine the sentiment score of a given text.
    
"""

import spacy
from spacy import displacy
from spacy.matcher import Matcher
import os


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

nlp = spacy.load('pt_core_news_lg')
# Initialize the Matcher
matcher = Matcher(nlp.vocab)

# Carregar os datasets
print("A carregar datasets...")
booster_words = load_data('data/BoosterWordList.txt')
emoticons = load_data('data/EmoticonLookupTable.txt')
expressions,emotions = load_data_sentilex('data/palavras.txt')
emotions2 = load_data('data/EmotionLookupTable.txt')
emotions.update(emotions2)
irony_terms = set(open('data/IronyTerms.txt', 'r', encoding='utf-8').read().splitlines())
negating_words = set(open('data/NegatingWordList.txt', 'r', encoding='utf-8').read().splitlines())
question_words = set(open('data/QuestionWords.txt', 'r', encoding='utf-8').read().splitlines())
slang_lookup_table = load_data('data/SlangLookupTable.txt',0)


# Add the multi-word expression pattern to the matcher
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
            
    rend = displacy.render(, style='dep')
    # escrever rend para um ficheiro html
    with open('test.html', 'w') as file:
        file.write(rend)
        file.write('<hr/>\n') 
            
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
    print(f"A carregar livro {book_path}...")
    book_score = 0
    with open(book_path, 'r', encoding='utf-8') as file:
        text = file.read()
        print("Livro carregado...")
        # dividir livro em capítulos (denotados por #)
        chapters = text.split('#')
        print("Há", len(chapters[1:]), "capítulos.")
        
        # criar pasta para guardar os capítulos, se não existir
        if not os.path.exists('chapters'):
            os.makedirs('chapters')
        os.chdir('chapters')
        
        # analisar cada capítulo
        for i, chapter in enumerate(chapters[1:]):
            with open(f'chapter_{i}.txt', 'w') as chapter_file:
                # split por frases (\n) (primeira frase é o número do capítulo)
                sentences = chapter.split('\n')
                chapter_number = sentences.pop(0)                
                chapter_file.write(f"\nCapítulo {chapter_number}\n")
                chapter_score = 0
                # separar por frases (\n)
                # analisar cada frase
                for sentence in sentences:
                    if sentence:
                        avaliacao = analyze_sentiment_sentence(sentence)
                        chapter_file.write(f"\nFrase: {sentence}\n")
                        chapter_file.write(f"Num palavras: {avaliacao['num_palavras']}\n")
                        chapter_file.write(f"Pontuação de sentimento: {avaliacao['score']}\n")
                        chapter_score += avaliacao['score']
                        # imprimir evidencias
                        chapter_file.write("Evidências:\n")
                        for key in avaliacao['evidencias']:
                            chapter_file.write(f"\t{key}: {avaliacao['evidencias'][key]}\n")
                        chapter_file.write("\n")
                chapter_file.write(f"\nPontuação do capítulo: {chapter_score}\n")
                chapter_file.write("\n")
            print(f"Capítulo {chapter_number} analisado -> score: {chapter_score}")
            book_score += chapter_score
        
    return book_score

def user_input():
    while(text:=input("\nInsira frase: ")):
        # guardar valores de avaliação num dicionario com a frase, evidencias e score
        avaliacao = analyze_sentiment_sentence(text)
        print("Num palavras:", avaliacao['num_palavras'])
        print("Pontuação de sentimento:", avaliacao['score'])
        # imprimir evidencias
        print("Evidências:")
        for key in avaliacao['evidencias']:
            print("\t", key,":",avaliacao['evidencias'][key])
    
    
def frases_teste():
    frases = """
    O café muito quente queimou-me a minha língua, mas eu gosto.
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
            print("Num palavras:", avaliacao['num_palavras'])
            print("Pontuação de sentimento:", avaliacao['score'])
            # imprimir evidencias
            print("Evidências:")
            for key in avaliacao['evidencias']:
                print("\t", key,":",avaliacao['evidencias'][key])
            print("\n")
    
def main():
    #book_score = analyze_sentiment_book('HP.txt')
    #print(f"\nPontuação do livro: {book_score}")
    frases_teste()
    
    
if __name__ == '__main__':
    main()
    #user_input()

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
        
        
    Frases de teste:
    O café muito quente queimou-me a minha língua, mas eu gosto.
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