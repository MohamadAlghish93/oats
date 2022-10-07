# Wordcloud
import nltk

from lib.doc_process import read_pdf_resume, read_word_resume
from lib.wordcloud import clean_job_decsription, create_word_cloud
from ml.compare import get_resume_score

# CLI 
if __name__ == '__main__':

    # download missing requirement for nltk
    nltk.download('stopwords')
    nltk.download('punkt')

    extn = input("Enter File Extension: ")
    if extn == "pdf":
        resume = read_pdf_resume('Mohamad_Alghosh-2022.pdf')
    else:
        resume = read_word_resume('test_resume.docx')
    
    job_description = input("\nEnter the Job Description: ")

    ## Get a Keywords Cloud
    clean_jd = clean_job_decsription(job_description)
    create_word_cloud(clean_jd)
    
    text = [resume, job_description]
    
    ## Get a Match
    get_resume_score(text)
