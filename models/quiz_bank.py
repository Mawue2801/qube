import gdown 
import csv 
import os 
 
class QuizBank:        
    @staticmethod
    def load_store_info(): 
        # Download CSV file 
        csv_file_path = 'quiz_store.csv'
        folder_id = '17rcjuUga_WW33UaKyZwLOiIpDFm387tf'
        url = f"https://drive.google.com/uc?id={folder_id}" 
        gdown.download(url, csv_file_path, quiet=False) 
 
        # Parse CSV file to get file names and IDs 
        quizzes = [] 
        with open(csv_file_path, 'r', encoding='utf-8') as file: 
            reader = csv.DictReader(file) 
            for row in reader: 
                quizzes.append( 
                    { 
                    'file_id': row['file_id'], 
                    'year': row['year'], 
                    'stage': row['stage'], 
                    'day': row['day'], 
                    'contest': row['contest'], 
                    'file_name': row['file_name'], 
                    'schools': row['schools'] 
                } 
                ) 
        # Delete the downloaded CSV file
        os.remove(csv_file_path)
 
        return quizzes
    
    @staticmethod
    def download_file(file_id,output_path): 
        # Download file from qube store 
        url = f"https://drive.google.com/uc?id={file_id}" 
        gdown.download(url, output_path, quiet=False) 
    
    @staticmethod
    def append_to_local_csv(item, output_path):
        # Create the directory if it does not exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Check if file is empty, write header if needed
            if os.path.getsize(output_path) == 0:
                writer.writerow(['file_id', 'year', 'stage', 'day', 'contest', 'file_name', 'schools'])

            writer.writerow([
                item['file_id'],
                item['year'],
                item['stage'],
                item['day'],
                item['contest'],
                item['file_name'],
                item['schools']
            ])

    @staticmethod
    def read_local_csv(file_path):
        data = []
        with open(file_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append({
                    'file_id': row['file_id'],
                    'year': row['year'],
                    'stage': row['stage'],
                    'day': row['day'],
                    'contest': row['contest'],
                    'file_name': row['file_name'],
                    'schools': row['schools']
                })
        return data