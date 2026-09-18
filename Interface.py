from tkinter import *
from tkinter import scrolledtext, filedialog
from tkinter import ttk
import spacy

nlp = spacy.load("en_core_web_sm")


def browse_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Text files", "*.txt")]
    )
    if file_path:
        with open(file_path, 'r') as file:
            file_content = file.read()
            text_area.delete('1.0', END)
            text_area.insert(END, file_content)


def perform_tokenization():
    content = text_area.get('1.0', END).strip()

    if content:
        doc = nlp(content)
        tokens_area.delete('1.0', END)
        tokens = [token.text for token in doc]
        tokens_area.insert(END, "\n".join(tokens))
    else:
        tokens_area.delete('1.0', END)
        tokens_area.insert(END, "No text available for tokenization.")


def perform_ner():
    content = text_area.get('1.0', END).strip()

    if content:
        doc = nlp(content)
        ner_area.delete('1.0', END)
        for ent in doc.ents:
            ner_area.insert(END, f"{ent.text} ({ent.label_})\n")

    else:
        ner_area.delete('1.0', END)
        ner_area.insert(END, "No text available for Named Entity Recognition.")


def extract_sentences_with_keywords():
    content = text_area.get('1.0', END).strip()
    targets = target_entry.get().strip().split(",")

    if content and targets:

        doc = nlp(content)
        lemmatized_targets = [nlp(target.strip().lower())[0].lemma_ for target in targets]
        extracted_area.delete('1.0', END)
        extracted_area.insert(END, "Extracted Sentences (Containing Target Keywords):\n\n")

        for sentence in doc.sents:
            lemmatized_sentence = [token.lemma_ for token in sentence]
            if any(target in lemmatized_sentence for target in lemmatized_targets):
                extracted_area.insert(END, f"{sentence.text.strip()}\n\n")

    else:
        extracted_area.delete('1.0', END)
        extracted_area.insert(END, "No content or targets provided for extraction.")


def score_sentences_by_dependency():
    content = scoring_entry.get('1.0', END).strip()



    if content:
        scoring_area.delete('1.0', END)
        scoring_area.insert(INSERT, "Sentence Scores (identifying threats based on dependence parsing):\n\n")

        sentences = [sent.text.strip() for sent in nlp(content).sents]

        for sentence in sentences:
            doc = nlp(sentence)
            score = 0
            for token in doc:
                if token.dep_ in ["nsubj", "pobj", "dobj", "pcomp"]:
                    score += 1
            scoring_area.insert(INSERT, f"Sentence: {sentence}\nScore: {score}\n\n")

    else:
            scoring_area.delete('1.0', END)
            scoring_area.insert(END, "No text available for scoring.")


root = Tk()
root.title("Analysis Tool")
root.geometry("1000x800")

root.configure(bg="#f4f4f4")

canvas = Canvas(root, bg="#f4f4f4")
scrollbar = Scrollbar(root, orient=VERTICAL, command=canvas.yview)
scrollable_frame = Frame(canvas, bg="#f4f4f4", padx=10, pady=10)


scrollable_frame.bind(
    "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side=LEFT, fill=BOTH, expand=True)
scrollbar.pack(side=RIGHT, fill=Y)

file_frame = Frame(scrollable_frame, bg="#d9edf7", bd=2, relief=SOLID, padx=10, pady=10)
file_frame.pack(fill=X, pady=10)
Label(file_frame, text="Load Text File", bg="#d9edf7", font=("Arial", 14, "bold")).pack(side=LEFT, padx=10)
Button(file_frame, text="Browse File", command=browse_file, font=("Arial", 12), bg="#0275d8", fg="white").pack(side=RIGHT, padx=10)


text_frame = LabelFrame(scrollable_frame, text="Text Content", bg="#f4f4f4", font=("Arial", 14, "bold"), padx=10, pady=10)
text_frame.pack(fill=BOTH, expand=True, pady=10)
text_area = scrolledtext.ScrolledText(text_frame, wrap=WORD, width=100, height=10, font=("Arial", 12))
text_area.pack(fill=BOTH, expand=True)

# Tokenization Section
token_frame = LabelFrame(scrollable_frame, text="Tokens", bg="#f4f4f4", font=("Arial", 14, "bold"), padx=10, pady=10)
token_frame.pack(fill=BOTH, expand=True, pady=10)
Button(token_frame, text="Perform Tokenization", command=perform_tokenization, font=("Arial", 12), bg="green", fg="white").pack(side=TOP, pady=5)
tokens_area = scrolledtext.ScrolledText(token_frame, wrap=WORD, width=100, height=10, font=("Arial", 12))
tokens_area.pack(fill=BOTH, expand=True)

# NER Section
ner_frame = LabelFrame(scrollable_frame, text="Named Entities", bg="#f4f4f4", font=("Arial", 14, "bold"), padx=10, pady=10)
ner_frame.pack(fill=BOTH, expand=True, pady=10)
Button(ner_frame, text="Perform Named Entity Recognition", command=perform_ner, font=("Arial", 12), bg="blue", fg="white").pack(side=TOP, pady=5)
ner_area = scrolledtext.ScrolledText(ner_frame, wrap=WORD, width=100, height=10, font=("Arial", 12))
ner_area.pack(fill=BOTH, expand=True)

# Sentence Extraction Section
sentence_frame = LabelFrame(scrollable_frame, text="Extract Sentences by Keywords", bg="#f4f4f4", font=("Arial", 14, "bold"), padx=10, pady=10)
sentence_frame.pack(fill=BOTH, expand=True, pady=10)
Label(sentence_frame, text="Enter Keywords (comma-separated):", bg="#f4f4f4", font=("Arial", 12)).pack(side=TOP, pady=5)
target_entry = Entry(sentence_frame, font=("Arial", 12), width=50)
target_entry.pack(side=TOP, pady=5)
Button(sentence_frame, text="Extract Sentences", command=extract_sentences_with_keywords, font=("Arial", 12), bg="yellow", fg="black").pack(side=TOP, pady=5)
extracted_area = scrolledtext.ScrolledText(sentence_frame, wrap=WORD, width=90, height=10, font=("Arial", 12))
extracted_area.pack(fill=BOTH, expand=True)

# Sentence Scoring Section
scoring_label = Label(scrollable_frame, text="Enter sentences for dependency scoring:")
scoring_label.pack(anchor=W, pady=5)

scoring_entry = Text(scrollable_frame, width=60, height=5)
scoring_entry.pack(pady=5)

score_button = Button(scrollable_frame, text="Score Sentences by Dependency", command=score_sentences_by_dependency)
score_button.pack(pady=5, padx=10)

scoring_area_label = Label(scrollable_frame, text="Scores:")
scoring_area_label.pack(anchor=W, pady=5)

scoring_area = Text(scrollable_frame, width=60, height=10)
scoring_area.pack(pady=5)



root.mainloop()