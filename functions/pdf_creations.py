from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from db.uploaded_files import save_file
from fastapi import HTTPException
from pymongo.errors import PyMongoError
import os



def pdf_creations(nameFile, Name, date, nat):
    try:
        if not os.path.exists("pdf_files"):
            os.makedirs("pdf_files")
        file_name = f"{nameFile}.pdf"
        directory = "pdf_files"
        print(os.getcwd())
        full_path = os.path.join(os.getcwd(), directory, file_name)
        print(full_path)
        doc = SimpleDocTemplate(full_path, pagesize=A4)
        document_title = "TEST_PDF"
        styles = getSampleStyleSheet()
        normal_style = styles["Normal"]
        title_style = styles["Title"]

        
        elements = []

    
        title = Paragraph("Nachweis für die Anerkennung der Staatenlosigkeit", title_style)
        elements.append(title)
        elements.append(Spacer(1, 12))

        
        subtitle = Paragraph(f"von {Name}", normal_style)
        elements.append(subtitle)
        elements.append(Spacer(1, 24))

        
        main_text = f"""
        Die folgenden Informationen wurden nach den Bestimmungen des Übereinkommens über die
        Rechtsstellung von Staatenlosen und völkerrechtlichen Standards erhoben.
        Alle Angaben unterliegen der Schweigepflicht.
        """
        paragraph = Paragraph(main_text, normal_style)
        elements.append(paragraph)
        elements.append(Spacer(1, 24))
        
        main_text = f"""
        Ich, {Name}, stelle einen Antrag auf Zuerkennung internationalen Schutzes (Rechtsstellung der
        Staatenlosen gemäß Art. 1 des Übereinkommens über die Rechtsstellung von Staatenlosen, in
        Kraft getreten gemäß Art. 3 Abs. 2 des Gesetzes vom 12. April 1976 zum Übereinkommen über
        die Rechtsstellung von Staatenlosen (BGBl. 1976 II S. 473)).
        """
        paragraph = Paragraph(main_text, normal_style)
        elements.append(paragraph)
        elements.append(Spacer(1, 24))
        
        name_field = Paragraph(f"Name: {Name}", normal_style)
        birthday_field = Paragraph(f"Birthday: {date}", normal_style)
        nationality_field = Paragraph(f"Nationality: {nat}", normal_style)

        elements.extend([name_field, Spacer(1, 12), birthday_field, Spacer(1, 12), nationality_field])

        
        doc.build(elements)

        try:
            save_file(full_path, f"{nameFile}.pdf", "dima")
            if os.path.exists(full_path):
                os.remove(full_path)
        except PyMongoError as e:
            raise HTTPException(status_code=404, detail=f"Some error with database'{str(e)}'")
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=f"File system error: file not found -'{str(e)}'")
        except PermissionError as e:
            raise HTTPException(status_code=404, detail=f"Access error: not enough permissions -'{str(e)}'")
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Some error'{str(e)}'")
    except Exception as e:
            raise HTTPException(status_code=404, detail=f"Some error'{str(e)}'")