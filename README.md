# Sentiment Analysis

This project is focused on sentiment analysis, which is the task of determining the sentiment or emotional tone behind a piece of text. The code provided includes functions for loading data, analyzing sentiment at the sentence and book level, and providing user input for sentiment analysis.

## Getting Started

To get started with this project, follow the steps below:

1. Clone the repository to your local machine.
2. Install the required dependencies by running `pip install -r requirements.txt`.
3. Run the `main()` function to perform sentiment analysis on test sentences or a book.

## Code Overview

The code is organized into the following sections:

1. Data Loading: Functions for loading data from various files, such as booster words, emoticons, sentiment lexicons, irony terms, negating words, question words, and slang lookup table.
2. Sentence Sentiment Analysis: The `analyze_sentiment_sentence()` function analyzes the sentiment of a given sentence by tokenizing it, lemmatizing the tokens, and calculating a sentiment score based on the presence of booster words, emoticons, and sentiment lexicons. It also considers factors like irony, negation, and question words to adjust the sentiment score.
3. Book Sentiment Analysis: The `analyze_sentiment_book()` function analyzes the sentiment of a given book by splitting it into chapters, analyzing each chapter using the `analyze_sentiment_sentence()` function, and calculating a cumulative sentiment score for the entire book.
4. User Input: The `user_input()` function allows the user to input a sentence and get the sentiment analysis results.
5. Test Sentences: The `frases_teste()` function provides a set of test sentences for sentiment analysis.

## Usage

To use this project, you can either run the `main()` function to perform sentiment analysis on test sentences or a book, or use the `user_input()` function to input your own sentences for sentiment analysis.

## Contributing

Contributions to this project are welcome. If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
