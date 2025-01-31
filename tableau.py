import tableauserverclient as TSC
from dotenv import load_dotenv
import os
import zipfile
import shutil
import csv
load_dotenv()

# Load sensitive credentials from environment variables
TABLEAU_USERNAME = os.getenv("TABLEAU_USERNAME")
TABLEAU_PASSWORD = os.getenv("TABLEAU_PASSWORD")
TABLEAU_SITE_ID = os.getenv("TABLEAU_SITE_ID")
TABLEAU_SERVER_URL = os.getenv("TABLEAU_SERVER_URL")

chart_type_to_url = {
    "piechart": "piechart_workbook",
    "bargraph": "bargraph_workbook",
    "bubbles": "bubbles_workbook",
    "map": "map_workbook",
    "linegraph": "linegraph_workbook",
}

def update_tableau_workbook(csv_content, workbook_id, chart_type):
    try:
        # Step 1: Save CSV content to a file
        print("Saving CSV content to file...")
        csv_file_path = "data_source.csv"
        with open(csv_file_path, "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile)
            for line in csv_content:
                cleaned_line = line.replace("```", "").strip()
                if cleaned_line:
                    csvwriter.writerow(cleaned_line.split(","))
        print(f"CSV content saved to {csv_file_path}")

        # Step 2: Authenticate with Tableau server
        print("Authenticating with Tableau server...")
        tableau_auth = TSC.TableauAuth(TABLEAU_USERNAME, TABLEAU_PASSWORD, site_id=TABLEAU_SITE_ID)
        server = TSC.Server(TABLEAU_SERVER_URL)

        with server.auth.sign_in(tableau_auth):
            print("Successfully authenticated with Tableau server.")

            # Step 3: Download the workbook (only once)
            print(f"Downloading workbook with ID {workbook_id}...")
            file_path = server.workbooks.download(workbook_id)
            print(f"Downloaded workbook to {file_path}.")

            # Step 4: Extract the workbook content
            print("Extracting workbook content...")
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                zip_ref.extractall("extracted_workbook")
            print("Workbook content extracted to 'extracted_workbook'.")

            # Step 5: Replace all CSVs in the extracted workbook with new data
            print(f"Replacing CSV files in 'extracted_workbook' with {csv_file_path}...")
            csv_replaced = False  # To track if the CSV was replaced
            for root, dirs, files in os.walk("extracted_workbook"):
                print(f"Root: {root}, Dirs: {dirs}, Files: {files}")
                for file in files:
                    print(f"Found file: {file}")
                    if file.endswith(".csv"):
                        target_csv = os.path.join(root, file)
                        shutil.copy2(csv_file_path, target_csv)  # Replace the CSV file
                        print(f"Replaced {target_csv} with the new CSV data.")
                        csv_replaced = True
            
            # Ensure the CSV file was actually replaced
            if not csv_replaced:
                print("No CSV files found to replace.")
                return

            # Step 6: Repack the workbook
            print("Repacking the workbook...")
            new_workbook_path = "repacked_workbook.twbx"
            with zipfile.ZipFile(new_workbook_path, "w") as zipf:
                for root, dirs, files in os.walk("extracted_workbook"):
                    for file in files:
                        file_path = os.path.join(root, file)
                        archive_path = os.path.relpath(file_path, "extracted_workbook")
                        zipf.write(file_path, archive_path)
            print(f"Repacked workbook saved to {new_workbook_path}.")

            # Step 7: Publish the workbook with updated data
            print(f"Publishing the workbook with the name: {chart_type_to_url[chart_type]}")
            new_workbook = TSC.WorkbookItem(name=chart_type_to_url[chart_type], project_id="457072ed-5eff-4cf1-9d16-e09aa7b2556d")
            published_workbook = server.workbooks.publish(new_workbook, new_workbook_path, "Overwrite")
            print(f"Workbook published with ID {published_workbook.id}.")

            # Step 8: Generate the workbook URL
            workbook_url = f"{TABLEAU_SERVER_URL}/#/site/{TABLEAU_SITE_ID}/views/{published_workbook.name}/Sheet1#1"
            print(f"Generated workbook URL: {workbook_url}")
            return workbook_url

    except Exception as e:
        print(f"Error occurred: {e}")


# Test the function with the workbook ID and chart type
csv_content = [
    "Category,Value",
    "Category A,156",
    "Category B,156",
    "Category C,45"
]
workbook_id = "0fda6ed2-87d9-4c00-9a35-ed6c0cddfe49"
chart_type = "piechart"
url = update_tableau_workbook(csv_content, workbook_id, chart_type)
if url:
    print(f"Updated workbook URL: {url}")
else:
    print("Failed to update the workbook.")
