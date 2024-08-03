import os
import streamlit as st
import google.generativeai as genai
import mimetypes
import docx2txt
import importlib

# Import transformation scripts
transform_script_1 = importlib.import_module("transform_script_1")

def upload_to_gemini(file, mime_type=None):
    """Uploads the given file to Gemini."""
    genai_file = genai.upload_file(file, mime_type=mime_type)
    st.write(f"Uploaded file '{genai_file.display_name}' as: {genai_file.uri}")
    return genai_file

def process_text_file(file):
    if file.name.lower().endswith('.docx'):
        return docx2txt.process(file)
    else:  # For .txt, .md, and other text files
        return file.getvalue().decode('utf-8')

def correct_german_chars(text):
    return text.replace('ß', 'ss')

def save_response(text, index, suffix="", file_prefix="", output_folder="."):
    output_filename = os.path.join(output_folder, f"{file_prefix}_response_{index}{suffix}.txt")
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(correct_german_chars(text))
    return output_filename

def main():
    st.title("Gemini API Text Generator")

    # User input for Gemini API key
    api_key = st.text_input("Enter your Gemini API key:", type="password")
    if not api_key:
        st.warning("Please enter your Gemini API key to proceed.")
        return

    genai.configure(api_key=api_key)

    # Create the model
    generation_config = {
        "temperature": 0.5,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        system_instruction="""
placeholder
        """
    )

    # Pre-saved messages to send to the model
    messages = [
        """//steps SC
1. The user uploads an image file with content from a textbook.
2. You always answer in German per 'Sie-Form' or in the Language of the upload
3. You generate 5 questions for each processed image or text. 
4. extract {page_number} from the bottom of the image or text.
5. extract {subject} from the top left or right 5% of the image or text.
6. You develop materials based on the //instruction and //output
7. if there is a graphical representation you generate at least 3 questions about it, focusing on the testing the understanding of the graphical representation and its data.

//instruction
- read the text and identify informations
- refer to 'bloom_levels_closed' for types of question to formulate according to the content of the image or text
- refer to the 'templates_closed.txt' for formatting the questions in your output
- STRICTLY follow the formatting of 'templates_closed.txt'

//bloom_levels_closed 
# Bloom Level: 'Erinnern'
Question Type: For recall-based tasks
Design Approach:
Focus on recognition and recall of facts.
Use straightforward questions that require identification of correct information.
Example:
"How many members are in the Swiss Federal Council? "

# Bloom Level: 'Verstehen'
Question Type: Questions at this level assess comprehension and interpretation
Design Approach:
Emphasize explanation of ideas or concepts.
Questions should assess comprehension through interpretation or summary.
Example:
"Which of the following best describes the role of cantonal governments in Switzerland?"

# Bloom Level: 'Anwenden'
Question Type: Application-based questions evaluate practical knowledge.
Design Approach:
Questions should require the application of knowledge in new situations.
Include scenarios that necessitate the use of learned concepts in practical contexts.
Example:
"If a canton wants to introduce a new educational reform that differs from federal standards, which of the following steps is necessary? "

//output
- OUTPUT should only include the generated questions
- ALWAYS generate 10 questions
- READ the //rules to understand the rules for points and answers.
- STRICTLY follow the formatting of the 'templates_closed.txt'.
- IMPORTANT: the output is just the questions
- No additional explanation. ONLY the questions as plain text. never use ':' as a separator.

//rules
- rules SC ALWAYS 1 correct answer and 2 wrong: Typ\tSC\nKeywords\tSeite {page_number}\nCoverage\tLehrmittel Allgemeinbildung\nSubject\t/Allgemeinbildung/{subject}\nLevel\t{bloom_level}\nTitle\tgeneral_title_of_the_question\nQuestion\tgeneral_question_text_placeholder\nPoints\t1\n1\tcorrect_answer_placeholder_1\n-0.5\tincorrect_answer_placeholder_1\n-0.5\tincorrect_answer_placeholder_2\n-0.5\tincorrect_answer_placeholder_3

//templates_closed.txt
Typ	SC
Keywords	Seite {page_number}
Coverage	Lehrmittel Allgemeinbildung
Subject	/Allgemeinbildung/{subject}
Level	{bloom_level}
Title	Fussball: Gewinner
Question	Welche Mannschaft gewann 1982 die Fussball Weltmeisterschaft?
Points	1
1	Italien
-0.5	Brasilien
-0.5	Südafrika
-0.5	Spanien
""",        
        """//steps MC
1. The user uploads an image or text with content from a textbook.
2. You always answer in German per 'Sie-Form' or in the Language of the upload
3. You generate 5 questions for each processed image or text. 
4. extract {page_number} from the bottom of the image or text.
5. extract {subject} from the top left or right 5% of the image or text.
6. You develop materials based on the //instruction and //output
7. if there is a graphical representation you generate at least 3 questions about it, focusing on the testing the understanding of the graphical representation and its data.

//instruction
- read the text and identify informations
- refer to 'bloom_levels_closed' for types of question to formulate according to the content of the image or text
- refer to the 'templates_closed.txt' for formatting the questions in your output
- STRICTLY follow the formatting of 'templates_closed.txt'

//bloom_levels_closed 
# Bloom Level: 'Erinnern'
Question Type: For recall-based tasks
Design Approach:
Focus on recognition and recall of facts.
Use straightforward questions that require identification of correct information.
Example:
"How many members are in the Swiss Federal Council? "

# Bloom Level: 'Verstehen'
Question Type: Questions at this level assess comprehension and interpretation
Design Approach:
Emphasize explanation of ideas or concepts.
Questions should assess comprehension through interpretation or summary.
Example:
"Which of the following best describes the role of cantonal governments in Switzerland?"

# Bloom Level: 'Anwenden'
Question Type: Application-based questions evaluate practical knowledge.
Design Approach:
Questions should require the application of knowledge in new situations.
Include scenarios that necessitate the use of learned concepts in practical contexts.
Example:
"If a canton wants to introduce a new educational reform that differs from federal standards, which of the following steps is necessary? "

//output
- OUTPUT should only include the generated questions
- ALWAYS generate 10 questions
- READ the //rules to understand the rules for points and answers.
- STRICTLY follow the formatting of the 'templates_closed.txt'.
- IMPORTANT: the output is just the questions
- No additional explanation. ONLY the questions as plain text. never use ':' as a separator.

//rules
- rules MC ALWAYS 4 Answers ALWAYS 3 Points
    - 1 correct: Typ\tMC\nKeywords\tSeite {page_number}\nCoverage\tLehrmittel Allgemeinbildung\nSubject\t/Allgemeinbildung/{subject}\nLevel\t{bloom_level}\nTitle\tgeneral_title_of_the_question\nQuestion\tgeneral_question_text_placeholder\nMax answers\t4\nMin answers\t0\nPoints\t3\n-1\tincorrect_answer_placeholder_1\n-1\tincorrect_answer_placeholder_1\n3\tcorrect_answer_placeholder_1\n-1\tincorrect_answer_placeholder_1
    - 2 correct: Typ\tMC\nKeywords\tSeite {page_number}\nCoverage\tLehrmittel Allgemeinbildung\nSubject\t/Allgemeinbildung/{subject}\nLevel\t{bloom_level}\nTitle\tgeneral_title_of_the_question\nQuestion\tgeneral_question_text_placeholder\nMax answers\t4\nMin answers\t0\nPoints\t3\n-1\tincorrect_answer_placeholder_1\n-1\tincorrect_answer_placeholder_1\n1.5\tcorrect_answer_placeholder_1\n1.5\tcorrect_answer_placeholder_1
    - 3 correct: Typ\tMC\nKeywords\tSeite {page_number}\nCoverage\tLehrmittel Allgemeinbildung\nSubject\t/Allgemeinbildung/{subject}\nLevel\t{bloom_level}\nTitle\tgeneral_title_of_the_question\nQuestion\tgeneral_question_text_placeholder\nMax answers\t4\nMin answers\t0\nPoints\t3\n-1\tincorrect_answer_placeholder_1\n1\tcorrect_answer_placeholder_1\n1\tcorrect_answer_placeholder_1\n1\tcorrect_answer_placeholder_1
    - 4 correct: Typ\tMC\nKeywords\tSeite {page_number}\nCoverage\tLehrmittel Allgemeinbildung\nSubject\t/Allgemeinbildung/{subject}\nLevel\t{bloom_level}\nTitle\tgeneral_title_of_the_question\nQuestion\tgeneral_question_text_placeholder\nMax answers\t4\nMin answers\t0\nPoints\t3\n0.75\tcorrect_answer_placeholder_1\n0.75\tcorrect_answer_placeholder_1\n0.75\tcorrect_answer_placeholder_1\n0.75\tcorrect_answer_placeholder_1
      
//templates_closed.txt
Typ	MC
Keywords	Seite {page_number}
Coverage	Lehrmittel Allgemeinbildung
Subject	/Allgemeinbildung/{subject}
Level	{bloom_level}
Title	Fussball: Austragungsort
Question	In welchen Ländern wurde zwischen dem Jahr 2000 und 2015 eine Fussball Weltmeisterschaft ausgetragen?
Max answers	4
Min answers	0
Points	3
1	Deutschland
1	Brasilien
1	Südafrika
-1	Schweiz
Typ	MC
Keywords	Seite {page_number}
Coverage	Lehrmittel Allgemeinbildung
Subject	/Allgemeinbildung/{subject}
Level	{bloom_level}
Title	Fussball: WM-Titeln
Question	Welche Ländern haben mindestens eine WM gewonnen?
Max answers	4
Min answers	0
Points	3
1.5	Deutschland
1.5	Brasilien
-1	Südafrika
-1	Schweiz
Typ	MC
Keywords	Seite {page_number}
Coverage	Lehrmittel Allgemeinbildung
Subject	/Allgemeinbildung/{subject}
Level	{bloom_level}
Title	Fussball: WM-Titeln
Question	Welche Ländern haben mindestens drei WM gewonnen?
Max answers	4
Min answers	0
Points	3
0.75	Deutschland
0.75	Brasilien
0.75	Italien
0.75	Argentinien
Typ	MC
Keywords	Seite {page_number}
Coverage	Lehrmittel Allgemeinbildung
Subject	/Allgemeinbildung/{subject}
Level	{bloom_level}
Title	Fussball: Austragungsort
Question	Welches Land hat noch nie eine WM gewonnen?
Max answers	4
Min answers	0
Points	3
-1	Deutschland
-1	Brasilien
-1	Südafrika
3	Schweiz
        """,
        """//steps KPRIM
1. The user uploads an image or text with content from a textbook.
2. You always answer in German per 'Sie-Form' or in the Language of the upload
3. You generate 5 questions for each processed image or text. 
4. extract {page_number} from the bottom of the image or text.
5. extract {subject} from the top left or right 5% of the image or text.
6. You develop materials based on the //instruction and //output
7. if there is a graphical representation you generate at least 3 questions about it, focusing on the testing the understanding of the graphical representation and its data.

//instruction
- read the text and identify informations
- refer to 'bloom_levels_closed' for types of question to formulate according to the content of the image or text
- refer to the 'templates_closed.txt' for formatting the questions in your output
- STRICTLY follow the formatting of 'templates_closed.txt'

//bloom_levels_closed 
# Bloom Level: 'Erinnern'
Question Type: For recall-based tasks
Design Approach:
Focus on recognition and recall of facts.
Use straightforward questions that require identification of correct information.
Example:
"How many members are in the Swiss Federal Council? "

# Bloom Level: 'Verstehen'
Question Type: Questions at this level assess comprehension and interpretation
Design Approach:
Emphasize explanation of ideas or concepts.
Questions should assess comprehension through interpretation or summary.
Example:
"Which of the following best describes the role of cantonal governments in Switzerland?"

# Bloom Level: 'Anwenden'
Question Type: Application-based questions evaluate practical knowledge.
Design Approach:
Questions should require the application of knowledge in new situations.
Include scenarios that necessitate the use of learned concepts in practical contexts.
Example:
"If a canton wants to introduce a new educational reform that differs from federal standards, which of the following steps is necessary? "

//output
- OUTPUT should only include the generated questions
- ALWAYS generate 10 questions
- READ the //rules to understand the rules for points and answers.
- STRICTLY follow the formatting of the 'templates_closed.txt'.
- IMPORTANT: the output is just the questions
- No additional explanation. ONLY the questions as plain text. never use ':' as a separator.

//rules
- rules KPRIM ALWAYS 4 Answers, 0 to 4 correct: Typ\tKPRIM\nKeywords\tSeite {page_number}\nCoverage\tLehrmittel Allgemeinbildung\nSubject\t/Allgemeinbildung/{subject}\nLevel\t{bloom_level}\nTitle\tgeneral_title_of_the_question\nQuestion\tgeneral_question_text_placeholder\nPoints\t5\n+\tcorrect_answer_placeholder_1\n-\tincorrect_answer_placeholder_2\n-1\tincorrect_answer_placeholder_1\n{points_according_to_number_correct_answers}\tcorrect_answer_placeholder_1

//templates_closed.txt
Typ	KPRIM
Keywords	Seite {page_number}
Coverage	Lehrmittel Allgemeinbildung
Subject	/Allgemeinbildung/{subject}
Level	{bloom_level}
Title	Fussball: Weltmeister
Question	Die folgenden Länder haben die Fussball Weltmeistertitel bereits mehr als einmal gewonnen.
Points	5
+	Deutschland
-	Schweiz
-	Norwegen
+	Uruguay
Typ	KPRIM
Keywords	Seite {page_number}
Coverage	Lehrmittel Allgemeinbildung
Subject	/Allgemeinbildung/{subject}
Level	{bloom_level}
Title	Fussball: Weltmeister
Question	Die folgenden Länder haben die Fussball Weltmeistertitel noch nie gewonnen.
Points	5
+	Irland
+	Schweiz
+	Norwegen
-	Uruguay
        """,
        """//steps Truefalse
1. The user uploads an image or text with content from a textbook.
2. You always answer in German per 'Sie-Form' or in the Language of the upload
3. You generate 5 questions for each processed image or text. 
4. extract {page_number} from the bottom of the image or text.
5. extract {subject} from the top left or right 5% of the image or text.
6. You develop materials based on the //instruction and //output
7. if there is a graphical representation you generate at least 3 questions about it, focusing on the testing the understanding of the graphical representation and its data.

//instruction
- read the text and identify informations
- refer to 'bloom_levels_closed' for types of question to formulate according to the content of the image or text
- refer to the 'templates_closed.txt' for formatting the questions in your output
- STRICTLY follow the formatting of 'templates_closed.txt'

//bloom_levels_closed 
# Bloom Level: 'Erinnern'
Question Type: For recall-based tasks
Design Approach:
Focus on recognition and recall of facts.
Use straightforward questions that require identification of correct information.
Example:
"How many members are in the Swiss Federal Council? "

# Bloom Level: 'Verstehen'
Question Type: Questions at this level assess comprehension and interpretation
Design Approach:
Emphasize explanation of ideas or concepts.
Questions should assess comprehension through interpretation or summary.
Example:
"Which of the following best describes the role of cantonal governments in Switzerland?"

# Bloom Level: 'Anwenden'
Question Type: Application-based questions evaluate practical knowledge.
Design Approach:
Questions should require the application of knowledge in new situations.
Include scenarios that necessitate the use of learned concepts in practical contexts.
Example:
"If a canton wants to introduce a new educational reform that differs from federal standards, which of the following steps is necessary? "

//output
- OUTPUT should only include the generated questions
- ALWAYS generate 10 questions
- READ the //rules to understand the rules for points and answers.
- STRICTLY follow the formatting of the 'templates_closed.txt'.
- IMPORTANT: the output is just the questions
- No additional explanation. ONLY the questions as plain text. never use ':' as a separator.

//rules
- rules Truefalse ALWAYS 4 Answers, 1 to 4 correct: Typ\tTruefalse\nKeywords\tSeite {page_number}\nCoverage\tLehrmittel Allgemeinbildung\nSubject\t/Allgemeinbildung/{subject}\nLevel\t{bloom_level}\nTitle\tgeneral_title_of_the_question\nQuestion\tgeneral_question_text_placeholder\nPoints\t2\n\tUnanswered\tRight\tWrong\tcorrect_answer_placeholder_1\t0\t0.5\t-0.25\tcorrect_answer_placeholder_1\t0\t0.5\t-0.25\tincorrect_answer_placeholder_1\t0\t-0.25\t0.5t0.5\t-0.25\tincorrect_answer_placeholder_1\t0\t-0.25\t0.5
- rules Drag&drop: Typ\tDrag&drop\nKeywords\tSeite {page_number}\nCoverage\tLehrmittel Allgemeinbildung\nSubject\t/Allgemeinbildung/{subject}\nLevel\t{bloom_level}\nTitle\tgeneral_title_of_the_question\nQuestion\tgeneral_question_text_placeholder\nPoints\t{Sum_of_correct_answer}\nAlgerien\tKenia\tNamibia\nNairobi\t-0.5\t1\t-0.5\nWindhoek\t-0.5\t-0.5\t1\nAlgier\t1\t-0.5\t-0.5

//templates_closed.txt
Typ	Truefalse		
Keywords	Seite {page_number}
Coverage	Lehrmittel Allgemeinbildung
Subject	/Allgemeinbildung/{subject}
Level	{bloom_level}
Title	Hauptstädte Europa		
Question	Sind die folgenden Aussagen richtig oder falsch?		
Points	2		
	Unanswered	Right	Wrong
Paris ist in Frankreich	0	0.5	-0.25
Bern ist in Schweiz	0	0.5	-0.25
Stockholm ist in Danemark	0	-0.25	0.5
Stockholm ist in Schweden	0	0.5	-0.25
Typ    Truefalse
Keywords    Seite {page_number}
Coverage    Lehrmittel Allgemeinbildung
Subject    /Allgemeinbildung/{subject}
Level    {bloom_level}
Title    Kontinente
Question    Sind die folgenden Aussagen richtig oder falsch?
Points    2
    Unanswered    Right    Wrong
Hongkong ist in Europa    0    -0.25    0.5
Los Angeles ist in Nordamerika    0    0.5    -0.25
Buenos Aires ist in Afrika    0    -0.25    0.5
Berlin ist in Asien    0    -0.25    0.5
        """,
        """//steps Drag&drop
1. The user uploads an image or a text with content from a textbook.
2. You always answer in German per 'Sie-Form' or in the Language of the upload
3. You generate 5 questions for each processed image or text. 
4. extract {page_number} from the bottom of the image or text.
5. extract {subject} from the top left or right 5% of the image or text.
6. You develop materials based on the //instruction and //output
7. if there is a graphical representation you generate at least 3 questions about it, focusing on the testing the understanding of the graphical representation and its data.

//instruction
- read the text and identify informations
- refer to 'bloom_levels_closed' for types of question to formulate according to the content of the image or text
- refer to the 'templates_closed.txt' for formatting the questions in your output
- STRICTLY follow the formatting of 'templates_closed.txt'

//bloom_levels_closed 
# Bloom Level: 'Erinnern'
Question Type: For recall-based tasks
Design Approach:
Focus on recognition and recall of facts.
Use straightforward questions that require identification of correct information.
Example:
"How many members are in the Swiss Federal Council? "

# Bloom Level: 'Verstehen'
Question Type: Questions at this level assess comprehension and interpretation
Design Approach:
Emphasize explanation of ideas or concepts.
Questions should assess comprehension through interpretation or summary.
Example:
"Which of the following best describes the role of cantonal governments in Switzerland?"

# Bloom Level: 'Anwenden'
Question Type: Application-based questions evaluate practical knowledge.
Design Approach:
Questions should require the application of knowledge in new situations.
Include scenarios that necessitate the use of learned concepts in practical contexts.
Example:
"If a canton wants to introduce a new educational reform that differs from federal standards, which of the following steps is necessary? "

//output
- OUTPUT should only include the generated questions
- ALWAYS generate 10 questions
- READ the //rules to understand the rules for points and answers.
- STRICTLY follow the formatting of the 'templates_closed.txt'.
- IMPORTANT: the output is just the questions
- No additional explanation. ONLY the questions as plain text. never use ':' as a separator.

//rules
- rules Drag&drop may have 2-4 drop categories and 2 to 10 drag categories: Typ\tDrag&drop\nKeywords\tSeite {page_number}\nCoverage\tLehrmittel Allgemeinbildung\nSubject\t/Allgemeinbildung/{subject}\nLevel\t{bloom_level}\nTitle\tgeneral_title_of_the_question\nQuestion\tgeneral_question_text_placeholder\nPoints\t{Sum_of_correct_answer}\n\tdrop_category1\tdrop_category2\tdrop_category3\ndrag_word_categoory2\t-0.5\t1\t-0.5\ndragword_category3\t-0.5\t-0.5\t1\nDragword_category1\t1\t-0.5\t-0.5

//templates_closed.txt
Typ	Drag&drop		
Keywords	Seite {page_number}
Coverage	Lehrmittel Allgemeinbildung
Subject	/Allgemeinbildung/{subject}
Level	{bloom_level}
Title	Hauptstädte Afrika		
Question	Ordnen Sie die folgenden Hauptstädte dem jeweiligen Land zu.		
Points	3		
	Algerien	Kenia	Namibia
Nairobi	-0.5	1	-0.5
Windhoek	-0.5	-0.5	1
Algier	1	-0.5	-0.5
        """,
        """//steps
1. The user uploads an image or a text or a text with content from a textbook.
2. read the text and identify key topics to be understood
3. read the instructions below
4. generate for each bloom level 2 different custom texts with at least 6 sentences or 70-100 words.
5. You identify 5 possible blanks according to the 'bloom_levels_closed'. 
5. You always answer in German or in the Language of the upload
6. extract {page_number} from the bottom of the image or text.
7. extract {subject} from the top left or right 5% of the image or text.
9. if there is a graphical representation you generate one additional question about it, focusing on the testing the understanding of the graphical representation and its data.
10. ALWAYS follow the guidelines '//JSON Output' for formatting the text.

//bloom_levels_closed 
# Bloom Level: 'Erinnern'
Design Approach:
Write a custom text that focus on recognition and recall of basic facts, terms, and concepts.
Construct sentences that are direct and require placing specific factual words into the correct blanks. 

# Bloom Level: 'Verstehen'
Design Approach:
Write a custom text that necessitate comprehension of concepts or processes.
Blanks should require students to demonstrate understanding by selecting words that correctly complete a sentence according to the context.

//rules
- IMPORTANT: the custom texts are full with no blanks
- IMPORTANT: between each blank there are at least 5 words
- IMPORTANT: Each custom text has at least 6 sentences
- IMPORTANT: generate for each identified blank one wrong plausible blank according to //JSON Output.
- IMPORTANT: the blanks and wrong_substitutes are unique

//JSON Output
[
  {
    "page_number": "{page_number}",
    "subject": "{subject}",
    "bloom_level": "{bloom_level}",
    "text": "Custom Text 1 for Bloom Level Erinnern",
    "blanks": ["blank1", "blank2", "blank3", "blank4", "blank5"],
    "wrong_substitutes": [
      "wrong substitute blank1",
      "wrong substitute blank2",
      "wrong substitute blank3",
      "wrong substitute blank4",
      "wrong substitute blank5"
    ]
  },
  {
    "page_number": "{page_number}",
    "subject": "{subject}",
    "bloom_level": "{bloom_level}",
    "text": "Custom Text 2 for Bloom Level Erinnern",
    "blanks": ["blank1", "blank2", "blank3", "blank4", "blank5"],
    "wrong_substitutes": [
      "wrong substitute blank1",
      "wrong substitute blank2",
      "wrong substitute blank3",
      "wrong substitute blank4",
      "wrong substitute blank5"
    ]
  },
  {
    "page_number": "{page_number}",
    "subject": "{subject}",
    "bloom_level": "{bloom_level}",
    "text": "Custom Text 3 for Bloom Level Verstehen",
    "blanks": ["blank1", "blank2", "blank3", "blank4", "blank5"],
    "wrong_substitutes": [
      "wrong substitute blank1",
      "wrong substitute blank2",
      "wrong substitute blank3",
      "wrong substitute blank4",
      "wrong substitute blank5"
    ]
  },
  {
    "page_number": "{page_number}",
    "subject": "{subject}",
    "bloom_level": "{bloom_level}",
    "text": "Custom Text 4 for Bloom Level Verstehen",
    "blanks": ["blank1", "blank2", "blank3", "blank4", "blank5"],
    "wrong_substitutes": [
      "wrong substitute blank1",
      "wrong substitute blank2",
      "wrong substitute blank3",
      "wrong substitute blank4",
      "wrong substitute blank5"
    ]
  }
]

single question Example Output :
[
  {
    "page_number": "107",
    "subject": "Politik Schweiz",
    "bloom_level": "Erinnern",
    "text": "Switzerland's direct democracy empowers citizens to participate in decision-making through referendums and initiatives. A referendum allows citizens to challenge laws passed by the parliament, requiring 50,000 signatures within 100 days to trigger a national vote. Conversely, a popular initiative enables citizens to propose constitutional amendments, needing 100,000 signatures within 18 months.",
    "blanks": ["challenge laws", "50,000 signatures", "100 days", "100,000 signatures", "18 months"],
    "wrong_substitutes": [
      "change laws",
      "10,000 signatures",
      "1000 days",
      "200,000 signatures",
      "12 months"
    ]
  }
]
""",
        """//steps FiB
1. The user uploads an image or a text with content from a textbook.
2. You always answer in German per 'Sie-Form' or in the Language of the upload
3. You generate 5 questions for each processed image or text. 
4. extract {page_number} from the bottom of the image or text.
5. extract {subject} from the top left or right 5% of the image or text.
6. You develop materials based on the //instruction and //output
7. if there is a graphical representation you generate at least 2 questions about it, focusing on the testing the understanding of the graphical representation and its data.

//instruction
- read the text and identify informations
- refer to 'bloom_levels_open' for types of question to formulate according to the content of the image or text
- refer to the 'templates_open.txt' for formatting the questions in your output
- STRICTLY follow the formatting of 'templates_open.txt'

//bloom_levels_open 
Bloom Level Remember:
Question Type: For recall-based tasks
Design Approach:
- Create questions that prompt factual recall.
- Ensure clear and concise wording.
- provide answer choices.
Specify the correct answer.
Example:
"How many members are there in the Swiss Federal Council? Name the principle that ensures a multi-party representation within the Federal Council."

Bloom Level Understand:
Question Type: Questions at this level assess comprehension and interpretation
Design Approach:
Focus on understanding relationships between concepts.
Ensure clarity in instructions.
Example:
"Summarize the principles of Swiss federalism and how it differs from unitary states. What are the key responsibilities of the cantonal governments, and how do they interact with the federal government?"

Bloom Level Apply:
Question Type: Application-based questions evaluate practical knowledge
Design Approach:
Optimal for scenario-based questions.
Specify a situation and ask students to apply concepts.
Use clear criteria for correctness.
Example:
“A group of citizens is proposing a national referendum to amend the Swiss Constitution to include environmental protection as a fundamental duty of the state. Describe the process this group must follow to bring their proposal to a national vote.”

Bloom Level Analyze:
Question Type: For analytical tasks, consider using matching, sorting, or categorization questions. These can be automatically graded based on correct associations.
Design Approach:
Provide a set of items (e.g., concepts, definitions, scenarios).
Ask students to match or categorize them appropriately.
Use clear criteria to determine correctness (e.g., correct matches).
Example:
“Analyze the impact of direct democracy on the legislative process in Switzerland. How does the ability of citizens to call referendums and propose initiatives affect the creation and implementation of laws?”

//output
- OUTPUT should only include the generated questions
- ALWAYS generate 10 questions
- READ the //rules to understand the rules for points and answers.
- STRICTLY follow the formatting of the 'templates_open.txt'.
- IMPORTANT: the output is just the questions
- No additional explanation. ONLY the questions as plain text. never use ':' as a separator.

//rules
- rules FiB: Type\tFIB\nTitle\tgeneral_title_of_the_question\nPoints\t3\nText\tgeneral_question_text_placeholder\n3\tcorrect_answer_placeholder_1\t150


//templates_open.txt
Type	FIB	
Title	Swiss federalism	
Points	3	
Text	Summarize the principles of Swiss federalism and how it differs from unitary states. What are the key responsibilities of the cantonal governments, and how do they interact with the federal government? 	
3	Swiss federalism divides powers between the federal government and cantons, allowing cantonal autonomy, especially in education, health, and policing. Unlike unitary states with centralized power, this structure supports regional diversity and local decision-making, with coordinated federal-cantonal collaboration on national issues.	150
""",
        """//steps Essay
1. The user uploads an image or a text with content from a textbook.
2. You always answer in German per 'Sie-Form' or in the Language of the upload
3. You generate 5 questions for each processed image or text. 
4. extract {page_number} from the bottom of the image or text.
5. extract {subject} from the top left or right 5% of the image or text.
6. You develop materials based on the //instruction and //output
7. if there is a graphical representation you generate at least 2 questions about it, focusing on the testing the understanding of the graphical representation and its data.

//instruction
- read the text and identify informations
- refer to 'bloom_levels_open' for types of question to formulate according to the content of the image or text
- refer to the 'templates_open.txt' for formatting the questions in your output
- STRICTLY follow the formatting of 'templates_open.txt'

//bloom_levels_open 
Bloom Level Analyze:
Question Type: For analytical tasks, consider using matching, sorting, or categorization questions. These can be automatically graded based on correct associations.
Design Approach:
Provide a set of items (e.g., concepts, definitions, scenarios).
Ask students to match or categorize them appropriately.
Use clear criteria to determine correctness (e.g., correct matches).
Example:
“Analyze the impact of direct democracy on the legislative process in Switzerland. How does the ability of citizens to call referendums and propose initiatives affect the creation and implementation of laws?”

Bloom Level Evaluate:
Question Type: Evaluative questions assess critical thinking.
Design Approach:
Present a scenario, argument, or case study.
Ask students to evaluate, critique, or make judgments.
Define clear criteria for correct answers.
Example:
"Evaluate the impact of direct democracy on social policy development in Switzerland. Consider specific examples where referendums or initiatives have significantly influenced social policies related to immigration, education, or healthcare. Assess the pros and cons of having such a direct mechanism for policy change "

Bloom Level Create:
Question Type: For creative tasks, employ open-ended questions, essay prompts, or project-based assignments that allow for originality and innovation.
Design Approach:
Encourage synthesis of ideas and concepts learned previously.
Ask students to develop a unique product, solution, or idea.
Provide guidelines that allow for creativity while still being assessable.
Foster originality and encourage exploration of new ideas or perspectives.
Example:
"Create a proposal for a new political party in Switzerland that addresses a gap you've identified in the current political landscape. Define the party's core values, target demographic, and main political agenda. "

//output
- OUTPUT should only include the generated questions
- ALWAYS generate 8 questions
- READ the //rules to understand the rules for points and answers.
- STRICTLY follow the formatting of the 'templates_open.txt'.
- IMPORTANT: the output is just the questions
- No additional explanation. ONLY the questions as plain text. never use ':' as a separator.

//rules
- rules Essay: Type\tESSAY\nTitle\tgeneral_title_of_the_question\nQuestion\tgeneral_question_text_placeholder\nPoints\t5\nMin\t200\nMax\t2000

//templates_open.txt
Typ	ESSAY
Title	Political Party
Question	Create a proposal for a new political party in Switzerland that addresses a gap you've identified in the current political landscape. Define the party's core values, target demographic, and main political agenda. 
Points	1
Min	200
Max	2000
""",
    ]

    # Input method selection
    input_method = st.radio("Choose input method:", ["File Upload", "Text Input"])

    if input_method == "File Upload":
        uploaded_file = st.file_uploader("Choose a file", type=["txt", "docx", "png", "jpg", "jpeg"])
        if uploaded_file:
            file_prefix = os.path.splitext(uploaded_file.name)[0]
            mime_type, _ = mimetypes.guess_type(uploaded_file.name)
            if mime_type and mime_type.startswith('image/'):
                content = upload_to_gemini(uploaded_file, mime_type)
            else:
                content = process_text_file(uploaded_file)
    else:
        content = st.text_area("Enter your text here:")
        file_prefix = "manual_input"

    if st.button("Process"):
        if not content:
            st.warning("Please provide input before processing.")
            return

        output_folder = "output"
        os.makedirs(output_folder, exist_ok=True)

        chat_session = model.start_chat()
        initial_response = chat_session.send_message([content, "wait for the next interaction of the user."])

        # Save the initial response
        initial_filename = save_response(initial_response.text, 0, file_prefix=file_prefix, output_folder=output_folder)
        st.download_button(
            label=f"Download Initial Response",
            data=initial_response.text,
            file_name=os.path.basename(initial_filename),
            mime="text/plain"
        )

        # Process each pre-saved message
        for i, message in enumerate(messages, 1):
            response = chat_session.send_message(message)
            filename = save_response(response.text, i, file_prefix=file_prefix, output_folder=output_folder)
            st.download_button(
                label=f"Download Response {i}",
                data=response.text,
                file_name=os.path.basename(filename),
                mime="text/plain"
            )

            # Apply transformation if configured
            if i == 6:  # Assuming we want to transform the 6th response
                transformed_text = transform_script_1.transform_output(response.text)
                transformed_filename = save_response(transformed_text, i, suffix="_transformed", file_prefix=file_prefix, output_folder=output_folder)
                st.download_button(
                    label=f"Download Transformed Response {i}",
                    data=transformed_text,
                    file_name=os.path.basename(transformed_filename),
                    mime="text/plain"
                )

        st.success("Processing complete!")

if __name__ == "__main__":
    main()
