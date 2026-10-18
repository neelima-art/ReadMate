
import re

def extract_features(text):
    sentences = [
        s.strip()
        for s in re.split(r"[.!?]+", text)
        if s.strip()
    ]

    words = re.findall(r"\b[A-Za-z]+\b", text.lower())

    if not words or not sentences:
        raise ValueError("Not enough text to analyze")

    word_count = len(words)
    sentence_count = len(sentences)

    avg_sentence_length = word_count / sentence_count
    avg_word_length = sum(len(w) for w in words) / word_count

    long_word_ratio = (
        sum(len(w) >= 7 for w in words) / word_count
    )

    unique_word_ratio = len(set(words)) / word_count

    return {
        "avg_sentence_length": round(avg_sentence_length, 3),
        "avg_word_length": round(avg_word_length, 3),
        "long_word_ratio": round(long_word_ratio, 3),
        "unique_word_ratio": round(unique_word_ratio, 3)
    }


if __name__ == "__main__":
    sample = """
    Alice was beginning to get very tired of sitting
    by her sister on the bank. She had nothing to do.
    Suddenly a white rabbit ran past her.
    """

    print(extract_features(sample))

