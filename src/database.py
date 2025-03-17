import mariadb  # type: ignore # Replace mysql.connector with mariadb
from json import dumps

# Konfigurasi database dengan meningkatkan ukuran paket
DB_CONFIG = {
    "host": "localhost",
    "user": "root",  # Ganti dengan username MariaDB kamu
    "password": "",  # Ganti dengan password MariaDB kamu
    "database": "gptscraper",  # Ganti dengan nama database yang ingin digunakan
    "charset": "utf8mb4",
    "pool_size": 5,
    "pool_name": "gpt_scraper_pool",
    "pool_reset_session": True
}

def create_connection():
    try:
        conn = mariadb.connect(**DB_CONFIG)
        if conn.is_connected():
            print("Koneksi ke MariaDB berhasil!")
            # Increase session parameters
            cursor = conn.cursor()
            cursor.execute("SET GLOBAL max_allowed_packet=1073741824;")  # 1GB
            cursor.execute("SET GLOBAL net_buffer_length=1048576;")  # 1MB
            cursor.execute("SET GLOBAL interactive_timeout=86400;")  # 24 hours
            cursor.execute("SET GLOBAL wait_timeout=86400;")  # 24 hours
            cursor.close()
        return conn
    except mariadb.Error as e:
        print(f"Error saat menghubungkan ke MariaDB: {e}")
        return None

def createTable():
    """Create Scraper table if doesnt exist"""
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute(""" 
CREATE TABLE IF NOT EXISTS Scraper (
                       scraper_id INT AUTO_INCREMENT PRIMARY KEY, 
                       link TEXT, 
                       title VARCHAR(255), 
                       text LONGTEXT, 
                       lowercased_text LONGTEXT, 
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
); """)
        conn.commit()
        cursor.close()
        conn.close()
        print("Scraper table berhasil dibuat")

def insertScraper(title, link, text, lowercased_text):
    """Add scraper to database"""
    # Convert to JSON strings in chunks if needed for large datasets
    try:
        text_json = dumps(text)
        lowercased_text_json = dumps(lowercased_text)
        
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            # Use prepared statements for better handling of large data
            query = "INSERT INTO Scraper (title, link, text, lowercased_text) VALUES (?,?,?,?)"
            cursor.execute(query, (title, link, text_json, lowercased_text_json))
            conn.commit()
            scraper_id = cursor.lastrowid
            cursor.close()
            conn.close()
            print(f"Scraper berhasil dimasukkan dengan ID: {scraper_id}")
            return scraper_id
    except mariadb.Error as e:
        print(f"Error inserting data: {e}")
        if "packet bigger than" in str(e):
            print("Data too large, trying alternative method...")
            # Try direct SQL method for large data
            return _insert_large_scraper(title, link, text, lowercased_text)
        return None

def _insert_large_scraper(title, link, text, lowercased_text):
    """Alternative method for inserting very large data"""
    import io
    
    text_json = dumps(text)
    lowercased_text_json = dumps(lowercased_text)
    
    # Create connection with local infile loading enabled
    conn = mariadb.connect(
        **DB_CONFIG
    )
    
    if conn:
        try:
            cursor = conn.cursor()
            
            # First insert a placeholder record
            query = "INSERT INTO Scraper (title, link, text, lowercased_text) VALUES (?, ?, '', '')"
            cursor.execute(query, (title, link))
            conn.commit()
            scraper_id = cursor.lastrowid
            
            # Then update with the actual large text data
            update_query = "UPDATE Scraper SET text = ?, lowercased_text = ? WHERE scraper_id = ?"
            cursor.execute(update_query, (text_json, lowercased_text_json, scraper_id))
            conn.commit()
            
            cursor.close()
            conn.close()
            print(f"Large scraper data inserted successfully with ID: {scraper_id}")
            return scraper_id
            
        except mariadb.Error as e:
            print(f"Error in alternative insert method: {e}")
            conn.close()
            return None

def getScraper():
    """Get all scraper from database"""
    conn = create_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Scraper")
        scraper = cursor.fetchall()
        cursor.close()
        conn.close()
        return scraper

def getScraperById(scraperId):
    """Get single scraper by ID from database"""
    conn = create_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM Scraper WHERE scraper_id = ?"
        cursor.execute(query, (scraperId,))
        scraper = cursor.fetchone()
        cursor.close()
        conn.close()
        return scraper
    
def updateScraperById(scraperId, title):
    """Update 1 scraper by ID from database"""
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        query = "UPDATE Scraper SET title = ? WHERE scraper_Id = ?"
        cursor.execute(query, (title, scraperId))
        conn.commit()
        cursor.close()
        conn.close()
        print("Scraper berhasil diupdate")

def deleteScraperById(scraperId):
    """Delete 1 scraper by ID from database"""
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        query = "DELETE FROM Scraper WHERE scraper_id = ?"
        cursor.execute(query, (scraperId,))
        conn.commit()
        cursor.close()
        conn.close()
        print("Scraper berhasil dihapus")

if __name__ == "__main__":
    connection = create_connection()
    #createTable() # Jalankan kode ini untuk membuat table scraper
    if connection:
        connection.close()