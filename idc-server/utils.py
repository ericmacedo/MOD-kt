def pdf_to_string(file):
    from io import StringIO

    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfdocument import PDFDocument
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.pdfpage import PDFPage
    from pdfminer.pdfparser import PDFParser

    output_string = StringIO()

    parser = PDFParser(file)
    doc = PDFDocument(parser)
    rsrcmgr = PDFResourceManager()
    device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.create_pages(doc):
        interpreter.process_page(page)

    return(output_string.getvalue())
    
def process_text(text:str) -> str:
    # TODO Develop text processing algorithm
    import string, re
    from nltk.corpus import stopwords

    def strip_tags(text: str) -> str:
        p = re.compile(r'<.*?>')
        return p.sub('', text)

    punctuation = r"[{0}]".format(re.sub(r"[-']", "", string.punctuation))

    stop_words = stopwords.words("english")
    
    tokens = list(filter(lambda x: x != "", [                       # 6th extra whitespaces
        re.sub(r"^\d+$", r"", i) for i in re.findall(r"\S+",    # 5th numerics
            re.sub(punctuation, " ",                            # 4th Punctuation 
                re.sub(r'[^\x00-\xb7f\xc0-\xff]', r' ',         # 3th symbols 
                    strip_tags(                                 # 2nd tags
                        text.lower()                            # 1st lowercase 
                    )
                ) 
            )
        )
    ]))

    tokens = [
        token
        for token in tokens
        if not token in stop_words]

    return " ".join(tokens).strip()

def get_userData(userId:str) -> list:
    from models import Corpus
    corpus = Corpus.get_items(userId=userId)

    return corpus