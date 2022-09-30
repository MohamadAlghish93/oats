# system libs
from distutils import extension
import io
import os
import re
import operator
from datetime import datetime
import time



# Wordcloud
import nltk
from nltk.tokenize import word_tokenize 
from nltk.corpus import stopwords
from wordcloud import WordCloud
from nltk.probability import FreqDist

# Chart libs
# import matplotlib
# import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ML libs
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Web interface UI
from pywebio.input import *
from pywebio.output import *
from pywebio import start_server, config


now = datetime.now()
tmp_folder = './tmp/'
CONST_PDF_EXT = '.pdf'
CONST_PNG_EXT = 'png'

# helper function
# loading spin
def loading():
    with put_loading(shape='border', color='primary').style('width:4rem; height:4rem'):
        time.sleep(2)


def clean_job_decsription(jd):
    ''' a function to create a word cloud based on the input text parameter '''
    ## Clean the Text
    # Lower
    clean_jd = jd.lower()
    # remove punctuation
    clean_jd = re.sub(r'[^\w\s]', '', clean_jd)
    # remove trailing spaces
    clean_jd = clean_jd.strip()
    # remove numbers
    clean_jd = re.sub('[0-9]+', '', clean_jd)
    # tokenize 
    clean_jd = word_tokenize(clean_jd)
    # remove stop words
    stop = stopwords.words('english')
    #stop.extend(["AT_USER","URL","rt","corona","coronavirus","covid","amp","new","th","along","icai","would","today","asks"])
    clean_jd = [w for w in clean_jd if not w in stop] 
    
    return(clean_jd)


def create_word_cloud(jd):
    corpus = jd
    fdist = FreqDist(corpus)
    #print(fdist.most_common(100))
    words = ' '.join(corpus)
    words = words.split()

    # create a empty dictionary
    data = dict()
    #  Get frequency for each words where word is the key and the count is the value
    for word in (words):
        word = word.lower()
        data[word] = data.get(word, 0) + 1
    # Sort the dictionary in reverse order to print first the most used terms    
    dict(sorted(data.items(), key=operator.itemgetter(1),reverse=True))
    word_cloud = WordCloud(width = 800, height = 800, background_color ='white',max_words = 500)
    word_cloud.generate_from_frequencies(data)

    return word_cloud.to_image()
    

#get the match percentage
def get_resume_score(text):
    cv = CountVectorizer(stop_words='english')
    count_matrix = cv.fit_transform(text)
    #Print the similarity scores
    print("\nSimilarity Scores:")
    #print(cosine_similarity(count_matrix))
    #get the match percentage
    matchPercentage = cosine_similarity(count_matrix)[0][1] * 100
    matchPercentage = round(matchPercentage, 2) # round to two decimal

    return matchPercentage
    # print("Your resume matches about "+ str(matchPercentage)+ "% of the job description.")


def draw_pie_chart(percentage):
    labels = ["Not Match", "Match"]

    # Create subplots: use 'domain' type for Pie subplot
    fig = make_subplots(rows=1, cols=1, specs=[[{'type':'domain'}]])
    fig.add_trace(go.Pie(labels=labels, values=[100 - percentage, percentage], name="resume matches"),
                1, 1)

    # Use `hole` to create a donut-like pie chart
    fig.update_traces(hole=.5, hoverinfo="label+percent+name")

    fig.update_layout(
        title_text="Your resume matches")
    html = fig.to_html(include_plotlyjs="require", full_html=False)
    put_html(html)

@config(theme='dark')
def main():
    try:
        
        # download missing requirement for nltk
        nltk.download('stopwords')
        nltk.download('punkt')

        resume_source = file_upload("Select a resume:", accept="application/*", required=True)
        # print(resume_source)
        filename, file_extension = os.path.splitext(resume_source['filename'])
        dt_string = now.strftime("%d%m%Y%H%M%S")
        print(file_extension)
        tmp_file = f'{filename}_tmp{file_extension}'

        with put_loading(shape='border', color='warning').style('width:4rem; height:4rem'):
            if resume_source is not None:
                # TODO check folder tmp exist
                file_tmp_path = f'{tmp_folder}{tmp_file}'
                with open(file_tmp_path, "wb") as file:
                    file.write(resume_source['content'])

                if file_extension.lower() == CONST_PDF_EXT:
                    resume = read_pdf_resume(file_tmp_path)
                else:
                    resume = read_word_resume(file_tmp_path)


        job_description = textarea('Enter the Job Description:', required=True, rows=20)

        ## Get a Keywords Cloud
        clean_jd = clean_job_decsription(job_description)
        word_cloud = create_word_cloud(clean_jd)

        text = [resume, job_description]

        # loading()

        put_processbar('bar', auto_close=True);
        for i in range(1, 11):
            set_processbar('bar', i / 10)
            time.sleep(0.2)

        # Get a Match
        resume_score = get_resume_score(text)
        put_markdown(rf""" # Resume Score
        Your resume matches about `{str(resume_score)}`% of the job description.
        """)

        draw_pie_chart(resume_score)

        img_byte_arr = io.BytesIO()
        word_cloud.save(img_byte_arr, format=CONST_PNG_EXT)
        put_collapse('Cloud Image', [
            put_markdown(rf""" # Cloud Image
            """),
            put_file(f'{dt_string}.{CONST_PNG_EXT}', img_byte_arr.getvalue()),
            put_image(word_cloud)
        ], open=True)


    except Exception as e:
        put_text(f'Error : {e}').style('color: red;')

if __name__ == '__main__':
    start_server(main, debug=True, port=8080, cdn=False)


# CLI 
# if __name__ == '__main__':

#     # download missing requirement for nltk
#     nltk.download('stopwords')
#     nltk.download('punkt')

#     extn = input("Enter File Extension: ")
#     #print(extn)
#     if extn == "pdf":
#         resume = read_pdf_resume('Mohamad_Alghosh-2022.pdf')
#     else:
#         resume = read_word_resume('test_resume.docx')
    
#     job_description = input("\nEnter the Job Description: ")

#     ## Get a Keywords Cloud
#     clean_jd = clean_job_decsription(job_description)
#     create_word_cloud(clean_jd)
    
#     text = [resume, job_description]
    
#     ## Get a Match
#     get_resume_score(text)