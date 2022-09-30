# system libs
import io
import os
from datetime import datetime
import time


# Wordcloud
import nltk


# Web interface UI
from pywebio.input import *
from pywebio.output import *
from pywebio import start_server, config

# local lib
from lib import doc_process, wordcloud, charty
from ml.compare import get_resume_score

now = datetime.now()
_tmp_folder = './tmp/'
CONST_PDF_EXT = '.pdf'
CONST_PNG_EXT = 'png'

# helper function
# loading spin
def loading():
    with put_loading(shape='border', color='primary').style('width:4rem; height:4rem'):
        time.sleep(2)


@config(theme='dark')
def main():
    try:        

        # download missing requirement for nltk
        nltk.download('stopwords')
        nltk.download('punkt')

        resume_source = file_upload("Select a resume:", accept="application/*", required=True)
        filename, file_extension = os.path.splitext(resume_source['filename'])
        dt_string = now.strftime("%d%m%Y%H%M%S")
        tmp_file = f'{filename}_tmp{file_extension}'

        with put_loading(shape='border', color='warning').style('width:4rem; height:4rem'):
            if resume_source is not None:
                # TODO check folder tmp exist
                file_tmp_path = f'{_tmp_folder}{tmp_file}'
                with open(file_tmp_path, "wb") as file:
                    file.write(resume_source['content'])

                if file_extension.lower() == CONST_PDF_EXT:
                    resume = doc_process.read_pdf_resume(file_tmp_path)
                else:
                    resume = doc_process.read_word_resume(file_tmp_path)


        job_description = textarea('Enter the Job Description:', required=True, rows=20)

        ## Get a Keywords Cloud
        clean_jd = wordcloud.clean_job_decsription(job_description)
        word_cloud = wordcloud.create_word_cloud(clean_jd)

        text = [resume, job_description]

        # loading()

        put_processbar('bar', auto_close=True);
        for i in range(1, 11):
            set_processbar('bar', i / 10)
            time.sleep(0.2)

        # Get a Match
        resume_score = get_resume_score(text)
        put_markdown(rf""" # Similarity Scores:
        Your resume matches about `{str(resume_score)}%` of the job description.
        """)

        html = charty.draw_pie_chart(resume_score)
        put_html(html)

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
