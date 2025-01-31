import tableauserverclient as TSC
from dotenv import load_dotenv
import os
load_dotenv()

tableau_auth = TSC.TableauAuth(
    os.getenv("TABLEAU_USERNAME"),
    os.getenv("TABLEAU_PASSWORD"),
    os.getenv("TABLEAU_SITE_ID")
)

server = TSC.Server(os.getenv("TABLEAU_SERVER_URL"))

with server.auth.sign_in(tableau_auth):
    workbooks, _ = server.workbooks.get()
    for workbook in workbooks:
        print(f"Workbook Name: {workbook.name}, ID: {workbook.id}")
    projects, _ = server.projects.get()
    for project in projects:
        print(f"Project Name: {project.name}, ID: {project.id}")