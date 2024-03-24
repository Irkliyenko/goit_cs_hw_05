import string
import requests
import matplotlib.pyplot as plt

from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict


def get_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        return response.text
    except requests.RequestException as e:
        return None


# Function to remove punctuation
def remove_punctuation(text):
    return text.translate(str.maketrans("", "", string.punctuation))


def map_function(word):
    return word, 1


def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()


def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)


def visualize_top_words(top_words: dict, top_n=5):
    """Visualize top N words with their counts."""
    # Sort dictionary by values and get the top N entries
    sorted_dict = dict(
        sorted(top_words.items(), key=lambda item: item[1], reverse=True)[:top_n])

    plt.bar(range(len(sorted_dict)), list(sorted_dict.values()),
            tick_label=list(sorted_dict.keys()))
    plt.xlabel('Words')
    plt.ylabel('Count')
    plt.title('Top Words Visualization')
    plt.show()


# Execute MapReduce
def map_reduce(text, search_words=None):
    # Remove punctuation
    text = remove_punctuation(text)
    words = text.split()

    # If a list of words to search for is provided, only consider these words
    if search_words:
        words = [word for word in words if word in search_words]

    # Parallel Mapping
    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    # Step 2: Shuffle
    shuffled_values = shuffle_function(mapped_values)

    # Parallel Reduction
    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    return dict(reduced_values)


if __name__ == '__main__':
    # Input text for processing
    url = "https://gutenberg.net.au/ebooks01/0100021.txt"
    text = get_text(url)
    if text:
        # Perform MapReduce on the input text
        result = map_reduce(text)

        print("Word count result:", result)
    else:
        print("Error: Failed to retrieve input text.")

    visualize_top_words(result, 7)
